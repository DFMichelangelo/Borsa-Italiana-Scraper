import datetime
from enum import Enum



class Frequency(Enum):
    pass

class Bond:
    name: str  #ok
    isin: str #ok
    negotiation_currency:str #ok
    liquidation_currency:str #ok
    field_type: str #ok
    total_volume:int #ok
    ask_price:float #ok
    bid_price:float #ok
    ask_volume:float #ok
    bid_volume:float #ok
    bond_type:str #ok
    coupoon_frequency:Frequency
    emission_date: datetime
    maturity_date: datetime
    payout_desription: str #ok
    bond_structure:str
    subordination:str #ok
    coupon_percentage:float #ok
    borsa_italiana_gross_yield:float
    minimun_amount: int #ok



    def calculate_yeld_to_maturity(self):
        print("optimize")







