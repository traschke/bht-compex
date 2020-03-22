import pytest
import os
from compex.io.tsv import TsvReader, TsvDocument
from compex.converter.tsv2competency import convert_tsv_to_competencies


class TestTsvToCompetenciesConverter:
    def test_one(self):
        # Read a sample tsv
        test_dir = os.path.dirname(__file__)
        reader = TsvReader()
        with open(os.path.join(test_dir, "../resources/test.tsv"), 'r') as tsv_file:
            document: TsvDocument = reader.read_tsv(tsv_file)
            sentences = convert_tsv_to_competencies(document)
            assert len(sentences) == 7
