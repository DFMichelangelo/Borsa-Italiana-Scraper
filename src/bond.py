from datetime import datetime, timedelta
from enum import Enum
from typing import Any, List, Union
from src.utils import datetimes_difference_in_years
from dateutil.rrule import rrule, MONTHLY
from scipy import optimize


class CouponFrequency(Enum):
  ANNUAL = "ANNUAL"
  SEMESTRAL = "SEMESTRAL"
  TRIMESTRAL = "TRIMESTRAL"
  UNDEFINED = "UNDEFINED"

  def to_annual_frequency(self) -> int:
    print(self)
    if (self == CouponFrequency.ANNUAL):
      return 1
    if (self == CouponFrequency.SEMESTRAL):
      return 2
    if (self == CouponFrequency.TRIMESTRAL):
      return 4
    return 0

  @staticmethod
  def of(string: Union[str, None]):
    if (string == "ANNUAL"):
      return CouponFrequency.ANNUAL
    if (string == "SEMESTRAL"):
      return CouponFrequency.SEMESTRAL
    if (string == "TRIMESTRAL"):
      return CouponFrequency.TRIMESTRAL
    return CouponFrequency.UNDEFINED


class SideType(Enum):
  ASK = "ASK"
  BID = "BID"


class BondType(Enum):
  FIXED = "FIXED"
  ZERO_COUPON = "ZERO_COUPON"
  UNDEFINED = "UNDEFINED"

  @staticmethod
  def of(string: Union[str, None]):
    if (string == "FIXED"):
      return BondType.FIXED
    if (string == "ZERO_COUPON"):
      return BondType.ZERO_COUPON
    else:
      return BondType.UNDEFINED


class Bond:

  def coupon_dates(self, start_date: datetime) -> List[datetime]:
    interval = int(12 / self.coupon_frequency.to_annual_frequency())
    if interval <= 0:
      raise Exception(f"Coupon frequency is less or equal to 0: {interval}")
    dates = list(rrule(
        dtstart=datetime(day=31, month=12, year=start_date.year - 1),
        until=self.maturity_date,
        freq=MONTHLY,
        bymonthday=-1,
        interval=interval
    ))

    return list(filter(lambda x: x > start_date, dates))

  def from_data(self,
                name: str,  # ok
                isin: str,  # ok
                negotiation_currency: str,  # ok
                liquidation_currency: str,  # ok
                field_type: str,  # ok
                total_volume: float,  # ok
                ask_price: float,  # ok
                bid_price: float,  # ok
                ask_volume: float,  # ok
                bid_volume: float,  # ok
                bond_type: BondType,  # ok
                coupon_frequency: CouponFrequency,
                emission_date: datetime,
                maturity_date: datetime,
                payout_desription: str,  # ok
                bond_structure: str,
                subordination: str,  # ok
                coupon_percentage: float,  # ok
                borsa_italiana_gross_yield: float,
                minimun_amount: int,  # ok
                face_value: float
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
    self.face_value = face_value

  def __init__(self, **kwargs: Any):
    if (len(kwargs) > 0):
      self.from_data(**kwargs)

  def calculate_yeld_to_maturity_non_floating_coupon(
          self,
          price_date: datetime,
          side_type=SideType
  ) -> float:
    # check if the liquidation currency is in euro
    if (self.liquidation_currency != "EUR"):
      raise Exception(
          f"Liquidation currency is not EUR, but {self.liquidation_currency}")
    # check if the negotiation currency is in euro
    if (self.negotiation_currency != "EUR"):
      raise Exception(
          f"negotiation currency is not EUR, but {self.negotiation_currency}")

    bond_price = self.bid_price if side_type == SideType.BID else self.ask_price
    # check if it's a zero counpon, if yes, use closed form
    if (self.bond_type == BondType.ZERO_COUPON):
      years = datetimes_difference_in_years(price_date, self.maturity_date)
      return self.get_ytm_zero_coupon_bond(bond_price, self.face_value, years)
    if (self.bond_type == BondType.FIXED):
      yield_to_maturity = lambda interest_rate: self.get_price(interest_rate, price_date) - bond_price
      return optimize.newton(yield_to_maturity, 0.0005)
    else:
      raise Exception(
          f"Bond is not of bond type: fixed or zero coupon bond, but {self.bond_type}")

    # if equal to zero, then it's a coupon day and coupon payment is assumed

  @staticmethod
  def get_ytm_zero_coupon_bond(bond_price: float, face_value: float, years: float) -> float:
    ytm = (face_value / bond_price)**(1 / years) - 1
    return ytm

  @staticmethod
  def get_coupon_present_value(coupon_amount: float, interest_rate: float, years: float) -> float:
    present_value = coupon_amount / (1 + interest_rate)**years
    return present_value

  @staticmethod
  def get_coupons_present_value(coupon_amount: float, interest_rate: float, years_list: List[float]) -> float:
    present_value = 0
    for years in years_list:
      present_value += Bond.get_coupon_present_value(coupon_amount, interest_rate, years)
    return present_value

  @staticmethod
  def get_face_value_present_value(face_value: float, interest_rate: float, years: float) -> float:
    return Bond.get_coupon_present_value(face_value, interest_rate, years)

  def get_price(self, interest_rate: float, price_date: datetime) -> float:
    coupon_dates = self.coupon_dates(price_date)
    coupon_dates.pop()
    years = [datetimes_difference_in_years(price_date, coupon_date) for coupon_date in coupon_dates]
    total_coupons_pv = Bond.get_coupons_present_value(self.coupon_percentage * self.face_value, interest_rate, years)
    face_value_pv = Bond.get_face_value_present_value(
        self.face_value, interest_rate, datetimes_difference_in_years(
            price_date, self.maturity_date))
    price = total_coupons_pv + face_value_pv
    return price
