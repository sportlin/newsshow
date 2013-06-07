
from commonutil import dateutil, stringutil
from searchengine import gnews, twitter

import globalutil

def search(keyword, twitterAccount):
    if not keyword:
        return []

    pages = []

    gpages = gnews.search(keyword, large=True)
    gpages.sort(key=lambda page: page.get('published'), reverse=True)
    gpages.sort(key=lambda page: bool(page.get('img')), reverse=True)
    if gpages:
        pages.append(gpages[0])
    if twitterAccount:
        tpages = twitter.search(keyword, twitterAccount)
        if tpages:
            pages.extend(tpages[:3])
    return pages

