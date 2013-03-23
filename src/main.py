import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import templateutil.filters

import configmanager.handlers
import headline.handlersadmin
import headline.handlersapi
import headline.handlers
import sourcenow.handlers
import sourcehistory.handlers

import globalconfig

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(os.path.dirname(__file__), 'html', 'templates'),
    'filters': {
        'utc14duration': templateutil.filters.utc14duration,
        'd14format': templateutil.filters.d14format,
    },
    'environment_args': {
        'extensions': ['jinja2.ext.loopcontrols', 'jinja2.ext.with_'],
    },
}

app = webapp2.WSGIApplication([
('/', headline.handlers.Home),
('/hello/', MainPage),
('/configitem/', configmanager.handlers.MainPage),
('/admin/clean/', headline.handlersadmin.CleanData),
('/api/headline/add/', headline.handlersapi.HeadlineAddRequest),
('/headline/add/', headline.handlersapi.HeadlineAddResponse),
webapp2.Route('/channel/group/<slug>/', handler=sourcenow.handlers.ChannelGroup, name='channel.group'),
webapp2.Route('/channel/picture/<slug>/', handler=sourcenow.handlers.ChannelPicture, name='channel.picture'),
webapp2.Route('/channel/<slug>/', handler=sourcenow.handlers.ChannelStatus, name='channel.status'),
webapp2.Route('/source/<slug:.+>', handler=sourcehistory.handlers.DatasourceHistory, name='datasource.history'),
],
debug=True, config=config)

