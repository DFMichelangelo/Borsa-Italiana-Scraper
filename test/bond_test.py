from datetime import datetime
import pytest
from src.bond import Bond, BondType, CouponFrequency, SideType


class TestBond:

  def test_calculate_yield_to_maturity_right_for_fixed_rate(self):
    price_date = datetime(day=15, month=4, year=2023)
    bond = Bond()
    bond.liquidation_currency = "EUR"
    bond.negotiation_currency = "EUR"
    bond.bid_price = 90
    bond.bond_type = BondType.FIXED
    bond.face_value = 100
    bond.maturity_date = datetime(
        day=31, month=12, year=price_date.year + 3)
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
        day=31, month=12, year=price_date.year + 3)

    bond_yield = bond.calculate_yeld_to_maturity_non_floating_coupon(price_date, SideType.BID)
    assert bond_yield == pytest.approx(0.028766298)  # 0.02876629839284628

  def test_coupon_date(self):
    price_date = datetime(day=15, month=4, year=2023)
    bond = Bond()
    bond.coupon_frequency = CouponFrequency.SEMESTRAL
    bond.maturity_date = datetime(
        day=31, month=12, year=price_date.year + 3)
    actual_dates = bond.coupon_dates(price_date)

    for e in actual_dates:
      assert False
