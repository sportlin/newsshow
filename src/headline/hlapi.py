
from . import modelapi

def saveItems(datasource, items):
    modelapi.updateDatasources(datasource, items)
    modelapi.saveItems(datasource, items)

def getItems():
    return modelapi.getItems()

def getDatasources():
    datasources = modelapi.getDatasources().values()
    return datasources

