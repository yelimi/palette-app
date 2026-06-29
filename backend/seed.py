from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

PRODUCTS = [
    # ────────────────────────────────────────────
    # 남성 상의
    # ────────────────────────────────────────────
    # 긴소매 티셔츠
    {"gender": "남성", "category": "상의", "subcategory": "긴소매 티셔츠", "name": "블랙 긴소매 티셔츠", "color_name": "블랙", "hex": "#1C1C1C", "price": 35000},
    {"gender": "남성", "category": "상의", "subcategory": "긴소매 티셔츠", "name": "화이트 긴소매 티셔츠", "color_name": "화이트", "hex": "#F5F5F0", "price": 32000},
    # 맨투맨/스웨트
    {"gender": "남성", "category": "상의", "subcategory": "맨투맨/스웨트", "name": "차콜 맨투맨", "color_name": "차콜", "hex": "#44474D", "price": 52000},
    {"gender": "남성", "category": "상의", "subcategory": "맨투맨/스웨트", "name": "네이비 스웨트셔츠", "color_name": "네이비", "hex": "#1B2B4B", "price": 55000},
    # 셔츠/블라우스
    {"gender": "남성", "category": "상의", "subcategory": "셔츠/블라우스", "name": "화이트 옥스퍼드 셔츠", "color_name": "화이트", "hex": "#F0EEE8", "price": 65000},
    {"gender": "남성", "category": "상의", "subcategory": "셔츠/블라우스", "name": "블루 체크 셔츠", "color_name": "블루", "hex": "#3B6BBF", "price": 72000},
    # 후드 티셔츠
    {"gender": "남성", "category": "상의", "subcategory": "후드 티셔츠", "name": "그레이 후드 티셔츠", "color_name": "그레이", "hex": "#909090", "price": 62000},
    {"gender": "남성", "category": "상의", "subcategory": "후드 티셔츠", "name": "블랙 후드 티셔츠", "color_name": "블랙", "hex": "#1C1C1C", "price": 65000},
    # 반소매 티셔츠
    {"gender": "남성", "category": "상의", "subcategory": "반소매 티셔츠", "name": "화이트 반팔 티셔츠", "color_name": "화이트", "hex": "#F5F5F0", "price": 25000},
    {"gender": "남성", "category": "상의", "subcategory": "반소매 티셔츠", "name": "네이비 반팔 티셔츠", "color_name": "네이비", "hex": "#1B2B4B", "price": 28000},
    # 피케/카라 티셔츠
    {"gender": "남성", "category": "상의", "subcategory": "피케/카라 티셔츠", "name": "화이트 피케 티셔츠", "color_name": "화이트", "hex": "#F5F5F0", "price": 42000},
    {"gender": "남성", "category": "상의", "subcategory": "피케/카라 티셔츠", "name": "올리브 카라 티셔츠", "color_name": "올리브", "hex": "#6B7645", "price": 45000},
    # 니트/스웨터
    {"gender": "남성", "category": "상의", "subcategory": "니트/스웨터", "name": "베이지 니트 스웨터", "color_name": "베이지", "hex": "#D4B896", "price": 75000},
    {"gender": "남성", "category": "상의", "subcategory": "니트/스웨터", "name": "버건디 울 스웨터", "color_name": "버건디", "hex": "#7B2D3B", "price": 82000},
    # 민소매 티셔츠
    {"gender": "남성", "category": "상의", "subcategory": "민소매 티셔츠", "name": "화이트 민소매 티셔츠", "color_name": "화이트", "hex": "#F5F5F0", "price": 22000},
    {"gender": "남성", "category": "상의", "subcategory": "민소매 티셔츠", "name": "그레이 민소매 티셔츠", "color_name": "그레이", "hex": "#909090", "price": 22000},
    # 기타 상의
    {"gender": "남성", "category": "상의", "subcategory": "기타 상의", "name": "카키 집업 스웨트", "color_name": "카키", "hex": "#7D7A40", "price": 58000},
    {"gender": "남성", "category": "상의", "subcategory": "기타 상의", "name": "머스타드 헨리넥 티셔츠", "color_name": "머스타드", "hex": "#C69B2B", "price": 45000},

    # ────────────────────────────────────────────
    # 여성 상의
    # ────────────────────────────────────────────
    # 긴소매 티셔츠
    {"gender": "여성", "category": "상의", "subcategory": "긴소매 티셔츠", "name": "크림 긴소매 티셔츠", "color_name": "크림", "hex": "#EEE5D3", "price": 32000},
    {"gender": "여성", "category": "상의", "subcategory": "긴소매 티셔츠", "name": "라벤더 긴소매 티셔츠", "color_name": "라벤더", "hex": "#B8A9C9", "price": 35000},
    # 맨투맨/스웨트
    {"gender": "여성", "category": "상의", "subcategory": "맨투맨/스웨트", "name": "핑크 오버핏 맨투맨", "color_name": "핑크", "hex": "#E8A0B4", "price": 55000},
    {"gender": "여성", "category": "상의", "subcategory": "맨투맨/스웨트", "name": "민트 크롭 맨투맨", "color_name": "민트", "hex": "#98D8C8", "price": 52000},
    # 셔츠/블라우스
    {"gender": "여성", "category": "상의", "subcategory": "셔츠/블라우스", "name": "화이트 리넨 블라우스", "color_name": "화이트", "hex": "#F0EEE8", "price": 58000},
    {"gender": "여성", "category": "상의", "subcategory": "셔츠/블라우스", "name": "더스티 핑크 셔츠", "color_name": "더스티 핑크", "hex": "#D6A7AD", "price": 62000},
    # 후드 티셔츠
    {"gender": "여성", "category": "상의", "subcategory": "후드 티셔츠", "name": "라이트 그레이 후드 티셔츠", "color_name": "라이트 그레이", "hex": "#C8C8C8", "price": 62000},
    {"gender": "여성", "category": "상의", "subcategory": "후드 티셔츠", "name": "세이지 크롭 후드 티셔츠", "color_name": "세이지", "hex": "#9BAA91", "price": 65000},
    # 반소매 티셔츠
    {"gender": "여성", "category": "상의", "subcategory": "반소매 티셔츠", "name": "화이트 베이직 반팔 티셔츠", "color_name": "화이트", "hex": "#F5F5F0", "price": 25000},
    {"gender": "여성", "category": "상의", "subcategory": "반소매 티셔츠", "name": "코랄 반팔 티셔츠", "color_name": "코랄", "hex": "#E07060", "price": 28000},
    # 피케/카라 티셔츠
    {"gender": "여성", "category": "상의", "subcategory": "피케/카라 티셔츠", "name": "네이비 피케 티셔츠", "color_name": "네이비", "hex": "#1B2B4B", "price": 42000},
    {"gender": "여성", "category": "상의", "subcategory": "피케/카라 티셔츠", "name": "민트 카라 티셔츠", "color_name": "민트", "hex": "#98D8C8", "price": 45000},
    # 니트/스웨터
    {"gender": "여성", "category": "상의", "subcategory": "니트/스웨터", "name": "크림 루즈핏 니트", "color_name": "크림", "hex": "#EEE5D3", "price": 78000},
    {"gender": "여성", "category": "상의", "subcategory": "니트/스웨터", "name": "와인 브이넥 니트", "color_name": "와인", "hex": "#722F37", "price": 82000},
    # 민소매 티셔츠
    {"gender": "여성", "category": "상의", "subcategory": "민소매 티셔츠", "name": "블랙 나시 티셔츠", "color_name": "블랙", "hex": "#1C1C1C", "price": 22000},
    {"gender": "여성", "category": "상의", "subcategory": "민소매 티셔츠", "name": "베이지 슬리브리스 티셔츠", "color_name": "베이지", "hex": "#D4B896", "price": 25000},
    # 기타 상의
    {"gender": "여성", "category": "상의", "subcategory": "기타 상의", "name": "옐로우 크롭 탑", "color_name": "옐로우", "hex": "#F5D060", "price": 38000},
    {"gender": "여성", "category": "상의", "subcategory": "기타 상의", "name": "라이트 블루 오프숄더 탑", "color_name": "라이트 블루", "hex": "#AFCBE3", "price": 42000},

    # ────────────────────────────────────────────
    # 남성 아우터
    # ────────────────────────────────────────────
    {"gender": "남성", "category": "아우터", "subcategory": "후드 집업", "name": "그레이 후드 집업", "color_name": "그레이", "hex": "#909090", "price": 72000},
    {"gender": "남성", "category": "아우터", "subcategory": "블루종", "name": "네이비 블루종 재킷", "color_name": "네이비", "hex": "#1B2B4B", "price": 95000},
    {"gender": "남성", "category": "아우터", "subcategory": "레더/라이더스 재킷", "name": "블랙 레더 라이더스 재킷", "color_name": "블랙", "hex": "#1C1C1C", "price": 189000},
    {"gender": "남성", "category": "아우터", "subcategory": "슈트/블레이저 재킷", "name": "차콜 슬림핏 블레이저", "color_name": "차콜", "hex": "#44474D", "price": 159000},
    {"gender": "남성", "category": "아우터", "subcategory": "카디건", "name": "베이지 버튼 카디건", "color_name": "베이지", "hex": "#D4B896", "price": 68000},
    {"gender": "남성", "category": "아우터", "subcategory": "경량 패딩/패딩", "name": "블랙 경량 패딩 조끼", "color_name": "블랙", "hex": "#1C1C1C", "price": 89000},
    {"gender": "남성", "category": "아우터", "subcategory": "사파리/헌팅 재킷", "name": "카키 사파리 재킷", "color_name": "카키", "hex": "#7D7A40", "price": 112000},
    {"gender": "남성", "category": "아우터", "subcategory": "트러커 재킷", "name": "인디고 데님 트러커 재킷", "color_name": "인디고", "hex": "#3B5B8C", "price": 98000},
    {"gender": "남성", "category": "아우터", "subcategory": "스타디움 재킷", "name": "네이비 스타디움 재킷", "color_name": "네이비", "hex": "#1B2B4B", "price": 135000},
    {"gender": "남성", "category": "아우터", "subcategory": "나일론/코치 재킷", "name": "블랙 나일론 코치 재킷", "color_name": "블랙", "hex": "#1C1C1C", "price": 89000},
    {"gender": "남성", "category": "아우터", "subcategory": "트레이닝 재킷", "name": "다크 그린 트레이닝 재킷", "color_name": "다크 그린", "hex": "#2D4A3E", "price": 78000},
    {"gender": "남성", "category": "아우터", "subcategory": "아노락 재킷", "name": "올리브 아노락 재킷", "color_name": "올리브", "hex": "#6B7645", "price": 92000},
    {"gender": "남성", "category": "아우터", "subcategory": "플리스/뽀글이", "name": "그레이 플리스 재킷", "color_name": "그레이", "hex": "#909090", "price": 85000},
    {"gender": "남성", "category": "아우터", "subcategory": "환절기 코트", "name": "카멜 싱글 환절기 코트", "color_name": "카멜", "hex": "#C19A6B", "price": 189000},
    {"gender": "남성", "category": "아우터", "subcategory": "무스탕/퍼", "name": "브라운 무스탕 재킷", "color_name": "브라운", "hex": "#8B5E3C", "price": 259000},
    {"gender": "남성", "category": "아우터", "subcategory": "겨울 싱글 코트", "name": "차콜 울 싱글 코트", "color_name": "차콜", "hex": "#44474D", "price": 219000},
    {"gender": "남성", "category": "아우터", "subcategory": "겨울 더블 코트", "name": "베이지 캐시미어 더블 코트", "color_name": "베이지", "hex": "#D4B896", "price": 289000},
    {"gender": "남성", "category": "아우터", "subcategory": "겨울 기타코트", "name": "그레이 발마칸 코트", "color_name": "그레이", "hex": "#909090", "price": 199000},
    {"gender": "남성", "category": "아우터", "subcategory": "숏패딩", "name": "블랙 구스 다운 숏패딩", "color_name": "블랙", "hex": "#1C1C1C", "price": 159000},
    {"gender": "남성", "category": "아우터", "subcategory": "롱패딩", "name": "네이비 롱패딩", "color_name": "네이비", "hex": "#1B2B4B", "price": 239000},
    {"gender": "남성", "category": "아우터", "subcategory": "기타 아우터", "name": "올리브 워크 재킷", "color_name": "올리브", "hex": "#6B7645", "price": 98000},

    # ────────────────────────────────────────────
    # 여성 아우터
    # ────────────────────────────────────────────
    {"gender": "여성", "category": "아우터", "subcategory": "후드 집업", "name": "핑크 후드 집업", "color_name": "핑크", "hex": "#E8A0B4", "price": 72000},
    {"gender": "여성", "category": "아우터", "subcategory": "블루종", "name": "크림 새틴 블루종", "color_name": "크림", "hex": "#EEE5D3", "price": 92000},
    {"gender": "여성", "category": "아우터", "subcategory": "레더/라이더스 재킷", "name": "블랙 페이크 레더 재킷", "color_name": "블랙", "hex": "#1C1C1C", "price": 159000},
    {"gender": "여성", "category": "아우터", "subcategory": "슈트/블레이저 재킷", "name": "아이보리 오버핏 블레이저", "color_name": "아이보리", "hex": "#F5EFE0", "price": 145000},
    {"gender": "여성", "category": "아우터", "subcategory": "카디건", "name": "크림 롱 카디건", "color_name": "크림", "hex": "#EEE5D3", "price": 68000},
    {"gender": "여성", "category": "아우터", "subcategory": "경량 패딩/패딩", "name": "라이트 핑크 경량 패딩", "color_name": "라이트 핑크", "hex": "#F0D0D8", "price": 129000},
    {"gender": "여성", "category": "아우터", "subcategory": "사파리/헌팅 재킷", "name": "베이지 사파리 재킷", "color_name": "베이지", "hex": "#D4B896", "price": 109000},
    {"gender": "여성", "category": "아우터", "subcategory": "트러커 재킷", "name": "라이트 블루 데님 트러커 재킷", "color_name": "라이트 블루", "hex": "#AFCBE3", "price": 95000},
    {"gender": "여성", "category": "아우터", "subcategory": "스타디움 재킷", "name": "버건디 스타디움 재킷", "color_name": "버건디", "hex": "#7B2D3B", "price": 132000},
    {"gender": "여성", "category": "아우터", "subcategory": "나일론/코치 재킷", "name": "세이지 나일론 코치 재킷", "color_name": "세이지", "hex": "#9BAA91", "price": 89000},
    {"gender": "여성", "category": "아우터", "subcategory": "트레이닝 재킷", "name": "민트 트레이닝 재킷", "color_name": "민트", "hex": "#98D8C8", "price": 78000},
    {"gender": "여성", "category": "아우터", "subcategory": "아노락 재킷", "name": "코랄 아노락 재킷", "color_name": "코랄", "hex": "#E07060", "price": 95000},
    {"gender": "여성", "category": "아우터", "subcategory": "플리스/뽀글이", "name": "아이보리 뽀글이 재킷", "color_name": "아이보리", "hex": "#F5EFE0", "price": 85000},
    {"gender": "여성", "category": "아우터", "subcategory": "환절기 코트", "name": "카멜 체크 트렌치 코트", "color_name": "카멜", "hex": "#C19A6B", "price": 189000},
    {"gender": "여성", "category": "아우터", "subcategory": "무스탕/퍼", "name": "브라운 무스탕 코트", "color_name": "브라운", "hex": "#8B5E3C", "price": 289000},
    {"gender": "여성", "category": "아우터", "subcategory": "겨울 싱글 코트", "name": "라이트 그레이 울 싱글 코트", "color_name": "라이트 그레이", "hex": "#C8C8C8", "price": 219000},
    {"gender": "여성", "category": "아우터", "subcategory": "겨울 더블 코트", "name": "베이지 더블 코트", "color_name": "베이지", "hex": "#D4B896", "price": 259000},
    {"gender": "여성", "category": "아우터", "subcategory": "겨울 기타코트", "name": "블랙 케이프 코트", "color_name": "블랙", "hex": "#1C1C1C", "price": 199000},
    {"gender": "여성", "category": "아우터", "subcategory": "숏패딩", "name": "와인 숏패딩", "color_name": "와인", "hex": "#722F37", "price": 159000},
    {"gender": "여성", "category": "아우터", "subcategory": "롱패딩", "name": "네이비 롱패딩", "color_name": "네이비", "hex": "#1B2B4B", "price": 249000},
    {"gender": "여성", "category": "아우터", "subcategory": "기타 아우터", "name": "라벤더 볼레로 재킷", "color_name": "라벤더", "hex": "#B8A9C9", "price": 79000},

    # ────────────────────────────────────────────
    # 남성 바지
    # ────────────────────────────────────────────
    {"gender": "남성", "category": "바지", "subcategory": "데님 팬츠", "name": "인디고 슬림 데님 팬츠", "color_name": "인디고", "hex": "#3B5B8C", "price": 79000},
    {"gender": "남성", "category": "바지", "subcategory": "데님 팬츠", "name": "블랙 스트레이트 데님 팬츠", "color_name": "블랙", "hex": "#1C1C1C", "price": 82000},
    {"gender": "남성", "category": "바지", "subcategory": "트레이닝/조거 팬츠", "name": "그레이 조거 팬츠", "color_name": "그레이", "hex": "#909090", "price": 55000},
    {"gender": "남성", "category": "바지", "subcategory": "트레이닝/조거 팬츠", "name": "블랙 트레이닝 팬츠", "color_name": "블랙", "hex": "#1C1C1C", "price": 55000},
    {"gender": "남성", "category": "바지", "subcategory": "코튼 팬츠", "name": "베이지 치노 팬츠", "color_name": "베이지", "hex": "#D4B896", "price": 65000},
    {"gender": "남성", "category": "바지", "subcategory": "코튼 팬츠", "name": "카키 카고 팬츠", "color_name": "카키", "hex": "#7D7A40", "price": 72000},
    {"gender": "남성", "category": "바지", "subcategory": "슈트 팬츠/슬랙스", "name": "차콜 슬림 슬랙스", "color_name": "차콜", "hex": "#44474D", "price": 95000},
    {"gender": "남성", "category": "바지", "subcategory": "슈트 팬츠/슬랙스", "name": "네이비 슬랙스", "color_name": "네이비", "hex": "#1B2B4B", "price": 98000},
    {"gender": "남성", "category": "바지", "subcategory": "숏 팬츠", "name": "카키 카고 숏 팬츠", "color_name": "카키", "hex": "#7D7A40", "price": 48000},
    {"gender": "남성", "category": "바지", "subcategory": "숏 팬츠", "name": "네이비 치노 숏 팬츠", "color_name": "네이비", "hex": "#1B2B4B", "price": 45000},
    {"gender": "남성", "category": "바지", "subcategory": "점프 슈트/오버올", "name": "인디고 데님 오버올", "color_name": "인디고", "hex": "#3B5B8C", "price": 115000},
    {"gender": "남성", "category": "바지", "subcategory": "기타 하의", "name": "올리브 와이드 팬츠", "color_name": "올리브", "hex": "#6B7645", "price": 72000},

    # ────────────────────────────────────────────
    # 여성 바지
    # ────────────────────────────────────────────
    {"gender": "여성", "category": "바지", "subcategory": "데님 팬츠", "name": "인디고 와이드 데님 팬츠", "color_name": "인디고", "hex": "#3B5B8C", "price": 72000},
    {"gender": "여성", "category": "바지", "subcategory": "데님 팬츠", "name": "라이트 블루 스키니 데님", "color_name": "라이트 블루", "hex": "#AFCBE3", "price": 75000},
    {"gender": "여성", "category": "바지", "subcategory": "트레이닝/조거 팬츠", "name": "민트 조거 팬츠", "color_name": "민트", "hex": "#98D8C8", "price": 52000},
    {"gender": "여성", "category": "바지", "subcategory": "트레이닝/조거 팬츠", "name": "라벤더 트레이닝 팬츠", "color_name": "라벤더", "hex": "#B8A9C9", "price": 55000},
    {"gender": "여성", "category": "바지", "subcategory": "코튼 팬츠", "name": "크림 와이드 코튼 팬츠", "color_name": "크림", "hex": "#EEE5D3", "price": 62000},
    {"gender": "여성", "category": "바지", "subcategory": "코튼 팬츠", "name": "세이지 코튼 팬츠", "color_name": "세이지", "hex": "#9BAA91", "price": 65000},
    {"gender": "여성", "category": "바지", "subcategory": "슈트 팬츠/슬랙스", "name": "블랙 테일러드 슬랙스", "color_name": "블랙", "hex": "#1C1C1C", "price": 89000},
    {"gender": "여성", "category": "바지", "subcategory": "슈트 팬츠/슬랙스", "name": "아이보리 와이드 슬랙스", "color_name": "아이보리", "hex": "#F5EFE0", "price": 92000},
    {"gender": "여성", "category": "바지", "subcategory": "숏 팬츠", "name": "인디고 데님 숏 팬츠", "color_name": "인디고", "hex": "#3B5B8C", "price": 45000},
    {"gender": "여성", "category": "바지", "subcategory": "숏 팬츠", "name": "화이트 면 숏 팬츠", "color_name": "화이트", "hex": "#F5F5F0", "price": 42000},
    {"gender": "여성", "category": "바지", "subcategory": "레깅스", "name": "블랙 요가 레깅스", "color_name": "블랙", "hex": "#1C1C1C", "price": 35000},
    {"gender": "여성", "category": "바지", "subcategory": "레깅스", "name": "네이비 스포츠 레깅스", "color_name": "네이비", "hex": "#1B2B4B", "price": 38000},
    {"gender": "여성", "category": "바지", "subcategory": "점프 슈트/오버올", "name": "다크 그린 리넨 점프 슈트", "color_name": "다크 그린", "hex": "#2D4A3E", "price": 109000},
    {"gender": "여성", "category": "바지", "subcategory": "점프 슈트/오버올", "name": "스카이 블루 데님 오버올", "color_name": "스카이 블루", "hex": "#87CEEB", "price": 115000},
    {"gender": "여성", "category": "바지", "subcategory": "기타 하의", "name": "머스타드 와이드 팬츠", "color_name": "머스타드", "hex": "#C69B2B", "price": 68000},

    # ────────────────────────────────────────────
    # 여성 원피스·스커트
    # ────────────────────────────────────────────
    # 미니 원피스
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "미니 원피스", "name": "화이트 플레어 미니 원피스", "color_name": "화이트", "hex": "#F5F5F0", "price": 85000},
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "미니 원피스", "name": "핑크 플로럴 미니 원피스", "color_name": "핑크", "hex": "#E8A0B4", "price": 89000},
    # 미디 원피스
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "미디 원피스", "name": "버건디 랩 미디 원피스", "color_name": "버건디", "hex": "#7B2D3B", "price": 109000},
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "미디 원피스", "name": "세이지 린넨 미디 원피스", "color_name": "세이지", "hex": "#9BAA91", "price": 115000},
    # 맥시 원피스
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "맥시 원피스", "name": "네이비 맥시 원피스", "color_name": "네이비", "hex": "#1B2B4B", "price": 129000},
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "맥시 원피스", "name": "크림 플로럴 맥시 원피스", "color_name": "크림", "hex": "#EEE5D3", "price": 135000},
    # 미니 스커트
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "미니 스커트", "name": "블랙 미니 스커트", "color_name": "블랙", "hex": "#1C1C1C", "price": 55000},
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "미니 스커트", "name": "라벤더 체크 미니 스커트", "color_name": "라벤더", "hex": "#B8A9C9", "price": 62000},
    # 미디 스커트
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "미디 스커트", "name": "카멜 A라인 미디 스커트", "color_name": "카멜", "hex": "#C19A6B", "price": 75000},
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "미디 스커트", "name": "머스타드 플리츠 미디 스커트", "color_name": "머스타드", "hex": "#C69B2B", "price": 72000},
    # 롱스커트
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "롱스커트", "name": "블랙 맥시 롱스커트", "color_name": "블랙", "hex": "#1C1C1C", "price": 85000},
    {"gender": "여성", "category": "원피스·스커트", "subcategory": "롱스커트", "name": "네이비 플로럴 롱스커트", "color_name": "네이비", "hex": "#1B2B4B", "price": 92000},
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
