import webapp2

from templateutil.handlers import BasicHandler

import globalconfig
import globalutil

from headline.handlers import MyHandler, TopicHandler
from sourcenow import bs


class ChannelStatus(TopicHandler):

    def get(self, slug):
        self.topicShowtype = 'status'
        self.topicSlug = slug
        if not self.prepare():
            return
        topic = bs.getTopicInStatus(slug)
        if not topic:
            self.error(404)
            return
        globalutil.populateSourceUrl(topic['pages'])
        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-status.html')


class ChannelGroup(TopicHandler):

    def get(self, slug):
        self.topicShowtype = 'group'
        self.topicSlug = slug
        if not self.prepare():
            return
        topic = bs.getTopicInGroup(slug)
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

    def get(self, slug):
        self.topicShowtype = 'picture'
        self.topicSlug = slug
        if not self.prepare():
            return
        topic = bs.getTopicInPicture(slug)
        if not topic:
            self.error(404)
            return

        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-picture.html')

class Hot(MyHandler):

    def get(self):
        if not self.prepare():
            return
        chartses = bs.getChartses()
        chartses.sort(key=lambda charts: charts['source']['added'], reverse=True)
        for charts in chartses:
            charts['url'] = webapp2.uri_for('charts', slug=charts['source']['slug'])
        templateValues = {
            'chartses': chartses,
        }
        self.render(templateValues, 'hot.html')

class Charts(MyHandler):

    def get(self, slug):
        if not self.prepare():
            return
        charts = bs.getCharts(slug)
        if not charts:
            self.error(404)
            return
        templateValues = {
            'charts': charts,
        }
        self.render(templateValues, 'charts.html')

class Latest(MyHandler):

    def get(self):
        if not self.prepare():
            return
        pages = bs.getLatestPages()
        pages.sort(key=lambda page: page.get('added'), reverse=True)
        globalutil.populateSourceUrl(pages)
        templateValues = {
            'pages': pages,
        }
        self.render(templateValues, 'latest.html')

