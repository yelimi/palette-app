from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

PRODUCTS = [
    {"name": "네이비 코튼 셔츠", "category": "상의", "color_name": "네이비", "hex": "#26354A", "price": 49000},
    {"name": "크림 니트 카디건", "category": "아우터", "color_name": "크림", "hex": "#EEE5D3", "price": 69000},
    {"name": "세이지 와이드 팬츠", "category": "하의", "color_name": "세이지", "hex": "#9BAA91", "price": 59000},
    {"name": "버건디 미디 원피스", "category": "원피스", "color_name": "버건디", "hex": "#7B2D3B", "price": 89000},
    {"name": "라이트 블루 블라우스", "category": "상의", "color_name": "라이트 블루", "hex": "#AFCBE3", "price": 52000},
    {"name": "차콜 슬랙스", "category": "하의", "color_name": "차콜", "hex": "#44474D", "price": 64000},
    {"name": "더스티 핑크 셔츠", "category": "상의", "color_name": "더스티 핑크", "hex": "#D6A7AD", "price": 48000},
    {"name": "머스타드 스웨터", "category": "상의", "color_name": "머스타드", "hex": "#C69B2B", "price": 57000},
    {"name": "올리브 트렌치코트", "category": "아우터", "color_name": "올리브", "hex": "#6B7645", "price": 129000},
    {"name": "화이트 린넨 셔츠", "category": "상의", "color_name": "화이트", "hex": "#F5F5F0", "price": 45000},
    {"name": "블랙 스키니진", "category": "하의", "color_name": "블랙", "hex": "#1C1C1C", "price": 79000},
    {"name": "코랄 니트 탑", "category": "상의", "color_name": "코랄", "hex": "#E07060", "price": 42000},
]


def seed():
    db = SessionLocal()
    if db.query(models.Product).count() > 0:
        print("이미 시드 데이터가 있습니다.")
        db.close()
        return
    for p in PRODUCTS:
        db.add(models.Product(**p))
    db.commit()
    db.close()
    print(f"{len(PRODUCTS)}개 상품 데이터 삽입 완료")


if __name__ == "__main__":
    seed()
