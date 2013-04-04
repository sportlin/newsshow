import webapp2

from headline.handlers import MyHandler
from sourcehistory import bs

class DatasourceHistory(MyHandler):

    def get(self, source):
        datasource = bs.getDatasourceHistory(source)
        if not datasource:
            self.error(404)
            return

        templateValues = {
            'datasource': datasource,
        }
        self.render(templateValues, 'datasource-history.html')

