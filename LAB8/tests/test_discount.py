import pytest
from src.discount import calculate_discounted_price


def test_normal_discount():
    assert calculate_discounted_price(100, 20) == 80.0
    assert calculate_discounted_price(200, 50) == 100.0
    assert calculate_discounted_price(75, 10) == 67.5


def test_zero_and_full_discount():
    assert calculate_discounted_price(100, 0) == 100.0
    assert calculate_discounted_price(100, 100) == 0.0


def test_rounding():
    assert calculate_discounted_price(100, 33.33) == 66.67
    assert calculate_discounted_price(10, 33.33) == 6.67
    assert calculate_discounted_price(1, 33.33) == 0.67


def test_price_type_validation():
    with pytest.raises(ValueError,
                       match="Cena nie moze byc ujemna"):
        calculate_discounted_price(-50, 10)

    with pytest.raises(ValueError,
                       match="Cena nie moze byc ujemna"):
        calculate_discounted_price("100", 10)


def test_discount_type_validation():
    with pytest.raises(ValueError,
                       match="Znizka musi byc numerem miedzy 0 a 100"):
        calculate_discounted_price(100, -10)

    with pytest.raises(ValueError,
                       match="Znizka musi byc numerem miedzy 0 a 100"):
        calculate_discounted_price(100, 110)

    with pytest.raises(ValueError,
                       match="Znizka musi byc numerem miedzy 0 a 100"):
        calculate_discounted_price(100, "20")