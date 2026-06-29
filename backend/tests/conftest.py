import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

TEST_DB_URL = "postgresql://palette:palette123@localhost:5432/palette_test"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(test_engine):
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(test_engine):
    Session = sessionmaker(bind=test_engine)

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.rollback()
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def seed_products(test_engine):
    import models
    Session = sessionmaker(bind=test_engine)
    db = Session()
    if db.query(models.Product).count() == 0:
        products = [
            models.Product(name="네이비 코튼 셔츠", gender="남성", category="상의", subcategory="셔츠/블라우스", color_name="네이비", hex="#26354A", price=49000),
            models.Product(name="크림 니트 카디건", gender="여성", category="아우터", subcategory="카디건", color_name="크림", hex="#EEE5D3", price=69000),
            models.Product(name="차콜 슬랙스", gender="남성", category="바지", subcategory="슈트 팬츠/슬랙스", color_name="차콜", hex="#44474D", price=64000),
        ]
        db.add_all(products)
        db.commit()
    db.close()
