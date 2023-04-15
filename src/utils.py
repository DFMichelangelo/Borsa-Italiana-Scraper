import datetime


def difference_in_years(start_date: datetime.datetime, end_date: datetime.datetime) -> float:
  diff = end_date - start_date
  return diff.days / 365
