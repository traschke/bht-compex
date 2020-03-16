import argparse
import sys
import os
import jsonpickle
from pathlib import Path
from typing import Dict, List, TextIO

from compex.extractor.corenlp_semgrex_extractor import SemgrexAnnotator
from compex.io.tsv import TsvReader, TsvDocument
from compex.converter.tsv2competency import convert_tsv_to_competencies
from compex.evaluator.evaluators import EvaluationSet, FMeasureEvaluator
from compex.model.competency import Competency
from compex.model.taxonomy import TaxonomyManager, BloomsTaxonomyDimensionEnum


class BloomsTaxonomyLevelEnumHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj: BloomsTaxonomyDimensionEnum, data):  # data contains {}
        data = obj.value
        return data


class FileGlob(object):
    def __init__(self, mode='r', glob_expr='**/*',
                 bufsize=-1, encoding=None, errors=None):
        self._glob_expr = glob_expr
        self._mode = mode
        self._bufsize = bufsize
        self._encoding = encoding
        self._errors = errors

    def __call__(self, string):
        is_File = False
        if os.path.isfile(string):
            is_File = True
        elif os.path.isdir(string):
            is_File = False
        else:
            raise argparse.ArgumentTypeError(
                f"readable_dir:{string} is not a valid path or file")

        if is_File:
            file_paths = [Path(string)]
        else:
            file_paths = Path(string).rglob(self._glob_expr)

        files = []
        for file_path in file_paths:
            try:
                files.append(open(file_path, self._mode,
                                  self._bufsize, self._encoding, self._errors))
            except OSError as e:
                message = "can't open '%s': %s"
                raise argparse.ArgumentTypeError(message % (file_path, e))

        return files


def parse_args():
    parser = argparse.ArgumentParser("compex")
    subparser = parser.add_subparsers(dest="mode")

    # Setup evaluate args
    evaluation_parser = subparser.add_parser(
        "evaluate", help="Evaluate the implemented extraction model.")
    evaluation_parser.add_argument("tsvpath", action="store", type=FileGlob(glob_expr="*.tsv", mode="r"),
                                   help="Path a single or multiple (a folder) WebAnno TSV file(s) with annotated data. Scans recursively if folder. See README.md for further information.")
    evaluation_parser.add_argument("--objects", action="store_true",
                                   help="Consider objects in evaluation.")
    evaluation_parser.add_argument("--contexts", action="store_true",
                                   help="Consider contexts in evaluation.")
    evaluation_parser.add_argument("--taxonomyjson", action="store", type=argparse.FileType("r"),
                                   help="Check if competency verbs are part of a taxonomy json file. If found, append their taxonomy dimension. If not found, a competency is not valid.")

    # Setup extract args
    extract_parser = subparser.add_parser(
        "extract", help="Extract competencies from given plain text sentences. Prints results as json to stdout.")
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


def evaluate(tsv_files: List[TextIO], consider_objects: bool = False,
             consider_contexts: bool = False, taxonomy_json: TextIO = None):
    taxonomy_verbs = None
    if taxonomy_json:
        taxonomy_manager = TaxonomyManager()
        taxonomy_verbs = taxonomy_manager.read_json(taxonomy_json)
        jsonpickle.handlers.registry.register(
            BloomsTaxonomyDimensionEnum, BloomsTaxonomyLevelEnumHandler)

    test_data: Dict[str, List[Competency]] = {}
    text: List[str] = []

    reader: TsvReader = TsvReader()
    for tsv_file in tsv_files:
        document: TsvDocument = reader.read_tsv(tsv_file)
        test_data.update(convert_tsv_to_competencies(document))

    for sentence in test_data:
        text.append(sentence)

    annotator = SemgrexAnnotator()
    annotated_data = annotator.annotate(text, taxonomy_verbs)

    evaluation_set = EvaluationSet(test_data, annotated_data)

    evaluator = FMeasureEvaluator()
    result = evaluator.evaluate_with_annotated_sentences(
        evaluation_set, consider_objects, consider_contexts)
    output_json = jsonpickle.encode(result, unpicklable=False)
    print(output_json)


def extract(text_file: TextIO, taxonomy_json: TextIO):
    taxonomy_verbs = None
    if taxonomy_json:
        taxonomy_manager = TaxonomyManager()
        taxonomy_verbs = taxonomy_manager.read_json(taxonomy_json)
        jsonpickle.handlers.registry.register(
            BloomsTaxonomyDimensionEnum, BloomsTaxonomyLevelEnumHandler)
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
        evaluate(args.tsvpath, args.objects, args.contexts, args.taxonomyjson)


if __name__ == '__main__':
    main()
