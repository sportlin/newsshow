import webapp2

from templateutil.handlers import BasicHandler

import globalconfig

from headline.handlers import TopicHandler
from sourcehistory import bs as bsHistory

class TopicHistory(TopicHandler):

    def get(self, slug):
        self.topicShowtype = 'history'
        self.topicSlug = slug
        if not self.prepare():
            return
        topic = bsHistory.getTopicHistory(slug)
        if not topic:
            self.error(404)
            return

        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-history.html')

class TopicPicture(TopicHandler):

    def get(self, slug):
        self.topicShowtype = 'picture'
        self.topicSlug = slug
        if not self.prepare():
            return
        topic = bsHistory.getTopicPicture(slug)
        if not topic:
            self.error(404)
            return

        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic-picture.html')

