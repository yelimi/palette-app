import uuid

import pytest

from .helpers import OMIT, assert_error_detail, build_payload, timed, unique_email


def _max_length_local_part(total_len=64):
    suffix = uuid.uuid4().hex[:12]
    return "a" * (total_len - len(suffix)) + suffix

BASE_PAYLOAD = {"name": "홍길동", "email": None, "password": "Test1234!"}


def _payload(**overrides):
    base = dict(BASE_PAYLOAD)
    base["email"] = unique_email()
    return build_payload(base, **overrides)


REGISTER_CASES = [
    # case_id (TC번호)                          overrides                                          expected_status
    ("TC1_정상_가입", {}, 201),
    ("TC2_이름_누락", {"name": OMIT}, 422),
    ("TC3_이메일_누락", {"email": OMIT}, 422),
    ("TC4_패스워드_누락", {"password": OMIT}, 422),
    ("TC5_전체_누락", {"name": OMIT, "email": OMIT, "password": OMIT}, 422),
    ("TC6_이름_공백", {"name": ""}, 422),
    ("TC7_이메일_공백", {"email": ""}, 422),
    ("TC8_패스워드_공백", {"password": ""}, 422),
    ("TC9_전체_공백", {"name": "", "email": "", "password": ""}, 422),
    ("TC10_특수문자_이름", {"name": "홍길_동"}, 422),
    ("TC11_이메일에_골뱅이_누락", {"email": f"{unique_email().split('@')[0]}gmail.com"}, 422),
    ("TC12_이메일에_도메인_누락", {"email": f"{unique_email().split('@')[0]}@"}, 422),
    ("TC13_한글_이메일", {"email": f"길동{unique_email()}"}, 422),
    ("TC14_유효한_특수문자_이메일", {"name": "김영수", "email": f"yo_ung{unique_email()}", "password": "youngsu123@"}, 201),
    ("TC15_유효하지_않은_특수문자_이메일", {"email": f"abc:{unique_email().split('@')[0]}@@gmail.com"}, 422),
    ("TC17_8자리_미만_패스워드", {"password": "hong!"}, 422),
    ("TC18_이름_최대길이", {"name": "가" * 100}, 201),
    ("TC19_이름_최대길이_초과", {"name": "가" * 101}, 422),
    ("TC20_패스워드_최대길이", {"password": "A" + "a" * 252 + "1!"}, 201),
    ("TC21_패스워드_최대길이_초과", {"password": "A" + "a" * 253 + "1!"}, 422),
    ("TC22_이메일_최대길이", {"email": f"{_max_length_local_part(64)}@example.com"}, 201),
    ("TC23_이메일_최대길이_초과", {"email": "a" * 65 + "@example.com"}, 422),
    ("TC25_이름_앞뒤_공백", {"name": " 김상철 "}, 201),
    ("TC26_이름_중간_공백", {"name": "이수 지"}, 201),
    ("TC27_이메일_앞뒤_공백", {"email": f" {unique_email()} "}, 201),
    ("TC28_이메일_중간_공백", {"email": f"kim11 {unique_email()}"}, 422),
    ("TC29_패스워드_앞뒤_공백", {"password": " kim123123@ "}, 422),
    ("TC30_패스워드_중간_공백", {"password": "kim123 123 @"}, 201),
    ("TC32_숫자_이름", {"name": "홍1동"}, 422),
    ("TC33_영어_이름", {"name": "janggildong"}, 201),
]


@pytest.mark.parametrize(
    "case_id, overrides, expected_status",
    REGISTER_CASES,
    ids=[c[0] for c in REGISTER_CASES],
)
def test_register_scenarios(client, case_id, overrides, expected_status):
    payload = _payload(**overrides)
    response = timed(client.post, "/auth/register", json=payload)
    assert response.status_code == expected_status
    body = response.json()
    if response.status_code == 201:
        for field in ("id", "name", "email"):
            assert field in body
        assert "password" not in body
        if case_id == "TC1_정상_가입":
            assert body["name"] == payload["name"]
            assert body["email"] == payload["email"]
    else:
        assert_error_detail(response)


def test_TC16_이메일_중복(client):
    email = unique_email()
    first = timed(client.post, "/auth/register", json=_payload(email=email))
    assert first.status_code == 201

    second = timed(client.post, "/auth/register", json=_payload(email=email, name="다른유저"))
    assert second.status_code == 409
    assert_error_detail(second)


def test_TC24_이름_중복(client):
    first = timed(client.post, "/auth/register", json=_payload(name="홍동아"))
    assert first.status_code == 201

    second = timed(client.post, "/auth/register", json=_payload(name="홍동아"))
    assert second.status_code == 201


def test_TC31_이메일_대소문자_처리(client):
    email = unique_email()
    first = timed(client.post, "/auth/register", json=_payload(email=email))
    assert first.status_code == 201

    second = timed(client.post, "/auth/register", json=_payload(email=email.upper(), name="다른유저"))
    assert second.status_code == 409
    assert_error_detail(second)
