import pytest
import os
from compex.io.tsv import TsvReader, TsvDocument
from compex.converter.tsv2competency import convert_tsv_to_competencies

class TestTsvToCompetenciesConverter:
    def test_one(self):
        # Read a sample tsv
        test_dir = os.path.dirname(__file__)
        reader = TsvReader()
        document: TsvDocument = reader.read_tsv(os.path.join(test_dir, "test.tsv"))

        sentences = convert_tsv_to_competencies(document)
        print(sentences)
