from typing import Any
from .bond import Bond


class SingleTableDTO:
  bonds: list[Bond]
  next_url_to_click: Any
