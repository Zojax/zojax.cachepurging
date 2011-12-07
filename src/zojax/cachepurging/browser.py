from StringIO import StringIO

from zope.component import getUtility
from zope.event import notify


from zojax.cachepurging.interfaces import IPurger
from zojax.cachepurging.interfaces import ICachePurgingConfiglet

from zojax.cache.purge import Purge

from zojax.cachepurging.utils import getPathsToPurge
from zojax.cachepurging.utils import getURLsToPurge
from zojax.cachepurging.utils import isCachePurgingEnabled

class QueuePurge(object):
    """Manually initiate a purge
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self):
        
        if not isCachePurgingEnabled():
            return 'Caching not enabled'
        
        notify(Purge(self.context))
        return 'Queued'

class PurgeImmediately(object):
    """Purge immediately
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self):
        
        if not isCachePurgingEnabled():
            return 'Caching not enabled'
        
        settings = getUtility(ICachePurgingConfiglet)
        
        purger = getUtility(IPurger)
        
        out = StringIO()
        
        for path in getPathsToPurge(self.context, self.request):
            for url in getURLsToPurge(path, settings.cachingProxies):
                status, xcache, xerror = purger.purgeSync(url)
                print >>out, "Purged", url, "Status", status, "X-Cache", xcache, "Error:", xerror
        
        return out.getvalue()

