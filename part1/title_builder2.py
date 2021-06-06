import numpy as np
import pandas as pd
import re
from spacy.lang.en import English
nlp = English()

from ngrams import Word_Frequency
ngrams = Word_Frequency()



# IN: text
# OUT: subtitles

def build_subtitles(text, window=None, max_words=10):

    if type(text) == str:
        text = [text]

    # Remove punctuation
    for t in range(len(text)):
        if type(text[t]) == list:
            text[t] = ' '.join(text[t])
        text[t] = text[t].replace('\n',' ').replace('\t','').replace("'s ",' ').replace("'ll ",' will ').replace("'re ", ' are ').replace("n't ", ' not ').replace("'ve ", " have ").replace("'m", " am")
        text[t] = re.sub('[,\.!?]', '', text[t])
        text[t] = re.sub('[_-]', ' ', text[t])
        text[t] = re.sub('(\s){2,8}', ' ', text[t])
        text[t] = text[t].rstrip().lstrip()
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


    data = [{'app_freq':0, 'app_freq_f':0, 'app_freq_w':0, 'most_app':0, 'most_words':0} for _ in range(len(docs))]
    # save results to csv
    for i,table in enumerate(table_appearance_freq):
        dataset = pd.DataFrame(table.T, columns=word2row.keys())
        dataset.to_csv(f'result_words_{i}.csv', index=None)
        data[i]['app_freq'] = dataset

        # dataset with One Hot encoding for most frequent words
        dataset_filtered = dataset.copy(True)
        for j in range(dataset_filtered.shape[0]):
            limit = sorted(dataset_filtered.loc[j], reverse=True)[max_words]
            dataset_filtered.loc[j] = (dataset_filtered.loc[j] > limit) * 1
        data[i]['app_freq_f'] = dataset_filtered.fillna(0)


    for i,table in enumerate(table_most_appearance):
        dataset = pd.DataFrame(table, columns=[str(x) for x in range(1,max_words+1)])
        dataset.to_csv(f'result_best_ind_{i}.csv', index=None)
        data[i]['most_app'] = dataset

    for i,table in enumerate(table_most_appearance_words):
        dataset = pd.DataFrame(table, columns=[str(x) for x in range(1,max_words+1)])
        dataset.to_csv(f'result_best_words_{i}.csv', index=None)
        data[i]['most_words'] = dataset


    # print(dataset)
    # print(dict_words['woke']/total_words, ngrams.get_frequency(['woke']))
    return data



if __name__ == '__main__':

    q = 2

    if q == 1:
        with open('../data_test/kb04.cha', 'r') as f:
            file1 = f.readlines()

    else:
        file1 = pd.read_csv('../data_test/text.csv')
        file1 = list(file1['text'])

    build_subtitles([file1], window=30, max_words=10)
    print(ngrams)

