from typing import Dict, List
from stanfordnlp.server import CoreNLPClient

from compex.competencies.competency_types import Competency, CompetencyObject, ObjectContext, Word, WordChunk

# Die Studierenden beherrschen die grundlegenden Techniken zum wissenschaftlichen Arbeiten.
# Die Studierenden können eine serverseitige Schnittstelle für moderne Webanwendungen konzipieren und implementieren.
# {tag:VVINF}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det {tag:NN}=objectdet)
# {tag:VVINF}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja))
# {tag:VVINF}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>/conj:.*/ {tag:VVINF}=competency2
# {tag:/VVINF|VVFIN/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>/conj:.*/ {tag:VVINF}=competency2
# {tag:/VVINF|VVFIN/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>nmod ({}=context ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:VVINF}=competency2
# {tag:/VVINF|VVFIN/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:VVINF}=competency2
# {tag:/VVINF|VVFIN|VVIZU/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:/VVINF|VVFIN|VVIZU/}=competency2
# pattern = '{tag:/VVINF|VVFIN/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:VVINF}=competency2'

class SemgrexAnnotator:
    """
    An annotator that annotates compentencies, their objects and contexts.
    Uses CoreNLPs dependency parser and appplies a semgrex-query after that.
    """

    annotators = ['tokenize','ssplit','depparse']
    properties = "german"
    timeout = 30000
    memory = "4G"

    pattern = '{tag:/VVINF|VVFIN|VVIZU/}=competency ?>dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja ?>det {tag:ART}=objectdetart)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:/VVINF|VVFIN|VVIZU/}=competency2'
    semgrex_properties = {"annotators": "tokenize,ssplit,depparse"}

    def annotate(self, sentences: List[str], use_bloom: bool = False) -> Dict[str, List[Competency]]:
        """Annotates multiple sentences."""
        sentences = [sentence.strip() for sentence in sentences]
        text = " ".join(sentences)
        matches = self.__run_corenlp_server_semgrex(text)
        competencies = self.__convert_to_competencies(matches)
        dicti = dict(zip(sentences, competencies))
        return dicti

    def __run_corenlp_server_semgrex(self, text: str) -> Dict:
        with CoreNLPClient(annotators=self.annotators, properties=self.properties, timeout=self.timeout, memory=self.memory) as client:
            matches = client.semgrex(text, self.pattern, properties=self.semgrex_properties)
        return matches

    def __convert_to_competencies(self, input: Dict, use_bloom: bool = False) -> List[Competency]:
        competencies: List[List[Competency]] = []
        for i, sentence in enumerate(input["sentences"]):
            sentence_competencies = []
            for key, match in sentence.items():
                if key != "length":
                    temp = match
                    competency = Competency(Word(temp["$competency"]["begin"], temp["$competency"]["text"]))

                    if "$object" in temp:
                        object_chunk = WordChunk()

                        if "$objectadja" in temp:
                            object_chunk.words.append(Word(temp["$objectadja"]["begin"], temp["$objectadja"]["text"]))

                        object_chunk.words.append(Word(temp["$object"]["begin"], temp["$object"]["text"]))

                        if "$objectdet" in temp:
                            if "$objectdetadja" in temp:
                                object_chunk.words.append(Word(temp["$objectdetadja"]["begin"], temp["$objectdetadja"]["text"]))
                            if "$objectdetart" in temp:
                                object_chunk.words.append(Word(temp["$objectdetart"]["begin"], temp["$objectdetart"]["text"]))

                            object_chunk.words.append(Word(temp["$objectdet"]["begin"], temp["$objectdet"]["text"]))

                        # Sort the words by index to remain context
                        object_chunk.words.sort(key=lambda word: word.index)

                        contexts = []

                        if "$context" in temp:
                            context_chunk = WordChunk()
                            if "$contextadja" in temp:
                                context_chunk.words.append(Word(temp["$contextadja"]["begin"], temp["$contextadja"]["text"]))

                            context_chunk.words.append(Word(temp["$context"]["begin"], temp["$context"]["text"]))

                            # Sort the words by index to remain context
                            context_chunk.words.sort(key=lambda word: word.index)

                            contexts.append(ObjectContext(context_chunk))


                        # Add the object to the competency
                        competency.objects.append(CompetencyObject(object_chunk, contexts))
                    sentence_competencies.append(competency)
            competencies.append(sentence_competencies)
        return competencies
