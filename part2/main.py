##!/usr/bin/python

import sys

TEST = False

#read sentence to search from console
if len(sys.argv) < 2 and not TEST:
    print('Please write a search words like: python main.py "haredi child news"')
    exit()
else:
    if TEST:
        search_sentence = 'haredi child news'
    else:
        search_sentence = ' '.join(sys.argv[1:])
print('Searching:', search_sentence)


from search_yt import YT_searcher, download_mp4
from title_filter import get_best_parts, build_plots
from title_builder import build_subtitles
from concatenate_clips import make_clip


YT = YT_searcher()

MAX_VIDEOS_TO_PARSE = 2

# step 1
# This library uses native YouTube search.
# Instead of searching, you can download the text of the video by ID:
# df_subtitles = YT.download_subtitles(id)
ids, df_subtitles = YT.search(search_sentence, MAX_VIDEOS_TO_PARSE)

print('Videos found:', len(ids))

# step 2
# output tables with frequencies of words and most frequently words
data = build_subtitles([list(df['text']) for df in df_subtitles], window=100, max_words=7, parse_text_parts=True)

# step 3
best_part, best_part_timings = get_best_parts(data, search_sentence, df_subtitles)
build_plots(data)

print(f'{best_part = }\n{best_part_timings = }')
#step 4
# make video

# downloading
file_names, file_len = [], []
for link in ids:
    names, lens = download_mp4(link)
    file_names.append(names)
    file_len.append(lens)
print(f'{file_names = }')

# building video file
make_clip(file_names, file_len)

