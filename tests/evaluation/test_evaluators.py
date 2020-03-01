import pytest
import os
import copy
from typing import Dict, List
from compex.io.tsv import TsvReader, TsvDocument
from compex.competencies.competency_types import Competency, CompetencyObject, Word, WordChunk
from compex.converter.tsv2competency import convert_tsv_to_competencies
from compex.evaluation.evaluators import EvaluationSet, FMeasureEvaluator

class TestFMeasureEvaluator:
    evaluator = None
    test_data = None
    annotated_data = None

    def setup_method(self, method):
        test_dir = os.path.dirname(__file__)
        reader = TsvReader()
        with open(os.path.join(test_dir, "test.tsv"), 'r') as tsv_file:
            document: TsvDocument = reader.read_tsv(tsv_file)

            # Read a sample tsv to get test_data
            self.test_data: Dict[str, List[Competency]] = convert_tsv_to_competencies(document)
            # Make a deepcopy of the test data
            self.annotated_data: Dict[str, List[Competency]] = copy.deepcopy(self.test_data)

            # self.evaluation_set = EvaluationSet(test_data, annotated_data)
            self.evaluator = FMeasureEvaluator()

    def test_FMeasureEvaluator_only_competencies(self):
        # Inject a false positive to the annotated data
        d1 = self.annotated_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d1.append(Competency(Word(9, "False Positive")))

        # Inject two false negatives to the test data
        d2 = self.test_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d2.append(Competency(Word(8, "False negative1")))
        d2.append(Competency(Word(7, "False negative2")))

        evaluation_set = EvaluationSet(self.test_data, self.annotated_data)
        result = self.evaluator.evaluate_with_annotated_sentences(evaluation_set, False, False)

        # Make sure, the one false positive we've injected earlier is found
        assert result["false_positives"] == 1
        # Make sure, the two false negatives we've injected earlier are found
        assert result["false_negatives"] == 2
        # Make sure all true positives are found. There are 6 competencies in the tsv!
        assert result["true_positives"] == 6
        # Check the resulting measurement data
        # 6 / (6 + 1)
        assert result["precision"] == 0.8571428571428571
        # 6 / (6 + 2)
        assert result["recall"] == 0.75
        assert result["f1"] == 0.7999999999999999

    def test_FMeasureEvaluator_with_objects(self):
        # Inject a false positive to the annotated data
        d1 = self.annotated_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d1.append(
            Competency(
                Word(9, "wow"),
                [
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(3, "nice"),
                                Word(4, "false positive")
                            ]
                        )
                    )
                ]
            )
        )

        # Inject a false negative to the test data
        d2 = self.test_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d2.append(
            Competency(
                Word(9, "wow"),
                [
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(3, "nice"),
                                Word(5, "false negative1"),
                                Word(6, "false negative2")
                            ]
                        )
                    )
                ]
            )
        )

        evaluation_set = EvaluationSet(self.test_data, self.annotated_data)
        result = self.evaluator.evaluate_with_annotated_sentences(evaluation_set, True, False)

        # Make sure, the one false positive we've injected earlier is found
        assert result["false_positives"] == 1
        # Make sure, the two false negatives we've injected earlier are found
        assert result["false_negatives"] == 2
        # Make sure all true positives are found. There are 6 competencies in the tsv!
        assert result["true_positives"] == 28
        # Check the resulting measurement data
        # 28 / (28 + 1)
        assert result["precision"] == 0.9655172413793104
        # 28 / (28 + 2)
        assert result["recall"] == 0.9333333333333333
        assert result["f1"] == 0.9491525423728815
