import webapp2

from templateutil.handlers import BasicHandler
from commonutil import dateutil, stringutil

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

    def get(self):
        _LATEST_COUNT = 6
        sitePages = snapi.getSitePages()
        sitePages = [ page for page in sitePages if page['rank'] == 1 ]
        homeTags = globalconfig.getHomeTags()
        for homeTag in homeTags:
            homeTag['pages'] = snapi.getPagesByTags(sitePages, homeTag['tags'])
            homeTag['pages'].sort(key=lambda page: page.get('published') or page['added'], reverse=True)
            homeTag['pages'] = homeTag['pages'][:_LATEST_COUNT]
            globalutil.populateSourceUrl(homeTag['pages'])

        channels = globalconfig.getChannels()
        for channel in channels:
            slug = channel.get('slug')
            channel['url'] = webapp2.uri_for('channel', channel=slug)

            tags = channel.get('tags')
            channel['pages'] = bs.getPagesByTags(sitePages, tags)

            channel['pages'].sort(key=lambda page: page['added'], reverse=True)
            channel['pages'] = channel['pages'][:_LATEST_COUNT]
            globalutil.populateSourceUrl(channel['pages'])

        templateValues = {
            'homeTags': homeTags,
            'channels': channels,
        }
        self.render(templateValues, 'latest.html')

