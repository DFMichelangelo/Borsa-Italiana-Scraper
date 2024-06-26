from datetime import datetime
import time
from src.bond import Bond
import random
import string


class Random_Objects:

  @staticmethod
  def random_string() -> str:
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(8))

  @staticmethod
  def random_float() -> float:
    return 100 * random.random()

  @staticmethod
  def random_int() -> int:
    return random.randint(0, 1000)

  @staticmethod
  def random_datetime() -> datetime:
    d = random.randint(1, int(time.time()))
    return datetime.fromtimestamp(d)  # .strftime('%Y-%m-%d')

  @staticmethod
  def random_CouponFrequency() -> Bond.CouponFrequency:
    return random.choice(list(Bond.CouponFrequency))

  @staticmethod
  def random_BondStructure() -> Bond.BondStructure:
    return random.choice(list(Bond.BondStructure))

  @staticmethod
  def random_bond() -> Bond:
    bond = Bond()
    bond.name = Random_Objects.random_string()
    bond.isin = Random_Objects.random_string()
    bond.negotiation_currency = Random_Objects.random_string()
    bond.liquidation_currency = Random_Objects.random_string()
    bond.field_type = Random_Objects.random_string()
    bond.total_volume = Random_Objects.random_float()
    bond.ask_price = Random_Objects.random_float()
    bond.bid_price = Random_Objects.random_float()
    bond.ask_volume = Random_Objects.random_float()
    bond.bid_volume = Random_Objects.random_float()
    bond.bond_structure = Random_Objects.random_BondStructure()
    bond.coupon_frequency = Random_Objects.random_CouponFrequency()
    bond.emission_date = Random_Objects.random_datetime()
    bond.maturity_date = Random_Objects.random_datetime()
    bond.payout_desription = Random_Objects.random_string()
    bond.bond_type = Random_Objects.random_string()
    bond.subordination = Random_Objects.random_string()
    bond.coupon_percentage = Random_Objects.random_float()
    bond.borsa_italiana_gross_yield = Random_Objects.random_float()
    bond.minimun_amount = Random_Objects.random_int()
    return bond
