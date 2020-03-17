from typing import List, Iterator, Dict, TextIO
from enum import Enum
import re, uuid

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
    """Enum for TSV layer types."""

    SPAN_LAYER = 1
    CHAIN_LAYER = 2
    RELATION_LAYER = 3

class LayerDefinition:
    """Definition of a tsv layer."""

    def __init__(self, layer_type: LayerType, id: str):
        """Create a new intance.

        Parameters
        ----------
        layer_type : LayerType
            The type of the layer.
        id : str
            The id of the layer.
        """
        self.layer_type: LayerType = layer_type
        self.id: str = id
        self.features_definitions: List[FeatureDefinition] = []

    def add_feature_definition(self, name: str):
        """Adds a feature definition to the layer.

        Parameters
        ----------
        name : str
            name of the layer.
        """
        self.features_definitions.append(FeatureDefinition(name, self))

    def __hash__(self):
        return hash((self.layer_type, self.id))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            (self.layer_type, self.id) == (other.layer_type, other.id)
        )

class FeatureDefinition:
    """Definition of a feature of a layer definition."""

    def __init__(self, name: str, layer_definition: LayerDefinition):
        """Create a new instance.

        Parameters
        ----------
        name : str
            Name of the feature.
        layer_definition : LayerDefinition
            The LayerDefinition, the feature belongs to.
        """

        self.name: str = name
        self.layer_definition: LayerDefinition = layer_definition

    def __hash__(self):
        return hash((self.name, self.layer_definition))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            (self.name, self.layer_definition) == (other.name, other.layer_definition)
        )

class TsvSchema:
    """Represents the schema of a TSV document."""

    def __init__(self):
        """Creates a new instance.

        Use the members format, span_types, chain_layers and relation_layers to fill the schema.
        """

        self.format: str = None
        self.span_types: List[LayerDefinition] = []
        self.chain_layers: List[LayerDefinition] = []
        self.relation_layers: List[LayerDefinition] = []

    def get_layer_definitions(self) -> List[LayerDefinition]:
        """Get a combined List of all LayerDefinitions of the TSV document.

        Returns
        -------
        List[LayerDefinition]
            A combined List of all LayerDefinitions of the TSV document
        """

        return self.span_types + self.chain_layers + self.relation_layers

    def get_feature_definitions(self) -> List[FeatureDefinition]:
        """Get a combined List of all FeatureDefinitions of the TSV document.

        Returns
        -------
        List[FeatureDefinition]
            A combined List of all FeatureDefinitions of the TSV document
        """

        feature_definitions: List[FeatureDefinition] = []
        for span in self.span_types:
            feature_definitions = feature_definitions + span.features_definitions
        for chain in self.chain_layers:
            feature_definitions = feature_definitions + chain.features_definitions
        for relation in self.relation_layers:
            feature_definitions = feature_definitions + relation.features_definitions
        return feature_definitions

class Feature:
    """Represents a feature of a TSV document."""

    def __init__(self, feature_definition: FeatureDefinition, span_index: str, value: str):
        """Creates a new instance.

        Parameters
        ----------
        feature_definition : FeatureDefinition
            The FeatureDefinition of the feature
        span_index : str
            The span index of the feature
        value : str
            The value of the feature
        """

        self.feature_definition: FeatureDefinition = feature_definition
        self.span_index: str = span_index
        self.value: str = value
        # self.value: Dict[str, str] = values

    def __hash__(self):
        return hash((self.feature_definition, self.span_index, self.value))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            (self.feature_definition, self.span_index, self.value) == (other.feature_definition, other.span_index, other.value)
        )

class TsvToken:
    """Represents a token of a TSV document."""

    def __init__(self, sentence_number: int, token_number: int, offset_begin: int, offset_end: int, token: str, features: Dict):
        """Create a new instance.

        Parameters
        ----------
        sentence_number : int
            The number of the sentence in the TSV file
        token_number : int
            The number of the token in the sentence
        offset_begin : int
            The offset begin in the sentence of the token
        offset_end : int
            The offset end in the sentence of the token
        token : str
            The token string itself
        features : Dict
            A Dict of features belonging to the token
        """

        self.sentence_number: int = sentence_number
        self.token_number: int = token_number
        self.offset_begin: int = offset_begin
        self.offset_end: int = offset_end
        self.token: str = token
        self.features: Dict = features

class TokenChunk:
    """Represents a chunk of tokens."""

    def __init__(self, feature: Feature, tokens: List[TsvToken]):
        """Creates a new instance.

        Parameters
        ----------
        feature : Feature
            The feature the tokens belong to.
        tokens : List[TsvToken]
            The tokens in the chunk.
        """

        self.feature: Feature = feature
        self.tokens: List[TsvToken] = tokens
        self.relations: List[TokenChunk] = []

    def add_relation(self, token_chunk):
        """Add a relation to the token chunk.

        Parameters
        ----------
        token_chunk : [type]
            Another TokenChunk this TokenChunk should be related to
        """
        self.relations.append(token_chunk)

