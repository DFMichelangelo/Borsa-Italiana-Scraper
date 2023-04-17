from datetime import datetime
import pytest
from src.bond import Bond, BondType, CouponFrequency, SideType


class TestBond:

  def test_calculate_yield_to_maturity_right_for_fixed_rate(self):
    price_date = datetime(day=1, month=1, year=2023)
    bond = Bond()
    bond.liquidation_currency = "EUR"
    bond.negotiation_currency = "EUR"
    bond.bid_price = 90
    bond.bond_type = BondType.FIXED
    bond.face_value = 100
    bond.maturity_date = datetime(
        day=1, month=1, year=2026)
    bond.coupon_percentage = 0.02
    bond.coupon_frequency = CouponFrequency.SEMESTRAL

    bond_yield = bond.calculate_yeld_to_maturity_non_floating_coupon(price_date, SideType.BID)
    assert bond_yield == pytest.approx(0.028787830)

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


  def test_get_price(self):
    price_date = datetime(day=1, month=1, year=2023)
    interest_rate=0.02
    bond = Bond()
    bond.coupon_percentage=0.02
    bond.coupon_frequency=CouponFrequency.SEMESTRAL
    bond.face_value = 100
    bond.maturity_date = datetime(day=31, month=12, year=2024)
    price = bond.get_price(interest_rate,price_date)
    assert price == pytest.approx(bond.face_value,0.01) 


  def test_calculate_yield_to_maturity_right_for_fixed_rate2(self):
    price_date = datetime(day=1, month=1, year=2023)
    bond = Bond()
    bond.liquidation_currency = "EUR"
    bond.negotiation_currency = "EUR"
    bond.bid_price = 100
    bond.bond_type = BondType.FIXED
    bond.face_value = 100
    bond.maturity_date = datetime(day=1, month=1, year=2025)
    bond.coupon_percentage = 0.02
    bond.coupon_frequency = CouponFrequency.SEMESTRAL

    bond_yield = bond.calculate_yeld_to_maturity_non_floating_coupon(price_date, SideType.BID)
    assert bond_yield == pytest.approx(0.02,0.005)