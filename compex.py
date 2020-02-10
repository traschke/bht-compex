from stanfordnlp.server import CoreNLPClient

# example text
print('---')
print('input text')
print('')

text = "Die Studierenden beherrschen die grundlegenden Techniken zum wissenschaftlichen Arbeiten."

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
    pattern = '{tag:/VVINF|VVFIN/}=competency >dobj ({}=object ?>amod {tag:ADJA}=objectadja ?>det ({tag:NN}=objectdet ?>amod {tag:ADJA}=objectdetadja)) ?>nmod ({}=context ?>/conj:.*/ {}=context2 ?>amod {tag:ADJA}=contextadja) ?>/conj:.*/ {tag:VVINF}=competency2'
    matches = client.semgrex(text, pattern, properties={"annotators": "tokenize,ssplit,depparse"})
    print(matches)

    # Parse the values from semgrex
    competency = matches['sentences'][0]["0"]["$competency"]["text"]
    print("Competency: " + competency)

    if "$object" in matches['sentences'][0]["0"]:
        obj = matches['sentences'][0]["0"]["$object"]["text"]
    if "$objectadja" in matches['sentences'][0]["0"]:
        obj_adja = matches['sentences'][0]["0"]["$objectadja"]["text"]
    if "$objectdet" in matches['sentences'][0]["0"]:
        obj_det = matches['sentences'][0]["0"]["$objectdet"]["text"]
    if "$objectdetadja" in matches['sentences'][0]["0"]:
        obj_det_adja = matches['sentences'][0]["0"]["$objectdetadja"]["text"]
    print("Object: {} {} {} {}".format(obj_adja, obj, obj_det_adja, obj_det))

    if "$context" in matches['sentences'][0]["0"]:
        print("Context: " + matches['sentences'][0]["0"]["$context"]["text"])
    else:
        print("Context: NO!")
