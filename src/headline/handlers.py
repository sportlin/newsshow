from templateutil.handlers import BasicHandler

import globalconfig
from . import hlapi

class MyHandler(BasicHandler):

    def getExtraValues(self):
        menus = hlapi.getMenus()
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

class PageHistory(MyHandler):

    def get(self):
        pages = hlapi.getPageHistory()
        templateValues = {
            'pages': pages,
        }
        self.render(templateValues, 'history.html')

class Datasources(MyHandler):

    def get(self):
        datasources = hlapi.getDatasources()
        templateValues = {
            'datasources': datasources,
        }
        self.render(templateValues, 'datasources.html')

