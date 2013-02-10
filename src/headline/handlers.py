import webapp2

from templateutil.handlers import BasicHandler

import globalconfig

from . import hlapi

def _getMenu():
    topics = hlapi.getTopicsConfig()
    latestMenus = []
    topicMenus = []
    for topic in topics:
        topicSlug = topic.get('slug')
        topicName = topic.get('name')
        if not topicSlug:
            continue
        if not topicName:
            continue

        url = webapp2.uri_for('latest', slug=topicSlug)
        latestMenus.append({
            'name': topicName,
            'url': url,
        })

        url = webapp2.uri_for('topic', slug=topicSlug)
        topicMenus.append({
            'name': topicName,
            'url': url,
        })
    return {
            'latest': latestMenus,
            'topic': topicMenus,
        }

class MyHandler(BasicHandler):
    def prepareBaseValues(self):
        self.site = globalconfig.getSiteConfig()
        self.i18n = globalconfig.getI18N()

    def prepareValues(self):
        self.extraValues['menu'] = _getMenu()

class Topics(MyHandler):

    def get(self):
        if not self.prepare():
            return
        topics = hlapi.getTopics()
        templateValues = {
            'topics': topics,
        }
        self.render(templateValues, 'topics.html')

class Datasources(MyHandler):

    def get(self):
        if not self.prepare():
            return
        datasources = hlapi.getDatasources()
        templateValues = {
            'datasources': datasources,
        }
        self.render(templateValues, 'datasources.html')

class Topic(MyHandler):

    def get(self, slug):
        if not self.prepare():
            return
        topic = hlapi.getTopic(slug)
        if not topic:
            self.error(404)
            return
        for group in topic['groups']:
            for datasource in group['datasources']:
                sourceId = datasource.get('id')
                if sourceId:
                    datasource['history'] = webapp2.uri_for('datasource',
                        sourceId=sourceId)
        templateValues = {
            'topic': topic,
        }
        self.render(templateValues, 'topic.html')

class TopicLatest(MyHandler):

    def get(self, slug):
        if not self.prepare():
            return
        topic = hlapi.getTopicHistory(slug)
        topicUrl = webapp2.uri_for('topic', slug=slug)
        templateValues = {
            'topicUrl': topicUrl,
            'topic': topic,
        }
        self.render(templateValues, 'latest.html')

class Home(MyHandler):

    def get(self):
        if not self.prepare():
            return
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

class DatasourceHistory(MyHandler):

    def get(self, sourceId=None):
        if not self.prepare():
            return
        datasource = hlapi.getDatasourceHistory(sourceId)

        if not datasource:
            self.error(404)
            return

        datasource['topicLink'] = webapp2.uri_for('topic',
                    slug=datasource['topic'])
        templateValues = {
            'datasource': datasource,
        }
        self.render(templateValues, 'datasource.html')

