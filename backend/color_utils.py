import math
import io
from collections import Counter
from PIL import Image


# 32가지 팔레트 (seed.py와 동일)
PALETTE = [
    ("블랙",         "#1C1C1C"),
    ("화이트",       "#F5F5F0"),
    ("아이보리",     "#F5EFE0"),
    ("크림",         "#EEE5D3"),
    ("라이트 그레이","#C8C8C8"),
    ("그레이",       "#909090"),
    ("차콜",         "#44474D"),
    ("네이비",       "#1B2B4B"),
    ("블루",         "#3B6BBF"),
    ("스카이 블루",  "#87CEEB"),
    ("라이트 블루",  "#AFCBE3"),
    ("인디고",       "#3B5B8C"),
    ("민트",         "#98D8C8"),
    ("세이지",       "#9BAA91"),
    ("올리브",       "#6B7645"),
    ("카키",         "#7D7A40"),
    ("다크 그린",    "#2D4A3E"),
    ("베이지",       "#D4B896"),
    ("카멜",         "#C19A6B"),
    ("브라운",       "#8B5E3C"),
    ("머스타드",     "#C69B2B"),
    ("옐로우",       "#F5D060"),
    ("오렌지",       "#E07040"),
    ("코랄",         "#E07060"),
    ("레드",         "#CC3333"),
    ("버건디",       "#7B2D3B"),
    ("와인",         "#722F37"),
    ("핑크",         "#E8A0B4"),
    ("더스티 핑크",  "#D6A7AD"),
    ("라이트 핑크",  "#F0D0D8"),
    ("라벤더",       "#B8A9C9"),
    ("퍼플",         "#7B4B8E"),
]


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def _rgb_to_hsl(r: float, g: float, b: float) -> tuple:
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin

    l = (cmax + cmin) / 2

    s = 0.0 if delta == 0 else delta / (1 - abs(2 * l - 1))

    if delta == 0:
        h = 0.0
    elif cmax == r:
        h = 60 * (((g - b) / delta) % 6)
    elif cmax == g:
        h = 60 * ((b - r) / delta + 2)
    else:
        h = 60 * ((r - g) / delta + 4)

    return h, s * 100, l * 100


def _hue_distance(h1: float, h2: float) -> float:
    diff = abs(h1 - h2) % 360
    return min(diff, 360 - diff)


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


def recommend_colors(input_hex: str, top_n: int = 5) -> list:
    """
    색상환 조화(50%) + 명도 대비(35%) + 채도 균형(15%) 기반 색상 추천.
    팔레트 32색 중 입력색을 제외한 상위 top_n개 반환.
    Returns: list of {"color_name": str, "hex": str}
    """
    try:
        h_in, s_in, l_in = _rgb_to_hsl(*_hex_to_rgb(input_hex))
    except Exception:
        return []

    is_achromatic = s_in < 10

    # 색상환 목표 각도 (보색, 분할보색, 삼각배색, 유사색)
    harmonic_hues = [] if is_achromatic else [
        (h_in + 180) % 360,
        (h_in + 150) % 360,
        (h_in + 210) % 360,
        (h_in + 120) % 360,
        (h_in + 240) % 360,
        (h_in + 30)  % 360,
        (h_in - 30)  % 360,
    ]

    scores = []
    for color_name, hex_val in PALETTE:
        if hex_val.upper() == input_hex.upper():
            continue

        try:
            h_p, s_p, l_p = _rgb_to_hsl(*_hex_to_rgb(hex_val))
        except Exception:
            continue

        is_neutral = s_p < 15

        # 1. 색상환 조화 점수
        if is_achromatic or is_neutral:
            hue_score = 0.6
        elif not harmonic_hues:
            hue_score = 0.5
        else:
            min_dist = min(_hue_distance(h_p, t) for t in harmonic_hues)
            hue_score = max(0.0, 1.0 - min_dist / 60)

        # 2. 명도 대비 점수
        brightness_score = min(abs(l_p - l_in) / 50, 1.0)

        # 3. 채도 균형 점수
        if s_in > 60 and is_neutral:
            sat_score = 0.8
        elif s_in < 20 and s_p > 50:
            sat_score = 0.6
        else:
            sat_score = 0.0

        total = hue_score * 0.5 + brightness_score * 0.35 + sat_score * 0.15
        scores.append((total, color_name, hex_val))

    scores.sort(reverse=True)
    return [{"color_name": name, "hex": hx} for _, name, hx in scores[:top_n]]


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB


def extract_dominant_color(image_bytes: bytes) -> str:
    """이미지에서 가장 지배적인 색상을 hex로 추출."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((100, 100))

    raw = img.tobytes()
    pixels = [(raw[i], raw[i+1], raw[i+2]) for i in range(0, len(raw), 3)]
    most_common_rgb = Counter(pixels).most_common(1)[0][0]

    r, g, b = most_common_rgb
    return f"#{r:02X}{g:02X}{b:02X}"
