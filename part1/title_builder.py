import numpy as np
import pandas as pd
import re

import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
import nltk

# nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

from pprint import pprint


# IN: text
# OUT: subtitles

def build_subtitles(text):

    # Remove punctuation
    for t in text:
        t = re.sub('[,\.!?]', '', t)
        # Convert the titles to lowercase
        t = t.lower()

    # data =  text.lower()

    data = list(sent_to_words(text))
    print(f'{data = }')
    # remove stop words
    data = remove_stopwords(data)

    # Create Dictionary
    id2word = corpora.Dictionary(data)
    # Create Corpus
    texts = data
    # Term Document Frequency
    corpus = [id2word.doc2bow(text) for text in texts]
    print(f'{corpus = }')

    # number of topics
    num_topics = 10
    # Build LDA model
    lda_model = gensim.models.LdaMulticore(corpus=corpus, id2word=id2word, num_topics=num_topics)
    # Print the Keyword in the 10 topics
    pprint(lda_model.print_topics())
    doc_lda = lda_model[corpus]





# in: []sentences
def sent_to_words(sentences):
    for sentence in sentences:
        # deacc=True removes punctuations
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

# in: []documents
# out: [[]] docs, words
def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc))
             if word not in stop_words] for doc in texts]



if __name__ == '__main__':

    with open('../data_test/kb04.cha', 'r') as f:
        file1 = f.readlines()
    with open('../data_test/kb05.cha', 'r') as f:
        file2 = f.readlines()
    # print(f'{file1 = }')
    # exit()
    build_subtitles([file1[0], file2[0]])