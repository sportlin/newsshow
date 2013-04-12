import logging

import webapp2

from templateutil.handlers import BasicHandler
from searcher import gnews
from robotkeyword import rkapi

from hotword import hwapi
import globalconfig
import globalutil
from sourcenow import snapi

def _getMenu(selectedSlug):
    topics = snapi.getDisplayTopics()
    topicMenus = []
    for topic in topics:
        topicSlug = topic.get('slug')
        topicName = topic.get('name')
        if not topicSlug:
            continue
        if not topicName:
            continue
        url = webapp2.uri_for('channel', channel=topicSlug)
        topicMenus.append({
            'name': topicName,
            'url': url,
            'selected': selectedSlug == topicSlug,
        })
    return topicMenus

class MyHandler(BasicHandler):
    channelSlug = None
    showtype = None

    def doRedirection(self):
        if self.request.path.startswith('/search/'):
            return False
        referer = self.request.referer
        if not referer:
            return False
        keyword = rkapi.getRefererKeyword(referer)
        if not keyword:
            return False
        reserveds = self.site.get('reserved.keywords',[])
        for reserved in reserveds:
            if reserved in keyword:
                return False
        keyword = keyword.encode('utf8')
        url = webapp2.uri_for('search', keyword=keyword)
        self.redirect(url, permanent=True)
        return True

    def prepareBaseValues(self):
        self.site = globalconfig.getSiteConfig()
        self.i18n = globalconfig.getI18N()

    def prepareValues(self):
        self.channelSlug = self.request.route_kwargs.get('channel')
        self.extraValues['menu'] = _getMenu(self.channelSlug)


class Home(MyHandler):

    def get(self):
        sentenceSeparators = self.site.get('sentence.separator', [])

        hoturl = webapp2.uri_for('hot')
        latesturl = webapp2.uri_for('latest')

        siteWords = hwapi.getJsonWords(sentenceSeparators, 'sites')
        chartsWords = hwapi.getJsonWords(sentenceSeparators, 'chartses')
        templateValues = {
            'hoturl': hoturl,
            'latesturl': latesturl,
            'siteWords': siteWords,
            'chartsWords': chartsWords,
        }
        self.render(templateValues, 'home.html')


class Search(MyHandler):

    def get(self, keyword):
        pages = []
        gpages = []
        words = []
        gnewssize = 2
        if keyword:
            import jieba # May fail to load jieba
            jieba.initialize(usingSmall=True)
            words = list(jieba.cut(keyword, cut_all=False))
            words = [ word for word in words if len(word) > 1 ]
            # words = list(jieba.cut_for_search(keyword))
            keyword = keyword.decode('utf8')
            pages = snapi.getAllPages()
            pages = snapi.search(pages, words)
            pages.sort(key=lambda page: page.get('added'), reverse=True)
            pages.sort(key=lambda page: page.get('grade'), reverse=True)
            globalutil.populateSourceUrl(pages)

            gpages = gnews.search(keyword, large=True)
            if not gpages:
                for word in words:
                    gpages = gnews.search(word, large=True)
                    if gpages:
                        break
            gpages.sort(key=lambda page: page.get('published'), reverse=True)
            gpages.sort(key=lambda page: bool(page.get('img')), reverse=True)
            gpages = gpages[:gnewssize]

        gnewsUrl = gnews.getSearchUrl(keyword)

        templateValues = {
            'keyword': keyword,
            'pages': pages,
            'gpages': gpages,
            'gnewsurl': gnewsUrl,
            'words': words,
        }
        self.render(templateValues, 'search.html')

