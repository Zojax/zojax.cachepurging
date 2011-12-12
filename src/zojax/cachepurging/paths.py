from zope.interface import implements
from zope.component import adapts
from zope.location.interfaces import ILocation
from zope.traversing.api import getPath
from zope.globalrequest import getRequest
from zojax.cache.interfaces import IPurgePaths


class TraversablePurgePaths(object):
    """Default purge for Traversable-style objects
    """
    
    implements(IPurgePaths)
    adapts(ILocation)
    
    def __init__(self, context):
        self.context = context
        
    def getRelativePaths(self):
        return [getPath(self.context)]

    def getAbsolutePaths(self):
        return []