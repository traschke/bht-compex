from typing import Dict, List
from stanfordnlp.server import CoreNLPClient

from compex.model.competency import Competency, CompetencyObject, ObjectContext, Word, WordChunk
from compex.model.taxonomy import TaxonomyManager, BloomsTaxonomyDimensionEnum

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
    """An annotator that annotates competencies, their objects and contexts with CoreNLP and Semgrex.

    Uses CoreNLPs dependency parser and appplies a semgrex-query on the dependency graph to extract competency triples.
    """

    annotators = ['tokenize', 'ssplit', 'depparse']
    properties = "german"
    timeout = 30000
    memory = "4G"

    pattern = '{tag:/VVINF|VVFIN|VVIZU/}=competency ?>dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja ?>det {tag:ART}=objectdetart)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:/VVINF|VVFIN|VVIZU/}=competency2'
    semgrex_properties = {"annotators": "tokenize,ssplit,depparse"}

    def annotate(self, sentences: List[str], taxonomy_verbs: Dict[str,
                                                                  BloomsTaxonomyDimensionEnum] = None) -> Dict[str, List[Competency]]:
        """Annotates multiple sentences with a dependency parser and a Semgrex query.

        Uses the Semgrex query defined in self.pattern.

        Parameters
        ----------
        sentences : List[str]
            A list of sentences to extract competency triples from.
        taxonomy_verbs : Dict[str, BloomsTaxonomyDimensionEnum], optional
            An optional taxonomy dict. If set, only accept comptency verbs that are defined in this dict.
            Adds taxonomy dimenson to the Competency object. By default None.

        Returns
        -------
        Dict[str, List[Competency]]
            A dictionary with the sentences as keys and a list of extracted competency triples as values.
        """

        sentences = [sentence.strip() for sentence in sentences]
        matches = {}
        # Temporarely fix: Send each sentence seperately to CoreNLP, as CoreNLPs sentence splitter splits sentences differently than input testdata.
        # This generates a higher performance penalty to CoreNLP, as it loads
        # the needed annotators for each sentence.
        with CoreNLPClient(annotators=self.annotators, properties=self.properties, timeout=self.timeout, memory=self.memory) as client:
            for sentence in sentences:
                match = self.__run_corenlp_server_semgrex(client, sentence)
                matches[sentence] = match

        competencies = self.__convert_to_competencies(matches, taxonomy_verbs)
        return competencies

    def __run_corenlp_server_semgrex(self, client, text: str) -> Dict:
        """Runs executes the Semgrex query on text.

        Parameters
        ----------
        client : [type]
            The CoreNLP client to use.
        text : str
            The text to execute the semgrex query on.

        Returns
        -------
        Dict
            The response of the CoreNLP semgrex resource.
        """

        matches = client.semgrex(
            text, self.pattern, properties=self.semgrex_properties)
        return matches

    def __convert_to_competencies(
            self, input: Dict[str, Dict], taxonomy_verbs: Dict[str, BloomsTaxonomyDimensionEnum] = None) -> Dict[str, List[Competency]]:
        """Converts the response from CoreNLPs semgrex resource to competency triples.

        Parameters
        ----------
        input : Dict[str, Dict]
            A dictionary with sentences as keys and CoreNLP semgrex responses as values.
        taxonomy_verbs : Dict[str, BloomsTaxonomyDimensionEnum], optional
            An optional taxonomy dict. If set, only accept comptency verbs that are defined in this dict.
            Adds taxonomy dimenson to the Competency object. By default None.

        Returns
        -------
        Dict[str, List[Competency]]
            A dictionary with the sentences as keys and a list of extracted competency triples as values.
        """

        competencies: Dict[str, List[Competency]] = {}

        for sentenceSem, dicto in input.items():
            for i, sentence in enumerate(dicto["sentences"]):
                sentence_competencies = []
                for key, match in sentence.items():
                    if key != "length":
                        temp = match
                        competency_text = temp["$competency"]["text"]
                        taxonomy_verb_found: bool = False
                        if taxonomy_verbs:
                            if competency_text in taxonomy_verbs:
                                taxonomy_level: BloomsTaxonomyDimensionEnum = taxonomy_verbs[
                                    competency_text]
                                competency = Competency(
                                    Word(
                                        temp["$competency"]["begin"],
                                        competency_text),
                                    taxonomy_dimension=taxonomy_level)
                                taxonomy_verb_found = True
                        else:
                            competency = Competency(
                                Word(temp["$competency"]["begin"], competency_text))

                        if not taxonomy_verbs or taxonomy_verb_found:
                            if "$object" in temp:
                                object_chunk = WordChunk()

                                if "$objectadja" in temp:
                                    object_chunk.words.append(
                                        Word(
                                            temp["$objectadja"]["begin"],
                                            temp["$objectadja"]["text"]))

                                object_chunk.words.append(
                                    Word(temp["$object"]["begin"], temp["$object"]["text"]))

                                if "$objectdet" in temp:
                                    if "$objectdetadja" in temp:
                                        object_chunk.words.append(
                                            Word(
                                                temp["$objectdetadja"]["begin"],
                                                temp["$objectdetadja"]["text"]))
                                    if "$objectdetart" in temp:
                                        object_chunk.words.append(
                                            Word(
                                                temp["$objectdetart"]["begin"],
                                                temp["$objectdetart"]["text"]))

                                    object_chunk.words.append(
                                        Word(
                                            temp["$objectdet"]["begin"],
                                            temp["$objectdet"]["text"]))

                                # Sort the words by index to remain context
                                object_chunk.words.sort(
                                    key=lambda word: word.index)

                                contexts = []

                                if "$context" in temp:
                                    context_chunk = WordChunk()
                                    if "$contextadja" in temp:
                                        context_chunk.words.append(
                                            Word(temp["$contextadja"]["begin"], temp["$contextadja"]["text"]))

                                    context_chunk.words.append(
                                        Word(temp["$context"]["begin"], temp["$context"]["text"]))

                                    # Sort the words by index to remain context
                                    context_chunk.words.sort(
                                        key=lambda word: word.index)

                                    contexts.append(
                                        ObjectContext(context_chunk))

                                # Add the object to the competency
                                competency.objects.append(
                                    CompetencyObject(object_chunk, contexts))
                            sentence_competencies.append(competency)
                competencies[sentenceSem] = sentence_competencies
        return competencies
