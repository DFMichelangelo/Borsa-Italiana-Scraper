import datetime
from enum import Enum



class Frequency(Enum):
    pass

class Bond:
    name: str
    isin: str
    negotiation_currency:str
    liquidation_currency:str
    field_type: str
    total_volume:int
    ask_price:float
    bid_price:float
    ask_volume:float
    bid_volume:float
    bond_type:str
    coupoon_frequency:Frequency
    emission_date:datetime
    maturity_date: datetime
    payout_desription: str
    bond_structure:str
    subordination:str
    coupon_percentage:float
    borsa_italiana_gross_yield:float



    def calculate_yeld_to_maturity(self):
        print("optimize")







