# https://medium.com/@cmukesh8688/tf-idf-vectorizer-scikit-learn-dbc0244a911a
# https://www.programiz.com/python-programming/datetime/strptime

# in: array of videos from youtube simple search
# out: sorted input array by the super algorithm
def sorter(search_sentence, search_results):
    sorted_results = search_results.sort()
    return sorted_results


# in: array of videos from youtube simple search
# out: web links to videos
def filter_1(search_sentence, search_results):
    sorted_array = sorter(search_sentence, search_results)

    links_array = [ 'x.link' for x in sorted_array]

    return links_array
