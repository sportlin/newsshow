import webapp2

from templateutil.handlers import BasicHandler

import globalconfig
import globalutil

from headline.handlers import MyHandler
from sourcenow import bs

class Channel(MyHandler):

    def get(self, channel):
        channel = bs.getChannel(channel)
        if not channel:
            self.error(404)
            return

        for group in channel['groups']:
            globalutil.populateSourceUrl(group['pages'])

        templateValues = {
            'channel': channel,
        }
        self.render(templateValues, 'channel.html')

class Hot(MyHandler):

    def get(self):
        chartses = bs.getChartses()
        chartses.sort(key=lambda charts: charts['source']['added'], reverse=True)
        for charts in chartses:
            charts['url'] = webapp2.uri_for('charts', charts=charts['source']['slug'])
        templateValues = {
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
        _LATEST_COUNT = 50
        result = bs.getLatestPages()
        globalutil.populateSourceUrl(result['site'])
        pages = []
        pages.extend(result['site'])
        pages.extend(result['charts'])
        pages.sort(key=lambda page: page.get('published') or page.get('added'), reverse=True)
        pages = pages[:_LATEST_COUNT]
        templateValues = {
            'pages': pages,
        }
        self.render(templateValues, 'latest.html')

