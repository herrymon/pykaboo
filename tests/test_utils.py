import unittest
from pykaboo.pyka import expires_in

class TestUtilityFunctions(unittest.TestCase):
    def test_expires_in(self):
        from time import gmtime, strftime, mktime
        t = (2010, 2, 4, 8, 0, 0, 3, 35, 0)
        base = mktime(t)

        expected = "Thu, 04-Feb-2010 00:00:01 GMT"
        self.assertEqual(expected, expires_in(sec=1, time=base))
        expected = "Thu, 04-Feb-2010 00:01:00 GMT"
        self.assertEqual(expected, expires_in(min=1, time=base))
        expected = "Thu, 04-Feb-2010 01:00:00 GMT"
        self.assertEqual(expected, expires_in(hour=1, time=base))
        expected = "Fri, 05-Feb-2010 00:00:00 GMT"
        self.assertEqual(expected, expires_in(day=1, time=base))

        expected = "Fri, 05-Feb-2010 01:01:01 GMT"
        self.assertEqual(expected, expires_in(day=1, hour=1, min=1, sec=1, time=base))

