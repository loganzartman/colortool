from pytermfx import Terminal, Color
from pytermfx.tools import read_line
from css_named_colors import name_color_map as CSS_NAMED_COLORS
import colorsys

SWATCH_WIDTH = 4

class ColorParseError(Exception):
    pass

def main():
    t = Terminal()

    def update(s):
        t.style_reset()
        t.clear_line()
        fmt = ""
        try:
            col, fmt = parse_color(s)
            t.style(Color.rgb(col[0], col[1], col[2]).bg())
            t.write(" " * SWATCH_WIDTH)
            t.style_reset()
            t.write(" ")
        except ColorParseError:
            t.write(">" * SWATCH_WIDTH," ")
        finally:
            t.cursor_save()
            t.style(Color.hex(0x909090))
            t.cursor_move(0, 1).clear_to_end().write(fmt)
            t.cursor_restore().style_reset()
            t.write(s)

    with t.managed():
        t.set_cbreak(True)
        
        # make space
        t.writeln()
        t.cursor_move(0, -1).flush()
        
        try:
            # read and parse color
            col_str = read_line(t, update)
            col, fmt = parse_color(col_str)
        
            t.writeln().writeln()

            # write converted colors
            formats = (("RGBA", format_rgba(col)),
                       ("RGBA (hex)", format_hex_rgba(col)),
                       ("RGB (hex)", format_hex_rgb(col)))
            format_name_width = max((len(f[0]) for f in formats)) + 2
            for name, value in formats:
                padding = format_name_width - (len(name) + 1)
                t.style(Color.hex(0x909090)).write(name, ":", " " * padding)
                t.style_reset().writeln(value)
            t.flush()
        except ColorParseError:
            t.writeln().writeln()
            t.writeln("Not a color.")

def format_component(s):
    return "{:.4}".format(s)

def format_hex_rgba(col):
    r = int(col[0] * 0xFF) << 24
    g = int(col[1] * 0xFF) << 16
    b = int(col[2] * 0xFF) << 8
    a = int(col[3] * 0xFF)
    return "0x{:08x}".format(r | g | b | a)

def format_hex_rgb(col):
    r = int(col[0] * 0xFF) << 16
    g = int(col[1] * 0xFF) << 8
    b = int(col[2] * 0xFF)
    return "0x{:06x}".format(r | g | b)

def format_rgba(col):
    return ", ".join(format_component(c) for c in col)

def parse_color(s):
    s = s.lstrip().rstrip().lower()
    if s.startswith("#"):
        return parse_css(s[1:])
    if s.startswith("0x"):
        return parse_hex(s[2:])
    if s.startswith("rgb"):
        return parse_rgb(s[3:])
    if s.startswith("hsl"):
        return parse_hsl(s[3:])
    if s in CSS_NAMED_COLORS:
        return parse_css_named(s)
    raise ColorParseError("Unrecognized format")

def parse_color_tuple(s, n):
    try:
        s = s.lstrip("(").rstrip(")")
        components = s.split(",")
        assert(len(components) == n)
    except:
        raise ColorParseError("Malformed tuple")

    try:
        return [int(c) / 255 for c in components], "int"
    except:
        try:
            return [float(c) for c in components], "float"
        except:
            raise ColorParseError("Bad tuple component values")

def parse_rgb(s):
    components, fmt = parse_color_tuple(s, 3)
    return (components[0], components[1], components[2], 1.0), "rgb({})".format(fmt)

def parse_hsl(s):
    components, fmt = parse_color_tuple(s, 3)
    hls = colorsys.rgb_to_hls(components[0], components[1], components[2])
    return (hls[0], hls[2], hls[1], 1.0), "hsl({})".format(fmt)

def parse_css(s):
    try:
        if len(s) > 3:
            return parse_hex(s)[0], "CSS"
        assert(len(s) == 3)

        val = int(s, 16)
        # RGB shorthand
        r = (val >> 8) & 0xF
        g = (val >> 4) & 0xF
        b = (val) & 0xF
        r = r | (r << 4)
        g = g | (g << 4)
        b = b | (b << 4)
        return (r / 255.0, g / 255.0, b / 255.0, 1.0), "CSS (shorthand)"
    except:
        raise ColorParseError("Malformed CSS hex string")

def parse_css_named(s):
    if s not in CSS_NAMED_COLORS:
        raise ColorParseError("'{}' is not a CSS named color.".format(s))
    return parse_css(CSS_NAMED_COLORS[s][1:])[0], "CSS (named)"

def parse_hex(s):
    try:
        val = int(s, 16)
        if len(s) > 6:
            assert(len(s) == 8)
            # packed RGBA (32-bit)
            r = (val >> 24) & 0xFF
            g = (val >> 16) & 0xFF
            b = (val >> 8) & 0xFF
            a = (val) & 0xFF
            fmt = "Hex (RGBA)"
        else:
            assert(len(s) == 6)
            # packed RGB (24-bit)
            a = 255
            r = (val >> 16) & 0xFF
            g = (val >> 8) & 0xFF
            b = (val) & 0xFF
            fmt = "Hex (RGB)"
        return (r / 255.0, g / 255.0, b / 255.0, a / 255.0), fmt
    except:
        raise ColorParseError("Malformed hex string")

if __name__ == "__main__":
    main()