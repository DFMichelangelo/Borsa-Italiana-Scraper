from os import path
from .bond import Bond
from typing import Iterable, List, Tuple
import pandas as pd

class FileService():

  def str_safe(self, str_in) -> str:
    if(str_in == None): 
      return ""
  
    try:
      return str(str_in)
    except:
      return ""

  def create_csv(self, bonds: List[Bond]) -> str:
    print("Preparing CSV")
    out = "ISIN;Name;Field Type; Coupon; Frequency; Ask Price; Bid Price; Ask Volume; Bid volume; Negotiation currency; Liquidation Currency; Field Type; Total Volume; Emission Date; Maturity Date; Bond Structure; Subordination; Min Amount \n";
    for bond in bonds:
        out += bond.isin + ";" + bond.name + ";" + bond.field_type + ";"
        + self.str_safe(bond.coupon_percentage) + ";" 
        + self.str_safe(bond.coupoon_frequency)+";"
        + self.str_safe(bond.ask_price)+";" 
        + self.str_safe(bond.bid_price)+";"
        + self.str_safe(bond.ask_volume)+";" 
        + self.str_safe(bond.bid_volume)+";"
        + self.str_safe(bond.negotiation_currency)+";"
        + self.str_safe(bond.liquidation_currency)+";"
        + self.str_safe(bond.field_type)+";"
        + self.str_safe(bond.total_volume)+";"
        + self.str_safe(bond.emission_date)+";"
        + self.str_safe(bond.maturity_date)+";"
        + self.str_safe(bond.bond_self.str_safeucture)+";"
        + self.str_safe(bond.subordination)+";"
        + self.str_safe(bond.minimun_amount)+";"
        + "\n"
    return out;

  def save_csv(self, data: str) -> None:
    print("Saving CSV")
    f = open(path.join("out", "output_scrapring.csv"), "w")
    f.write(data)
    f.close()


  @staticmethod
  def create_dataframe_from_bonds(bonds: List[Bond])->pd.DataFrame:
    bond_dicts = [bond_dict.__dict__ for bond_dict in bonds]
    return pd.DataFrame(bond_dicts)
  
  # this function creates an excel given the pandas dataframes and their name
  @staticmethod
  def save_excel(data:Iterable[Tuple[str,pd.DataFrame]])->None:
    with pd.ExcelWriter(path.join("out", "output_scrapring.xlsx")) as writer:  
      map(data, lambda singleData: singleData[1].to_excel(writer, sheet_name=singleData[0]))
