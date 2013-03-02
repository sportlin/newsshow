import webapp2

from templateutil.handlers import BasicHandler

import globalconfig

from headline.handlers import TopicHandler
from sourcenow import bs as bsNow

class TopicGroup(TopicHandler):

    def get(self, slug):
        self.topicShowtype = 'source'
        self.topicSlug = slug
        if not self.prepare():
            return
        topic = bsNow.getTopicGroup(slug)
        if not topic:
            self.error(404)
            return
        for group in topic.get('groups', []):
            for datasource in group['datasources']:
                sourceId = datasource['source'].get('id')
                if sourceId:
                    datasource['source']['history'] = webapp2.uri_for('datasource',
                        sourceId=sourceId)
        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-group.html')

class TopicStatus(TopicHandler):

    def get(self, slug):
        self.topicShowtype = 'status'
        self.topicSlug = slug
        if not self.prepare():
            return
        topic = bsNow.getTopicStatus(slug)
        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-status.html')

