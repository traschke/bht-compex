from typing import List

class Word:
    def __init__(self, index: int, word: str):
        self.index: int = index
        self.word: str = word

class WordChunk:
    def __init__(self, words: List[Word] = None):
        if words is None:
            self.words: List[Word] = []
        else:
            self.words: List[Word] = words

class ObjectContext:
    def __init__(self, word_chunk: WordChunk):
        self.word_chunk: WordChunk = word_chunk

    def __str__(self) -> str:
        return " ".join(x.word for x in self.word_chunk.words)
class CompetencyObject:
    def __init__(self, word_chunk: WordChunk, contexts: List[ObjectContext] = None):
        self.word_chunk: WordChunk = word_chunk
        if contexts is None:
            self.contexts: List[ObjectContext] = []
        else:
            self.contexts: List[ObjectContext] = contexts

    def __str__(self) -> str:
        return " ".join(x.word for x in self.word_chunk.words)

    def __repr__(self):
        return self.__str__()

class Competency:
    def __init__(self, word: Word, objects: List[CompetencyObject] = None):
        self.word: Word = word
        if objects is None:
            self.objects: List[CompetencyObject] = []
        else:
            self.objects: List[CompetencyObject] = objects

    def __str__(self) -> str:
        return "{}: {}".format(self.word.word, str(self.objects))

class Sentence:
    def __init__(self, words: List[Word], competencies: List[Competency] = None):
        self.words: List[Word] = []
        if competencies is None:
            self.competencies: List[Competency] = []
        else:
            self.competencies: List[Competency] = competencies

    def __str__(self) -> str:
        return " ".join(x.word for x in self.words)
