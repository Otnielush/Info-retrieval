from moviepy.editor import *

from part2 import search_yt


def concat_clips(clips):
    final = clips[0]
    for clip in clips[1:]:
        final = concatenate_videoclips([final, clip])

    return final


def create_sub_clips_list(all_clips_times):
    clips = []
    folder = search_yt.Download_folder
    files = os.listdir(folder)

    for clip_times, clip_file in zip(all_clips_times, files):
      clip = VideoFileClip(clip_file)
      for time in clip_times:
        sub_clip = clip.sub_clip(time[0], time[1])
        clips.append(sub_clip)

    return clips


