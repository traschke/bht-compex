import pytest
import os
from compex.io.tsv import TsvReader, TsvDocument, TsvSchema, LayerDefinition, LayerType, FeatureDefinition


class TestTsvReader:
    def test_read_schema(self):
        test_dir = os.path.dirname(__file__)
        reader = TsvReader()
        with open(os.path.join(test_dir, "../resources/test.tsv"), 'r') as tsv_file:
            document: TsvDocument = reader.read_tsv(tsv_file)

            layer1 = LayerDefinition(
                LayerType.SPAN_LAYER,
                "webanno.custom.TestLayer")
            layer1.add_feature_definition(
                FeatureDefinition("CompType", layer1))
            layer2 = LayerDefinition(
                LayerType.RELATION_LAYER,
                "webanno.custom.TestLayerRelation")
            layer2.add_feature_definition(
                FeatureDefinition(
                    "BT_webanno.custom.TestLayer", layer2))

            assert document.schema.format == "WebAnno TSV 3.2"
            assert len(document.schema.get_layer_definitions()) == 2
            assert document.schema.span_types[0] == layer1
            assert document.schema.relation_layers[0] == layer2

    def test_read_sentences(self):
        test_dir = os.path.dirname(__file__)
        reader = TsvReader()
        with open(os.path.join(test_dir, "../resources/test.tsv"), 'r') as tsv_file:
            document: TsvDocument = reader.read_tsv(tsv_file)

            assert document.sentences
            assert len(document.sentences) == 7
