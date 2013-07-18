import logging

import webapp2

from commonutil import dateutil, stringutil
from templateutil.handlers import BasicHandler
from robotkeyword import rkapi

import globalconfig
import globalutil
from sourcenow import snapi
from hotword import hwapi
from hotevent import heapi
from . import bs

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
        menus = [
            {
                'name': self.i18n['headlineLatest'],
                'url': webapp2.uri_for('latest'),
            },
            {
                'name': self.i18n['headlineHot'],
                'url': webapp2.uri_for('hot'),
            },
        ]
        self.extraValues['extramenus'] = menus

        channels = globalconfig.getChannels()
        for channel in channels:
            slug = channel.get('slug')
            channel['url'] = webapp2.uri_for('channel', channel=slug)
        self.extraValues['channelMenus'] = channels


class Home(MyHandler):

    def get(self):
        _LATEST_COUNT = 6

        channels = globalconfig.getChannels()
        for channel in channels:
            slug = channel.get('slug')
            channel['url'] = webapp2.uri_for('channel', channel=slug)

            events = heapi.getEventPages(slug)
            for page in events:
                if page['event']['exposed']:
                    eventUrlType = 'event'
                else:
                    eventUrlType = 'hidden-event'
                # if eventId=0, error happens: 'Missing argument "eventId" to build URI.'
                page['event']['url'] = webapp2.uri_for(eventUrlType, eventScope=slug, eventId=page['event']['id'])
            events.sort(key=lambda page: page['weight'], reverse=True)
            events = events[:_LATEST_COUNT]
            globalutil.populateSourceUrl(events)
            channel['events'] = events

        chartses = snapi.getChartses()
        chartses.sort(key=lambda charts: charts['source']['added'], reverse=True)
        for charts in chartses:
            charts['url'] = webapp2.uri_for('charts', charts=charts['source']['slug'])
            charts['pages'] = charts['pages'][:_LATEST_COUNT]

        templateValues = {
            'channels': channels,
            'chartses': chartses,
        }
        self.render(templateValues, 'home.html')


class Search(MyHandler):

    def get(self, keyword):
        pages = []
        spages = []
        words = []
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

            twitterAccount = globalconfig.getTwitterAccount()
            spages = bs.search(words[0], twitterAccount)

        templateValues = {
            'keyword': keyword,
            'pages': pages,
            'spages': spages,
            'words': words,
        }
        self.render(templateValues, 'search.html')


class Hot(MyHandler):

    def get(self):
        siteEvents = heapi.getEventPages('sites')
        for page in siteEvents:
            if page['event']['exposed']:
                eventUrlType = 'event'
            else:
                eventUrlType = 'hidden-event'
            # if eventId=0, error happens: 'Missing argument "eventId" to build URI.'
            page['event']['url'] = webapp2.uri_for(eventUrlType, eventScope='sites', eventId=page['event']['id'])
        siteEvents.sort(key=lambda page: page['weight'], reverse=True)
        globalutil.populateSourceUrl(siteEvents)

        chartsEvents = heapi.getEventPages('chartses')
        for page in chartsEvents:
            if page['event']['exposed']:
                eventUrlType = 'event'
            else:
                eventUrlType = 'hidden-event'
            # if eventId=0, error happens: 'Missing argument "eventId" to build URI.'
            page['event']['url'] = webapp2.uri_for(eventUrlType, eventScope='chartses', eventId=page['event']['id'])
        chartsEvents.sort(key=lambda page: page['weight'], reverse=True)

        _LATEST_COUNT = 10
        chartses = snapi.getChartses()
        chartses.sort(key=lambda charts: charts['source']['added'], reverse=True)
        for charts in chartses:
            charts['url'] = webapp2.uri_for('charts', charts=charts['source']['slug'])
            charts['pages'] = charts['pages'][:_LATEST_COUNT]


        templateValues = {
            'siteEvents': siteEvents,
            'chartsEvents': chartsEvents,
            'chartses': chartses,
        }
        self.render(templateValues, 'hot.html')

