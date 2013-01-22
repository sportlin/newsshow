import webapp2

from templateutil.handlers import BasicHandler

import globalconfig
from . import hlapi

def _getTopicMenus(selected):
    topics = hlapi.getTopicsConfig()
    menus = []
    for topic in topics:
        topicSlug = topic.get('slug')
        topicName = topic.get('name')
        if not topicSlug:
            continue
        if not topicName:
            continue
        url = webapp2.uri_for('topic', slug=topicSlug)
        menus.append({
            'name': topicName,
            'url': url,
            'selected': topicSlug == selected,
        })
    return menus

def _getLatestMenus():
    topics = hlapi.getTopicsConfig()
    menus = []
    for topic in topics:
        topicSlug = topic.get('slug')
        topicName = topic.get('name')
        if not topicSlug:
            continue
        if not topicName:
            continue
        url = webapp2.uri_for('latest', slug=topicSlug)
        menus.append({
            'name': topicName,
            'url': url,
        })
    return menus

class MyHandler(BasicHandler):
    menu = None

    def getExtraValues(self):
        menus = _getTopicMenus(self.menu)
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

class Datasources(MyHandler):

    def get(self):
        datasources = hlapi.getDatasources()
        templateValues = {
            'datasources': datasources,
        }
        self.render(templateValues, 'datasources.html')

class Topic(MyHandler):

    def get(self, slug):
        self.menu = slug
        topic = hlapi.getTopic(slug)
        if not topic:
            self.error(404)
            return
        topicUrl = webapp2.uri_for('topic', slug=slug)
        latestUrl = webapp2.uri_for('latest', slug=slug)
        templateValues = {
            'topicUrl': topicUrl,
            'latestUrl': latestUrl,
            'topic': topic,
        }
        self.render(templateValues, 'topic.html')

class TopicHistory(MyHandler):

    def get(self, slug=None):
        topic = hlapi.getTopicHistory(slug)
        if not slug:
            topicUrl = None
        else:
            topicUrl = webapp2.uri_for('topic', slug=slug)
        latestMenus = _getLatestMenus()
        templateValues = {
            'topicUrl': topicUrl,
            'topic': topic,
            'latestMenus': latestMenus,
        }
        self.render(templateValues, 'history.html')

class Home(MyHandler):

    def get(self):
        homeData = hlapi.getHomeData()
        for topic in homeData['topics']:
            topicSlug = topic.get('slug')
            topic['url'] = {
                'topic': webapp2.uri_for('topic', slug=topicSlug),
                'latest': webapp2.uri_for('latest', slug=topicSlug),
            }
        templateValues = {
            'homeData': homeData,
        }
        self.render(templateValues, 'home.html')

