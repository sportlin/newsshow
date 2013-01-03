import os

from google.appengine.ext.webapp import template
import webapp2

from . import hlapi

class HomePage(webapp2.RequestHandler):
    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'datasources.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self):
        datasources = hlapi.getDatasources()
        datasources = sorted(datasources, key=lambda datasource:
                                datasource.get('order'))
        datasources = sorted(datasources, key=lambda datasource:
                                datasource.get('topic'))
        templateValues = {
            'datasources': datasources,
        }
        self._render(templateValues)

