import copy
import datetime
import logging

from commonutil import stringutil
from commonutil import dateutil, collectionutil
import globalconfig
import sourcenow.bs as bsNow

def getTopicsConfig():
    return [topic.get('ui') for topic in modelapi.getDisplayTopics()]

def getHomeData():
    topics = bsNow.getTopics4Home()
    return {
        'topics': resultTopics,
    }