class TsvSentence:
    """Represents a sentence of a TSV document."""

    def __init__(self, text: str, tokens: List[TsvToken]):
        """Creates a new instance.

        Parameters
        ----------
        text : str
            The sentence string
        tokens : List[TsvToken]
            A List of all tokens
        """

        self.text: str = text
        self.tokens: List[TsvToken] = tokens
        self.features: Dict[Feature, List[TsvToken]] = {}
        self.token_chunks: Dict[Feature, TokenChunk] = {}
        for token in self.tokens:
            for feature in token.features:
                if not feature in self.features:
                    self.features[feature]: List[TsvToken] = []
                self.features[feature].append(token)
        for feature, tokens in self.features.items():
            self.token_chunks[feature] = TokenChunk(feature, tokens)
        for feature, token_chunk in self.token_chunks.items():
            if token_chunk.feature.feature_definition.layer_definition.layer_type == LayerType.RELATION_LAYER:
                partos = token_chunk.feature.value.split("-")
                sentence_no = partos[0]
                token_no = partos[1]
                child: TokenChunk = None
                parent: TokenChunk = None
                for f, tc in self.token_chunks.items():
                    if tc.tokens[0].sentence_number == sentence_no and tc.tokens[0].token_number == token_no and tc.feature.feature_definition.layer_definition.layer_type != LayerType.RELATION_LAYER:
                        child = tc
                    elif tc.tokens[0].sentence_number == token_chunk.tokens[0].sentence_number and tc.tokens[0].token_number == token_chunk.tokens[0].token_number and tc.feature.feature_definition.layer_definition.layer_type != LayerType.RELATION_LAYER:
                        parent = tc
                if parent is not None and child is not None:
                    parent.add_relation(child)
        features_to_del = []
        for feature, token_chunk in self.token_chunks.items():
            if feature.feature_definition.layer_definition.layer_type == LayerType.RELATION_LAYER:
                features_to_del.append(feature)
        for feature_to_del in features_to_del:
            del self.token_chunks[feature_to_del]

class TsvDocument:
    """Represents a TSV document."""

    def __init__(self, schema: TsvSchema, sentences: List[TsvSentence]):
        """Creates a new instance.

        Parameters
        ----------
        schema : TsvSchema
            The schema of the document
        sentences : List[TsvSentence]
            A List of sentences of the TSV document
        """

        self.schema: TsvSchema = schema
        self.sentences: List[TsvSentence] = sentences

class TsvReader:
    """A class to read/parse TSV documents."""

    def read_tsv(self, tsvFile: TextIO) -> TsvDocument:
        """Reads a TSV document.

        Parameters
        ----------
        tsvFile : TextIO
            The TSV file

        Returns
        -------
        TsvDocument
            The parsed tsv document
        """

        lines = tsvFile.readlines()
        lines = [x.rstrip('\n') for x in lines]
        iterator = iter(lines)

        schema: TsvSchema = self.read_schema(iterator)
        sentences: List[TsvSentence] = self.read_sentences(iterator, schema)
        document: TsvDocument = TsvDocument(schema, sentences)

        return document

    def read_schema(self, iterator: Iterator[str]) -> TsvSchema:
        """Reads the schema of a TSV document.

        Parameters
        ----------
        iterator : Iterator[str]
            The line by line iterator of the tsv file

        Returns
        -------
        TsvSchema
            The parsed schema of the TSV document
        """

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
                    layer_def.add_feature_definition(feature)
                schema.span_types.append(layer_def)
            elif line.startswith(HEADER_PREFIX_CHAIN_LAYER):
                value = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
                layer_id = value.split("|")[0]
                features = value.split("|")[1:]
                layer_def = LayerDefinition(LayerType.CHAIN_LAYER, layer_id)
                for feature in features:
                    layer_def.add_feature_definition(feature)
                schema.chain_layers.append(layer_def)
            elif line.startswith(HEADER_PREFIX_RELATION_LAYER):
                value = line.split(HEADER_LAYER_PREFIX_SEPARATOR, 1)[1]
                layer_id = value.split("|")[0]
                features = value.split("|")[1:]
                layer_def = LayerDefinition(LayerType.RELATION_LAYER, layer_id)
                for feature in features:
                    layer_def.add_feature_definition(feature)
                schema.relation_layers.append(layer_def)
            else:
                break
        return schema

    def read_sentences(self, iterator: Iterator[str], schema: TsvSchema) -> List[TsvSentence]:
        """Reads/parses all sentences of a TSV document.

        Parameters
        ----------
        iterator : Iterator[str]
            The line by line iterator of the tsv file.
            The iterator should be at the position of the first line of the first sentence.
        schema : TsvSchema
            The schema of the TSV document

        Returns
        -------
        List[TsvSentence]
            A list of parsed sentences
        """

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
                features = self.parse_features(parts[3:], schema.get_feature_definitions())
                tokens.append(TsvToken(sentence_number, token_number, offset_begin, offset_end, token, features))

        # FIXME Dirty hack to complete the last sentence in tsv
        if sentence_started:
                    # Sentence ends
                    sentences.append(TsvSentence(current_text, tokens))
                    current_text = None
                    tokens = []
                    sentence_started = False

        return sentences

    def parse_features(self, features: List[str], feature_definitions: List[FeatureDefinition]) -> List[Feature]:
        """Parses features of a token in a TSV document.

        Parameters
        ----------
        features : List[str]
            A List of features of a token
        feature_definitions : List[FeatureDefinition]
            A list of feature definitions

        Returns
        -------
        List[Feature]
            A List of parsed features

        Raises
        ------
        Exception
            If the number of features does not match the number of feature definitions in the schema
        """

        if not features[-1]:
            del features[-1]
        if len(features) != len(feature_definitions):
            raise Exception("The number of features does not match the number of feature definitions in the schema.")
        parsed_features: List[Feature] = []

        for i, layer in enumerate(features, start=0):
            if layer != NULL_COLUMN:
                parts = layer.split("|")
                for part in parts:
                    searcho = re.search(r"^([A-Za-z0-9\-]+)(\[(\d+(_\d+)?)\])?$", part)
                    name = searcho.group(1)
                    if searcho.group(3) is None:
                        # FIXME Dirty hack to distinguish features without span-index
                        # Assign each of them a random id, so they are not part of the same span
                        span_index = uuid.uuid1()
                    else:
                        span_index = searcho.group(3)
                    parsed_features.append(Feature(feature_definitions[i], span_index, name))

        return parsed_features
