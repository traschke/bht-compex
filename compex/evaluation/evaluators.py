from typing import Dict, List
from enum import Enum

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

class CalculationType(Enum):
    POSITIVE = 0,
    NEGATIVE = 1

class FMeasureEvaluator:
    """Evaluator precision, recall and f1-score"""

    def evaluate_with_annotated_sentences(self, evaluation_set: EvaluationSet, consider_objects: bool = False, consider_contexts = False):
        """
        Evaluates the parser against pre-annotated sentences.
        By default, only bare competencies are used in the calculation.
        Use the appropriate parameters to also consider objects and contexts of competencies.
        """

        # TODO Take objects and contexts into account!
        # Calculate true positives and false positives
        true_positives, false_positives = self.__count_positive_negative(evaluation_set, CalculationType.POSITIVE, consider_objects, consider_contexts)

        # Calculate true negatives and false negatives
        true_negatives, false_negatives = self.__count_positive_negative(evaluation_set, CalculationType.NEGATIVE, consider_objects, consider_contexts)

        precision = self.__calculate_precision(true_positives, false_positives)
        recall = self.__calculate_recall(true_positives, false_negatives)
        f1 = self.__calculate_f1_score(precision, recall)

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "true_negatives": true_negatives,
            "false_negatives": false_negatives
            }

    def __count_positive_negative(self, evaluation_set: EvaluationSet, mode: CalculationType = CalculationType.POSITIVE, consider_objects: bool = False, consider_contexts: bool = False):
        """
        Counts either positive or negative based objects in evaluationset.
        Default is positive.
        """
        trues = 0
        falses = 0

        for _, data in evaluation_set.merged_data.items():
            if len(data) == 2:
                # Switch dicts if needed according to positive or negative mode
                if mode == CalculationType.POSITIVE:
                    dict1 = data["annotated_data"]
                    dict2 = data["test_data"]
                elif mode == CalculationType.NEGATIVE:
                    dict1 = data["test_data"]
                    dict2 = data["annotated_data"]

                for dict1_competency in dict1:
                    competency_is_found: bool = False
                    for dict2_compentency in dict2:
                        if dict2_compentency.word == dict1_competency.word:
                            competency_is_found = True
                            trues += 1
                            if consider_objects:
                                # Check the competencies objects
                                for dict1_object in dict1_competency.objects:
                                    is_whole_object_found: bool = False
                                    for dict2_object in dict2_compentency.objects:
                                        if dict2_object == dict1_object:
                                            is_whole_object_found = True
                                            # Add the count of the objects words to
                                            trues += len(dict1_object.word_chunk.words)
                                            break
                                    # Check each word of objects if the whole object is not correct
                                    if not is_whole_object_found:
                                        for dict1_object_word in dict1_object.word_chunk.words:
                                            for dict2_object in dict2_compentency.objects:
                                                is_object_word_found: bool = False
                                                for dict2_object_word in dict2_object.word_chunk.words:
                                                    if dict1_object_word == dict2_object_word:
                                                        is_object_word_found = True
                                                        trues += 1
                                                        break
                                                if not is_object_word_found:
                                                    falses += 1
                            break
                    if not competency_is_found:
                        falses += 1

        return [trues, falses]

    def __calculate_precision(self, true_positives, false_positives):
        return true_positives / (true_positives + false_positives) if true_positives or false_positives else 0.0

    def __calculate_recall(self, true_positives, false_negatives):
        return true_positives / (true_positives + false_negatives) if true_positives or false_negatives else 0.0

    def __calculate_f1_score(self, precision, recall):
        return 2 * ((precision * recall) / (precision + recall)) if precision or recall else 0.0
