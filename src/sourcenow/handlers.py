import webapp2

from templateutil.handlers import BasicHandler

import globalconfig
import globalutil

from headline.handlers import MyHandler
from hotword import hwapi
from sourcenow import bs, snapi

class Channel(MyHandler):

    def get(self, channel):
        channel = bs.getChannel(channel)
        if not channel:
            self.error(404)
            return

        for group in channel['groups']:
            globalutil.populateSourceUrl(group['pages'])

        words, pages = hwapi.getWords(channel['slug'])
        pages.sort(key=lambda page: page.get('published') or page.get('added'), reverse=True)

        templateValues = {
            'words': words,
            'pages': pages,
            'channel': channel,
        }
        self.render(templateValues, 'channel.html')

class Hot(MyHandler):

    def get(self):
        PAGE_COUNT = 10
        words, pages = hwapi.getWords('chartses')
        pages.sort(key=lambda page: page.get('published') or page.get('added'), reverse=True)
        chartses = bs.getChartses()
        chartses.sort(key=lambda charts: charts['source']['added'], reverse=True)
        for charts in chartses:
            charts['url'] = webapp2.uri_for('charts', charts=charts['source']['slug'])
            charts['pages'] = charts['pages'][:PAGE_COUNT]
        templateValues = {
            'words': words,
            'pages': pages,
            'chartses': chartses,
        }
        self.render(templateValues, 'hot.html')

class Charts(MyHandler):

    def get(self, charts):
        charts = bs.getCharts(charts)
        if not charts:
            self.error(404)
            return
        hoturl = webapp2.uri_for('hot')
        templateValues = {
            'hoturl': hoturl,
            'charts': charts,
        }
        self.render(templateValues, 'charts.html')

class Latest(MyHandler):

    def get(self):
        words, pages = hwapi.getWords('sites')
        pages.sort(key=lambda page: page.get('published') or page.get('added'), reverse=True)
        globalutil.populateSourceUrl(pages)
        templateValues = {
            'words': words,
            'pages': pages,
        }
        self.render(templateValues, 'latest.html')

