from typing import Dict, List

from compex.competencies.competency_types import Competency

class FMeasureEvaluator:
    """Evaluator precision, recall and f1-score"""

    def evaluate_with_annotated_sentences(self, annotated_sentences: Dict[str, List[Competency]]):
        """Evaluates the parser against pre-annotated sentences"""

        for annotated_sentence in annotated_sentences:
            # TODO Annotate with compex!

            # TODO Fetch true positives, false positives and false negatives competencies, objects and contexts
            true_positives = None
            false_positives = None
            false_negatives = None

            # TODO Calculate precision
            precision = self.__calculate_precision(true_positives, false_negatives, false_positives)

            # TODO Calcalate recall
            recall = self.__calculate_recall(true_positives, false_negatives)

            # TODO Calculate F1-score
            f1 = self.__calculate_f1_score(precision, recall)
        return

    def __calculate_precision(self, true_positives, false_negatives, false_positives):
        raise NotImplementedError()

    def __calculate_recall(self, true_positives, false_negatives):
        raise NotImplementedError()

    def __calculate_f1_score(self, precision, recall):
        return 2 * ((precision * recall) / (precision + recall))
