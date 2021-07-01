#!/usr/bin/python

import sys

#read sentence to search from console
if len(sys.argv) < 2:
    print('Please write a search words like: "python main.py search words"')
    exit()
else:
    search_sentence = ' '.join(sys.argv[1:])
print('Searching:', search_sentence)


from search_yt import YT_searcher
from title_filter import get_best_parts, build_plots


sys.path.append('..')
YT = YT_searcher()
from part1.title_builder2 import build_subtitles

MAX_VIDEOS_TO_PARSE = 2

# step 1
ids, df_subtitles = YT.search(search_sentence, MAX_VIDEOS_TO_PARSE)

print('Videos found:', len(ids))

# step 2
data = build_subtitles([list(df['text']) for df in df_subtitles], window=100, max_words=7, parse_text_parts=True)

# step 3
best_part, best_part_timings = get_best_parts(data, search_sentence, df_subtitles)
build_plots(data)

print(f'{best_part = }\n{best_part_timings = }')
#step 4
# make video


