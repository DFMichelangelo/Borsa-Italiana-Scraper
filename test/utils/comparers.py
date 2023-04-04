import typing

class Comparer:
  
  @staticmethod
  def type_aware_dict_equals(d1: typing.Dict, d2: typing.Dict) -> bool:
    """Compares dictionaries with strong check on equality of values"""
    
    # Return early if standard equality fails
    if d1 != d2:
      return False

    # Compare types
    values = zip(d1.values(), d2.values())
    for value in values:
      if type(value[0]) != type(value[1]):
        return False
    return True 