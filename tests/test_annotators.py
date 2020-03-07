import pytest
import os

from compex.annotators import SemgrexAnnotator
from compex.competencies.competency_types import Competency, CompetencyObject, ObjectContext, Word, WordChunk
from compex.taxonomy.taxonomy_manager import TaxonomyManager, BloomsTaxonomyDimensionEnum

class TestSemgrexAnnotator:
    def test_simple(self):
        os.environ["CORENLP_HOME"] = "/home/timo/Downloads/stanford-corenlp-full-2018-10-05"
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
        os.environ["CORENLP_HOME"] = "/home/timo/Downloads/stanford-corenlp-full-2018-10-05"
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
        test_dir = os.path.dirname(__file__)
        with open(os.path.join(test_dir, "resources/test.json"), 'r') as json_file:
            taxonomy_verbs = taxonomy_manager.read_json(json_file)

            annotator = SemgrexAnnotator()
            result = annotator.annotate(sample, taxonomy_verbs)

            assert result[sample[0]][0] == c1
            assert result[sample[1]][0] == c2

    def test_simple_with_taxonomy_not_found(self):
            os.environ["CORENLP_HOME"] = "/home/timo/Downloads/stanford-corenlp-full-2018-10-05"
            sample = [
                "Studierende kochen.",
                "Die Studierenden kennen die Grundlagen des wissenschaftlichen Arbeitens."
                ]

            # c1 = Competency(Word(1, "implementieren"))
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
            test_dir = os.path.dirname(__file__)
            with open(os.path.join(test_dir, "resources/test.json"), 'r') as json_file:
                taxonomy_verbs = taxonomy_manager.read_json(json_file)

                annotator = SemgrexAnnotator()
                result = annotator.annotate(sample, taxonomy_verbs)

                assert not result[sample[0]]
                assert result[sample[1]][0] == c2
