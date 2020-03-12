import pytest
import os

from compex.annotators import SemgrexAnnotator
from compex.model.competency import Competency, CompetencyObject, ObjectContext, Word, WordChunk
from compex.model.taxonomy import TaxonomyManager, BloomsTaxonomyDimensionEnum

class TestSemgrexAnnotator:
    test_dir = None

    def setup_class(self):
        self.test_dir = os.path.dirname(__file__)
        os.environ["CORENLP_HOME"] = os.path.join(self.test_dir, "../.corenlp")

    def test_simple_without_taxonomy(self):
        sample = [
            "Studierende implementieren.",
            "Die Studierenden kennen die Grundlagen des wissenschaftlichen Arbeitens."
            ]

        c1 = Competency(Word(1, "implementieren"))
        c2 = Competency(
            Word(2, "kennen"),
            CompetencyObject(
                WordChunk(
                    [
                        Word(4, "Grundlagen"),
                        Word(5, "des"),
                        Word(6, "wissenschaftlichen"),
                        Word(7, "Arbeitens"),
                    ]
                )
            )
        )

        annotator = SemgrexAnnotator()
        result = annotator.annotate(sample)

        assert result[sample[0]][0] == c1
        assert result[sample[1]][0] == c2

    def test_simple_with_taxonomy(self):
        sample = [
            "Studierende implementieren.",
            "Die Studierenden kennen die Grundlagen des wissenschaftlichen Arbeitens."
            ]

        c1 = Competency(Word(1, "implementieren"))
        c2 = Competency(
            Word(2, "kennen"),
            CompetencyObject(
                WordChunk(
                    [
                        Word(4, "Grundlagen"),
                        Word(5, "des"),
                        Word(6, "wissenschaftlichen"),
                        Word(7, "Arbeitens"),
                    ]
                )
            )
        )

        taxonomy_manager = TaxonomyManager()
        with open(os.path.join(self.test_dir, "resources/test.json"), 'r') as json_file:
            taxonomy_verbs = taxonomy_manager.read_json(json_file)

            annotator = SemgrexAnnotator()
            result = annotator.annotate(sample, taxonomy_verbs)

            assert result[sample[0]][0] == c1
            assert result[sample[1]][0] == c2

    def test_simple_with_taxonomy_not_found(self):
            sample = [
                "Studierende kochen.",
                "Die Studierenden kennen die Grundlagen des wissenschaftlichen Arbeitens."
                ]

            c2 = Competency(
                Word(2, "kennen"),
                CompetencyObject(
                    WordChunk(
                        [
                            Word(4, "Grundlagen"),
                            Word(5, "des"),
                            Word(6, "wissenschaftlichen"),
                            Word(7, "Arbeitens"),
                        ]
                    )
                )
            )

            taxonomy_manager = TaxonomyManager()
            with open(os.path.join(self.test_dir, "resources/test.json"), 'r') as json_file:
                taxonomy_verbs = taxonomy_manager.read_json(json_file)

                annotator = SemgrexAnnotator()
                result = annotator.annotate(sample, taxonomy_verbs)

                assert not result[sample[0]]
                assert result[sample[1]][0] == c2
