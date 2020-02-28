import pytest
import os
import copy
from typing import Dict, List
from compex.io.tsv import TsvReader, TsvDocument
from compex.competencies.competency_types import Competency, Word
from compex.converter.tsv2competency import convert_tsv_to_competencies
from compex.evaluation.evaluators import EvaluationSet, FMeasureEvaluator

class TestFMeasureEvaluator:
    def test_FMeasureEvaluator(self):
        test_dir = os.path.dirname(__file__)
        reader = TsvReader()
        document: TsvDocument = reader.read_tsv(os.path.join(test_dir, "test.tsv"))

        # Read a sample tsv to get test_data
        test_data: Dict[str, List[Competency]] = convert_tsv_to_competencies(document)
        # Make a deepcopy of the test data
        annotated_data: Dict[str, List[Competency]] = copy.deepcopy(test_data)

        # Inject a false positive to the annotated data
        d1 = annotated_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d1.append(Competency(Word(9, "False Positive")))

        # Inject two false negatives to the test data
        d2 = test_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d2.append(Competency(Word(8, "False negative1")))
        d2.append(Competency(Word(7, "False negative2")))

        evaluation_set = EvaluationSet(test_data, annotated_data)

        evaluator = FMeasureEvaluator()
        result = evaluator.evaluate_with_annotated_sentences(evaluation_set)

        # Make sure, the one false positive we've injected earlier is found
        assert result["false_positives"] == 1

        # Make sure, the two false negatives we've injected earlier are found
        assert result["false_negatives"] == 2

        # Make sure all true positives are found. There are 6 competencies in the tsv!
        assert result["true_positives"] == 6

        # Check the resulting measurement data
        # 6 / (6 + 1) = 0.8571428571428571
        assert result["precision"] == 0.8571428571428571
        # 6 / (6 + 2) = 0.75
        assert result["recall"] == 0.75
        assert result["f1"] == 0.7999999999999999
