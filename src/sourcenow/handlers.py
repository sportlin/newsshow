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

        globalutil.populateSourceUrl(channel['pages'])
        channel['pages'].sort(key=lambda page: page['added'], reverse=True)

        words, pages = hwapi.getWords(channel['slug'])
        pages.sort(key=lambda page: page['weight'], reverse=True)

        templateValues = {
            'words': words,
            'pages': pages,
            'channel': channel,
        }
        self.render(templateValues, 'channel.html')

class Chartses(MyHandler):

    def get(self):
        PAGE_COUNT = 10
        words, pages = hwapi.getWords('chartses')
        pages.sort(key=lambda page: page['weight'], reverse=True)
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
        self.render(templateValues, 'chartses.html')

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

class Sites(MyHandler):

    def get(self):
        words, pages = hwapi.getWords('sites')
        pages.sort(key=lambda page: page['weight'], reverse=True)
        globalutil.populateSourceUrl(pages)
        templateValues = {
            'words': words,
            'pages': pages,
        }
        self.render(templateValues, 'sites.html')

class Latest(MyHandler):

    def get(self):
        sitePages = snapi.getSitePages()
        globalutil.populateSourceUrl(sitePages)
        chartsPages = snapi.getChartsPages()
        pages = sitePages + chartsPages
        pages.sort(key=lambda page: page.get('published') or page['added'], reverse=True)
        templateValues = {
            'pages': pages,
        }
        self.render(templateValues, 'latest.html')

