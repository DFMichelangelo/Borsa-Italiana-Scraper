from datetime import datetime
from src.bond import Bond, CouponType, Frequency, SideType


class TestBond:
  def test_calculate_yield_to_maturity_right_for_fixed_rate(self):
    bond = Bond(
      liquidation_currency="EUR",
      ask_price=91,
      bid_price=90,
      coupon_frequency=CouponType.FIXED,
      face_value=100,
      maturity_date=datetime(
        day=31, month=12, year=datetime.now().year+3),
      coupon_percentage=0.02,
      coupon_frequency=Frequency.SEMESTRAL
    )
    
    bond_yield = bond.calculate_yeld_to_maturity_fixed_coupon(SideType.BID)
