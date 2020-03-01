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
        # Inject a false positive to the annotated data, so that we have a competency, that is 2/3 correct and 1/3 incorrect
        d1 = self.annotated_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d1.append(
            Competency(
                Word(9, "wow"), # correct
                [
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(3, "nice"), # correct
                                Word(4, "false positive") # incorrect
                            ]
                        )
                    )
                ]
            )
        )

        # Inject  two false negatives to the test data, so that we have a competency, that is 1/2 correct and a 1/2 false
        d2 = self.test_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d2.append(
            Competency(
                Word(9, "wow"), # correct
                [
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(3, "nice"), # correct
                                Word(5, "false negative1"), # incorrect
                                Word(6, "false negative2") # incorrect
                            ]
                        )
                    )
                ]
            )
        )

        evaluation_set = EvaluationSet(self.test_data, self.annotated_data)
        result = self.evaluator.evaluate_with_annotated_sentences(evaluation_set, True, False)

        # Make sure, the 1/3 false positive we've injected earlier is found
        assert result["false_positives"] == 0.3333333333333333
        # Make sure, the 1/2 false negative we've injected earlier is found
        assert result["false_negatives"] == 0.5
        # Make sure all true positives are found. There are 6 competencies in the tsv + the 2/3 correct one we've injected
        assert result["true_positives"] == 6.666666666666666

        # Check the resulting measurement data
        # 6.666666666666666 / (6.666666666666666 + 0.3333333333333333)
        assert result["precision"] == 0.9523809523809524
        # 6.666666666666666 / (6.666666666666666 + 0.5)
        assert result["recall"] == 0.9302325581395349
        assert result["f1"] == 0.9411764705882354
