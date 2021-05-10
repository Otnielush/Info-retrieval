


def filter_2(search_sentence, yt_objects):
    # may be: % of relevance; recomendation in which part more relevance for search
    predictions = []

    # parsing info from yt_objects
    y_keywords = []
    y_views = []
    y_title = []
    y_author = []
    y_description = []   # replace '\n'
    y_length = []
    y_publish_date = []
    y_rating = []

    for i, obj in enumerate(yt_objects):
        y_keywords.append(obj.keywords) # list
        y_views.append(obj.views)
        y_title.append(obj.title)
        y_author.append(obj.author)
        y_description.append(obj.description.replace('\n', ' '))
        y_length.append(obj.length)
        y_publish_date.append(obj.publish_date)  # datetime
        y_rating.append(obj.rating)





    return predictions