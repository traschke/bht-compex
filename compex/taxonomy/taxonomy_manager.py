from typing import Dict, TextIO
from enum import IntEnum
import jsonpickle

class BloomsTaxonomyLevelEnum(IntEnum):
    REMEMBER = 0,
    UNDERSTAND = 1,
    APPLY = 2,
    ANALYZE = 3,
    EVALUATE = 4,
    CREATE = 5

class TaxonomyManager:
    def read_json(self, taxonomy_json_file: TextIO) -> Dict[str, BloomsTaxonomyLevelEnum]:
        return self.__parse_json(self.__read_file(taxonomy_json_file))

    def __read_file(self, taxonomy_json_file: TextIO) -> str:
        taxonomy_json: str = taxonomy_json_file.read()
        return taxonomy_json

    def __parse_json(self, taxonomy_json: str) -> Dict[str, BloomsTaxonomyLevelEnum]:
        taxonomy_verb_dict: Dict[str, BloomsTaxonomyLevelEnum] = {}
        decoded_json = jsonpickle.decode(taxonomy_json)
        for dimension in decoded_json:
            for verb in dimension["verbs"]:
                taxonomy_verb_dict[verb] = BloomsTaxonomyLevelEnum(dimension["dimension"])
        return taxonomy_verb_dict
