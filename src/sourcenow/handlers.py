import webapp2

from templateutil.handlers import BasicHandler

import globalconfig
import globalutil

from headline.handlers import MyHandler
from hotword import hwapi
from . import bs, snapi

class Channel(MyHandler):

    def get(self, channel):
        foundChannel = globalconfig.getChannel(channel)

        if not foundChannel:
            self.error(404)
            return

        sitePages = snapi.getSitePages()
        tags = foundChannel.get('tags')
        foundChannel['pages'] = bs.getPagesByTags(sitePages, tags)

        globalutil.populateSourceUrl(foundChannel['pages'])
        foundChannel['pages'].sort(key=lambda page: page['added'], reverse=True)

        words, pages = hwapi.getWords(foundChannel['slug'])
        pages.sort(key=lambda page: page['weight'], reverse=True)

        templateValues = {
            'words': words,
            'pages': pages,
            'channel': foundChannel,
        }
        self.render(templateValues, 'channel.html')

class Chartses(MyHandler):

    def get(self):
        words, pages = hwapi.getWords('chartses')
        pages.sort(key=lambda page: page['weight'], reverse=True)
        templateValues = {
            'words': words,
            'pages': pages,
        }
        self.render(templateValues, 'chartses.html')

class Charts(MyHandler):

    def get(self, charts):
        charts = bs.getCharts(charts)
        if not charts:
            self.error(404)
            return
        templateValues = {
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

    def get(self, scope=None):
        if scope == 'sites':
            pages = snapi.getSitePages()
            globalutil.populateSourceUrl(pages)
        elif scope == 'chartses':
            pages = snapi.getChartsPages()
        else:
            sitePages = snapi.getSitePages()
            globalutil.populateSourceUrl(sitePages)
            chartsPages = snapi.getChartsPages()
            pages = sitePages + chartsPages
        pages.sort(key=lambda page: page.get('published') or page['added'], reverse=True)
        templateValues = {
            'latesturl': webapp2.uri_for('latest'),
            'scope': scope,
            'pages': pages,
        }
        self.render(templateValues, 'latest.html')

