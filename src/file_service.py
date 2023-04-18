import os
from .bond import Bond
from typing import Iterable, List, Tuple
import pandas as pd


class FileService():

  def str_safe(self, str_in) -> str:
    if (str_in is None):
      return ""

    try:
      return str(str_in)
    except BaseException:
      return ""

  @staticmethod
  def create_dataframe_from_bonds(bonds: List[Bond]) -> pd.DataFrame:
    bond_dicts = [bond_dict.__dict__ for bond_dict in bonds]
    return pd.DataFrame(bond_dicts)

  # this function creates an excel given the pandas dataframes and their name
  @staticmethod
  def save_excel(data: Iterable[Tuple[str, pd.DataFrame]]) -> None:
    final_directory = "out"
    if os.path.exists(final_directory) == False:
      os.mkdir(final_directory)

    with pd.ExcelWriter(os.path.join(final_directory, "output_scrapring.xlsx")) as writer:
      map(lambda singleData: singleData[1].to_excel(
          writer, sheet_name=singleData[0]), data)
