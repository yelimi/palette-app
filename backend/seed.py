from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

COLORS = [
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

BASE_PRICES = {
    "긴소매 티셔츠":      29000,
    "맨투맨/스웨트":      52000,
    "셔츠/블라우스":      62000,
    "후드 티셔츠":        65000,
    "반소매 티셔츠":      25000,
    "피케/카라 티셔츠":   42000,
    "니트/스웨터":        79000,
    "민소매 티셔츠":      22000,
    "기타 상의":          45000,
    "후드 집업":          72000,
    "블루종":             95000,
    "레더/라이더스 재킷": 189000,
    "슈트/블레이저 재킷": 155000,
    "카디건":             68000,
    "경량 패딩/패딩":     99000,
    "사파리/헌팅 재킷":   112000,
    "트러커 재킷":        98000,
    "스타디움 재킷":      135000,
    "나일론/코치 재킷":   89000,
    "트레이닝 재킷":      75000,
    "아노락 재킷":        92000,
    "플리스/뽀글이":      85000,
    "환절기 코트":        185000,
    "무스탕/퍼":          259000,
    "겨울 싱글 코트":     219000,
    "겨울 더블 코트":     255000,
    "겨울 기타 코트":     199000,
    "숏패딩":             155000,
    "롱패딩":             239000,
    "기타 아우터":        95000,
    "데님 팬츠":          75000,
    "트레이닝/조거 팬츠": 52000,
    "코튼 팬츠":          65000,
    "슈트 팬츠/슬랙스":   92000,
    "숏 팬츠":            45000,
    "레깅스":             35000,
    "점프 슈트/오버올":   112000,
    "기타 하의":          65000,
    "미니 원피스":        89000,
    "미디 원피스":        109000,
    "맥시 원피스":        129000,
    "미니 스커트":        55000,
    "미디 스커트":        72000,
    "롱스커트":           85000,
}

# 핏 5종 × 소재 2종 = 상품 변형 10개
FITS = ["오버핏", "슬림핏", "레귤러핏", "루즈핏", "크롭핏"]

MATERIALS = {
    "상의":          ["면", "폴리에스터"],
    "아우터":        ["울", "나일론"],
    "바지":          ["면", "스트레치"],
    "원피스/스커트": ["면", "시폰"],
}

STRUCTURE = {
    "남성": {
        "상의": [
            "긴소매 티셔츠", "맨투맨/스웨트", "셔츠/블라우스", "후드 티셔츠",
            "반소매 티셔츠", "피케/카라 티셔츠", "니트/스웨터", "민소매 티셔츠", "기타 상의",
        ],
        "아우터": [
            "후드 집업", "블루종", "레더/라이더스 재킷", "슈트/블레이저 재킷", "카디건",
            "경량 패딩/패딩", "사파리/헌팅 재킷", "트러커 재킷", "스타디움 재킷",
            "나일론/코치 재킷", "트레이닝 재킷", "아노락 재킷", "플리스/뽀글이",
            "환절기 코트", "무스탕/퍼", "겨울 싱글 코트", "겨울 더블 코트",
            "겨울 기타 코트", "숏패딩", "롱패딩", "기타 아우터",
        ],
        "바지": [
            "데님 팬츠", "트레이닝/조거 팬츠", "코튼 팬츠", "슈트 팬츠/슬랙스",
            "숏 팬츠", "점프 슈트/오버올", "기타 하의",
        ],
    },
    "여성": {
        "상의": [
            "긴소매 티셔츠", "맨투맨/스웨트", "셔츠/블라우스", "후드 티셔츠",
            "반소매 티셔츠", "피케/카라 티셔츠", "니트/스웨터", "민소매 티셔츠", "기타 상의",
        ],
        "아우터": [
            "후드 집업", "블루종", "레더/라이더스 재킷", "슈트/블레이저 재킷", "카디건",
            "경량 패딩/패딩", "사파리/헌팅 재킷", "트러커 재킷", "스타디움 재킷",
            "나일론/코치 재킷", "트레이닝 재킷", "아노락 재킷", "플리스/뽀글이",
            "환절기 코트", "무스탕/퍼", "겨울 싱글 코트", "겨울 더블 코트",
            "겨울 기타 코트", "숏패딩", "롱패딩", "기타 아우터",
        ],
        "바지": [
            "데님 팬츠", "트레이닝/조거 팬츠", "코튼 팬츠", "슈트 팬츠/슬랙스",
            "숏 팬츠", "레깅스", "점프 슈트/오버올", "기타 하의",
        ],
        "원피스/스커트": [
            "미니 원피스", "미디 원피스", "맥시 원피스",
            "미니 스커트", "미디 스커트", "롱스커트",
        ],
    },
}


def _price(subcategory: str, variant_idx: int) -> int:
    """variant_idx(0~9)에 따라 기준가 ±25% 범위에서 가격 변동."""
    base = BASE_PRICES[subcategory]
    ratio = 0.75 + (variant_idx / 9) * 0.5   # 0.75 ~ 1.25
    return max(round(base * ratio / 1000) * 1000, 9000)


def generate_products() -> list:
    products = []
    for gender, categories in STRUCTURE.items():
        for category, subcategories in categories.items():
            mats = MATERIALS[category]
            for subcategory in subcategories:
                for color_name, hex_val in COLORS:
                    # 핏 5 × 소재 2 = 10가지 변형
                    idx = 0
                    for material in mats:
                        for fit in FITS:
                            products.append(models.Product(
                                gender=gender,
                                category=category,
                                subcategory=subcategory,
                                name=f"{color_name} {material} {fit} {subcategory}",
                                color_name=color_name,
                                hex=hex_val,
                                price=_price(subcategory, idx),
                            ))
                            idx += 1
    return products


def seed():
    db = SessionLocal()
    existing = db.query(models.Product).count()
    if existing > 0:
        print(f"기존 상품 {existing}개 삭제 후 재삽입합니다.")
        db.query(models.Product).delete()
        db.commit()

    products = generate_products()

    # 1000개씩 나눠서 커밋 (메모리 효율)
    batch_size = 1000
    for i in range(0, len(products), batch_size):
        db.bulk_save_objects(products[i:i + batch_size])
        db.commit()
        print(f"  {min(i + batch_size, len(products))}/{len(products)} 삽입 중...")

    db.close()

    male = sum(1 for p in products if p.gender == "남성")
    female = sum(1 for p in products if p.gender == "여성")
    print(f"\n완료: 총 {len(products):,}개 (남성 {male:,}개 / 여성 {female:,}개)")
    print(f"색상 {len(COLORS)}가지 × 세부 카테고리 81종 × 변형 10개")


if __name__ == "__main__":
    seed()
