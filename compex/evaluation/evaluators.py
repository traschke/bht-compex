from typing import Dict, List

from compex.competencies.competency_types import Competency
from compex.annotators import SemgrexAnnotator

class EvaluationSet:
    def __init__(self, test_data: Dict[str, List[Competency]], annotated_data: Dict[str, List[Competency]]):
        self.test_data: List[Competency] = test_data
        self.annotated_data: List[Competency] = annotated_data
        self.merged_data: Dict[str, Dict[str, Competency]] = self.__merge_data(test_data, annotated_data)

    def __merge_data(self, test_data, annotated_data):
        ''' Merge dictionaries and keep values of common keys in list'''
        merged_data = {}
        for key, item in test_data.items():
            if not key in merged_data:
                merged_data[key] = {}
            merged_data[key]["test_data"] = item

        for key, item in annotated_data.items():
            if not key in merged_data:
                merged_data[key] = {}
            merged_data[key]["annotated_data"] = item

        return merged_data

class FMeasureEvaluator:
    """Evaluator precision, recall and f1-score"""

    def evaluate_with_annotated_sentences(self, evaluation_set: EvaluationSet, respect_objects: bool = False, respect_contexts = False):
        """
        Evaluates the parser against pre-annotated sentences.
        By default, only bare competencies are used in the calculation.
        Use the appropriate parameters to also consider objects and contexts of competencies.
        """

        # Fetch true positives, false positives and false negatives competencies, objects and contexts
        # TODO Take objects and contexts into account!
        true_positives = 0
        false_positives = 0
        false_negatives = 0

        # Calculate true positives and false positives
        for sentence, data in evaluation_set.merged_data.items():
            if len(data) == 2:
                for annotated_data_competency in data["annotated_data"]:
                    is_found: bool = False
                    for test_data_compentency in data["test_data"]:
                        if test_data_compentency == annotated_data_competency:
                            is_found = True
                            true_positives += 1
                    if not is_found:
                        false_positives += 1

        # Calculate false negatives
        for sentence, data in evaluation_set.merged_data.items():
            if len(data) == 2:
                for test_data_compentency in data["test_data"]:
                    is_found: bool = False
                    for annotated_data_competency in data["annotated_data"]:
                        if test_data_compentency == annotated_data_competency:
                            is_found = True
                    if not is_found:
                        false_negatives += 1

        precision = self.__calculate_precision(true_positives, false_negatives, false_positives)
        recall = self.__calculate_recall(true_positives, false_negatives)
        f1 = self.__calculate_f1_score(precision, recall)

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives
            }

    def __calculate_precision(self, true_positives, false_negatives, false_positives):
        return true_positives / (true_positives + false_positives) if true_positives or false_positives else 0.0

    def __calculate_recall(self, true_positives, false_negatives):
        return true_positives / (true_positives + false_negatives) if true_positives or false_negatives else 0.0

    def __calculate_f1_score(self, precision, recall):
        return 2 * ((precision * recall) / (precision + recall)) if precision or recall else 0.0
