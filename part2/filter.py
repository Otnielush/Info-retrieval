import spacy

# spacy english model (large)
try:
    nlp = spacy.load('en_core_web_lg')
except:
    print('need to download model\npython -m spacy download en_core_web_lg')


def filter():
    pass
