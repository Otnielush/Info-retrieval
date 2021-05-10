import pytube
import pandas as pd
import numpy as np
import youtubesearchpython as ys
import datetime


# in: sentence to search in youtube
# out: array of videos are scrubbed from search page
def search_1(sentence, num_of_results=50):
    # videosSearch = ys.Search(search, limit=50, region='IS')
    videosSearch = ys.VideosSearch(sentence, region='IS')
    array_results = []
    for i in range(num_of_results//20 + 1):
        page = videosSearch.result()['result']
        for p in page:
            if p['duration']:
                if len(p['duration'].split(':')) > 2:
                    date_time = datetime.datetime.strptime(p['duration'], '%H:%M:%S')
                else:
                    date_time = datetime.datetime.strptime(p['duration'], '%M:%S')
                a_timedelta = date_time - datetime.datetime(1900, 1, 1)
                seconds = a_timedelta.total_seconds()
                p['duration'] = int(seconds)
            else:
                p['duration'] = 0

            if p['viewCount']['text']:
                p['viewCount']['text'] = int(p['viewCount']['text'][:-6].replace(',', ''))
            else:
                p['viewCount']['text'] = 0

        # TODO if views and duration = 0 it`s most likely live stream and we don`t need it
        array_results.extend(page)

        videosSearch.next()

    return array_results[:num_of_results]