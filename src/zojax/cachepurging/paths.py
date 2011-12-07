from zope.interface import implements
from zope.component import adapts
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.globalrequest import getRequest
from zojax.cache.interfaces import IPurgePaths

from zope.traversing.interfaces import ITraversable

class TraversablePurgePaths(object):
    """Default purge for OFS.Traversable-style objects
    """
    
    implements(IPurgePaths)
    adapts(ITraversable)
    
    def __init__(self, context):
        self.context = context
        
    def getRelativePaths(self):
        return [absoluteURL(self.context, getRequest())]
    
    def getAbsolutePaths(self):
        return []
