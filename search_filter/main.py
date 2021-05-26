#!/usr/bin/python

from yt_search_l1 import search_1
from filter_1 import filter_1
from parser_l3 import you_parse
from filter_2 import filter_2

import sys


MAX_VIDEOS_TO_PARSE = 15

#read sentence to search from console
if len(sys.argv) < 2:
    print('Please write a search words like: "python main.py search words"')
    exit()
else:
    search_sentence = ' '.join(sys.argv[1:])
print('Searching:', search_sentence)
# step 1
search_results = search_1(search_sentence)
print('Videos found:', len(search_results))

#step 2
sorted_youtube_links = filter_1(search_sentence, search_results)

#step 3
parsed_array = you_parse(sorted_youtube_links, MAX_VIDEOS_TO_PARSE)

#step 4
predictions = filter_2(search_sentence, parsed_array)





