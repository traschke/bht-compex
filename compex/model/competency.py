from typing import List
from enum import Enum

from compex.model.taxonomy import BloomsTaxonomyDimensionEnum

class Word:
    """Represents a word of a competency triple."""

    def __init__(self, index: int, word: str):
        """Creates a new instance.

        Parameters
        ----------
        index : int
            The 0 based index of the word in it's sentence
        word : str
            The word itself
        """

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
    """Represents a chunk of words."""

    def __init__(self, words: List[Word] = None):
        """Creates a new instance.

        Parameters
        ----------
        words : List[Word], optional
            A list of words, by default None
        """
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
    """Represents a context of an object of a competency triple."""

    def __init__(self, word_chunk: WordChunk):
        """Creates a new instance.

        Parameters
        ----------
        word_chunk : WordChunk
            A WordChunk representing the context
        """

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
    """Represents an object of a competency triple."""

    def __init__(self, word_chunk: WordChunk, contexts: List[ObjectContext] = None):
        """Creates a new instance.

        Parameters
        ----------
        word_chunk : WordChunk
            A WordChunk representing the object.
        contexts : List[ObjectContext], optional
            A List of contexts belonging to the object, by default None
        """

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
    """Represents a competency triple."""

    def __init__(self, word: Word, objects: List[CompetencyObject] = None, taxonomy_dimension: BloomsTaxonomyDimensionEnum = None):
        """Creates a new instance.

        Parameters
        ----------
        word : Word
            The competency verb
        objects : List[CompetencyObject], optional
            A List of objects belonging to the competency verb, by default None
        taxonomy_dimension : BloomsTaxonomyDimensionEnum, optional
            Optional taxonomy dimension of the competency verb, by default None
        """

        self.word: Word = word
        if objects is None:
            self.objects: List[CompetencyObject] = []
        else:
            self.objects: List[CompetencyObject] = objects
        self.taxonomy_dimension = taxonomy_dimension

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
    """Represents a sentence with competency triples."""

    def __init__(self, words: List[Word], competencies: List[Competency] = None):
        """Creates a new instance.

        Parameters
        ----------
        words : List[Word]
            A List of Words defining the sentence.
        competencies : List[Competency], optional
            A List of competency triples belonging to the sentence, by default None
        """

        self.words: List[Word] = []
        if competencies is None:
            self.competencies: List[Competency] = []
        else:
            self.competencies: List[Competency] = competencies

    def __str__(self) -> str:
        return " ".join(x.word for x in self.words)

    def __repr__(self):
        return self.__str__()
