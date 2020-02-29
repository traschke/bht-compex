import pytest
import os

from compex.annotators import SemgrexAnnotator
from compex.competencies.competency_types import Competency, CompetencyObject, ObjectContext, Word, WordChunk

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
