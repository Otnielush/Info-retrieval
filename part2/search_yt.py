import pytube
import pandas as pd
import numpy as np
import youtubesearchpython as ys
import datetime
from youtube_transcript_api import YouTubeTranscriptApi


y_link = 'https://www.youtube.com/watch?v='

# in: sentence to search in youtube
# out: arrays of ids and  subtitles
def search_yt(sentence, num_of_results=50):
    videosSearch = ys.VideosSearch(sentence, region='IS')
    ids = []
    subtitles = []

    for i in range(3):
        page = videosSearch.result()['result']
        for p in page:
            # downloading subtitles if exists
            try:
                subtitles.append(YouTubeTranscriptApi.get_transcripts([p['id']], languages=['en'])[0][p['id']])
                ids.append(p['id'])
            except:
                continue
            if len(ids) >= num_of_results:
                return ids, subtitles

        videosSearch.next()

    return ids, subtitles