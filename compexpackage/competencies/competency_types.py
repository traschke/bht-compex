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

class Sentence:
    def __init__(self, words: List[Word], competencies: List[Competency] = None):
        self.words: List[Word] = []
        if competencies is None:
            self.competencies: List[Competency] = []
        else:
            self.competencies: List[Competency] = competencies

class Competency:
    def __init__(self, word: Word, objects: List[CompetencyObject] = None):
        self.word: Word = word
        if objects is None:
            self.objects: List[CompetencyObject] = []
        else:
            self.objects: List[CompetencyObject] = objects

class CompetencyObject:
    def __init__(self, word_chunk: WordChunk, contexts: List[ObjectContext] = None):
        self.word_chunk: WordChunk = word_chunk
        if contexts is None:
            self.contexts: List[ObjectContext] = []
        else:
            self.contexts: List[ObjectContext] = contexts

class ObjectContext:
    def __init__(self, word_chunk: WordChunk):
        self.word_chunk: WordChunk = word_chunk
