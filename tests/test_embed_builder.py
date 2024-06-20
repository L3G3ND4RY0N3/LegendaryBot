import pytest
import datetime as dt
from utils.embeds.embedbuilder import calc_member_account_age

#region date fixtures
@pytest.fixture()
def date_now() -> dt.date:
    return dt.date(2024, 6, 20)


@pytest.fixture()
def date_under_month() -> dt.date:
    return dt.date(2024, 6, 10)


@pytest.fixture()
def date_under_one_year() -> dt.date:
    return dt.date(2023, 12, 24)


@pytest.fixture()
def date_over_one_year() -> dt.date:
    return dt.date(2021, 4, 14)


@pytest.fixture()
def date_decade_past() -> dt.date:
    return dt.date(2013, 1, 23)
#endregion

#region calc_member_age_tests
def test_empty_account_age(date_now) -> None:
    assert calc_member_account_age(date_now, None) == "0 days"


def test_under_one_month(date_now, date_under_month) -> None:
    assert calc_member_account_age(date_now, date_under_month) == "0 years, 0 months, 10 days"


def test_under_one_year(date_now, date_under_one_year) -> None:
    assert calc_member_account_age(date_now, date_under_one_year) == "0 years, 5 months, 29 days"


def test_over_one_year(date_now, date_over_one_year) -> None:
    assert calc_member_account_age(date_now, date_over_one_year) == "3 years, 2 months, 8 days"


def test_over_decade(date_now, date_decade_past) -> None:
    assert calc_member_account_age(date_now, date_decade_past) == "11 years, 5 months, 1 days"
#endregion