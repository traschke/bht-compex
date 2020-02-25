import pytest
from compex.io.tsv import TsvReader, TsvDocument

def tsv_schema_test():
    reader = TsvReader()
    document: TsvDocument = reader.read_tsv("./test.tsv")
    print(document)
