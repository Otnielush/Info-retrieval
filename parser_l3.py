from pytube import YouTube


# in: youtube links; number how much to parse
# out: youtube objects of parsed videos
def you_parse(yt_links):
    results = []
    for i, link in enumerate(yt_links):
        print('\rParsing:', i+1, 'of', len(yt_links), end='')

        connects = 0
        while connects < 3:
            try:
                yt_obj = YouTube(link)
                results.append(yt_obj)
                break
            except:
                connects += 1

    print('\rParsing done')

    return results



if __name__ == '__main__':
    res = you_parse(['https://www.youtube.com/watch?v=_L5mbQZQx2s'])
    print(res)