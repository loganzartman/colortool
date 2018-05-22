from pytermfx import Terminal, Color
from pytermfx.tools import read_line
import colorsys

SWATCH_WIDTH = 4

class ColorParseError(Exception):
    pass

def main():
    t = Terminal()

    def update(s):
        t.style_reset()
        t.clear_line()
        try:
            col = parse_color(s)
            t.style(Color.rgb(col[0], col[1], col[2]).bg())
            t.write(" " * SWATCH_WIDTH)
            t.style_reset()
            t.write(" ")
        except ColorParseError:
            t.write("░" * SWATCH_WIDTH," ")
        finally:
            t.write(s)

    with t.managed():
        t.set_cbreak(True)
        t.writeln("input color:").flush()
        col_str = read_line(t, update)
        col = parse_color(col_str)
        t.writeln("RGB = ", ", ".join(format_component(c) for c in col[0:3]))
        t.writeln("hex = ", format_hex(col))

def format_component(s):
    return "{:.4}".format(s)

def format_hex(col):
    r = int(col[0] * 255)
    g = int(col[1] * 255)
    b = int(col[2] * 255)
    return "0x{:x}{:x}{:x}".format(r,g,b)

def parse_color(s):
    s = s.lstrip().rstrip().lower()
    if s.startswith("#"):
        return parse_css(s[1:])
    if s.startswith("0x"):
        return parse_hex(s[2:])
    if s.startswith("rgb"):
        components = parse_color_tuple(s[3:], 3)
        return parse_rgb(components)
    if s.startswith("hsl"):
        components = parse_color_tuple(s[3:], 3)
        return parse_hsl(components)
    raise ColorParseError("Unrecognized format")

def parse_color_tuple(s, n):
    try:
        s = s.lstrip("(").rstrip(")")
        components = s.split(",")
        assert(len(components) == n)
    except:
        raise ColorParseError("Malformed tuple")

    try:
        return [int(c) / 255 for c in components]
    except:
        try:
            return [float(c) for c in components]
        except:
            raise ColorParseError("Bad tuple component values")

def parse_rgb(components):
    return (components[0], components[1], components[2], 1.0)

def parse_hsl(components):
    hls = colorsys.rgb_to_hls(components[0], components[1], components[2])
    return (hls[0], hls[2], hls[1], 1.0)

def parse_css(s):
    try:
        if len(s) > 3:
            return parse_hex(s)
        assert(len(s) == 3)

        val = int(s, 16)
        # RGB shorthand
        r = (val >> 8) & 0xF
        g = (val >> 4) & 0xF
        b = (val) & 0xF
        r = r | (r << 4)
        g = g | (g << 4)
        b = b | (b << 4)
        return (r / 255.0, g / 255.0, b / 255.0, 1.0)
    except:
        raise ColorParseError("Malformed CSS hex string")

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
        else:
            assert(len(s) == 6)
            # packed RGB (24-bit)
            a = 255
            r = (val >> 16) & 0xFF
            g = (val >> 8) & 0xFF
            b = (val) & 0xFF
        return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)
    except:
        raise ColorParseError("Malformed hex string")

if __name__ == "__main__":
    main()