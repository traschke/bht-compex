# CompEx
![release](https://img.shields.io/github/v/release/traschke/bht-compex)
![license](https://img.shields.io/github/license/traschke/bht-compex)
![pythonversion](https://img.shields.io/github/pipenv/locked/python-version/traschke/bht-compex)
![jreversion](https://img.shields.io/badge/JRE-1.8+-blue)
![corenlpversion](https://img.shields.io/badge/CoreNLP-3.9.1-blue)
![coverage](coverage.svg)

Extract competency triples from written text.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.7 
* [pipenv](https://github.com/pypa/pipenv)
* (optional) [pyenv](https://github.com/pyenv/pyenv) to automatically install required Pythons
  * If pyenv is not installed, Python 3.7 is required, otherwise pyenv will install it
* Java JRE 1.8+ for CoreNLP server
* [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/index.html)

### Installing

Setup a python virtual environment and download all dependencies

```console
$ pipenv install --dev
```

ComPex requires an installation of CoreNLP with german models. Download required CoreNLP Java server and german models from [here](https://stanfordnlp.github.io/CoreNLP/download.html) to destination of your choosing. You can use the following script to automate this process, which downloads all required files to `./.corenlp`:
```console
$ ./download_corenlp.sh
```

Enter pipenv virtual environment
```console
$ pipenv shell
```

### Running
Set environment variable `$CORENLP_HOME` to the directory, where CoreNLP and german models are located. If you used the helper script `download_corenlp.sh`, the files are in `./.corenlp`.
```console
$ export CORENLP_HOME=./.corenlp
```

Show help
```console
$ python -m compex -h
```

#### Extraction

Show help
```console
$ python -m compex extract -h
```

Extract competencies of a simple sentence (you can pipe textdata into compex!)
```console
$ echo "Die studierenden beherrschen grundlegende Techniken des wissenschaftlichen Arbeitens." | python -m compex extract
```

or use a file
```console
$ python -m compex extract testsentences.txt
```

or use `stdin`
```console
$ python -m compex extract < testsentences.txt
```

Check for taxonomy verbs. Checks if a found competency verb is in the given taxonomy verb dictionary. If not, it's ignored. In addition, this parameter fills the `taxonomy_dimension` parameter of the extracted competency. You can use the sample file `blooms_taxonomy.json`.
```console
$ python -m compex extract --taxonomyjson blooms_taxonomy.json testsentences.txt
```

Sample output on `stdout` (formatted for better readability)
```json
{
    "Die studierenden beherrschen grundlegende Techniken des wissenschaftlichen Arbeitens.": [
        {
            "objects": [],
            "taxonomy_dimension": null,
            "word": {
                "index": 2,
                "word": "beherrschen"
            }
        }
    ]
}
```

#### Evaluation
Evaluate compex against pre-annotated data. Outputs recall, precision and F1.
To evaluate a pre-annoted [WebAnno](https://webanno.github.io/webanno/) TSV 3.2 file is needed. See [here](https://webanno.github.io/webanno/releases/3.6.4/docs/user-guide.html#sect_webannotsv) for the file format. You can use WebAnno to annotate data and evaluate compex with it. This repository contains pre-annotated data from Modulhandbooks of Department~VI of Beuth University of Applied Sciences Berlin. They can be found here: `tests/resources/bht-annotated`. The corresponding WebAnno Projekt is located at `tests/resources/webanno/BHT+Test_2020-03-22_1808.zip`.

Show help
```console
$ python -m compex evaluate -h
```

Evaluate only competency verbs
```console
$ python -m compex evaluate tests/resources/test.tsv
```

Evaluate competency verbs and objects
```console
$ python -m compex evaluate --objects tests/resources/test.tsv
```

Evaluate competency verbs, objects and contexts
```console
$ python -m compex evaluate --objects --contexts tests/resources/test.tsv
```

It is possible to use a dedicated taxonomy json file just like with the `extract` function
```console
$ python -m compex evaluate --taxonomyjson blooms_taxonomy.json tests/resources/test.tsv
```

Sample evaluation output on `stdout` (formatted for better readability)
```json
{
    "f1": 0.5024705551113972,
    "negatives": {
        "false": 168.36206347622323,
        "true": 81.63793652377686
    },
    "positives": {
        "false": 137.53333333333336,
        "true": 154.4666666666666
    },
    "precision": 0.5289954337899542,
    "recall": 0.4784786862008745
}
```

## Running the tests

Run unit tests. CoreNLP server in `./.corenlp` is required!

```console
$ pytest
```

### Get test coverage
Run coverage
```console
$ coverage run --source=./compex/ -m pytest
```

Export coverage report as html
```console
$ coverage html
```

Generate coverage badge
```console
$ coverage-badge -o coverage.svg
```
## Built With

* [Python 3.7](https://docs.python.org/3.7/)
* [pipenv](https://pipenv.pypa.io/en/latest/) - Python Development Workflow for Humans
* [stanfordnlp](https://stanfordnlp.github.io/stanfordnlp/) - Python NLP Library for many Human Languages
* [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/index.html) - Natural language software 
* [jsonpickle](https://jsonpickle.github.io/) - Python library for serialization and deserialization of complex Python objects


## Authors

* **Timo Raschke** - *Initial work* - [traschke](https://github.com/traschke)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

### Sources for Bloom's Taxonomy verbs:
* https://www.qualifizierungdigital.de/_medien/downloads/Verben_fuer_Kompetenzbeschreibung.pdf
* https://tips.uark.edu/blooms-taxonomy-verb-chart/
