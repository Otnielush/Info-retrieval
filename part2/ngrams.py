import sqlite3 as sql
import os
import numpy as np
import pandas as pd
import requests
from time import sleep
import re

class Word_Frequency():
    def __init__(self):
        self.path2db = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, 'ngrams.db'))
        if not os.path.isfile(self.path2db):
            con = sql.connect('ngrams.db')
            command = 'CREATE TABLE word_freq (word TEXT UNIQUE NOT NULL, frequency INTEGER NOT NULL)'
            con.execute(command)
            con.close()
            print('table ngrams created')

        self.load_db()


    def load_db(self):
        con = sql.connect(self.path2db)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM word_freq ORDER BY word')
        self.ngrams = {x[0]:x[1] for x in cur.fetchall()}

        self.tokens = set(self.ngrams.keys())
        print('Ngrams base loaded. Words in base:', len(self.tokens))
        con.close()


    # databese name, columns names, list of data
    def insert_to_db(self, data: list):

        command = 'INSERT OR IGNORE INTO word_freq (word, frequency) VALUES (?,?)'

        insert_data = []
        if type(data[0]) == tuple:
            for dd in data:
                insert_data.append(dd)
        elif type(data[0]) == list:
            for dd in data:
                insert_data.append(tuple(dd))
        elif type(data[0]) == dict:
            for dd in data:
                tt = tuple()
                for col in cols:
                    tt += (dd[col],)
                insert_data.append(tt)

        con = sql.connect(self.path2db)
        cur = con.cursor()

        if len(insert_data) > 1:
            cur.executemany(command, insert_data)
        else:
            cur.execute(command, insert_data[0])

        con.commit()
        con.close()

        # print('info added to DB')


    def get_frequency(self, tokens: list):
        freqs = np.zeros((len(tokens)))
        need2parse = []
        need2parse_ind = []
        for i, token in enumerate(tokens):
            if token in self.tokens:
                freqs[i] = self.ngrams[token]
            else:
                need2parse.append(token)
                need2parse_ind.append(i)

        # all words found in our base
        if len(need2parse_ind) == 0:
            return freqs

        new_freqs = self.parse_ngrams(need2parse)
        to_db = []
        for k,i in enumerate(need2parse_ind):
            freqs[i] = new_freqs[k]
            if freqs[i] != 0:
                to_db.append((need2parse[k], new_freqs[k]))
                self.ngrams[need2parse[k]] = new_freqs[k]

        self.tokens = set(self.ngrams.keys())

        # to db
        if len(to_db) > 0:
            self.insert_to_db(to_db)

        return freqs



    def parse_ngrams(self, tokens):

        freqs = np.zeros((len(tokens)))

        n_words = 11
        start = 0
        stop = int(len(tokens) / n_words + 1)
        step = n_words
        num_problems = 0
        print('\rParsing ngrams frequencies')
        print('00.00%', end='')
        for i in np.arange(start, stop, 1):
            if (i + 1) * n_words > len(tokens):
                step = len(tokens) - i * n_words
            try:
                freqs[i * n_words:i * n_words + step] = self._parse_frequency(tokens[i * n_words:i * n_words + step])
                num_problems = 0
            except:
                for bb in np.arange(i * n_words, i * n_words + step, 1):
                    try:
                        freqs[bb] = self._parse_frequency(tokens[bb])[0]
                        # print(' parsed',tokens[bb], freqs[bb])
                        num_problems = 0
                    except:
                        print('\r',i, f'with problems ({tokens[bb]})')
                        num_problems += 1
                    if num_problems >= 3:
                        break

            sleep(3)
            print('\r{:2.2f}%          i = {}'.format(i / stop * 100, i), end='')

            if (i + 1) % 30 == 0:
                print('\r{:2.2f}% sleeping i = {}'.format(i / stop * 100, i), end='')
                sleep(70)
        print('\r Done', ' '*15)
        return freqs

    # Getting frequency for each word from google ngrams viewer
    def _get_massive(self, html):
        return re.search(r'ngrams\.data.+\]\}\]', html)

    def _get_data_f_script(self, r_e):
        freqs = re.findall(r'(\d\.\d+\w-\d+|\d+\.\d+|\d+)\]\}', r_e.group(0))
        freqs_d = np.zeros(len(freqs))
        for i in range(len(freqs_d)):
            freqs_d[i] = float(freqs[i])
        return freqs_d

    # input: massive of words
    def _parse_frequency(self, words):
        if (type(words) == list or type(words) == np.ndarray) and len(words) > 1:
            words = '%2C'.join(words)
        url = 'https://books.google.com/ngrams/graph?content={}&year_start=1999&year_end=2000&smoothing=3'.format(
            words)

        html = requests.get(url)
        gm = self._get_massive(html.text)

        return self._get_data_f_script(gm)

    def __repr__(self):
        rep = f'dict size: {len(self.tokens)}\n'
        for i, key in enumerate(self.tokens):
            if i == 100:
                rep += '  ...  '
                break
            else:
                rep += f'"{key}": {self.ngrams[key]:1.9f}\n'
        return rep



if __name__ == '__main__':
    nn = Word_Frequency()
    words = ['mother','whatever','stream','lots of','froglets','picks','wading','apart',
 'from', 'one', 'say', 'goodbye', 'instruments']
    freqs = nn.get_frequency(words)
    print([a for a in zip(words, freqs)])
    print(nn._parse_frequency(words))
