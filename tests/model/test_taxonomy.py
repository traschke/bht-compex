import pytest
import os

from compex.model.taxonomy import TaxonomyManager, BloomsTaxonomyDimensionEnum

class TestTaxonomyManager:
    def test_load_json(self):
        test_dir = os.path.dirname(__file__)
        manager = TaxonomyManager()
        with open(os.path.join(test_dir, "../resources/test.json"), 'r') as json_file:
            json = manager.read_json(json_file)
            # Test some values
            assert json["erkennen"] == BloomsTaxonomyDimensionEnum.REMEMBER
            assert json["erkunden"] == BloomsTaxonomyDimensionEnum.APPLY
            assert json["prüfen"] == BloomsTaxonomyDimensionEnum.ANALYZE
            assert json["kritisieren"] == BloomsTaxonomyDimensionEnum.EVALUATE
            assert json["komponieren"] == BloomsTaxonomyDimensionEnum.CREATE
