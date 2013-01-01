
from . import modelapi

def saveItems(items):
    modelapi.addItems(items)

def getItems():
    return modelapi.getItems()

