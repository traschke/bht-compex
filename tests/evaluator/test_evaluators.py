import pytest
import os
import copy
from typing import Dict, List
from compex.io.tsv import TsvReader, TsvDocument
from compex.model.competency import Competency, CompetencyObject, ObjectContext, Word, WordChunk
from compex.converter.tsv2competency import convert_tsv_to_competencies
from compex.evaluator.evaluators import EvaluationSet, FMeasureEvaluator

class TestFMeasureEvaluator:
    evaluator = None
    test_data = None
    annotated_data = None

    def setup_method(self, method):
        test_dir = os.path.dirname(__file__)
        reader = TsvReader()
        with open(os.path.join(test_dir, "../resources/test.tsv"), 'r') as tsv_file:
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
        # Inject a false positive to the annotated data, so that we have a competency, that is 2/5 correct and 3/5 incorrect
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
                    ),
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(64, "false positve"), # incorrect
                                Word(65, "false positve")  # incorrect
                            ]
                        )
                    )
                ]
            )
        )

        # Inject  two false negatives to the test data, so that we have a competency, that is 2/7 correct and a 5/7 false
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
                                Word(6, "false negative2"), # incorrect
                                Word(7, "false negative3")  # incorrect
                            ]
                        )
                    ),
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(48, "false negative4"),
                                Word(49, "false negative5")
                            ]
                        )
                    )
                ]
            )
        )

        evaluation_set = EvaluationSet(self.test_data, self.annotated_data)
        result = self.evaluator.evaluate_with_annotated_sentences(evaluation_set, True, False)

        # Make sure, the 3/5 false positive we've injected earlier is found
        assert result["false_positives"] == 0.6
        # Make sure, the 5/7 false negative we've injected earlier is found
        assert result["false_negatives"] == 0.7142857142857143
        # Make sure all true positives are found. There are 6 competencies in the tsv + the 2/5 correct one we've injected
        assert result["true_positives"] == 6.4

        # Check the resulting measurement data
        # 6.4 / (6.4 + 0.6)
        assert result["precision"] == 0.9142857142857144
        # 6.4 / (6.4 + 0.7142857142857143)
        assert result["recall"] == 0.8995983935742972
        assert result["f1"] == 0.9068825910931175

    def test_FMeasureEvaluator_with_objects_and_contexts(self):
        # Inject a false positive to the annotated data, so that we have a competency, that is 2/3 correct and 1/3 incorrect
        # 3/7 true positive, 4/7 false positive
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
                        ),
                        [
                            ObjectContext(
                                WordChunk(
                                    [
                                        Word(12, "nice word"), # correct
                                        Word(13, "false positive context1") # incorrect
                                    ]
                                )
                            ),
                            ObjectContext(
                                WordChunk(
                                    [
                                        Word(45, "false positive context2"), # incorrect
                                        Word(46, "false positive context3") # incorrect
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        )

        # 3/8 true negative, 5/8 false negative
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
                        ),
                        [
                            ObjectContext(
                                WordChunk(
                                    [
                                        Word(11, "false negative context 1"), # incorrect
                                        Word(12, "nice word") # correct
                                    ]
                                )
                            ),
                            ObjectContext(
                                WordChunk(
                                    [
                                        Word(78, "false negative context 2"), # incorrect
                                        Word(79, "false negative context 3"), # incorrect
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        )

        evaluation_set = EvaluationSet(self.test_data, self.annotated_data)
        result = self.evaluator.evaluate_with_annotated_sentences(evaluation_set, True, True)

        # Make sure, the 4/7 false positive we've injected earlier is found
        assert result["false_positives"] == 0.5714285714285714
        # Make sure, the 5/8 false negative we've injected earlier is found
        assert result["false_negatives"] == 0.625
        # Make sure all true positives are found. There are 6 competencies in the tsv + the 3/7 correct one we've injected
        assert result["true_positives"] == 6.428571428571429

        # Check the resulting measurement data
        # 6.428571428571429 / (6.428571428571429 + 0.5714285714285714)
        assert result["precision"] == 0.9183673469387755
        # 6.428571428571429 / (6.428571428571429 + 0.625)
        assert result["recall"] == 0.9113924050632911
        assert result["f1"] == 0.914866581956798

    def test_FMeasureEvaluator_100(self):
        d1 = self.annotated_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d1.append(
            Competency(Word(99, "Correct"))
        )

        d2 = self.test_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d2.append(
            Competency(Word(99, "Correct"))
        )
        evaluation_set = EvaluationSet(self.test_data, self.annotated_data)
        result = self.evaluator.evaluate_with_annotated_sentences(evaluation_set, False, False)

        # Make sure, the 3/5 false positive we've injected earlier is found
        assert result["false_positives"] == 0
        # Make sure, the 5/7 false negative we've injected earlier is found
        assert result["false_negatives"] == 0
        # Make sure all true positives are found. There are 6 competencies in the tsv + the 2/5 correct one we've injected
        assert result["true_positives"] == 7

        # Check the resulting measurement data
        # 6.4 / (6.4 + 0.6)
        assert result["precision"] == 1
        # 6.4 / (6.4 + 0.7142857142857143)
        assert result["recall"] == 1
        assert result["f1"] == 1

    def test_FMeasureEvaluator_with_objects_100(self):
        d1 = self.annotated_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d1.append(
            Competency(
                Word(99, "Correct"),
                [
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(89, "Correct"),
                                Word(90, "nice"),
                            ]
                        )
                    )
                ]
            )
        )

        d2 = self.test_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d2.append(
            Competency(
                Word(99, "Correct"),
                [
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(89, "Correct"),
                                Word(90, "nice"),
                            ]
                        )
                    )
                ]
            )
        )

        evaluation_set = EvaluationSet(self.test_data, self.annotated_data)
        result = self.evaluator.evaluate_with_annotated_sentences(evaluation_set, True, False)

        # Make sure, the 3/5 false positive we've injected earlier is found
        assert result["false_positives"] == 0
        # Make sure, the 5/7 false negative we've injected earlier is found
        assert result["false_negatives"] == 0
        # Make sure all true positives are found. There are 6 competencies in the tsv + the 2/5 correct one we've injected
        assert result["true_positives"] == 7

        # Check the resulting measurement data
        # 6.4 / (6.4 + 0.6)
        assert result["precision"] == 1
        # 6.4 / (6.4 + 0.7142857142857143)
        assert result["recall"] == 1
        assert result["f1"] == 1

    def test_FMeasureEvaluator_with_objects_and_contexts_100(self):
        d1 = self.annotated_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d1.append(
            Competency(
                Word(99, "Correct"),
                [
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(89, "Correct"),
                                Word(90, "nice"),
                            ]
                        ),
                        [
                            ObjectContext(
                                WordChunk(
                                    [
                                        Word(100, "such"),
                                        Word(101, "wow")
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        )

        d2 = self.test_data["Die Studierenden sollen in der Lage sein, eine komplexe Anwendung mit projektspezifischen Basistechniken in Teamarbeit zu konzipieren und umzusetzen."]
        d2.append(
            Competency(
                Word(99, "Correct"),
                [
                    CompetencyObject(
                        WordChunk(
                            [
                                Word(89, "Correct"),
                                Word(90, "nice"),
                            ]
                        ),
                        [
                            ObjectContext(
                                WordChunk(
                                    [
                                        Word(100, "such"),
                                        Word(101, "wow")
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        )

        evaluation_set = EvaluationSet(self.test_data, self.annotated_data)
        result = self.evaluator.evaluate_with_annotated_sentences(evaluation_set, True, True)

        # Make sure, the 3/5 false positive we've injected earlier is found
        assert result["false_positives"] == 0
        # Make sure, the 5/7 false negative we've injected earlier is found
        assert result["false_negatives"] == 0
        # Make sure all true positives are found. There are 6 competencies in the tsv + the 2/5 correct one we've injected
        assert result["true_positives"] == 7

        # Check the resulting measurement data
        # 6.4 / (6.4 + 0.6)
        assert result["precision"] == 1
        # 6.4 / (6.4 + 0.7142857142857143)
        assert result["recall"] == 1
        assert result["f1"] == 1
