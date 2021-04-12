from pytube import YouTube


#in: youtube links; number how much to parse
#out: youtube objects of parsed videos
def you_parse(yt_links, num_to_parse):
    results = []
    for i in range(num_to_parse):
        print('\rParsing:', i+1, 'of', num_to_parse, end='')

        connects = 0
        while connects < 3:
            try:
                yt_obj = YouTube(yt_links[i])
                results.append(yt_obj)
                break
            except:
                connects += 1

    print('\rParsing done')


    return results