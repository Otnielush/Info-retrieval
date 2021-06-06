import spacy

# spacy english model (large)
try:
    nlp = spacy.load('en_core_web_lg')
except:
    print('need to download model\npython -m spacy download en_core_web_lg')


def filter_2(search_sentence, yt_objects):
    # may be: % of relevance; recomendation in which part more relevance for search
    predictions = []

    tokens = nlp(search_sentence)

    # parsing info from yt_objects
    y_keywords = []
    y_views = []
    y_title = []
    y_author = []
    y_description = []   # replace '\n'
    y_length = []
    y_publish_date = []
    y_rating = []
    spacy_similarity = []

    for i, obj in enumerate(yt_objects):
        y_keywords.append(obj.keywords) # list
        y_views.append(obj.views)
        y_title.append(obj.title)
        y_author.append(obj.author)
        y_description.append(obj.description.replace('\n', ' '))
        y_length.append(obj.length)
        y_publish_date.append(obj.publish_date)  # datetime
        y_rating.append(obj.rating)

            # We can add here weights
        ss = tokens.similarity(nlp(' '.join(y_keywords[-1])))
        ss += tokens.similarity(nlp(y_title[-1]))
        ss += tokens.similarity(nlp(y_author[-1]))
        ss += tokens.similarity(nlp(y_description[-1]))

        spacy_similarity.append(ss)
        obj.similarity = ss

    return sorted(yt_objects, key=lambda x: x.similarity, reverse=True)

