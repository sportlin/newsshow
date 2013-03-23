import webapp2

from templateutil.handlers import BasicHandler

import globalconfig

from . import hlapi

class MyHandler(BasicHandler):

    def prepareBaseValues(self):
        self.site = globalconfig.getSiteConfig()
        self.i18n = globalconfig.getI18N()

class CleanData(MyHandler):

    def get(self):
        if not self.prepare():
            return
        self.response.out.write('Cleaned.')

