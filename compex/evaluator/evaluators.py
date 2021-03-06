from typing import Dict, List
from enum import Enum

from compex.model.competency import Competency
from compex.extractor.corenlp_semgrex_extractor import SemgrexAnnotator


class EvaluationSet:
    """Helper class to manage testdata and data annotated by an algorithm."""

    def __init__(self, test_data: Dict[str, List[Competency]],
                 annotated_data: Dict[str, List[Competency]]):
        self.test_data: List[Competency] = test_data
        self.annotated_data: List[Competency] = annotated_data
        self.merged_data: Dict[str, Dict[str, Competency]
                               ] = self.__merge_data(test_data, annotated_data)

    def __merge_data(self, test_data: Dict[str, List[Competency]],
                     annotated_data: Dict[str, List[Competency]]) -> Dict[str, Dict[str, Competency]]:
        """Merge dictionaries and keep values of common keys in list.

        Parameters
        ----------
        test_data : Dict[str, List[Competency]]
            The testdata.
        annotated_data : Dict[str, List[Competency]]
            Data annotated by an algorithm.

        Returns
        -------
        Dict[str, Dict[str, Competency]]
            A dict containing merged data, so that both dicts have same keys.
        """

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

    def evaluate_with_annotated_sentences(
            self, evaluation_set: EvaluationSet, consider_objects: bool = False, consider_contexts=False):
        """Evaluates the parser against pre-annotated sentences.

        By default, only bare competencies are used in the calculation.
        Use the appropriate parameters to also consider objects and contexts of competencies.

        Parameters
        ----------
        evaluation_set : EvaluationSet
            The EvaluationSet to use for evaluation.
        consider_objects : bool, optional
            Consider competency triple's objects in the calculation, by default False
        consider_contexts : bool, optional
            Consider competency triple's contexts in the calculation, by default False

        Returns
        -------
        Dict
            Dictionary with evaluation results such as precision, recall and f1.
        """

        # Calculate true positives and false positives
        true_positives, false_positives = self.__count_positive_negative(
            evaluation_set, CalculationType.POSITIVE, consider_objects, consider_contexts)

        # Calculate true negatives and false negatives
        true_negatives, false_negatives = self.__count_positive_negative(
            evaluation_set, CalculationType.NEGATIVE, consider_objects, consider_contexts)

        precision = self.__calculate_precision(true_positives, false_positives)
        recall = self.__calculate_recall(true_positives, false_negatives)
        f1 = self.__calculate_f1_score(precision, recall)

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "positives": {
                "true": true_positives,
                "false": false_positives
            },
            "negatives": {
                "true": true_negatives,
                "false": false_negatives
            }
        }

    def __count_positive_negative(self, evaluation_set: EvaluationSet, mode: CalculationType = CalculationType.POSITIVE,
                                  consider_objects: bool = False, consider_contexts: bool = False) -> List[float]:
        """Counts either positive or negative based objects in evaluationset.

        A completely correct competency gets a score of 1.0. If considered, every object and context
        is treated equally in the calculation, so that a correct competency which has a two worded object,
        but only one of them is found, it's 2/3 correct (competency + one object word) and 1/3 incorrect
        (the other object word). If the competency is not found, it's score is 0.0.
        Default mode is positive.

        Parameters
        ----------
        evaluation_set : EvaluationSet
            The EvaluationSet to use for evaluation.
        mode : CalculationType, optional
            Positive or negative based calculation, by default CalculationType.POSITIVE
        consider_objects : bool, optional
            Consider competency triple's objects in the calculation, by default False
        consider_contexts : bool, optional
            Consider competency triple's contexts in the calculation, by default False

        Returns
        -------
        List[float]
            A list with two values, true and false postives/negatives.
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
                    in_comp_trues = 0
                    in_comp_falses = 0
                    competency_is_found: bool = False
                    for dict2_compentency in dict2:
                        if dict2_compentency.word == dict1_competency.word:
                            competency_is_found = True
                            in_comp_trues += 1
                            if consider_objects:
                                # Check the competencies objects
                                for dict1_object in dict1_competency.objects:
                                    is_whole_object_found: bool = False
                                    for dict2_object in dict2_compentency.objects:
                                        if dict2_object == dict1_object:
                                            is_whole_object_found = True
                                            # Add the count of the objects
                                            # words to
                                            in_comp_trues += len(
                                                dict1_object.word_chunk.words)
                                            break
                                    # Check each word of objects if the whole
                                    # object is not correct
                                    if not is_whole_object_found:
                                        for dict1_object_word in dict1_object.word_chunk.words:
                                            is_object_word_found: bool = False
                                            for dict2_object in dict2_compentency.objects:
                                                for dict2_object_word in dict2_object.word_chunk.words:
                                                    if dict1_object_word == dict2_object_word:
                                                        is_object_word_found = True
                                                        in_comp_trues += 1
                                                        break
                                                if is_object_word_found:
                                                    break
                                            if not is_object_word_found:
                                                in_comp_falses += 1
                                    # Check the objects contexts
                                    if consider_contexts:
                                        for dict1_context in dict1_object.contexts:
                                            is_whole_context_found: bool = False
                                            for dict2_object in dict2_compentency.objects:
                                                for dict2_context in dict2_object.contexts:
                                                    if dict2_context == dict1_context:
                                                        is_whole_context_found = True
                                                        in_comp_trues += len(
                                                            dict1_context.word_chunk.words)
                                                        break
                                            # Check each word of context if the
                                            # whole context is not correct
                                            if not is_whole_context_found:
                                                for dict1_context_word in dict1_context.word_chunk.words:
                                                    is_context_word_found: bool = False
                                                    for dict2_object in dict2_compentency.objects:
                                                        for dict2_context in dict2_object.contexts:
                                                            for dict2_context_word in dict2_context.word_chunk.words:
                                                                if dict1_context_word == dict2_context_word:
                                                                    is_context_word_found = True
                                                                    in_comp_trues += 1
                                                                    break
                                                            if is_context_word_found:
                                                                break
                                                    if not is_context_word_found:
                                                        in_comp_falses += 1
                            break
                    if not competency_is_found:
                        in_comp_falses += 1
                    trues += in_comp_trues / (in_comp_trues + in_comp_falses)
                    falses += in_comp_falses / (in_comp_trues + in_comp_falses)

        return [trues, falses]

    def __calculate_precision(self, true_positives: float,
                              false_positives: float) -> float:
        """Calculates precision.

        Parameters
        ----------
        true_positives : float
            true_positives
        false_positives : float
            true_positives

        Returns
        -------
        float
            precision based from 0.0 to 1.0
        """

        return true_positives / \
            (true_positives + false_positives) if true_positives or false_positives else 0.0

    def __calculate_recall(self, true_positives: float,
                           false_negatives: float) -> float:
        """Calculates recall.

        Parameters
        ----------
        true_positives : float
            true_positives
        false_negatives : float
            false_negatives

        Returns
        -------
        float
            recall based from 0.0 to 1.0
        """

        return true_positives / \
            (true_positives + false_negatives) if true_positives or false_negatives else 0.0

    def __calculate_f1_score(self, precision: float, recall: float) -> float:
        """Calculates f1 score.

        Parameters
        ----------
        precision : float
            precision based from 0.0 to 1.0
        recall : float
            recall based from 0.0 to 1.0

        Returns
        -------
        float
            f1 score based from 0.0 to 1.0
        """

        return 2 * ((precision * recall) / (precision + recall)
                    ) if precision or recall else 0.0
