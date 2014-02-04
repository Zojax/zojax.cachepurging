import unittest

from zope.interface import implements
from zope.traversing.interfaces import ITraversable, IPhysicallyLocatable
from zojax.cachepurging.paths import TraversablePurgePaths

class FauxTraversable(object):
    implements(ITraversable, IPhysicallyLocatable)

    def getPath(self):
        return '/foo'

class TestTraversablePaths(unittest.TestCase):

    def test_traversable_paths(self):

        context = FauxTraversable()
        paths = TraversablePurgePaths(context)

        self.assertEquals(['/foo'], paths.getRelativePaths())
        self.assertEquals([], paths.getAbsolutePaths())
        
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
