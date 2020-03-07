import argparse
import sys
import jsonpickle
from typing import Dict, List, TextIO

from compex.annotators import SemgrexAnnotator
from compex.io.tsv import TsvReader, TsvDocument
from compex.converter.tsv2competency import convert_tsv_to_competencies
from compex.evaluation.evaluators import EvaluationSet, FMeasureEvaluator
from compex.competencies.competency_types import Competency
from compex.taxonomy.taxonomy_manager import TaxonomyManager, BloomsTaxonomyLevelEnum

class BloomsTaxonomyLevelEnumHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj: BloomsTaxonomyLevelEnum, data):  # data contains {}
        data = obj.value
        return data

def parse_args():
    parser = argparse.ArgumentParser("compex")
    subparser = parser.add_subparsers(dest="mode")

    # Setup evaluate args
    evaluation_parser = subparser.add_parser("evaluate", help="Evaluate the implemented extraction model.")
    evaluation_parser.add_argument("tsv", action="store", type=argparse.FileType("r"),
                                    help="Path to a WebAnno TSV file with annotated data. See README.md for further information.")
    evaluation_parser.add_argument("--objects", action="store_true",
                                    help="Consider objects in evaluation.")
    evaluation_parser.add_argument("--contexts", action="store_true",
                                    help="Consider contexts in evaluation.")

    # Setup extract args
    extract_parser = subparser.add_parser("extract",help="Extract competencies from given plain text sentences. Prints results as json to stdout.")
    extract_parser.add_argument("sentences", nargs="?", action="store", type=argparse.FileType("r"), default=sys.stdin,
                                help="Path to either a single file containing one sentence per line or a folder with multiple files. Can also be piped through stdin.")
    extract_parser.add_argument("--taxonomyjson", action="store", type=argparse.FileType("r"),
                                help="Check if competency verbs are part of a taxonomy json file. If found, append their taxonomy dimension. If not found, a competency is not valid.")

    args = parser.parse_args()

    # Error handling
    if args.mode == "evaluate":
        if args.contexts and args.objects is False:
            parser.error("--contexts requires --objects.")


    return args

def evaluate(tsv_file: TextIO, consider_objects: bool = False, consider_contexts: bool = False):
    reader: TsvReader = TsvReader()
    document: TsvDocument = reader.read_tsv(tsv_file)

    test_data: Dict[str, List[Competency]] = convert_tsv_to_competencies(document)

    text: List[str] = []
    for sentence in document.sentences:
        text.append(sentence.text)

    annotator = SemgrexAnnotator()
    annotated_data = annotator.annotate(text)

    evaluation_set = EvaluationSet(test_data, annotated_data)

    evaluator = FMeasureEvaluator()
    result = evaluator.evaluate_with_annotated_sentences(evaluation_set, consider_objects, consider_contexts)
    output_json = jsonpickle.encode(result, unpicklable=False)
    print(output_json)

def extract(text_file: TextIO, taxonomy_json: TextIO):
    taxonomy_verbs = None
    if taxonomy_json:
        taxonomy_manager = TaxonomyManager()
        taxonomy_verbs = taxonomy_manager.read_json(taxonomy_json)
        jsonpickle.handlers.registry.register(BloomsTaxonomyLevelEnum, BloomsTaxonomyLevelEnumHandler)
    text = text_file.readlines()
    annotator = SemgrexAnnotator()
    result = annotator.annotate(text, taxonomy_verbs)
    output_json = jsonpickle.encode(result, unpicklable=False)
    print(output_json)

def main():
    args = parse_args()

    if args.mode == "extract":
        extract(args.sentences, args.taxonomyjson)
    elif args.mode == "evaluate":
        evaluate(args.tsv, args.objects, args.contexts)

if __name__ == '__main__':
    main()
