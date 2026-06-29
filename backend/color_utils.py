import math


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def _rgb_to_lab(r: float, g: float, b: float) -> tuple:
    def linear(v):
        return ((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92

    r, g, b = linear(r), linear(g), linear(b)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722)
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    def f(v):
        return v ** (1/3) if v > 0.008856 else 7.787 * v + 16/116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def color_distance(hex1: str, hex2: str) -> float:
    try:
        lab1 = _rgb_to_lab(*_hex_to_rgb(hex1))
        lab2 = _rgb_to_lab(*_hex_to_rgb(hex2))
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))
    except Exception:
        return float("inf")
