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
        maxChartsCount = 4
        maxChartsChildCount = 6
        homedata = snapi.getData4Home()
        chartses = homedata['chartses']
        chartses.sort(key=lambda charts: charts['source']['added'], reverse=True)
        # chartses = chartses[:maxChartsCount]
        for charts in chartses:
            charts['pages'] = charts['pages'][:maxChartsChildCount]

        maxPageCount = 10
        pages = homedata['pages']
        pages['site'] = [ page for page in pages['site'] if page.get('rank') == 1 ]
        pages['charts'].sort(key=lambda page: page.get('published') or page.get('added'), reverse=True)
        pages['site'].sort(key=lambda page: page.get('added'), reverse=True)
        pages['charts'] = pages['charts'][:maxPageCount]
        pages['site'] = pages['site'][:maxPageCount]
        globalutil.populateSourceUrl(pages['site'])

        hoturl = webapp2.uri_for('hot')
        latesturl = webapp2.uri_for('latest')
        templateValues = {
            'hoturl': hoturl,
            'latesturl': latesturl,
            'pages': pages,
            'chartses': chartses,
            'words': hwapi.getJsonWords(),
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
            # words = list(jieba.cut_for_search(keyword))
            keyword = keyword.decode('utf8')
            pages = []
            titles = set()
            for word in words:
                if len(word) < 2:
                    continue
                wpages = snapi.search(word)
                for wpage in wpages:
                    if wpage.get('title') in titles:
                        continue
                    titles.add(wpage.get('title'))
                    pages.append(wpage)
            pages.sort(key=lambda page: page.get('added'), reverse=True)
            globalutil.populateSourceUrl(pages)

            gpages = gnews.search(keyword, large=True)
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

