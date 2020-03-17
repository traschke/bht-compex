from typing import List, Dict

from compex.io.tsv import TsvDocument, Feature, TokenChunk
from compex.model.competency import Competency, CompetencyObject, ObjectContext, Word, WordChunk

TSV_COMPETENCY_TYPE = "CompType"
TSV_COMPETENCY_VALUE = "competency"
TSV_OBJECT_VALUE = "object"
TSV_CONTEXT_VALUE = "context"

def convert_tsv_to_competencies(tsv: TsvDocument) -> Dict[str, List[Competency]]:
    """Coverts an annotated tsv file to competency triples. Correct annotation format is needed! (see README.md)

    Parameters
    ----------
    tsv : TsvDocument
        The TSVDocument to convert

    Returns
    -------
    Dict[str, List[Competency]]
        A Dict with sentences as keys and a List of competency triples as values.
    """

    sentences = {}
    for sentence in tsv.sentences:
        current_comps: List[Competency] = []
        # 1. Find competencies
        for feature, token_chunk in sentence.token_chunks.items():
            if token_chunk.feature.feature_definition.name == TSV_COMPETENCY_TYPE and token_chunk.feature.value == TSV_COMPETENCY_VALUE:
                current_comps.append(Competency(Word(convert_token_number(token_chunk.tokens[0].token_number), token_chunk.tokens[0].token)))

        # 2. Find objects of competencies
        for feature, token_chunk in sentence.token_chunks.items():
            if token_chunk.feature.feature_definition.name == TSV_COMPETENCY_TYPE and token_chunk.feature.value == TSV_OBJECT_VALUE:
                for related_token_chunk in token_chunk.relations:
                    if related_token_chunk.feature.feature_definition.name == TSV_COMPETENCY_TYPE and related_token_chunk.feature.value == TSV_COMPETENCY_VALUE:
                        # find the competency
                        for comp in current_comps:
                            if comp.word.index == convert_token_number(related_token_chunk.tokens[0].token_number):
                                # Convert tokens from object to wordchunk
                                words = []
                                for token in token_chunk.tokens:
                                    words.append(Word(convert_token_number(token.token_number), token.token))
                                # Leave contexts emtpy, because we don't know about them yet
                                comp.objects.append(CompetencyObject(WordChunk(words)))

        # 3. Find the context of objects
        for feature, token_chunk in sentence.token_chunks.items():
            if token_chunk.feature.feature_definition.name == TSV_COMPETENCY_TYPE and token_chunk.feature.value == TSV_CONTEXT_VALUE:
                for related_token_chunk in token_chunk.relations:
                    if related_token_chunk.feature.feature_definition.name == TSV_COMPETENCY_TYPE and related_token_chunk.feature.value == TSV_OBJECT_VALUE:
                        # find the object
                        for comp in current_comps:
                            for obj in comp.objects:
                                if obj.word_chunk.words[0].index == convert_token_number(related_token_chunk.tokens[0].token_number):
                                    # Convert tokens from object to wordchunk
                                    words = []
                                    for token in token_chunk.tokens:
                                        words.append(Word(convert_token_number(token.token_number), token.token))
                                    obj.contexts.append(ObjectContext(WordChunk(words)))

        # Competencies, objects and contexts converted, add them to sentence list
        sentences[sentence.text] = current_comps
    return sentences

def convert_token_number(token_number: str) -> int:
    """Helper function to convert the token index from 1 and string based to 0 and int based index.

    Parameters
    ----------
    token_number : str
        The token number as it appears in the tsv.

    Returns
    -------
    int
        The word index as it's needed for the competency triple.
    """

    return int(token_number) - 1
