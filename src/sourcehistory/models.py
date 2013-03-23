import logging

import configmanager.models
from configmanager import cmapi

from headline import datareceiver

class DatasourceHistory(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(DatasourceHistory)

class DataReceiver(datareceiver.BasicDataReceiver):

    def __init__(self, name):
        datareceiver.BasicDataReceiver.__init__(self, name)

    def onData(self, datasource, items):
        receiveData(datasource, items)

datareceiver.registerReceiver(DataReceiver('Source History Receiver'))

def getDatasourceHistoryKey(slug):
    return slug

def getDatasourceHistory(slug):
    key = getDatasourceHistoryKey(slug)
    return cmapi.getItemValue(key, {}, modelname=DatasourceHistory)

def saveDatasourceHistory(datasource, items):
    logging.info('DatasourceHistory receives: %s.' % (datasource,))
    _MAX_COUNT = 20
    slug = datasource['slug']
    value = getDatasourceHistory(slug)
    value['source'] = datasource
    pages = value.get('pages', [])
    for item in reversed(items):
        if item['added'] == datasource['added']:
            pages.insert(0, item)
    pages = pages[:_MAX_COUNT]
    value['pages'] = pages

    key = getDatasourceHistoryKey(slug)
    cmapi.saveItem(key, value, modelname=DatasourceHistory)

def receiveData(datasource, items):
    if datasource.get('charts'):
        return
    saveDatasourceHistory(datasource, items)

