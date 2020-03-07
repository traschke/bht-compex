# CompEx

Extract competencies from written text

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.7 
* [pipenv](https://github.com/pypa/pipenv)
* (optional) [pyenv](https://github.com/pyenv/pyenv) to automatically install required Pythons
  * If pyenv is not installed, Python 3.7 is required, otherwise pyenv will install it
* Java 1.8+ for CoreNLP server
* [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/index.html)

### Installing

Setup a python virtual environment and download all dependencies

```
$ pipenv install
```

ComPex requires an installation of CoreNLP with german models. Download required CoreNLP Java server and german models from [here](https://stanfordnlp.github.io/CoreNLP/download.html) to destination of your choosing. You can use the following script to automate this process, which downloads all required files to `./.corenlp`:
```
$ ./download_corenlp.sh
```

Enter pipenv virtual environment

```
$ pipenv shell
```

### Running
Set environment variable `$CORENLP_HOME` to the directory, where CoreNLP and german models are located. If you used the helper script `download_corenlp.sh`, the files are in `./.corenlp`.
```
$ export CORENLP_HOME=./.corenlp
```

Show help
```
$ python -m compex -h
```

#### Extraction

Show help
```
$ python -m compex extract -h
```

Extract competencies of a simple sentence (you can pipe textdata into compex!)
```
$ echo "Die studierenden beherrschen grundlegende Techniken des wissenschaftlichen Arbeitens." | python -m compex extract
```

or use a file
```
$ python -m compex extract testsentences.txt
```

Check for taxonomy verbs. Checks if a found competency verb is in the given taxonomy verb dictionary. If not, it's ignored. In addition, this parameter fills the `taxonomy_dimension` parameter of the extracted competency. You can use the sample file `blooms_taxonomy.json`.
```
python -m compex extract --taxonomyjson blooms_taxonomy.json testsentences.txt
```

Sample output (formatted for better readability)
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
To evaluate a pre-annoted [WebAnno](https://webanno.github.io/webanno/) TSV 3.2 file is needed. See [here](https://webanno.github.io/webanno/releases/3.6.4/docs/user-guide.html#sect_webannotsv) for the file format. You can use WebAnno to annotate data and evaluate compex with it. Use the ?? and ?? for the project files.

Show help
```
$ python -m compex evaluate -h
```

Evaluate only competency verbs
```
$ python -m compex evaluate tests/resources/test.tsv
```

Evaluate competency verbs and objects
```
$ python -m compex evaluate --objects tests/resources/test.tsv
```

Evaluate competency verbs, objects and contexts
```
$ python -m compex evaluate --objects --contexts tests/resources/test.tsv
```

Sample output (formatted for better readability)
```json
{
    "f1": 0.7058823529411764,
    "false_negatives": 0.0,
    "false_positives": 5.0,
    "precision": 0.5454545454545454,
    "recall": 1.0,
    "true_negatives": 6.0,
    "true_positives": 6.0
}
```

## Running the tests

Run unit tests. CoreNLP server in `./.corenlp` is required!

```
$ pytest
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
