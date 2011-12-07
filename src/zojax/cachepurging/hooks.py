from zope.app.publication.interfaces import IEndRequestEvent
from zope.component import adapter, queryUtility, getUtility
from zope.annotation.interfaces import IAnnotations

from zope.globalrequest import getRequest

from zojax.cache.interfaces import IPurgeEvent


from zojax.cachepurging.interfaces import ICachePurgingConfiglet
from zojax.cachepurging.interfaces import IPurger

from zojax.cachepurging.utils import getPathsToPurge
from zojax.cachepurging.utils import isCachePurgingEnabled
from zojax.cachepurging.utils import getURLsToPurge

KEY = "zojax.cachepurging.urls"

@adapter(IPurgeEvent)
def queuePurge(event):
    """Find URLs to purge and queue them for later
    """
    
    request = getRequest()
    if request is None:
        return
    
    annotations = IAnnotations(request, None)
    if annotations is None:
        return
    
    if not isCachePurgingEnabled():
        return
    
    paths = annotations.setdefault(KEY, set())
    paths.update(getPathsToPurge(event.object, request))

@adapter(IEndRequestEvent)
def purge(event):
    """Asynchronously send PURGE requests
    """
    
    request = event.request
    
    annotations = IAnnotations(request, None)
    if annotations is None:
        return
    
    paths = annotations.get(KEY, None)
    if paths is None:
        return
    
    if not isCachePurgingEnabled():
        return
    
    purger = queryUtility(IPurger)
    if purger is None:
        return
    
    settings = getUtility(ICachePurgingConfiglet)
    for path in paths:
        for url in getURLsToPurge(path, settings.cachingProxies):
            purger.purgeAsync(url)
