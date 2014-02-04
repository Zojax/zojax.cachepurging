import unittest
from zope.app.publication.interfaces import EndRequestEvent
import zope.component.testing

from zope.interface import implements
from zope.interface import alsoProvides

from zope.component import adapts
from zope.component import provideUtility, getUtility
from zope.component import provideAdapter
from zope.component import provideHandler
from zope.app.publication.interfaces import EndRequestEvent

from zope.event import notify

from zope.annotation.attribute import AttributeAnnotations
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable

from zope.globalrequest import setRequest

from zojax.cache.interfaces import IPurgePaths
from zojax.cache.purge import Purge

from zojax.cachepurging.interfaces import IPurger, ICachePurgingConfiglet
from zojax.cachepurging.configlet import CachePurgingConfiglet

from zojax.cachepurging.hooks import queuePurge, purge


class FauxContext(dict):
    pass

class FauxRequest(dict):
    pass

class TestQueueHandler(unittest.TestCase):
    
    def setUp(self):
        provideAdapter(AttributeAnnotations)

        provideHandler(queuePurge)
        
    def tearDown(self):
        zope.component.testing.tearDown()
        setRequest(None)
    
    def test_no_request(self):
        context = FauxContext()
        
        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)
        
        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        class FauxPurgePaths(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo', '/bar']
        
            def getAbsolutePaths(self):
                return []
        
        provideAdapter(FauxPurgePaths, name="test1")
        
        try:
            notify(Purge(context))
        except:
            self.fail()
    
    def test_request_not_annotatable(self):
        context = FauxContext()
        
        request = FauxRequest()
        setRequest(request)

        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        class FauxPurgePaths(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo', '/bar']
        
            def getAbsolutePaths(self):
                return []
        
        provideAdapter(FauxPurgePaths, name="test1")
        
        try:
            notify(Purge(context))
        except:
            self.fail()
        
    def test_caching_disabled(self):
        context = FauxContext()
        
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)
        setRequest(request)

        configlet= CachePurgingConfiglet()
        
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = False
        settings.cachingProxies = ('http://localhost:1234',)
        
        class FauxPurgePaths(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo', '/bar']
        
            def getAbsolutePaths(self):
                return []
        
        provideAdapter(FauxPurgePaths, name="test1")
        
        notify(Purge(context))
        
        self.assertEquals({}, dict(IAnnotations(request)))
    
    def test_enabled_no_paths(self):
        context = FauxContext()
        
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)
        setRequest(request)

        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        notify(Purge(context))
        
        self.assertEquals({'zojax.cachepurging.urls': set()},
                          dict(IAnnotations(request)))

    def test_enabled(self):
        context = FauxContext()
        
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)
        setRequest(request)

        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        class FauxPurgePaths(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo', '/bar']
        
            def getAbsolutePaths(self):
                return []
        
        provideAdapter(FauxPurgePaths, name="test1")
        
        notify(Purge(context))
        
        self.assertEquals({'zojax.cachepurging.urls': set(['/foo', '/bar'])},
                          dict(IAnnotations(request)))

class TestPurgeHandler(unittest.TestCase):
    
    def setUp(self):
        provideAdapter(AttributeAnnotations)

        provideHandler(purge)
        
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_request_not_annotatable(self):
        request = FauxRequest()

        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        class FauxPurger(object):
            implements(IPurger)
            
            def __init__(self):
                self.purged = []
            
            def purgeAsync(self, url, httpVerb='PURGE'):
                self.purged.append(url)
        
        purger = FauxPurger()
        provideUtility(purger)
        
        notify(EndRequestEvent(None, request))
        
        self.assertEquals([], purger.purged)
    
    def test_no_path_key(self):
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)

        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        class FauxPurger(object):
            implements(IPurger)
            
            def __init__(self):
                self.purged = []
            
            def purgeAsync(self, url, httpVerb='PURGE'):
                self.purged.append(url)
        
        purger = FauxPurger()
        provideUtility(purger)
        
        notify(EndRequestEvent(None,request))
        
        self.assertEquals([], purger.purged)

    def test_no_paths(self):
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)
        
        IAnnotations(request)['zojax.cachepurging.urls'] = set()

        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        class FauxPurger(object):
            implements(IPurger)
            
            def __init__(self):
                self.purged = []
            
            def purgeAsync(self, url, httpVerb='PURGE'):
                self.purged.append(url)
        
        purger = FauxPurger()
        provideUtility(purger)
        
        notify(EndRequestEvent(None, request))
        
        self.assertEquals([], purger.purged)
    
    def test_caching_disabled(self):
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)
        
        IAnnotations(request)['zojax.cachepurging.urls'] = set(['/foo', '/bar'])

        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = False
        settings.cachingProxies = ('http://localhost:1234',)
        
        class FauxPurger(object):
            implements(IPurger)
            
            def __init__(self):
                self.purged = []
            
            def purgeAsync(self, url, httpVerb='PURGE'):
                self.purged.append(url)
        
        purger = FauxPurger()
        provideUtility(purger)
        
        notify(EndRequestEvent(None, request))
        
        self.assertEquals([], purger.purged)
    
    def test_no_purger(self):
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)
        
        IAnnotations(request)['zojax.cachepurging.urls'] = set(['/foo', '/bar'])

        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        try:
            notify(EndRequestEvent(None, request))
        except:
            self.fail()
    
    def test_purge(self):
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)
        
        IAnnotations(request)['zojax.cachepurging.urls'] = set(['/foo', '/bar'])

        configlet= CachePurgingConfiglet()
        provideUtility(configlet, ICachePurgingConfiglet)

        settings = getUtility(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        class FauxPurger(object):
            implements(IPurger)
            
            def __init__(self):
                self.purged = []
            
            def purgeAsync(self, url, httpVerb='PURGE'):
                self.purged.append(url)
        
        purger = FauxPurger()
        provideUtility(purger)
        
        notify(EndRequestEvent(None, request))
        
        self.assertEquals(['http://localhost:1234/foo', 'http://localhost:1234/bar'],
                          purger.purged)
        
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

