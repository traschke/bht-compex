from typing import List
from enum import Enum

from compex.taxonomy.taxonomy_manager import BloomsTaxonomyLevelEnum

class Word:
    def __init__(self, index: int, word: str):
        self.index: int = index
        self.word: str = word

    def __hash__(self):
        return hash((self.index, self.word))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            (self.index, self.word) == (other.index, other.word)
        )

    def __str__(self) -> str:
        return "<{}: {}>".format(self.index, self.word)

    def __repr__(self):
        return self.__str__()

class WordChunk:
    def __init__(self, words: List[Word] = None):
        if words is None:
            self.words: List[Word] = []
        else:
            self.words: List[Word] = words

    def __hash__(self):
        return hash(self.words)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.words == other.words
        )

class ObjectContext:
    def __init__(self, word_chunk: WordChunk):
        self.word_chunk: WordChunk = word_chunk

    def __hash__(self):
        return hash(self.word_chunk)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self.word_chunk == other.word_chunk)

    def __str__(self) -> str:
        return " ".join(x.word for x in self.word_chunk.words)

    def __repr__(self):
        return self.__str__()

class CompetencyObject:
    def __init__(self, word_chunk: WordChunk, contexts: List[ObjectContext] = None):
        self.word_chunk: WordChunk = word_chunk
        if contexts is None:
            self.contexts: List[ObjectContext] = []
        else:
            self.contexts: List[ObjectContext] = contexts

    def __hash__(self):
        return hash(self.word_chunk)

    def __eq__(self, other):
        # TODO Consider contexts!
        return (self.__class__ == other.__class__ and self.word_chunk == other.word_chunk)

    def __str__(self) -> str:
        return " ".join(x.word for x in self.word_chunk.words)

    def __repr__(self):
        return self.__str__()

class Competency:
    def __init__(self, word: Word, objects: List[CompetencyObject] = None, taxonomy_level: BloomsTaxonomyLevelEnum = None):
        self.word: Word = word
        if objects is None:
            self.objects: List[CompetencyObject] = []
        else:
            self.objects: List[CompetencyObject] = objects
        self.taxonomy_level = taxonomy_level

    def __hash__(self):
        return hash(self.word)

    def __eq__(self, other):
        # FIXME Consider objects too
        return (
            self.__class__ == other.__class__ and
            self.word == other.word
        )

    def __str__(self) -> str:
        return "{}: {}".format(self.word.word, str(self.objects))

    def __repr__(self):
        return self.__str__()

class Sentence:
    def __init__(self, words: List[Word], competencies: List[Competency] = None):
        self.words: List[Word] = []
        if competencies is None:
            self.competencies: List[Competency] = []
        else:
            self.competencies: List[Competency] = competencies

    def __str__(self) -> str:
        return " ".join(x.word for x in self.words)

    def __repr__(self):
        return self.__str__()
