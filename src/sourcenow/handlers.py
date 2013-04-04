import webapp2

from templateutil.handlers import BasicHandler

import globalconfig
import globalutil

from headline.handlers import MyHandler, TopicHandler
from sourcenow import bs


class ChannelStatus(TopicHandler):
    showtype = 'status'

    def get(self, channel):
        topic = bs.getTopicInStatus(channel)
        if not topic:
            self.error(404)
            return
        globalutil.populateSourceUrl(topic['pages'])
        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-status.html')


class ChannelGroup(TopicHandler):
    showtype = 'group'

    def get(self, channel):
        topic = bs.getTopicInGroup(channel)
        if not topic:
            self.error(404)
            return
        for group in topic['groups']:
            globalutil.populateSourceUrl(group['pages'])
        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-group.html')


class ChannelPicture(TopicHandler):
    showtype = 'picture'

    def get(self, channel):
        topic = bs.getTopicInPicture(channel)
        if not topic:
            self.error(404)
            return

        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-picture.html')

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
        templateValues = {
            'charts': charts,
        }
        self.render(templateValues, 'charts.html')

class Latest(MyHandler):

    def get(self):
        result = bs.getLatestPages()
        globalutil.populateSourceUrl(result['site'])
        pages = []
        pages.extend(result['site'])
        pages.extend(result['charts'])
        pages.sort(key=lambda page: page.get('published') or page.get('added'), reverse=True)
        templateValues = {
            'pages': pages,
        }
        self.render(templateValues, 'latest.html')

