from stanfordnlp.server import CoreNLPClient
from compex.competencies.competency_types import Word, WordChunk, Competency, CompetencyObject, ObjectContext

if __name__ == '__main__':
    # example text
    print('---')
    print('input text')
    print('')

    text = "Die Studierenden beherrschen die grundlegenden Techniken des wissenschaftlichen Arbeitens."
    # text = "Die Studierenden können eine serverseitige Schnittstelle für moderne Webanwendungen konzipieren und implementieren."

    print(text)

    # set up the client
    print('---')
    print('starting up Java Stanford CoreNLP Server...')

    # set up the client
    with CoreNLPClient(annotators=['tokenize','ssplit','depparse'], properties='german', timeout=30000, memory='16G') as client:
        # Dependency parse, semrex
        # Die Studierenden beherrschen die grundlegenden Techniken zum wissenschaftlichen Arbeiten.
        # Die Studierenden können eine serverseitige Schnittstelle für moderne Webanwendungen konzipieren und implementieren.
        # {tag:VVINF}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det {tag:NN}=objectdet)
        # {tag:VVINF}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja))
        # {tag:VVINF}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>/conj:.*/ {tag:VVINF}=competency2
        # {tag:/VVINF|VVFIN/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>/conj:.*/ {tag:VVINF}=competency2
        # {tag:/VVINF|VVFIN/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>nmod ({}=context ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:VVINF}=competency2
        # {tag:/VVINF|VVFIN/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:VVINF}=competency2
        # {tag:/VVINF|VVFIN|VVIZU/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:/VVINF|VVFIN|VVIZU/}=competency2
        # pattern = '{tag:/VVINF|VVFIN/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:VVINF}=competency2'
        pattern = '{tag:/VVINF|VVFIN|VVIZU/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja ?>det {tag:ART}=objectdetart)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:/VVINF|VVFIN|VVIZU/}=competency2'
        matches = client.semgrex(text, pattern, properties={"annotators": "tokenize,ssplit,depparse"})
        print(matches)

        # Parse the values from semgrex
        temp = matches['sentences'][0]["0"]
        competency = Competency(Word(temp["$competency"]["begin"], temp["$competency"]["text"]))

        if "$object" in temp:
            object_chunk = WordChunk()

            if "$objectadja" in temp:
                object_chunk.words.append(Word(temp["$objectadja"]["begin"], temp["$objectadja"]["text"]))

            object_chunk.words.append(Word(temp["$object"]["begin"], temp["$object"]["text"]))

            if "$objectdet" in temp:
                if "$objectdetadja" in temp:
                    object_chunk.words.append(Word(temp["$objectdetadja"]["begin"], temp["$objectdetadja"]["text"]))
                if "$objectdetart" in temp:
                    object_chunk.words.append(Word(temp["$objectdetart"]["begin"], temp["$objectdetart"]["text"]))

                object_chunk.words.append(Word(temp["$objectdet"]["begin"], temp["$objectdet"]["text"]))

            # Sort the words by index to remain context
            object_chunk.words.sort(key=lambda word: word.index)

            contexts = []

            if "$context" in temp:
                context_chunk = WordChunk()
                if "$contextadja" in temp:
                    context_chunk.words.append(Word(temp["$contextadja"]["begin"], temp["$contextadja"]["text"]))

                context_chunk.words.append(Word(temp["$context"]["begin"], temp["$context"]["text"]))

                # Sort the words by index to remain context
                context_chunk.words.sort(key=lambda word: word.index)

                contexts.append(ObjectContext(context_chunk))


            # Add the object to the competency
            competency.objects.append(CompetencyObject(object_chunk, contexts))

        print("Competency : {}".format(competency))
        # print("  Object   : {}".format(competency.objects[0]))
        # print("    Context: {}".format(competency.objects[0].contexts[0]))

        # if "$object" in matches['sentences'][0]["0"]:
        #     obj = matches['sentences'][0]["0"]["$object"]["text"]
        # if "$objectadja" in matches['sentences'][0]["0"]:
        #     obj_adja = matches['sentences'][0]["0"]["$objectadja"]["text"]
        # if "$objectdet" in matches['sentences'][0]["0"]:
        #     obj_det = matches['sentences'][0]["0"]["$objectdet"]["text"]
        # if "$objectdetadja" in matches['sentences'][0]["0"]:
        #     obj_det_adja = matches['sentences'][0]["0"]["$objectdetadja"]["text"]
        # print("Object: {} {} {} {}".format(obj_adja, obj, obj_det_adja, obj_det))

        # if "$context" in matches['sentences'][0]["0"]:
        #     print("Context: " + matches['sentences'][0]["0"]["$context"]["text"])
        # else:
        #     print("Context: NO!")
