import pytest
import os

from compex.taxonomy.taxonomy_manager import TaxonomyManager, BloomsTaxonomyLevelEnum

class TestTaxonomyManager:
    def test_load_json(self):
        test_dir = os.path.dirname(__file__)
        manager = TaxonomyManager()
        with open(os.path.join(test_dir, "test.json"), 'r') as json_file:
            json = manager.read_json(json_file)
            # Test some values
            assert json["erkennen"] == BloomsTaxonomyLevelEnum.REMEMBER
            assert json["erkunden"] == BloomsTaxonomyLevelEnum.APPLY
            assert json["prüfen"] == BloomsTaxonomyLevelEnum.ANALYZE
            assert json["kritisieren"] == BloomsTaxonomyLevelEnum.EVALUATE
            assert json["komponieren"] == BloomsTaxonomyLevelEnum.CREATE
