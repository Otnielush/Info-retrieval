from pytube import YouTube
from os import rename, path, getcwd, remove, stat
from requests import get
Download_folder = path.abspath('.')+'\\downloads\\'

import pandas as pd
import youtubesearchpython as ys
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
                if len(self.ids) >= num_of_results:
                    full = True
                    break
                # downloading subtitles if exists
                subtitles = self._download_subtitles(p['id'])
                if subtitles != None:
                    self.subtitles.append(subtitles)
                    self.ids.append(p['id'])
                else:
                    continue

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

    def _download_subtitles(self, id_youtube):
        try:
            subs = YouTubeTranscriptApi.get_transcripts([id_youtube], languages=['en'])[0][id_youtube]
        except Exception as e:
            print('Error with downloading subtitles') #, e)
            subs = None
        return subs


    def download_subtitles(self, id_youtube):
        self.ids = []
        self.subtitles = []
        data = self._download_subtitles(id_youtube)
        if data != None:
            self.subtitles.append(data)
            self._convert2pandas()
            return self.DFs
        else:
            return None



# in: url youtube video
# out: path to file, length of video
def download_mp4(url, yt_obj=None):
    if len(url) == 11:
        urll = 'https://www.youtube.com/watch?v='+url
    else:
        urll = url

    if yt_obj == None:
        connects = 0
        while connects < 3:
            try:
                yt_obj = YouTube(urll)
                break

            except:
                connects += 1
        if connects >= 3:
            return '', 0


    # checking if file already downloaded (not working)
    # new_name = getcwd()+'\\downloads\\'+yt_obj.title+'.mp3'
    # if path.isfile(new_name):
    #     return new_name

    yt_stream = yt_obj.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
    end_name = 3

    tries = 0
    while tries <= 3:
        try:
            ytd = yt_stream.download(Download_folder)
            break
        except:
            tries += 1

    # failed to download
    if tries >= 3:
        try:
            if stat(ytd).st_size <= 1:
                remove(ytd)
        except:
            pass

        return '', 0

    # new_name = ytd[:-end_name]+'mp4'
    # try:
    #     if stat(ytd).st_size <= 1:
    #         remove(ytd)
    #     else:
    #         try:
    #             remove(new_name)
    #         except:
    #             pass
    #         finally:
    #             rename(ytd, new_name)
    # except:
    #     return '', 0

    return ytd, int(yt_obj.length/60)


if __name__ == '__main__':
    files, lens = download_mp4('https://www.youtube.com/watch?v=SyHlFEQ9Jtc')