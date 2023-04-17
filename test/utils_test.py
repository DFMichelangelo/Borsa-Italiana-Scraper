from datetime import datetime

from src.utils import datetimes_difference_in_years


class TestUtils:
  def test_datetimes_difference_in_years(self):
    start_date = datetime(day=1, month=1, year=2023)
    end_date = datetime(day=31, month=12, year=2024)
    years = datetimes_difference_in_years(start_date, end_date)
    assert years == 2
