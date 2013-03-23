import webapp2

from headline.handlers import MyHandler
from sourcehistory import bs

class DatasourceHistory(MyHandler):

    def get(self, slug):
        if not self.prepare():
            return
        datasource = bs.getDatasourceHistory(slug)
        if not datasource:
            self.error(404)
            return

        templateValues = {
            'datasource': datasource,
        }
        self.render(templateValues, 'datasource-history.html')

