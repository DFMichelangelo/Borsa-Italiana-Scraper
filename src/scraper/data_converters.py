from src.bond import Bond


def scraped_str_to_subordination(string: str) -> Bond.Subordination:
  if string == "SUBORDINATO":
    return Bond.Subordination.SUBORDINATED
  return Bond.Subordination.of(string)


def str_to_bond_structure(string: str) -> Bond.BondStructure:
  if string == "Currency Linked":
    return Bond.BondStructure.CURRENCY_LINKED
  if string == "Index Linked":
    return Bond.BondStructure.INDEX_LIKED
  if string == "Plain Vanilla":
    return Bond.BondStructure.PLAIN_VANILLA
  if string == "Structured Interest Rate":
    return Bond.BondStructure.STRUCTURED_INTEREST_RATE
  if string == "Titoli Indicizzati All'inflazione":
    return Bond.BondStructure.INFLATION_LINKED
  return Bond.BondStructure.UNDEFINED


def str_to_coupon_frequency(string: str) -> Bond.CouponFrequency:
  if string == "Annuale":
    return Bond.CouponFrequency.ANNUAL
  if string == "Semestrale":
    return Bond.CouponFrequency.SEMESTRAL
  if string == "Mensile":
    return Bond.CouponFrequency.MONTHLY
  if string == "Trimestrale":
    return Bond.CouponFrequency.TRIMESTRAL
  return Bond.CouponFrequency.UNDEFINED
