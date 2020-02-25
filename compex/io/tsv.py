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
    def __init__(self, sentence_number: int, token_number: int, offset_begin: int, offset_end: int, token: str, layers: List):
        self.sentence_number: int = sentence_number
        self.token_number: int = token_number
        self.offset_begin: int = offset_begin
        self.offset_end: int = offset_end
        self.token: str = token
        self.layers: List = []

class TsvSentence:
    def __init__(self, text: str, tokens: List[TsvToken]):
        self.text: str = text
        self.tokens: List[TsvToken] = tokens

class TsvDocument:
    def __init__(self, schema: TsvSchema, sentences: List[TsvSentence]):
        self.schema: TsvSchema = schema
        self.sentences: List[TsvSentence] = sentences

class TsvReader:
    def read_tsv(self, tsvFile: str) -> TsvDocument:
        lines = []
        with open(tsvFile, 'r') as file1:
            lines = file1.readlines()
            lines = [x.rstrip('\n') for x in lines]
        iterator = iter(lines)

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
                schema.span_types.append(line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1])
            elif line.startswith(HEADER_PREFIX_CHAIN_LAYER):
                schema.chain_layers.append(line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1])
            elif line.startswith(HEADER_PREFIX_RELATION_LAYER):
                schema.relation_layers.append(line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1])
            else:
                break
        return schema

    def read_sentences(self, iterator: Iterator[str]) -> List[TsvSentence]:
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
                layers = parts[3:]
                tokens.append(TsvToken(sentence_number, token_number, offset_begin, offset_end, token, layers))

        # Dirty hack to complete the last sentence in tsv
        if sentence_started:
                    # Sentence ends
                    sentences.append(TsvSentence(current_text, tokens))
                    current_text = None
                    tokens = []
                    sentence_started = False

        return sentences
