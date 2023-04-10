from datetime import datetime
from enum import Enum
from typing import List

class Frequency(Enum):
  TRIMESTRAL=4
  SEMESTRAL=2
  ANNUAL=1

class SideType(Enum):
  ASK="ASK"
  BID="BID"

class CouponType(Enum):
  FIXED="FIXED"

class Bond:
  
  def from_data(self,
    name: str, #ok
    isin: str, #ok
    negotiation_currency:str, #ok
    liquidation_currency:str, #ok
    field_type: str, #ok
    total_volume:float, #ok
    ask_price:float, #ok
    bid_price:float, #ok
    ask_volume:float, #ok
    bid_volume:float, #ok
    bond_type:CouponType, #ok
    coupon_frequency:Frequency,
    emission_date: datetime,
    maturity_date: datetime,
    payout_desription: str, #ok
    bond_structure:str,
    subordination:str, #ok
    coupon_percentage:float, #ok
    borsa_italiana_gross_yield:float,
    minimun_amount: int, #ok
    face_value:float
    ) -> None:
    self.name = name 
    self.isin = isin 
    self.negotiation_currency = negotiation_currency
    self.liquidation_currency = liquidation_currency
    self.field_type = field_type 
    self.total_volume = total_volume
    self.ask_price = ask_price
    self.bid_price = bid_price
    self.ask_volume = ask_volume
    self.bid_volume = bid_volume
    self.bond_type = bond_type
    self.coupon_frequency = coupon_frequency
    self.emission_date = emission_date 
    self.maturity_date = maturity_date 
    self.payout_desription = payout_desription 
    self.bond_structure = bond_structure
    self.subordination = subordination
    self.coupon_percentage = coupon_percentage
    self.borsa_italiana_gross_yield = borsa_italiana_gross_yield
    self.minimun_amount = minimun_amount 
    self.face_value=face_value

  def __init__(self, **kwargs):
    print(len(kwargs)>0)
    if(len(kwargs)>0):
      self.from_data(**kwargs)

  @staticmethod
  def get_coupon_dates_by_frequency_type()->List[datetime]:
    pass



  def get_next_coupon_date(self)->datetime:
    now_datetime = datetime.now()



  def calculate_yeld_to_maturity_fixed_coupon(self, side_type=SideType)->float:
    # check if the liquidation currency is in euro
    if(self.liquidation_currency!="EUR"):
      raise Exception(f"Liquidation currency is not EUR, but {self.liquidation_currency}")
    # check if it's fixed coupoon bond
    if(self.bond_type!=CouponType.FIXED):
      raise Exception(f"Bond is not of bond type: fixed coupon bond, but {self.bond_type}")
    
    # check if coupon payments is less than or equal to the
    # the frequency so that the  unpaid interest has accrued
    # can be accounted for the yield calculation
    now_datetime = datetime.now()
    # get the amount of days betwen "now" and the next coupon

    # if equal to zero, then it's a coupon day and coupon payment is assumed  



