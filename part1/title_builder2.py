import numpy as np
import pandas as pd
import re
from spacy.lang.en import English
nlp = English()
from ngrams import Word_Frequency
ngrams = Word_Frequency()



# IN: text
# OUT: subtitles

def build_subtitles(text, window=None, max_words=6):

    if type(text) == str:
        text = [text]

    # Remove punctuation
    for t in range(len(text)):
        if type(text[t]) == list:
            text[t] = ' '.join(text[t])
        text[t] = text[t].replace('\n',' ').replace('\t','').rstrip().lstrip()
        text[t] = re.sub('[,\.!?]', '', text[t])
        text[t] = re.sub('[_]', ' ', text[t])
        text[t] = re.sub('(\s){2,8}', ' ', text[t])
        # Convert the titles to lowercase
        text[t] = text[t].lower()

    # dictionary
    docs = []
    for doc in text:
        tt = doc.split(' ')
        docs.append(tt)
    del(tt, text)

    dict_words = dict()
    doc_words = []
    for doc in docs:
        num_words = 0
        for word in doc:
            if not len(word) > 0:
                continue
            if word in dict_words:
                dict_words[word] += 1
            else:
                dict_words[word] = 1
            num_words += 1
        doc_words.append(num_words)


    # building frequencies
    total_words = sum(doc_words)
    dict_freq = dict()
    ngrams_freqs = ngrams.get_frequency(dict_words.keys())
    for i,key in enumerate(dict_words.keys()):
        if ngrams_freqs[i] == 0:
            dict_freq[key] = dict_words[key] / total_words
        else:
            dict_freq[key] = ngrams_freqs[i]


    # # Spacy not delete '.' '\n'
    # docs = []
    # for doc in text:
    #     docs.append([token.text for token in nlp(doc)])
    #
    # dict_words = dict()
    # doc_words = [len(doc) for doc in docs]


    # accumulative table
    word2row = dict()
    row2word = dict()
    array_freqs = np.zeros((len(dict_words)))
    for i,word in enumerate(sorted(dict_words.keys())):
        word2row[word] = i
        row2word[i] = word
        array_freqs[i] = dict_freq[word]

    # [num docs, word, possition in doc] => (0,1)
    table_appearance = [np.zeros((len(dict_words), doc_len)) for doc_len in doc_words]
    for d,doc in enumerate(docs):
        possition = 0
        for word in doc:
            table_appearance[d][word2row[word], possition] += 1
            possition += 1

    # calculating frequency of words in window
    if not window:
        window = int(total_words/len(docs)/5)
    print(f'{window = }')

    table_appearance_freq = [np.zeros((table.shape[0], table.shape[1]-window)) for table in table_appearance]
    for d, table in enumerate(table_appearance):
        for i in range(table.shape[1]-window):
            table_appearance_freq[d][:,i] = (table[:,i:i+window].sum(axis=1) / window) / array_freqs


    # choising best words
    table_most_appearance = [[[best for best in np.argsort(-step)[:max_words]] for step in doc.T] for doc in table_appearance_freq]
    table_most_appearance_words = [[[row2word[ind] for ind in step] for step in doc] for doc in table_most_appearance]


    # save results to csv
    for i,table in enumerate(table_appearance_freq):
        dataset = pd.DataFrame(table.T, columns=word2row.keys())
        dataset.to_csv(f'result_words_{i}.csv', index=None)

    for i,table in enumerate(table_most_appearance):
        dataset = pd.DataFrame(table, columns=[str(x) for x in range(1,max_words+1)])
        dataset.to_csv(f'result_best_ind_{i}.csv', index=None)

    for i,table in enumerate(table_most_appearance_words):
        dataset = pd.DataFrame(table, columns=[str(x) for x in range(1,max_words+1)])
        dataset.to_csv(f'result_best_words_{i}.csv', index=None)

    # print(dataset)
    # print(dict_words['woke']/total_words, ngrams.get_frequency(['woke']))



if __name__ == '__main__':

    q = 1

    if q == 1:
        with open('../data_test/kb04.cha', 'r') as f:
            file1 = f.readlines()
        with open('../data_test/kb05.cha', 'r') as f:
            file2 = f.readlines()
    else:
        text = [1,2,3,7,9,6,5,4,2,5,5,3,4,5,3,6,8,9,6,4,2,3,7,8,8,3,1,3,4,6,7,8,0,1,4,6,8,8,0,1,4,6,5,0,7,8,6,7,8,6,7,9,2,3,3,4,3,1,4,1,1,3]
        file1 = ' '.join([str(x) for x in text])
        file2 = ' '.join([str(x) for x in text[:len(text)//2]])
    build_subtitles([file1, file2], window=100, max_words=10)
    print(ngrams)

