from datetime import datetime
from enum import Enum

class Frequency(Enum):
  TRIMESTRAL=4
  SEMESTRAL=2
  ANNUAL=1

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
    bond_type:str, #ok
    coupoon_frequency:Frequency,
    emission_date: datetime,
    maturity_date: datetime,
    payout_desription: str, #ok
    bond_structure:str,
    subordination:str, #ok
    coupon_percentage:float, #ok
    borsa_italiana_gross_yield:float,
    minimun_amount: int, #ok
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
    self.coupoon_frequency = coupoon_frequency
    self.emission_date = emission_date 
    self.maturity_date = maturity_date 
    self.payout_desription = payout_desription 
    self.bond_structure = bond_structure
    self.subordination = subordination
    self.coupon_percentage = coupon_percentage
    self.borsa_italiana_gross_yield = borsa_italiana_gross_yield
    self.minimun_amount = minimun_amount 

  def __init__(self, *args):
    if(len(args)>0):
      self.from_data(args)

  def calculate_yeld_to_maturity(self):
      print("optimize")



