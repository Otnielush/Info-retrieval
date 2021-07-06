import numpy as np
import pandas as pd
import re
from spacy.lang.en import English
nlp = English()

from .ngrams import Word_Frequency
ngrams = Word_Frequency()



# IN: text: list of documents. Documents - string of list of words
# OUT: subtitles
def build_subtitles(text, window=None, max_words=10, parse_text_parts=True):

    if type(text) == str:
        text = [text]

    # Remove punctuation
    # Remove punctuation and punctuation marks. The tokenizer will give a better result
    print('\rRemoving punctuation. part 1 of 6', end=' '*10)
    text_parts = []
    text_parts_num = []
    for t in range(len(text)):
        if type(text[t]) == list:
            if not parse_text_parts:
                text[t] = ' '.join(text[t])
                text[t] = clear_text(text[t])
            else:       # if not parse_text_parts
                text_part_num = [0]
                text_part = []
                accumulate = 0
                text_doc = ''
                for part in range(len(text[t])):
                    text[t][part] = clear_text(text[t][part])
                    tt = text[t][part].split(' ')
                    tt_set = set(tt)
                    while '' in tt_set:
                        tt.remove('')
                        tt_set = set(tt)
                    lenght_part = len(tt)
                    accumulate += lenght_part
                    text_part_num.append(accumulate)
                    text_part.extend([part for _ in range(lenght_part)])
                    text_doc = text_doc + ' ' + ' '.join(tt)

                text[t] = text_doc[1:]
        if parse_text_parts:
            text_parts.append(text_part)
            text_parts_num.append(text_part_num[:-1])
            del(text_part, text_part_num, text_doc)


    # dictionary
    # Create a bag of words and count them
    print('\rBuilding dictionary of words. part 2 of 6', end=' '*10)
    docs = []
    for doc in text:
        tt = doc.split(' ')
        tt_set = set(tt)
        while '' in tt_set:
            tt.remove('')
            tt_set = set(tt)
        docs.append(tt)
    del(tt, text)

    dict_words = dict()
    doc_words = []
    for doc in docs:
        num_words = 0
        for word in doc:
            # if not len(word) > 0:
            #     continue
            if word in dict_words:
                dict_words[word] += 1
            else:
                dict_words[word] = 1
            num_words += 1
        doc_words.append(num_words)

    # building frequencies
    # For each word in the dictionary and load its frequency from the ngrams server.
    # If an error occurs and the download fails, then the word frequency among all documents is sent.
    # The ngrams downloader has a SQLite database and first checks if there are these words in the database,
    # if not, then it parses the Google site.
    print('\rCalculating frequencies of words. part 3 of 6', end=' '*10)
    total_words = sum(doc_words)
    dict_freq = dict()
    ngrams_freqs = ngrams.get_frequency(dict_words.keys())
    for i, key in enumerate(dict_words.keys()):
        if ngrams_freqs[i] == 0:
            dict_freq[key] = dict_words[key] / total_words
        else:
            dict_freq[key] = ngrams_freqs[i]


    # accumulative table
    word2row = dict()
    row2word = dict()
    # Frequencies from ngrams
    array_freqs = np.zeros((len(dict_words)))
    for i,word in enumerate(sorted(dict_words.keys())):
        word2row[word] = i
        row2word[i] = word
        array_freqs[i] = dict_freq[word]

    # [num docs, word, possition in doc] => (0,1)
    # Where word appears in the word possitions in documents. axis X - words, axis Y - possition in document
    print('\rTable word appearance. part 4 of 6', end=' '*10)
    table_appearance = [np.zeros((len(dict_words), doc_len)) for doc_len in doc_words]
    for d,doc in enumerate(docs):
        possition = 0
        for word in doc:
            table_appearance[d][word2row[word], possition] += 1
            possition += 1

    # calculating frequency of words in window
    if not window:
        window = int(total_words/len(docs)/10)

    # how much times word appears in the window of words in text
    # To divide the document into parts, we count TF IDF in the interval of 100 words (window)
    # to understand which words are key at a given interval
    print(f'\rTable word appearance frequency in window({window}). part 5 of 6', end=' '*4)
    table_appearance_freq = [np.zeros((table.shape[0], table.shape[1])) for table in table_appearance]
    mean_freq_inverted = []
    for d, table in enumerate(table_appearance):
        half = window // 2
        end = table.shape[1] - 1
        for i in range(table.shape[1]):
            # Inverse Document Frequency
            IDF = (table[:, max(0, i - half):min(end, i + half)].sum(axis=1) / window) / array_freqs
            IDF_bm = 5*IDF/(IDF+4)  #BM25 transformation, k = 4
            table_appearance_freq[d][:,i] = IDF_bm
            mean_freq_inverted.append(np.mean(IDF_bm))

    mean_freq_inverted = np.mean(mean_freq_inverted)
    # print('\nmean limit', mean_freq_inverted)

    # choising best words
    # table_most_appearance = [[[best for best in np.argsort(-step)[:max_words]] for step in doc.T] for doc in table_appearance_freq]
    # table_most_appearance_words = [[[row2word[ind] for ind in step] for step in doc] for doc in table_most_appearance]


    data = [{'app_freq':0, 'app_freq_f':0, 'most_app':0, 'most_words':0} for _ in range(len(docs))]
    # choising best words
    # At each step of the segment, we take an estimate of the frequency of the n-th word (after sorting),
    # where n is the number of words that we want to take for the title. We get the minimum frequency for n words.
    # So we take the average estimate of the frequency of words in the document and choose the maximum of these two values.
    # It turns out at each step we get up to n words with the maximum score for this step.
    print('\rTable word most appearance in window. part 6 of 6', end=' '*10)
    for i,table in enumerate(table_appearance_freq):
        dataset = pd.DataFrame(table.T, columns=word2row.keys())
        # dataset.to_csv(f'result_words_{i}.csv', index=None)
        data[i]['app_freq'] = dataset

        # dataset with One Hot encoding for most frequent words
        dataset_filtered = dataset.copy(True)
        for j in range(dataset_filtered.shape[0]):
            limit = sorted(dataset_filtered.loc[j], reverse=True)[max_words] # taking frequency of last frequent word
            limit = max(limit, mean_freq_inverted)
            dataset_filtered.loc[j] = dataset_filtered.loc[j].mask(dataset_filtered.loc[j] < limit, 0)
        data[i]['app_freq_f'] = dataset_filtered.fillna(0)


    # for i,table in enumerate(table_most_appearance):
    #     dataset = pd.DataFrame(table, columns=[str(x) for x in range(1,max_words+1)])
    #     # dataset.to_csv(f'result_best_ind_{i}.csv', index=None)
    #     data[i]['most_app'] = dataset
    #
    # for i,table in enumerate(table_most_appearance_words):
    #     dataset = pd.DataFrame(table, columns=[str(x) for x in range(1,max_words+1)])
    #     # dataset.to_csv(f'result_best_words_{i}.csv', index=None)
    #     data[i]['most_words'] = dataset

    if parse_text_parts:
        for i in range(len(data)):
            data[i]['text_part'] = text_parts[i]
            data[i]['text_part_pos'] = text_parts_num[i]

    print('\rDocuments analysis is Done', ' '*30)
    # print(dataset)
    # print(dict_words['woke']/total_words, ngrams.get_frequency(['woke']))
    return data

def clear_text(text):
    text_part = text.replace('\n', ' ').replace('\t', '').replace('[', ' ').replace(']', ' ')
    text_part = re.sub('[,\.!?><"]', '', text_part)
    text_part = re.sub('[_-]', ' ', text_part)
    text_part = re.sub('(\s){2,8}', ' ', text_part)
    text_part = text_part.rstrip().lstrip()
    # Convert the titles to lowercase
    return text_part.lower()



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

