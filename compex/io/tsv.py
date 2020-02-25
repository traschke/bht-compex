from typing import List, Iterator

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

class TsvSchema:
    def __init__(self):
        self.format: str = None
        self.span_types: List[str] = []
        self.chain_layers: List[str] = []
        self.relation_layers: List[str] = []

class TsvToken:
    def __init__(self):
        self.sentence_number: int
        self.token_number: int
        self.offset_begin: int
        self.offset_end: int
        self.token: str
        self.layers: List

class TsvSentence:
    def __init__(self):
        self.text: str
        self.tokens: List[TsvToken]

class TsvDocument:
    def __init__(self, schema: TsvSchema, sentences: List[TsvSentence]):
        self.schema: TsvSchema
        self.sentences: List[TsvSentence]

class TsvReader:
    def read_tsv(self, tsvFile: str) -> TsvDocument:
        file1 = open(tsvFile, 'r')
        sentences = file1.readlines()
        iterator = iter(sentences)
        schema: TsvSchema = self.read_schema(iterator)
        sentences: List[TsvSentence] = self.read_sentences(iterator)
        document: TsvDocument = TsvDocument(schema, sentences)
        return document

    def read_schema(self, iterator: Iterator[str]) -> TsvSchema:
        schema: TsvSchema = TsvSchema()
        for line in iterator:
            if line.startswith(HEADER_PREFIX_FORMAT):
                schema.format = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
            elif line.startswith(HEADER_PREFIX_SPAN_LAYER):
                schema.span_types = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
            elif line.startswith(HEADER_PREFIX_CHAIN_LAYER):
                schema.chain_layers = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
            elif line.startswith(HEADER_PREFIX_RELATION_LAYER):
                schema.relation_layers = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
            else:
                break
        return schema

    def read_sentences(self, iterator: Iterator[str]) -> List[TsvSentence]:
        return []



