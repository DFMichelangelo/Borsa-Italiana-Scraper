from datetime import datetime, timedelta
import pytest
from src.bond import Bond, BondType, CouponFrequency, SideType


class TestBond:

  def test_CouponFrequency_to_annual_frequency(self):
    assert CouponFrequency.ANNUAL.to_annual_frequency() == 1
    assert CouponFrequency.SEMESTRAL.to_annual_frequency() == 2
    assert CouponFrequency.TRIMESTRAL.to_annual_frequency() == 4
    assert CouponFrequency.UNDEFINED.to_annual_frequency() == 0

  def test_CouponFrequency_of(self):
    assert CouponFrequency.of("ANNUAL") == CouponFrequency.ANNUAL
    assert CouponFrequency.of("SEMESTRAL") == CouponFrequency.SEMESTRAL
    assert CouponFrequency.of("TRIMESTRAL") == CouponFrequency.TRIMESTRAL
    assert CouponFrequency.of("UNDEFINED") == CouponFrequency.UNDEFINED

  def test_BondType_of(self):
    assert BondType.of("FIXED") == BondType.FIXED
    assert BondType.of("ZERO_COUPON") == BondType.ZERO_COUPON
    assert BondType.of("UNDEFINED") == BondType.UNDEFINED

  def test_coupon_dates(self):
    price_date = datetime(day=15, month=4, year=2023)
    bond = Bond()
    bond.coupon_frequency = CouponFrequency.SEMESTRAL
    bond.maturity_date = datetime(
        day=31, month=12, year=price_date.year + 3)
    actual_dates = bond.coupon_dates(price_date)

    expected_dates = [
        datetime(2023, 6, 30),
        datetime(2023, 12, 31),
        datetime(2024, 6, 30),
        datetime(2024, 12, 31),
        datetime(2025, 6, 30),
        datetime(2025, 12, 31),
        datetime(2026, 6, 30),
        datetime(2026, 12, 31)
    ]
    for (actual_date, expected_date) in zip(actual_dates, expected_dates):
      assert actual_date == expected_date

  def test_get_ytm_zero_coupon_bond(self):
    price_date = datetime(day=1, month=1, year=2023)
    bond = Bond()
    bond.bid_price = 90
    bond.face_value = 100
    bond.maturity_date = datetime(day=31, month=12, year=2024)
    ytm = bond.get_ytm_zero_coupon_bond(SideType.BID, price_date)
    assert ytm == pytest.approx(0.0541, 0.0005)

  def test_get_annual_coupon_percentage(self):
    bond = Bond()
    bond.coupon_frequency = CouponFrequency.SEMESTRAL
    bond.coupon_percentage = 0.02
    annual_coupon_percentage = bond.get_annual_coupon_percentage()
    assert annual_coupon_percentage == pytest.approx(0.0404)

  def test_get_coupon_percentage_from_annual_coupon_percentage(self):
    bond = Bond()
    bond.coupon_frequency = CouponFrequency.SEMESTRAL
    annual_coupon_percentage = 0.0404
    coupon_percentage = bond.get_coupon_percentage_from_annual_coupon_percentage(annual_coupon_percentage)
    assert coupon_percentage == pytest.approx(0.02)

  def test_get_coupon_present_value(self):
    price_date = datetime(day=1, month=1, year=2023)
    coupon_date = datetime(day=1, month=1, year=2023) + timedelta(days=60)
    bond = Bond()
    bond.face_value = 100
    bond.coupon_percentage = 0.02
    pv_actual = bond.get_coupon_present_value(0.02, price_date, coupon_date)
    pv_expected = bond.coupon_percentage * bond.face_value
    assert pv_actual == pytest.approx(pv_expected, 0.01)

  def test_get_face_value_present_value(self):
    price_date = datetime(day=1, month=1, year=2023)
    maturity_date = datetime(day=1, month=1, year=2023) + timedelta(days=365)
    bond = Bond()
    bond.face_value = 100
    bond.maturity_date = maturity_date
    pv_actual = bond.get_face_value_present_value(0.1, price_date)
    assert pv_actual == pytest.approx(90.9, 0.001)

  def test_calculate_yield_to_maturity_right_for_fixed_rate(self):
    price_date = datetime(day=1, month=1, year=2023)
    bond = Bond()
    bond.liquidation_currency = "EUR"
    bond.negotiation_currency = "EUR"
    bond.bid_price = 100
    bond.bond_type = BondType.FIXED
    bond.face_value = 100
    bond.maturity_date = datetime(
        day=1, month=1, year=2026)
    bond.coupon_percentage = 0.02
    bond.coupon_frequency = CouponFrequency.SEMESTRAL

    bond_yield = bond.calculate_yeld_to_maturity_non_floating_coupon(price_date, SideType.BID)
    assert bond_yield == pytest.approx(0.0404, 0.001)

  def test_calculate_yield_to_maturity_right_for_zero_coupon(self):
    price_date = datetime(day=15, month=4, year=2023)
    bond = Bond()
    bond.liquidation_currency = "EUR"
    bond.negotiation_currency = "EUR"
    bond.bid_price = 90
    bond.bond_type = BondType.ZERO_COUPON
    bond.face_value = 100
    bond.maturity_date = datetime(
        day=31, month=12, year=2026)

    bond_yield = bond.calculate_yeld_to_maturity_non_floating_coupon(price_date, SideType.BID)
    assert bond_yield == pytest.approx(0.028766298)  # 0.02876629839284628

  def test_get_price(self):
    price_date = datetime(day=1, month=1, year=2023)
    interest_rate = 0.0404
    bond = Bond()
    bond.coupon_percentage = 0.02
    bond.coupon_frequency = CouponFrequency.SEMESTRAL
    bond.face_value = 100
    bond.maturity_date = datetime(day=31, month=12, year=2024)
    price = bond.get_price(interest_rate, price_date)
    assert price == pytest.approx(bond.face_value, 0.0001)
