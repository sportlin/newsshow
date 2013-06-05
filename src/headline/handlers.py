import logging

import webapp2

from commonutil import dateutil, stringutil
from templateutil.handlers import BasicHandler
from searchengine import gnews
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


class Home(MyHandler):

    def get(self):
        _LATEST_COUNT = 6
        sitePages = snapi.getSitePages()
        sitePages.sort(key=lambda page: page.get('published') or page['added'], reverse=True)
        sitePages = sitePages[:_LATEST_COUNT]
        globalutil.populateSourceUrl(sitePages)

        chartsPages = snapi.getChartsPages()
        chartsPages.sort(key=lambda page: page.get('published') or page['added'], reverse=True)
        chartsPages = chartsPages[:_LATEST_COUNT]

        siteEvents = heapi.getEventPages('sites')
        for page in siteEvents:
            if page['event']['exposed']:
                eventUrlType = 'event'
            else:
                eventUrlType = 'hidden-event'
            # if eventId=0, error happens: 'Missing argument "eventId" to build URI.'
            page['event']['url'] = webapp2.uri_for(eventUrlType, eventScope='sites', eventId=page['event']['id'])
        siteEvents.sort(key=lambda page: page['weight'], reverse=True)
        siteEvents = siteEvents[:_LATEST_COUNT]
        globalutil.populateSourceUrl(siteEvents)

        chartsEvents = heapi.getEventPages('chartses')
        for page in chartsEvents:
            if page['event']['exposed']:
                eventUrlType = 'event'
            else:
                eventUrlType = 'hidden-event'
            page['event']['url'] = webapp2.uri_for(eventUrlType, eventScope='chartses', eventId=page['event']['id'])
        chartsEvents.sort(key=lambda page: page['weight'], reverse=True)
        chartsEvents = chartsEvents[:_LATEST_COUNT]

        chartses = snapi.getChartses()
        chartses.sort(key=lambda charts: charts['source']['added'], reverse=True)
        for charts in chartses:
            charts['url'] = webapp2.uri_for('charts', charts=charts['source']['slug'])
            charts['pages'] = charts['pages'][:_LATEST_COUNT]

        templateValues = {
            'sitePages': sitePages,
            'chartsPages': chartsPages,
            'siteEvents': siteEvents,
            'chartsEvents': chartsEvents,
            'chartses': chartses,
            'latesturl': webapp2.uri_for('latest'),
            'latestsitesurl': webapp2.uri_for('latestScope', scope='sites'),
            'latestchartsesurl': webapp2.uri_for('latestScope', scope='chartses'),
            'hotsitesurl': webapp2.uri_for('sites'),
            'hotchartsesurl': webapp2.uri_for('chartses')
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
            keyword = stringutil.parseUnicode(keyword)
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

