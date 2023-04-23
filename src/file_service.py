import os
from .bond import Bond
import pandas as pd
from openpyxl import Workbook


class FileService():

  def str_safe(self, str_in) -> str:
    if (str_in is None):
      return ""

    try:
      return str(str_in)
    except BaseException:
      return ""

  @staticmethod
  def create_dataframe_from_bonds(bonds: list[Bond]) -> pd.DataFrame:
    bond_dicts = [bond_dict.__dict__ for bond_dict in bonds]
    return pd.DataFrame(bond_dicts)

  # this function creates an excel given the pandas dataframes and their name
  @staticmethod
  def save_excel(data: list[tuple[str, pd.DataFrame]]) -> None:
    final_directory = "out"
    final_file_directory = os.path.join(final_directory, "scraped.xlsx")
    if not os.path.exists(final_directory):
      os.mkdir(final_directory)
    if os.path.exists(final_file_directory):
      os.remove(final_file_directory)
    wb = Workbook()
    wb.save(final_file_directory)
    with pd.ExcelWriter(final_file_directory, mode="a", engine='openpyxl') as writer:
      for (sheet_name, df) in data:
        df.to_excel(writer, sheet_name=sheet_name)
    # if 'Sheet' in wb.sheetnames:
    #   wb.remove('Sheet')
