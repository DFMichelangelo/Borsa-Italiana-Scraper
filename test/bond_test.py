from datetime import datetime
from src.bond import Bond, BondType, Frequency, SideType


class TestBond:
  def test_calculate_yield_to_maturity_right_for_fixed_rate(self):
    bond = Bond()
    bond.liquidation_currency="EUR",
    bond.ask_price=91,
    bond.bid_price=90,
    bond.bond_type=BondType.FIXED,
    bond.face_value=100,
    bond.maturity_date=datetime(day=31, month=12, year=datetime.now().year+3),
    bond.coupon_percentage=0.02,
    bond.coupon_frequency=Frequency.SEMESTRAL
    
    
    bond_yield = bond.calculate_yeld_to_maturity_fixed_coupon(SideType.BID)
