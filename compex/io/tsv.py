from typing import List, Iterator, Dict
from enum import Enum
import re

# See https://webanno.github.io/webanno/releases/3.4.5/docs/user-guide.html#sect_webannotsv

HEADER_LAYER_PREFIX_SEPARATOR = "="
HEADER_PREFIX_FORMAT =         "#FORMAT" + HEADER_LAYER_PREFIX_SEPARATOR
HEADER_PREFIX_CHAIN_LAYER =    "#T_CH"   + HEADER_LAYER_PREFIX_SEPARATOR
HEADER_PREFIX_RELATION_LAYER = "#T_RL"   + HEADER_LAYER_PREFIX_SEPARATOR
HEADER_PREFIX_SPAN_LAYER =     "#T_SP"   + HEADER_LAYER_PREFIX_SEPARATOR

SENTENCE_IDENTIFICATOR = "#Text="
FIELD_SEPARATOR = "\t"
RANGE_SEPERATOR = "-"
LINE_BREAK      = '\n'
NULL_COLUMN     = "_"

class LayerType(Enum):
    SPAN_LAYER = 1
    CHAIN_LAYER = 2
    RELATION_LAYER = 3

# FORMAT=WebAnno TSV 3.2
# T_SP=webanno.custom.TestLayer|CompType
# T_RL=webanno.custom.TestLayerRelation|BT_webanno.custom.TestLayer
#
#Text=Die Studierenden beherrschen die grundlegenden Techniken zum wissenschaftlichen Arbeiten.
# 6-1	703-706	Die	_	_
# 6-2	707-719	Studierenden	_	_
# 6-3	720-731	beherrschen	competency	_
# 6-4	732-735	die	_	_
# 6-5	736-749	grundlegenden	object[4]	6-3[0_4]
# 6-6	750-759	Techniken	object[4]	_
# 6-7	760-763	zum	object[4]	_
# 6-8	764-782	wissenschaftlichen	object[4]	_
# 6-9	783-791	Arbeiten	object[4]	_
# 6-10	791-792	.	_	_

class LayerDefinition:
    def __init__(self, layer_type: LayerType, id: str):
        self.layer_type: LayerType = layer_type
        self.id: str = id
        self.features: List[FeatureDefinition] = []

    def add_feature(self, name: str):
        self.features.append(FeatureDefinition(name, self))

class FeatureDefinition:
    def __init__(self, name: str, layer_definition: LayerDefinition):
        self.name: str = name
        self.layer_definition: LayerDefinition = layer_definition



class TsvSchema:
    def __init__(self):
        self.format: str = None
        self.span_types: List[LayerDefinition] = []
        self.chain_layers: List[LayerDefinition] = []
        self.relation_layers: List[LayerDefinition] = []

    def get_layer_definitions(self) -> List[LayerDefinition]:
        # Layer
        # spans = {self.span_types[i]: LayerType.SPAN_LAYER for i in range(0, len(self.span_types))}
        # chains = {self.chain_layers[i]: LayerType.CHAIN_LAYER for i in range(0, len(self.chain_layers))}
        # relas = {self.relation_layers[i]: LayerType.RELATION_LAYER for i in range(0, len(self.relation_layers))}
        return self.span_types + self.chain_layers + self.relation_layers

    def get_feature_definitions(self) -> List[FeatureDefinition]:
        feature_definitions: List[FeatureDefinition] = []
        for span in self.span_types:
            feature_definitions = feature_definitions + span.features
        for chain in self.chain_layers:
            feature_definitions = feature_definitions + chain.features
        for relation in self.relation_layers:
            feature_definitions = feature_definitions + relation.features
        return feature_definitions

class TsvToken:
    def __init__(self, sentence_number: int, token_number: int, offset_begin: int, offset_end: int, token: str, features: Dict):
        self.sentence_number: int = sentence_number
        self.token_number: int = token_number
        self.offset_begin: int = offset_begin
        self.offset_end: int = offset_end
        self.token: str = token
        self.features: Dict = features

class TsvSentence:
    def __init__(self, text: str, tokens: List[TsvToken]):
        self.text: str = text
        self.tokens: List[TsvToken] = tokens

class TsvDocument:
    def __init__(self, schema: TsvSchema, sentences: List[TsvSentence]):
        self.schema: TsvSchema = schema
        self.sentences: List[TsvSentence] = sentences

