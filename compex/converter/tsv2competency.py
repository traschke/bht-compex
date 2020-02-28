from typing import List, Dict

from compex.io.tsv import TsvDocument, Feature, TokenChunk
from compex.competencies.competency_types import Competency, CompetencyObject, ObjectContext, Word

TSV_COMPETENCY_TYPE = "CompType"
TSV_COMPETENCY_VALUE = "competency"
TSV_OBJECT_VALUE = "object"
TSV_CONTEXT_VALUE = "context"

def convert_tsv_to_competencies(tsv: TsvDocument) -> Dict[str, List[Competency]]:
    sentences = {}
    for sentence in tsv.sentences:
        current_comps: List[Competency] = []
        for feature, token_chunk in sentence.token_chunks.items():
            # TODO Go through chunks in reverse order to maintain relation chain
            # TODO find the objects and contexts that are related to the competency
            if token_chunk.feature.feature_definition.name == TSV_COMPETENCY_TYPE and token_chunk.feature.value == TSV_COMPETENCY_VALUE:
                current_comps.append(Competency(Word(token_chunk.tokens[0].token_number, token_chunk.tokens[0].token)))

        sentences[sentence.text] = current_comps
    return sentences
