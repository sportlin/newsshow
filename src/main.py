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

import hotword.handlersapi
import hotword.handlers

import globalconfig

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
webapp2.Route('/search/<keyword:.*>', handler=headline.handlers.Search, name='search'),
('/configitem/', configmanager.handlers.MainPage),
('/admin/clean/', headline.handlersadmin.CleanData),
('/api/headline/add/', headline.handlersapi.HeadlineAddRequest),
('/headline/add/', headline.handlersapi.HeadlineAddResponse),

webapp2.Route('/hot/', handler=sourcenow.handlers.Hot, name='hot'),
webapp2.Route('/latest/', handler=sourcenow.handlers.Latest, name='latest'),
webapp2.Route('/charts/<charts:.+>', handler=sourcenow.handlers.Charts, name='charts'),
webapp2.Route('/channel/group/<channel>/', handler=sourcenow.handlers.ChannelGroup, name='channel.group'),
webapp2.Route('/channel/picture/<channel>/', handler=sourcenow.handlers.ChannelPicture, name='channel.picture'),
webapp2.Route('/channel/<channel>/', handler=sourcenow.handlers.ChannelStatus, name='channel.status'),
webapp2.Route('/source/<source:.+>', handler=sourcehistory.handlers.DatasourceHistory, name='datasource.history'),

('/words/start/', hotword.handlersapi.Start),
('/words/run/', hotword.handlersapi.Run),
('/words/show/', hotword.handlers.Show),
],
debug=True, config=config)

