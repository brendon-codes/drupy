from mako.template import Template
from mako import lookup
import unittest, os
from util import result_lines

if not os.access('./test_htdocs', os.F_OK):
    os.mkdir('./test_htdocs')

class MockCache(object):
    def __init__(self, realcache):
        self.realcache = realcache
    def get(self, key, **kwargs):
        self.key = key
        self.kwargs = kwargs.copy()
        self.kwargs.pop('createfunc', None)
        return self.realcache.get(key, **kwargs)
    
class CacheTest(unittest.TestCase):
    def test_def(self):
        t = Template("""
        <%!
            callcount = [0]
        %>
        <%def name="foo()" cached="True">
            this is foo
            <%
            callcount[0] += 1
            %>
        </%def>
    
        ${foo()}
        ${foo()}
        ${foo()}
        callcount: ${callcount}
""")
        m = self._install_mock_cache(t)
        assert result_lines(t.render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        assert m.kwargs == {}

    def test_nested_def(self):
        t = Template("""
        <%!
            callcount = [0]
        %>
        <%def name="foo()">
            <%def name="bar()" cached="True">
                this is foo
                <%
                callcount[0] += 1
                %>
            </%def>
            ${bar()}
        </%def>

        ${foo()}
        ${foo()}
        ${foo()}
        callcount: ${callcount}
""")
        m = self._install_mock_cache(t)
        assert result_lines(t.render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        assert m.kwargs == {}
        
    def test_page(self):
        t = Template("""
        <%!
            callcount = [0]
        %>
        <%page cached="True"/>
        this is foo
        <%
        callcount[0] += 1
        %>
        callcount: ${callcount}
""")
        m = self._install_mock_cache(t)
        t.render()
        t.render()
        assert result_lines(t.render()) == [
            "this is foo",
            "callcount: [1]"
        ]
        assert m.kwargs == {}
        
    def test_fileargs_implicit(self):
        l = lookup.TemplateLookup(module_directory='./test_htdocs')
        l.put_string("test","""
                <%!
                    callcount = [0]
                %>
                <%def name="foo()" cached="True" cache_type='dbm'>
                    this is foo
                    <%
                    callcount[0] += 1
                    %>
                </%def>

                ${foo()}
                ${foo()}
                ${foo()}
                callcount: ${callcount}
        """)
        
        m = self._install_mock_cache(l.get_template('test'))
        assert result_lines(l.get_template('test').render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        assert m.kwargs == {'type':'dbm', 'data_dir':'./test_htdocs'}
        
    def test_fileargs_deftag(self):
        t = Template("""
        <%!
            callcount = [0]
        %>
        <%def name="foo()" cached="True" cache_type='file' cache_dir='./test_htdocs'>
            this is foo
            <%
            callcount[0] += 1
            %>
        </%def>

        ${foo()}
        ${foo()}
        ${foo()}
        callcount: ${callcount}
""")
        m = self._install_mock_cache(t)
        assert result_lines(t.render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        assert m.kwargs == {'type':'file','data_dir':'./test_htdocs'}

    def test_fileargs_pagetag(self):
        t = Template("""
        <%page cache_dir='./test_htdocs' cache_type='dbm'/>
        <%!
            callcount = [0]
        %>
        <%def name="foo()" cached="True">
            this is foo
            <%
            callcount[0] += 1
            %>
        </%def>

        ${foo()}
        ${foo()}
        ${foo()}
        callcount: ${callcount}
""")
        m = self._install_mock_cache(t)
        assert result_lines(t.render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        assert m.kwargs == {'data_dir':'./test_htdocs', 'type':'dbm'}

    def test_args_complete(self):
        t = Template("""
        <%def name="foo()" cached="True" cache_timeout="30" cache_dir="./test_htdocs" cache_type="file" cache_key='somekey'>
            this is foo
        </%def>

        ${foo()}
""")
        m = self._install_mock_cache(t)
        t.render()
        assert m.kwargs == {'data_dir':'./test_htdocs', 'type':'file', 'expiretime':30}
        
        t2 = Template("""
        <%page cached="True" cache_timeout="30" cache_dir="./test_htdocs" cache_type="file" cache_key='somekey'/>
        hi
        """)
        m = self._install_mock_cache(t2)
        t2.render()
        assert m.kwargs == {'data_dir':'./test_htdocs', 'type':'file', 'expiretime':30}

    def test_fileargs_lookup(self):
        l = lookup.TemplateLookup(cache_dir='./test_htdocs', cache_type='file')
        l.put_string("test","""
                <%!
                    callcount = [0]
                %>
                <%def name="foo()" cached="True">
                    this is foo
                    <%
                    callcount[0] += 1
                    %>
                </%def>

                ${foo()}
                ${foo()}
                ${foo()}
                callcount: ${callcount}
        """)
    
        t = l.get_template('test')
        m = self._install_mock_cache(t)
        assert result_lines(l.get_template('test').render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        assert m.kwargs == {'data_dir':'./test_htdocs', 'type':'file'}
    
    def test_buffered(self):
        t = Template("""
        <%!
            def a(text):
                return "this is a " + text.strip()
        %>
        ${foo()}
        ${foo()}
        <%def name="foo()" cached="True" buffered="True">
            this is a test
        </%def>
        """, buffer_filters=["a"])
        assert result_lines(t.render()) == ["this is a this is a test", "this is a this is a test"]
        
    def _install_mock_cache(self, template):
        m = MockCache(template.module._template_cache)
        template.module._template_cache = m
        return m
            
if __name__ == '__main__':
    unittest.main()