class Feature:
    def __init__(self, feature_definition: FeatureDefinition, values: Dict[str, str]):
        self.feature_definition: FeatureDefinition = feature_definition
        self.value: Dict[str, str] = values

class TsvReader:
    def read_tsv(self, tsvFile: str) -> TsvDocument:
        lines = []
        with open(tsvFile, 'r') as file1:
            lines = file1.readlines()
            lines = [x.rstrip('\n') for x in lines]
        iterator = iter(lines)

        schema: TsvSchema = self.read_schema(iterator)
        sentences: List[TsvSentence] = self.read_sentences(iterator, schema)
        document: TsvDocument = TsvDocument(schema, sentences)

        return document

    def read_schema(self, iterator: Iterator[str]) -> TsvSchema:
        schema: TsvSchema = TsvSchema()
        for line in iterator:
            if line.startswith(HEADER_PREFIX_FORMAT):
                schema.format = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
            elif line.startswith(HEADER_PREFIX_SPAN_LAYER):
                value = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
                layer_id = value.split("|")[0]
                features = value.split("|")[1:]
                layer_def = LayerDefinition(LayerType.SPAN_LAYER, layer_id)
                for feature in features:
                    layer_def.add_feature(feature)
                schema.span_types.append(layer_def)
            elif line.startswith(HEADER_PREFIX_CHAIN_LAYER):
                value = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
                layer_id = value.split("|")[0]
                features = value.split("|")[1:]
                layer_def = LayerDefinition(LayerType.CHAIN_LAYER, layer_id)
                for feature in features:
                    layer_def.add_feature(feature)
                schema.chain_layers.append(layer_def)
            elif line.startswith(HEADER_PREFIX_RELATION_LAYER):
                value = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
                layer_id = value.split("|")[0]
                features = value.split("|")[1:]
                layer_def = LayerDefinition(LayerType.RELATION_LAYER, layer_id)
                for feature in features:
                    layer_def.add_feature(feature)
                schema.relation_layers.append(layer_def)
            else:
                break
        return schema

    def read_sentences(self, iterator: Iterator[str], schema: TsvSchema) -> List[TsvSentence]:
        sentences: List[TsvSentence] = []
        tokens: List[TsvToken] = []
        current_text = None
        sentence_started = False
        for line in iterator:
            if line.startswith(SENTENCE_IDENTIFICATOR):
                # Sentence starts
                current_text = line.split(HEADER_LAYER_PREFIX_SEPARATOR)[1]
                sentence_started = True
            elif not line:
                if sentence_started:
                    # Sentence ends
                    # TODO link the relations
                    # TODO Create token chunks if span relation
                    sentences.append(TsvSentence(current_text, tokens))
                    current_text = None
                    tokens = []
                    sentence_started = False
            else:
                # parse token
                parts = line.split(FIELD_SEPARATOR)
                sentence_number, token_number = parts[0].split(RANGE_SEPERATOR)
                offset_begin, offset_end = parts[1].split(RANGE_SEPERATOR)
                token = parts[2]
                layers = self.parse_features(parts[3:], schema.get_feature_definitions())
                tokens.append(TsvToken(sentence_number, token_number, offset_begin, offset_end, token, layers))

        # Dirty hack to complete the last sentence in tsv
        if sentence_started:
                    # Sentence ends
                    sentences.append(TsvSentence(current_text, tokens))
                    current_text = None
                    tokens = []
                    sentence_started = False

        return sentences

    def parse_features(self, features: List[str], feature_definitions: List[FeatureDefinition]) -> List[Feature]:
        if not features[-1]:
            del features[-1]
        if len(features) != len(feature_definitions):
            raise Exception("The number of features does not match the number of features definitions in the schema.")
        parsed_features: List[Feature] = []

        for i, layer in enumerate(features, start=0):
            if layer != NULL_COLUMN:
                parts = layer.split("|")
                for part in parts:
                    searcho = re.search(r"^([A-Za-z0-9\-]+)(\[(\d+(_\d+)?)\])?$", part)
                    name = searcho.group(1)
                    if searcho.group(3) is None:
                        index = 0
                    else:
                        index = searcho.group(3)
                    parsed_features.append(Feature(feature_definitions[i], {index: name}))

        return parsed_features
