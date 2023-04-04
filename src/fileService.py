from .bond import Bond
from typing import List

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
        f = open("output_scrapring.csv", "w")
        f.write(data)
        f.close()
