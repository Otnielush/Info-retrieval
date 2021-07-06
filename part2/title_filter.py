import spacy
# spacy english model (large)
try:
    nlp = spacy.load('en_core_web_lg')
except:
    try:
        nlp = spacy.load('en_core_web_md')
    except:
        print('need to download model\npython -m spacy download en_core_web_md')
        spacy.cli.download('en_core_web_md')


import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
plt.style.use('seaborn')


# data: list(datatset from build_subtitles); query: String; yt_subtitles: list(dataset from YT_searcher->download_subtitles)
def get_best_parts(data, query, yt_subtitles=None):
    docs_num = len(data)

    # kmeans labels
    # At the input, the classifier receives a table of n words with the highest score. The rest of the words are rated 0.
    # Thus we divide the text into several parts according to their subject matter
    print('\rkmeans labels. part 1 of 4', end=' ' * 35)
    kmeans_labels = []
    n_clusters = 7
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    for i in range(docs_num):
        # print('len', data[i]['app_freq_f'].shape)
        kmeans.fit(data[i]['app_freq_f'])  # .mask(data[0]['app_freq_f'] > 0, 1))
        labels = kmeans.labels_
        kmeans_labels.append(labels)
        data[i]['labels'] = labels

    # grouping words in each group
    # After K-means, we can analyze each group for the most frequent words.
    print('\rgrouping words in each group. part 2 of 4', end=' ' * 20)
    for i in range(docs_num):
        for k in range(n_clusters):
            groups = []
            rows = data[i]['app_freq_f'].loc[kmeans_labels[i] == k].reset_index()
            for j in range(rows.shape[0]):
                cols = rows.loc[j] >= 1
                groups.extend(rows.columns[cols])
            data[i][f'clus{k}_words'] = list(set(groups))
    #             print('==', len(data[i][f'clus{i}_words']))

    # nlp similarity
    # Using a neural network, we will compare the query vectors with each group to assess how similar they are.
    # Estimate using the cosine of the angle vectors
    print('\rnlp similarity. part 3 of 4', end=' ' * 25)
    search_nlp = nlp(query)
    max_sim = -1
    for i in range(docs_num):
        for k in range(n_clusters):
            sim = search_nlp.similarity(nlp(' '.join(data[i][f'clus{k}_words'])))
            data[i][f'clus{k}_similarity'] = sim
            if sim > max_sim:
                max_sim = sim

    # from labels and similarity getting text parts
    # Using the similarity score from the neural network, we select groups that are similar to our query.
    # We select the intervals from the text that we need to cut and then connect into one video.
    limit = 0.6
    if limit > max_sim:
        limit = max_sim * 0.99
    print(f'\rfrom similarity({limit = }) getting best text parts. part 4 of 4', end='')
    best_parts = []
    sub_parts = []
    for i in range(docs_num):
        best_part, sub_part = _clusters2parts(kmeans_labels[i], data[i], threshold=limit)
        best_parts.append(best_part)
        sub_parts.append(sub_part)

    best_part_timings = []
    if 'text_part' in data[0].keys() and yt_subtitles:
        # getting timings
        for i in range(docs_num):
            best_part_timings.append(_parts2timings(sub_parts[i], yt_subtitles[i]))
    print('\rTimings builded', end=' ' * 65)
    print()

    return best_parts, best_part_timings


# parts of text to timings
# dfs[0]
def _parts2timings(sub_parts, yt_subtitles):
    timings = []
    for part in sub_parts:
    #     print(part)
        start = yt_subtitles.loc[part[0], 'start']
        end = yt_subtitles.loc[part[1], 'start'] + yt_subtitles.loc[part[1], 'duration']
        timings.append((start, end))
    return timings


# kmeans.labels_, data[0]['text_part'...]:dict
def _clusters2parts(labels, data, threshold=0.6):
    clusters = []
    # gathering best clusters
    for i in range(max(labels)):
        if data[f'clus{i}_similarity'] > threshold:
            clusters.append(i)

    # finding parts in text for each cluster
    lable_array = _knn_mean(labels, 30)
    best_parts = []

    start = False
    lable = -1
    start_ind = 0

    # choising and connectiong text parts acording labels
    for i in range(len(lable_array)):
        #         print(f'{i} l:{lable_array[i]} st:{start_ind} in:{lable_array[i] in clusters} start:({start})')
        if lable_array[i] == lable:
            continue
        else:
            if lable_array[i] in clusters:
                lable = lable_array[i]
                if not start:
                    start_ind = i
                    start = True

            else:
                lable = -1
                if start:
                    start = False
                    best_parts.append((start_ind, i - 1))

    if start:
        best_parts.append((start_ind, len(lable_array) - 1))

    # if text from youtube subtitles, so he divided to parts with timings
    parts_in_subtitles = []
    if 'text_part' in data.keys():
        for part in best_parts:
            start = data['text_part'][part[0]]
            #             print(f'{part[1] = }')
            end = data['text_part'][part[1]]
            parts_in_subtitles.append((start, end))

    return best_parts, parts_in_subtitles


def _knn_mean(arr, n=20):
    half = n // 2
    end = len(arr) - 1
    mean = []
    for n in range(len(arr)):
        labels, counts = np.unique(arr[max(0, n-half): min(end, n+half)], return_counts=True)
        mean.append(labels[np.argmax(counts)])
    return np.array(mean)

# data: list(datasets)
def build_plots(data):
    print('Building plots:')
    for i in range(len(data)):
        fig = data[i]['app_freq'].plot(figsize=(20, 5), legend=None).get_figure()
        f_name = f'word_frequency_mean{i}.jpeg'
        print('\tsaved:', f_name, end='')
        fig.savefig(f_name)
        fig = data[i]['app_freq_f'].plot(figsize=(20, 5), legend=None).get_figure()
        f_name = f'word_most_frequency_mean{i}.jpeg'
        print('\t', f_name, end='')
        fig.savefig(f_name)

        fig = plt.figure(figsize=(20, 5), dpi=150)
        plt.scatter(x=range(data[i]['app_freq_f'].shape[0]), y=data[i]['labels'], color='b', label='original')
        plt.plot(_knn_mean(data[i]['labels'], 40), 'r.', label='after knn')
        plt.title('X: words, Y: group')
        plt.legend()
        f_name = f'kmeans_groups{i}.jpeg'
        print('\t', f_name)
        fig.savefig(f_name)




