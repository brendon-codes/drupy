# -*- coding: utf-8 -*-
import sys
import unittest

from mako import exceptions
from mako.template import Template

class ExceptionsTest(unittest.TestCase):
    def test_html_error_template(self):
        """test the html_error_template"""
        code = """
% i = 0
"""
        try:
            template = Template(code)
            template.render()
        except exceptions.CompileException, ce:
            html_error = exceptions.html_error_template().render()
            assert ("CompileException: Fragment 'i = 0' is not a partial "
                    "control statement") in html_error
            assert '<style>' in html_error
            assert '</style>' in html_error
            html_error_stripped = html_error.strip()
            assert html_error_stripped.startswith('<html>')
            assert html_error_stripped.endswith('</html>')

            not_full = exceptions.html_error_template().render(full=False)
            assert '<html>' not in not_full
            assert '</html>' not in not_full
            assert '<style>' in not_full
            assert '</style>' in not_full

            no_css = exceptions.html_error_template().render(css=False)
            assert '<style>' not in no_css
            assert '</style>' not in no_css
        else:
            assert False, ("This function should trigger a CompileException, "
                           "but didn't")

    def test_utf8_html_error_template(self):
        """test the html_error_template with a Template containing utf8 chars"""
        code = """# -*- coding: utf-8 -*-
% if 2 == 2: /an error
${u'привет'}
% endif
"""
        try:
            template = Template(code)
            template.render()
        except exceptions.CompileException, ce:
            html_error = exceptions.html_error_template().render()
            assert ("CompileException: Fragment 'if 2 == 2: /an "
                    "error' is not a partial control "
                    "statement at line: 2 char: 1") in html_error
            assert u"3 ${u'привет'}".encode(sys.getdefaultencoding(),
                                            'htmlentityreplace') in html_error
        else:
            assert False, ("This function should trigger a CompileException, "
                           "but didn't")
            
if __name__ == '__main__':
    unittest.main()
