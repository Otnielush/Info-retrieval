from moviepy.editor import *
from os import path
from search_yt import Download_folder


def concat_clips(clips):
    final = clips[0]
    for clip in clips[1:]:
        final = concatenate_videoclips([final, clip])

    return final


def create_sub_clips_list(file_names, all_clips_times):
    clips = []
    # folder = Download_folder
    # files = os.listdir(folder)

    for clip_times, clip_file in zip(all_clips_times, file_names):
      clip = VideoFileClip(clip_file)
      for time in clip_times:
        sub_clip = clip.subclip(time[0] * 60, time[1] * 60)
        clips.append(sub_clip)

    return clips

def make_clip(file_names, timmings):
    clip_parts = create_sub_clips_list(file_names, timmings)
    clip_1 = concat_clips(clip_parts)
    suffix = 0
    file_name = 'new_super_clip.mp4'
    while path.isfile(path.join(Download_folder, file_name)):
        suffix += 1
        file_name = file_name[:-4]+str(suffix)+'.mp4'
    clip_1.write_videofile(path.join(Download_folder, file_name))
    print('File saved in:', path.join(Download_folder, file_name))


if __name__ == "__main__":
    files = [path.join(Download_folder, 'In Flames.mp4')]
    timmings = [[(1.0, 3.0)]]
    make_clip(files, timmings)


