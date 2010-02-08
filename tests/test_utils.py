import unittest
from pykaboo.pyka import expires_in, mako_render
import os

class TestUtilityFunctions(unittest.TestCase):

    def setUp(self):
        self.template_path = os.path.realpath(os.path.dirname(__file__))
        self.module_path = self.template_path
        self.template = 'template.html'
        self.header = 'template.header.html'
        self.html_header = "<h1>header</h1>"
        self.html = """<html>
        <head><title>sample file</title></head>
        <body>
        <%include file="{0}"/>
        ${{body}}
        </body>
        </html>""".format(self.header)

        f = open(os.path.join(self.template_path, self.template), 'w')
        f.write(self.html)
        f.close()

        f = open(os.path.join(self.template_path, self.header), 'w')
        f.write(self.html_header)
        f.close()

    def tearDown(self):
        for tmp_file in (self.template, self.header):
            os.remove(os.path.join(self.template_path, tmp_file))
            os.remove(os.path.join(self.template_path, tmp_file + '.py'))
            os.remove(os.path.join(self.template_path, tmp_file + '.pyc'))

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

    def test_mako_render(self):
        bdy = "<p>body</p>"
        html_output = """<html>
        <head><title>sample file</title></head>
        <body>
        {0}
        {1}
        </body>
        </html>""".format(self.html_header, bdy)
        actual = mako_render(self.template, 
                            template_paths=[self.template_path], 
                            module_path=self.module_path, 
                            body=bdy)
        self.assertEquals(html_output, actual)
