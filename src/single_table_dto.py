from .bond import Bond
from typing import List

class SingleTableDTO:
    bonds: List[Bond]
    next_url: str