import pytube
import pandas as pd
import numpy as np
import youtubesearchpython as ys
import datetime
from youtube_transcript_api import YouTubeTranscriptApi


class YT_searcher():
    def __init__(self):
        self.y_link = 'https://www.youtube.com/watch?v='
        self.ids = []
        self.subtitles = []
        self.DFs = []

    # in: sentence to search in youtube
    # out: arrays of ids and  subtitles
    def search(self, sentence, num_of_results=50):
        videosSearch = ys.VideosSearch(sentence, region='IS')
        self.ids = []
        self.subtitles = []
        full = False

        for i in range(3) or full:
            page = videosSearch.result()['result']
            for p in page:
                # downloading subtitles if exists
                try:
                    self.subtitles.append(YouTubeTranscriptApi.get_transcripts([p['id']], languages=['en'])[0][p['id']])
                    self.ids.append(p['id'])
                except:
                    continue
                if len(self.ids) >= num_of_results:
                    full = True
                    break

            videosSearch.next()

        self._convert2pandas()
        return self.ids, self.DFs


    def _convert2pandas(self):
        self.DFs = []
        for st in self.subtitles:
            data = pd.DataFrame([], columns=['text', 'start','duration'])
            data['text'] = [tt['text'] for tt in st]
            data['start'] = [tt['start'] for tt in st]
            data['duration'] = [tt['duration'] for tt in st]
            self.DFs.append(data)
            del(data)