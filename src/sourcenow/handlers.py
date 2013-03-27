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

class Chartses(MyHandler):

    def get(self):
        if not self.prepare():
            return
        chartses = bs.getChartses()
        templateValues = {
            'chartses': chartses,
        }
        self.render(templateValues, 'chartses.html')

