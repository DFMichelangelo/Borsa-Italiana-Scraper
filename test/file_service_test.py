
#from src.file_service import FileService
#from .utils.comparers import Comparer
#from .utils.random_objects import Random_Objects

#class TestFileService:
  #def test_create_dataframe_correctly(self):
  #  bonds = [Random_Objects.random_bond(),Random_Objects.random_bond(),Random_Objects.random_bond()]
  #  bonds_dicts = [bond_dict.__dict__ for bond_dict in bonds]
  #  df = FileService.create_dataframe(bonds)
  #  new_bonds_dicts =df.to_dict('records')
  #  for (old, new) in zip(bonds_dicts,new_bonds_dicts):
  #    assert Comparer.type_aware_dict_equals(old, new) == True