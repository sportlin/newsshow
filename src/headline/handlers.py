import os

from google.appengine.ext.webapp import template
import webapp2

from . import hlapi

class HomePage(webapp2.RequestHandler):
    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self):
        items = hlapi.getItems()
        templateValues = {
            'items': items,
        }
        self._render(templateValues)

