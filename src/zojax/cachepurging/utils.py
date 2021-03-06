from zope.component import queryUtility, getUtility
from zope.component import getAdapters

from zojax.cache.interfaces import IPurgePaths


from zojax.cachepurging.interfaces import ICachePurgingConfiglet
from zojax.cachepurging.interfaces import IPurgePathRewriter

def isCachePurgingEnabled(context=None):
    """Return True if caching is enabled
    """
    settings = getUtility(ICachePurgingConfiglet, context=context)
    return (settings.enabled and bool(settings.cachingProxies))

def getPathsToPurge(context, request):
    """Given the current request and an object, look up paths to purge for
    the object and yield them one by one. An IPurgePathRewriter adapter may
    be used to rewrite the paths.
    """
    
    rewriter = IPurgePathRewriter(request, None)
    
    for name, pathProvider in getAdapters((context,), IPurgePaths):
        # add relative paths, which are rewritten
        relativePaths = pathProvider.getRelativePaths()
        if relativePaths:
            for relativePath in relativePaths:
                if rewriter is None:
                    yield relativePath
                else:
                    rewrittenPaths = rewriter(relativePath) or [] # None -> []
                    for rewrittenPath in rewrittenPaths:
                        yield rewrittenPath
        
        # add absoute paths, which are not
        absolutePaths = pathProvider.getAbsolutePaths()
        if absolutePaths:
            for absolutePath in absolutePaths:
                yield absolutePath

def getURLsToPurge(path, proxies):
    """Yield full purge URLs for a given path, taking the caching proxies
    listed in the registry into account.
    """
    
    if not path.startswith('/'):
        path = '/' + path
    
    for proxy in proxies:
        if proxy.endswith('/'):
            proxy = proxy[:-1]
        yield proxy + path
