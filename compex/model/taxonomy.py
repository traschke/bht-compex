from typing import Dict, TextIO
from enum import IntEnum
import jsonpickle

class BloomsTaxonomyDimensionEnum(IntEnum):
    """Represents taxonomy dimensions according to Bloom."""

    REMEMBER = 0,
    UNDERSTAND = 1,
    APPLY = 2,
    ANALYZE = 3,
    EVALUATE = 4,
    CREATE = 5

class TaxonomyManager:
    """Represents a taxonomy. Reads it's values from a given json file (see README.md for file format)"""

    def read_json(self, taxonomy_json_file: TextIO) -> Dict[str, BloomsTaxonomyDimensionEnum]:
        """Reads a json file.

        Parameters
        ----------
        taxonomy_json_file : TextIO
            The json file

        Returns
        -------
        Dict[str, BloomsTaxonomyDimensionEnum]
            A Dict with the verb as key and the taxonomy dimension as value
        """

        return self.__parse_json(self.__read_file(taxonomy_json_file))

    def __read_file(self, taxonomy_json_file: TextIO) -> str:
        """Helper function to read the contents of the file.

        Parameters
        ----------
        taxonomy_json_file : TextIO
            The json file

        Returns
        -------
        str
            The contents of the file
        """

        taxonomy_json: str = taxonomy_json_file.read()
        return taxonomy_json

    def __parse_json(self, taxonomy_json: str) -> Dict[str, BloomsTaxonomyDimensionEnum]:
        """Reads a taxonomy json document.

        Parameters
        ----------
        taxonomy_json : str
            The json document as string

        Returns
        -------
        Dict[str, BloomsTaxonomyDimensionEnum]
            A Dict with the verb as key and the taxonomy dimension as value
        """

        taxonomy_verb_dict: Dict[str, BloomsTaxonomyDimensionEnum] = {}
        decoded_json = jsonpickle.decode(taxonomy_json)
        for dimension in decoded_json:
            for verb in dimension["verbs"]:
                taxonomy_verb_dict[verb] = BloomsTaxonomyDimensionEnum(dimension["dimension"])
        return taxonomy_verb_dict
