import webapp2

from templateutil.handlers import BasicHandler

import globalconfig

from headline.handlers import MyHandler, TopicHandler
from sourcenow import bs

def _populateSourceUrl(pages):
    for page in pages:
        page['source']['url'] = webapp2.uri_for('datasource.history',
                                    slug=page['source']['slug'])

class ChannelStatus(TopicHandler):

    def get(self, slug):
        self.topicShowtype = 'status'
        self.topicSlug = slug
        if not self.prepare():
            return
        topic = bs.getTopicStatus(slug)
        if not topic:
            self.error(404)
            return
        _populateSourceUrl(topic['pages'])
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
        topic = bs.getTopicGroup(slug)
        if not topic:
            self.error(404)
            return
        for group in topic['groups']:
            _populateSourceUrl(group['pages'])
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
        topic = bs.getTopicPicture(slug)
        if not topic:
            self.error(404)
            return

        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-picture.html')

