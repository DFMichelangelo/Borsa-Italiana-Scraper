from os import path
from .bond import Bond
from typing import Iterable, List, Tuple
import pandas as pd

class FileService():

  def create_csv(self, bonds: List[Bond]) -> str:
    print("Preparing CSV")
    out = "ISIN;Name;Field Type; Coupon; Ask Price; Bid Price; Ask Volume; Bid volume \n";
    for bond in bonds:
        out += bond.isin + ";" + bond.name + ";" + bond.field_type + ";"
        + str(bond.coupon_percentage) + ";" 
        + str(bond.ask_price)+";" 
        + str(bond.bid_price)+";"
        + str(bond.ask_volume)+";" 
        + str(bond.bid_volume)+";"
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
