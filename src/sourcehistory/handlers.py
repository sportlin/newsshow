import webapp2

from templateutil.handlers import BasicHandler

import globalconfig

from headline.handlers import MyHandler, TopicHandler
from sourcehistory import bs as bsHistory

class DatasourceHistory(MyHandler):

    def get(self, slug):
        if not self.prepare():
            return
        datasource = bsHistory.getDatasourceHistory(slug)
        if not datasource:
            self.error(404)
            return

        templateValues = {
            'datasource': datasource,
        }
        self.render(templateValues, 'datasource-history.html')

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

