import webapp2

from templateutil.handlers import BasicHandler

import globalconfig

from . import hlapi

class MyHandler(BasicHandler):

    def prepareBaseValues(self):
        self.site = globalconfig.getSiteConfig()
        self.i18n = globalconfig.getI18N()

class DatasourceExpose(MyHandler):

    def get(self):
        if not self.prepare():
            return
        exposeds = hlapi.getDisplayDatasources()
        unexposeds = hlapi.getUnexposedDatasources()
        templateValues = {
            'exposeds': exposeds,
            'unexposeds': unexposeds,
        }
        self.render(templateValues, 'expose.html')

    def post(self):
        action = self.request.get('action')
        if action == 'Expose':
            topic = self.request.get('topic')
            slug = self.request.get('slug')
            sourceId = self.request.get('id')
            if sourceId:
                hlapi.exposeDatasource(topic, slug, sourceId)
        elif action == 'Close':
            sourceId = self.request.get('id')
            if sourceId:
                hlapi.closeDatasource(sourceId)
        self.get()

