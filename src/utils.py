import asyncio
import datetime
import decimal


def datetimes_difference_in_years(start_date: datetime.datetime, end_date: datetime.datetime) -> float:
  diff = end_date - start_date  # (start_date -datetime.timedelta(days=1)
  return float(decimal.Decimal(diff.days) / decimal.Decimal(365))


async def promise_all(funcs):
  tasks = [asyncio.create_task(func()) for func in funcs]
  return [await task for task in tasks]
