import webapp2

from templateutil.handlers import BasicHandler

import globalconfig
from . import hlapi

class MyHandler(BasicHandler):
    menu = None

    def getExtraValues(self):
        menus = hlapi.getMenus(self.menu)
        result = {
            'site': globalconfig.getSiteConfig(),
            'i18n': globalconfig.getI18N(),
            'menus': menus,
        }
        return result

class Topics(MyHandler):

    def get(self):
        topics = hlapi.getTopics()
        templateValues = {
            'topics': topics,
        }
        self.render(templateValues, 'topics.html')

class TopicHistory(MyHandler):

    def get(self, slug=None):
        topic = hlapi.getTopicHistory(slug)
        if slug == globalconfig.getHomeTopicSlug() or not slug:
            topicUrl = None
        else:
            topicUrl = webapp2.uri_for('topic', slug=slug)
        templateValues = {
            'topicUrl': topicUrl,
            'topic': topic,
        }
        self.render(templateValues, 'history.html')

class Datasources(MyHandler):

    def get(self):
        datasources = hlapi.getDatasources()
        templateValues = {
            'datasources': datasources,
        }
        self.render(templateValues, 'datasources.html')

class Topic(MyHandler):

    def get(self, slug=None):
        if not slug:
            slug = 'home'
        self.menu = slug
        topic = hlapi.getTopic(slug)
        if not topic:
            self.error(404)
            return
        if slug == globalconfig.getHomeTopicSlug():
            topicUrl = None
        else:
            topicUrl = webapp2.uri_for('topic', slug=slug)
        latestUrl = webapp2.uri_for('latest', slug=slug)
        templateValues = {
            'topicUrl': topicUrl,
            'latestUrl': latestUrl,
            'topic': topic,
        }
        self.render(templateValues, 'topic.html')

