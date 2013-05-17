import logging

import webapp2

from commonutil import dateutil
from templateutil.handlers import BasicHandler
from searcher import gnews
from robotkeyword import rkapi

import globalconfig
import globalutil
from sourcenow import snapi
from hotword import hwapi
from hotevent import heapi

def _getMenus():
    channels = snapi.getChannels()
    menus = []
    for channel in channels:
        slug = channel.get('slug')
        name = channel.get('name')
        if not slug:
            continue
        if not name:
            continue
        url = webapp2.uri_for('channel', channel=slug)
        menus.append({
            'name': name,
            'url': url,
        })
    return menus

class MyHandler(BasicHandler):

    def doRedirection(self):
        if self.request.path.startswith('/search/'):
            return False
        referer = self.request.referer
        if not referer:
            return False
        keyword = rkapi.getRefererKeyword(referer)
        if not keyword:
            return False
        if self.request.path.startswith('/event/'):
            if keyword:
                self.extraValues['keyword'] = keyword
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
        self.extraValues['extramenus'] = _getMenus()
        self.extraValues['latesturl'] = webapp2.uri_for('latest')
        self.extraValues['sitesurl'] = webapp2.uri_for('sites')
        self.extraValues['chartsesurl'] = webapp2.uri_for('chartses')


class Home(MyHandler):

    def get(self):
        _LATEST_COUNT = 20
        sitePages = snapi.getSitePages()
        sitePages.sort(key=lambda page: page.get('published') or page['added'], reverse=True)
        sitePages = sitePages[:_LATEST_COUNT]
        globalutil.populateSourceUrl(sitePages)

        chartsPages = snapi.getChartsPages()
        chartsPages.sort(key=lambda page: page.get('published') or page['added'], reverse=True)
        chartsPages = chartsPages[:_LATEST_COUNT]

        latestPages = sitePages + chartsPages
        latestPages.sort(key=lambda page: page.get('published') or page['added'], reverse=True)
        latestPages = latestPages[:_LATEST_COUNT]

        sentenceSeparators = self.site.get('sentence.separator', [])

        siteWords, _ = hwapi.getWords('sites')
        sitePages = heapi.getEventPages('sites')
        for page in sitePages:
            if page['event']['exposed']:
                eventUrlType = 'event'
            else:
                eventUrlType = 'hidden-event'
            # if eventId=0, error happens: 'Missing argument "eventId" to build URI.'
            page['event']['url'] = webapp2.uri_for(eventUrlType, eventScope='sites', eventId=page['event']['id'])
        sitePages.sort(key=lambda page: page['weight'], reverse=True)
        globalutil.populateSourceUrl(sitePages)

        chartsWords, _ = hwapi.getWords('chartses')
        chartsPages = heapi.getEventPages('chartses')
        for page in chartsPages:
            if page['event']['exposed']:
                eventUrlType = 'event'
            else:
                eventUrlType = 'hidden-event'
            page['event']['url'] = webapp2.uri_for(eventUrlType, eventScope='chartses', eventId=page['event']['id'])
        chartsPages.sort(key=lambda page: page['weight'], reverse=True)

        templateValues = {
            'latestPages': latestPages,
            'siteWords': siteWords,
            'sitePages': sitePages,
            'chartsWords': chartsWords,
            'chartsPages': chartsPages,
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
            pages = globalutil.search(pages, words)
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

