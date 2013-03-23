import webapp2

from templateutil.handlers import BasicHandler

import globalconfig

from . import hlapi

def _getMenu(topicShowtype, selectedSlug):
    topics = hlapi.getTopicsConfig()
    topicMenus = []
    for topic in topics:
        topicSlug = topic.get('slug')
        topicName = topic.get('name')
        if not topicSlug:
            continue
        if not topicName:
            continue
        if topicShowtype == 'source':
            topicHandlerName = 'topic.source'
        elif topicShowtype == 'history':
            topicHandlerName = 'topic.history'
        elif topicShowtype == 'picture':
            topicHandlerName = 'topic.picture'
        else:
            topicHandlerName = 'topic.status'
        url = webapp2.uri_for(topicHandlerName, slug=topicSlug)
        topicMenus.append({
            'name': topicName,
            'url': url,
            'selected': selectedSlug == topicSlug,
        })
    return topicMenus

class MyHandler(BasicHandler):
    topicSlug = None
    topicShowtype = None

    def prepareBaseValues(self):
        self.site = globalconfig.getSiteConfig()
        self.i18n = globalconfig.getI18N()

    def prepareValues(self):
        self.extraValues['menu'] = _getMenu(self.topicShowtype, self.topicSlug)

class TopicHandler(MyHandler):

    def prepareValues(self):
        super(TopicHandler, self).prepareValues()
        slug = self.topicSlug
        self.extraValues['topicUrls'] = {
                'status': webapp2.uri_for('topic.status', slug=slug),
                'source': webapp2.uri_for('topic.source', slug=slug),
                'picture': webapp2.uri_for('topic.picture', slug=slug),
            }

class Datasources(MyHandler):

    def get(self):
        if not self.prepare():
            return
        datasources = hlapi.getDatasources()
        templateValues = {
            'datasources': datasources,
        }
        self.render(templateValues, 'datasources.html')

class Home(MyHandler):

    def get(self):
        if not self.prepare():
            return
        homeData = hlapi.getHomeData()
        for topic in homeData['topics']:
            topicSlug = topic.get('slug')
            topic['url'] = {
                'topic': webapp2.uri_for('topic.status', slug=topicSlug),
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

        datasource['topicLink'] = webapp2.uri_for('topic.status',
                    slug=datasource['topic'])
        templateValues = {
            'datasource': datasource,
        }
        self.render(templateValues, 'datasource.html')

