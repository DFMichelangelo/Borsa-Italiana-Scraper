from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Union
from src.utils import datetimes_difference_in_years
from dateutil.rrule import rrule, MONTHLY
from scipy import optimize


class SideType(Enum):
  ASK = "ASK"
  BID = "BID"


class Bond:

  class CouponFrequency(Enum):
    ANNUAL = "ANNUAL"
    SEMESTRAL = "SEMESTRAL"
    TRIMESTRAL = "TRIMESTRAL"
    MONTHLY = "MONTHLY"
    UNDEFINED = "UNDEFINED"

    def to_annual_frequency(self) -> int:
      if (self == Bond.CouponFrequency.ANNUAL):
        return 1
      if (self == Bond.CouponFrequency.SEMESTRAL):
        return 2
      if (self == Bond.CouponFrequency.TRIMESTRAL):
        return 4
      if (self == Bond.CouponFrequency.MONTHLY):
        return 12
      return 0

    @staticmethod
    def of(string: Union[str, None]):
      if (string == "ANNUAL"):
        return Bond.CouponFrequency.ANNUAL
      if (string == "SEMESTRAL"):
        return Bond.CouponFrequency.SEMESTRAL
      if (string == "TRIMESTRAL"):
        return Bond.CouponFrequency.TRIMESTRAL
      if (string == "MONTHLY"):
        return Bond.CouponFrequency.MONTHLY
      return Bond.CouponFrequency.UNDEFINED

  class BondStructure(Enum):
    PLAIN_VANILLA = "PLAIN_VANILLA"
    INDEX_LIKED = "INDEX_LIKED"
    CURRENCY_LINKED = "CURRENCY_LINKED"
    STRUCTURED_INTEREST_RATE = "STRUCTURED_INTEREST_RATE"
    INFLATION_LINKED = "INFLATION_LINKED"
    UNDEFINED = "UNDEFINED"

    @staticmethod
    def of(string: Union[str, None]):
      if (string == "PLAIN_VANILLA"):
        return Bond.BondStructure.PLAIN_VANILLA
      if (string == "INDEX_LIKED"):
        return Bond.BondStructure.INDEX_LIKED
      if (string == "CURRENCY_LINKED"):
        return Bond.BondStructure.CURRENCY_LINKED
      if (string == "STRUCTURED_INTEREST_RATE"):
        return Bond.BondStructure.STRUCTURED_INTEREST_RATE
      if (string == "INFLATION_LINKED"):
        return Bond.BondStructure.INFLATION_LINKED
      return Bond.BondStructure.UNDEFINED

  def get_annual_coupon_percentage(self):
    annual_frequency = self.coupon_frequency.to_annual_frequency()
    return (1 + self.coupon_percentage)**annual_frequency - 1

  def get_coupon_percentage_from_annual_coupon_percentage(self, annual_coupon_percentage):
    annual_frequency = self.coupon_frequency.to_annual_frequency()
    return (1 + annual_coupon_percentage)**(1 / annual_frequency) - 1

  def coupon_dates(self, start_date: datetime) -> list[datetime]:
    interval = int(12 / self.coupon_frequency.to_annual_frequency())
    if interval <= 0:
      raise Exception(f"Coupon frequency is less or equal to 0: {interval}")

    date_for_dtstart: datetime = self.date_start_maturation if hasattr(
        self, "date_start_maturation") else self.maturity_date
    dates = list(rrule(
        dtstart=datetime(
            day=date_for_dtstart.day,
            month=date_for_dtstart.month,
            year=start_date.year - 1),
        until=self.maturity_date + timedelta(days=1),
        freq=MONTHLY,
        bymonthday=date_for_dtstart.day,
        interval=interval
    ))

    return list(filter(lambda x: x > start_date, dates))

  def assign_ytm(self):
    now = datetime.today()
    if hasattr(self, "bid_price"):
      try:
        self.bid_ytm = self.calculate_yeld_to_maturity_non_floating_coupon(now, SideType.BID)
      except BaseException:
        pass
    if hasattr(self, "ask_price"):
      try:
        self.ask_ytm = self.calculate_yeld_to_maturity_non_floating_coupon(now, SideType.ASK)
      except BaseException:
        pass

    return self

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
                bond_structure: BondStructure,  # ok
                bond_structure_raw: str,
                coupon_frequency: CouponFrequency,
                coupon_frequency_raw: str,
                emission_date: datetime,
                maturity_date: datetime,
                payout_desription: str,  # ok
                bond_type: str,
                subordination: str,  # ok
                coupon_percentage: float,  # ok
                borsa_italiana_gross_yield: float,
                minimun_amount: int,  # ok
                face_value: float,
                issuer: str,
                date_start_maturation: datetime,
                BI_gross_ytm: float,
                BI_net_ytm: float,
                years_to_maturity: float,
                market: float
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
    self.bond_structure = bond_structure
    self.coupon_frequency = coupon_frequency
    self.emission_date = emission_date
    self.maturity_date = maturity_date
    self.payout_desription = payout_desription
    self.bond_type = bond_type
    self.subordination = subordination
    self.coupon_percentage = coupon_percentage
    self.borsa_italiana_gross_yield = borsa_italiana_gross_yield
    self.minimun_amount = minimun_amount
    self.face_value = face_value
    self.bond_structure_raw = bond_structure_raw
    self.coupon_frequency_raw = coupon_frequency_raw
    self.issuer = issuer
    self.date_start_maturation = date_start_maturation
    self.BI_gross_ytm = BI_gross_ytm
    self.BI_net_ytm = BI_net_ytm
    self.years_to_maturity = years_to_maturity
    self.market = market

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

    # check if it's a zero counpon, if yes, use closed form
    if (self.bond_structure == Bond.BondStructure.PLAIN_VANILLA and self.coupon_frequency == Bond.CouponFrequency.UNDEFINED):
      return self.get_ytm_zero_coupon_bond(side_type, price_date)
    if (self.bond_structure == Bond.BondStructure.PLAIN_VANILLA and self.bond_structure != Bond.BondStructure.UNDEFINED):
      bond_price = self.bid_price if side_type == SideType.BID else self.ask_price
      def yield_to_maturity(interest_rate): return self.get_price(interest_rate, price_date) - bond_price
      return optimize.newton(yield_to_maturity, 0.0005)
    else:
      raise Exception(
          f"Bond is not of bond type: fixed or zero coupon bond, but {self.bond_structure}")

  def get_bond_price_by_side(self, side_type: SideType) -> float:
    bond_price = self.bid_price if side_type == SideType.BID else self.ask_price
    return bond_price

  def get_ytm_zero_coupon_bond(self, side_type: SideType, price_date: datetime) -> float:
    years = datetimes_difference_in_years(price_date, self.maturity_date)
    bond_price = self.get_bond_price_by_side(side_type)
    ytm = (self.face_value / bond_price)**(1 / years) - 1
    return ytm

  def get_coupon_present_value(self, interest_rate: float, price_date: datetime, coupon_date: datetime) -> float:
    years = datetimes_difference_in_years(price_date, coupon_date)
    coupon_amount = self.face_value * self.coupon_percentage
    present_value = coupon_amount / (1 + interest_rate)**years
    return present_value

  def get_coupons_present_value(
          self,
          interest_rate: float,
          price_date: datetime,
          coupon_dates: list[datetime]) -> float:
    present_value: float = 0
    for coupon_date in coupon_dates:
      present_value += self.get_coupon_present_value(interest_rate, price_date, coupon_date)
    return present_value

  def get_face_value_present_value(self, interest_rate: float, price_date: datetime) -> float:
    years = datetimes_difference_in_years(price_date, self.maturity_date)
    present_value = self.face_value / (1 + interest_rate)**years
    return present_value

  def get_price(self, interest_rate: float, price_date: datetime) -> float:
    coupon_dates = self.coupon_dates(price_date)
    total_coupons_pv = self.get_coupons_present_value(interest_rate, price_date, coupon_dates)
    face_value_pv = self.get_face_value_present_value(interest_rate, price_date)
    price = total_coupons_pv + face_value_pv
    return price
