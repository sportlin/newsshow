import os

import webapp2
from webapp2_extras import jinja2

from . import hlapi

class IndexPage(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        content = self.jinja2.render_template('topics.html', **templateValues)
        self.response.out.write(content)

    def get(self):
        topics = hlapi.getTopics()
        templateValues = {
            'topics': topics,
        }
        self._render(templateValues)

class ListPage(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        content = self.jinja2.render_template('pages.html', **templateValues)
        self.response.out.write(content)

    def get(self):
        datasources = hlapi.getDatasourceHistory()
        templateValues = {
            'datasources': datasources,
        }
        self._render(templateValues)

