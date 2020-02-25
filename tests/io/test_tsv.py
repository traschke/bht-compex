import pytest
import os
from compex.io.tsv import TsvReader, TsvDocument, TsvSchema

class TestTsvReader:
    def test_read_schema(self):
        test_dir = os.path.dirname(__file__)
        reader = TsvReader()
        document: TsvDocument = reader.read_tsv(os.path.join(test_dir, "test.tsv"))

        assert document.schema.format == "WebAnno TSV 3.2"
        assert document.schema.span_types[0] == "webanno.custom.TestLayer|CompType"
        assert document.schema.relation_layers[0] == "webanno.custom.TestLayerRelation|BT_webanno.custom.TestLayer"
