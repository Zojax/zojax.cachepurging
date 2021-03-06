import unittest
import zope.component.testing

from zope.interface import implements
from zope.component import provideUtility
from zope.component import provideAdapter
from zope.component import adapts

from zojax.cache.interfaces import IPurgePaths

from zojax.cachepurging.interfaces import ICachePurgingConfiglet
from zojax.cachepurging.interfaces import IPurgePathRewriter

from zojax.cachepurging import utils

class FauxContext(object):
    pass

class FauxRequest(dict):
    pass

class TestIsCachingEnabled(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_no_registry(self):
        self.assertEquals(False, utils.isCachePurgingEnabled())

    def test_no_settings(self):
        registry = Registry()
        registry.registerInterface(ICachePurgingConfiglet)
        provideUtility(registry, IRegistry)
        self.assertEquals(False, utils.isCachePurgingEnabled())

    def test_disabled(self):
        registry = Registry()
        registry.registerInterface(ICachePurgingConfiglet)
        provideUtility(registry, IRegistry)
        
        settings = registry.forInterface(ICachePurgingConfiglet)
        settings.enabled = False
        settings.cachingProxies = ('http://localhost:1234',)
        
        self.assertEquals(False, utils.isCachePurgingEnabled())
        
    def test_no_proxies(self):
        registry = Registry()
        registry.registerInterface(ICachePurgingConfiglet)
        provideUtility(registry, IRegistry)
        
        settings = registry.forInterface(ICachePurgingConfiglet)
        settings.enabled = False
        
        settings.cachingProxies = None
        self.assertEquals(False, utils.isCachePurgingEnabled())
        
        settings.cachingProxies = ()
        self.assertEquals(False, utils.isCachePurgingEnabled())
    
    def test_enabled(self):
        registry = Registry()
        registry.registerInterface(ICachePurgingConfiglet)
        provideUtility(registry, IRegistry)
        
        settings = registry.forInterface(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        self.assertEquals(True, utils.isCachePurgingEnabled())
    
    def test_passed_registry(self):
        registry = Registry()
        registry.registerInterface(ICachePurgingConfiglet)
        settings = registry.forInterface(ICachePurgingConfiglet)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)
        
        self.assertEquals(False, utils.isCachePurgingEnabled())
        self.assertEquals(True, utils.isCachePurgingEnabled(registry))

class TestGetPathsToPurge(unittest.TestCase):
    
    def setUp(self):
        self.context = FauxContext()
        self.request = FauxRequest()
        
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_no_purge_paths(self):
        self.assertEquals([], list(utils.getPathsToPurge(self.context, self.request)))
    
    def test_empty_relative_paths(self):
        
        class FauxPurgePaths(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return []
        
            def getAbsolutePaths(self):
                return []
        
        provideAdapter(FauxPurgePaths, name="test1")
        
        self.assertEquals([], list(utils.getPathsToPurge(self.context, self.request)))
    
    def test_no_rewriter(self):
        class FauxPurgePaths(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo', '/bar']
        
            def getAbsolutePaths(self):
                return ['/baz']
        
        provideAdapter(FauxPurgePaths, name="test1")
        
        self.assertEquals(['/foo', '/bar', '/baz'],
            list(utils.getPathsToPurge(self.context, self.request)))
    
    def test_test_rewriter(self):
        class FauxPurgePaths(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo', '/bar']
        
            def getAbsolutePaths(self):
                return ['/baz']
        
        provideAdapter(FauxPurgePaths, name="test1")
        
        class DefaultRewriter(object):
            implements(IPurgePathRewriter)
            adapts(FauxRequest)
    
            def __init__(self, request):
                self.request = request
    
            def __call__(self, path):
                return ['/vhm1' + path, '/vhm2' + path]
        
        provideAdapter(DefaultRewriter)
        
        self.assertEquals(['/vhm1/foo', '/vhm2/foo',
                           '/vhm1/bar', '/vhm2/bar',
                           '/baz'],
            list(utils.getPathsToPurge(self.context, self.request)))
    
    def test_multiple_purge_paths(self):
        class FauxPurgePaths1(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo', '/bar']
        
            def getAbsolutePaths(self):
                return ['/baz']
        
        provideAdapter(FauxPurgePaths1, name="test1")
        
        class FauxPurgePaths2(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo/view']
        
            def getAbsolutePaths(self):
                return ['/quux']
        
        provideAdapter(FauxPurgePaths2, name="test2")
        
        class DefaultRewriter(object):
            implements(IPurgePathRewriter)
            adapts(FauxRequest)
    
            def __init__(self, request):
                self.request = request
    
            def __call__(self, path):
                return ['/vhm1' + path, '/vhm2' + path]
        
        provideAdapter(DefaultRewriter)
        
        self.assertEquals(['/vhm1/foo', '/vhm2/foo', '/vhm1/bar', '/vhm2/bar', '/baz',
                           '/vhm1/foo/view', '/vhm2/foo/view', '/quux'],
            list(utils.getPathsToPurge(self.context, self.request)))
    
    def test_rewriter_abort(self):
        class FauxPurgePaths1(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo', '/bar']
        
            def getAbsolutePaths(self):
                return ['/baz']
        
        provideAdapter(FauxPurgePaths1, name="test1")
        
        class FauxPurgePaths2(object):
            implements(IPurgePaths)
            adapts(FauxContext)
        
            def __init__(self, context):
                self.context = context
        
            def getRelativePaths(self):
                return ['/foo/view']
        
            def getAbsolutePaths(self):
                return ['/quux']
        
        provideAdapter(FauxPurgePaths2, name="test2")
        
        class DefaultRewriter(object):
            implements(IPurgePathRewriter)
            adapts(FauxRequest)
    
            def __init__(self, request):
                self.request = request
    
            def __call__(self, path):
                return []
        
        provideAdapter(DefaultRewriter)
        
        self.assertEquals(['/baz', '/quux'],
            list(utils.getPathsToPurge(self.context, self.request)))

class TestGetURLsToPurge(unittest.TestCase):
    
    def test_no_proxies(self):
        self.assertEquals([], list(utils.getURLsToPurge('/foo', [])))
    
    def test_absolute_path(self):
        self.assertEquals(['http://localhost:1234/foo/bar', 'http://localhost:2345/foo/bar'],
            list(utils.getURLsToPurge('/foo/bar', ['http://localhost:1234', 'http://localhost:2345/'])))
    
    def test_relative_path(self):
        self.assertEquals(['http://localhost:1234/foo/bar', 'http://localhost:2345/foo/bar'],
            list(utils.getURLsToPurge('foo/bar', ['http://localhost:1234', 'http://localhost:2345/'])))    
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
