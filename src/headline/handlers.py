import webapp2

from templateutil.handlers import BasicHandler

import globalconfig
import globalutil

from sourcenow import snapi

def _getMenu(topicShowtype, selectedSlug):
    topics = snapi.getDisplayTopics()
    topicMenus = []
    for topic in topics:
        topicSlug = topic.get('slug')
        topicName = topic.get('name')
        if not topicSlug:
            continue
        if not topicName:
            continue
        if topicShowtype == 'group':
            topicHandlerName = 'channel.group'
        elif topicShowtype == 'picture':
            topicHandlerName = 'channel.picture'
        elif topicShowtype == 'status':
            topicHandlerName = 'channel.status'
        else:
            topicHandlerName = 'channel.group'
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
        self.extraValues['hoturl'] = webapp2.uri_for('hot')
        self.extraValues['menu'] = _getMenu(self.topicShowtype, self.topicSlug)

class TopicHandler(MyHandler):

    def prepareValues(self):
        super(TopicHandler, self).prepareValues()
        slug = self.topicSlug
        self.extraValues['topicUrls'] = {
                'status': webapp2.uri_for('channel.status', slug=slug),
                'group': webapp2.uri_for('channel.group', slug=slug),
                'picture': webapp2.uri_for('channel.picture', slug=slug),
            }

class Home(MyHandler):

    def get(self):
        if not self.prepare():
            return
        maxGroupCount = 4
        maxGroupChildCount = 6
        maxChartsCount = 4
        maxChartsChildCount = 6
        topics = snapi.getTopics(maxGroupCount)
        for topic in topics:
            topicSlug = topic.get('slug')
            topic['url'] = webapp2.uri_for('channel.status', slug=topicSlug)
            for group in topic['groups']:
                group['url'] =  webapp2.uri_for('channel.group', slug=topicSlug)
                group['pages'] = group['pages'][:maxGroupChildCount]
                globalutil.populateSourceUrl(group['pages'])

        chartses = snapi.getChartses()
        chartses = chartses[:maxChartsCount]
        for charts in chartses:
            charts['pages'] = charts['pages'][:maxChartsChildCount]

        templateValues = {
            'topics': topics,
            'chartses': chartses,
        }
        self.render(templateValues, 'home.html')

