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

        maxChartsCount = 4
        maxChartsChildCount = 6
        homedata = snapi.getData4Home()
        chartses = homedata['chartses']
        chartses.sort(key=lambda charts: charts['source']['added'], reverse=True)
        chartses = chartses[:maxChartsCount]
        for charts in chartses:
            charts['pages'] = charts['pages'][:maxChartsChildCount]

        maxPageCount = 10
        pages = homedata['pages']
        pages['charts'].sort(key=lambda page: page.get('added'), reverse=True)
        pages['site'].sort(key=lambda page: page.get('added'), reverse=True)
        pages['charts'] = pages['charts'][:maxPageCount]
        pages['site'] = pages['site'][:maxPageCount]
        globalutil.populateSourceUrl(pages['charts'])
        globalutil.populateSourceUrl(pages['site'])
        groups = []
        groups.append({
            'name': self.i18n.get('headline'),
            'pages': pages['site'],
            })
        groups.append({
            'name': self.i18n.get('hot'),
            'pages': pages['charts'],
            })

        hoturl = webapp2.uri_for('hot')
        latesturl = webapp2.uri_for('latest')
        templateValues = {
            'hoturl': hoturl,
            'latesturl': latesturl,
            'groups': groups,
            'chartses': chartses,
        }
        self.render(templateValues, 'home.html')

