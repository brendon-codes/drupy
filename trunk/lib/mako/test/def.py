from mako.template import Template
from mako import lookup
import unittest
from util import flatten_result, result_lines

class DefTest(unittest.TestCase):
    def test_def_noargs(self):
        template = Template("""
        
        ${mycomp()}
        
        <%def name="mycomp()">
            hello mycomp ${variable}
        </%def>
        
        """)
        assert template.render(variable='hi').strip() == """hello mycomp hi"""

    def test_def_blankargs(self):
        template = Template("""
        <%def name="mycomp()">
            hello mycomp ${variable}
        </%def>

        ${mycomp()}""")
        assert template.render(variable='hi').strip() == """hello mycomp hi"""

        
    def test_def_args(self):
        template = Template("""
        <%def name="mycomp(a, b)">
            hello mycomp ${variable}, ${a}, ${b}
        </%def>

        ${mycomp(5, 6)}""")
        assert template.render(variable='hi', a=5, b=6).strip() == """hello mycomp hi, 5, 6"""

    def test_inter_def(self):
        """test defs calling each other"""
        template = Template("""
        ${b()}

        <%def name="a()">\
        im a
        </%def>

        <%def name="b()">
        im b
        and heres a:  ${a()}
        </%def>

        <%def name="c()">
        im c
        </%def>
""")
        # check that "a" is declared in "b", but not in "c"
        assert "a" not in template.module.render_c.func_code.co_varnames
        assert "a" in template.module.render_b.func_code.co_varnames
        
        # then test output
        assert flatten_result(template.render()) == "im b and heres a: im a"

    def test_toplevel(self):
        """test calling a def from the top level"""
        template = Template("""
        
            this is the body
        
            <%def name="a()">
                this is a
            </%def>

            <%def name="b(x, y)">
                this is b, ${x} ${y}
            </%def>
                
        """)
        assert flatten_result(template.get_def("a").render()) == "this is a"
        assert flatten_result(template.get_def("b").render(x=10, y=15)) == "this is b, 10 15"
        assert flatten_result(template.get_def("body").render()) == "this is the body"
        
class ScopeTest(unittest.TestCase):
    """test scoping rules.  The key is, enclosing scope always takes precedence over contextual scope."""
    def test_scope_one(self):
        t = Template("""
        <%def name="a()">
            this is a, and y is ${y}
        </%def>

        ${a()}

        <%
            y = 7
        %>

        ${a()}

""")
        assert flatten_result(t.render(y=None)) == "this is a, and y is None this is a, and y is 7"

    def test_scope_two(self):
        t = Template("""
        y is ${y}

        <%
            y = 7
        %>

        y is ${y}
""")
        try:
            t.render(y=None)
            assert False
        except UnboundLocalError:
            assert True

    def test_scope_four(self):
        """test that variables are pulled from 'enclosing' scope before context."""
        t = Template("""
            <%
                x = 5
            %>
            <%def name="a()">
                this is a. x is ${x}.
            </%def>
            
            <%def name="b()">
                <%
                    x = 9
                %>
                this is b. x is ${x}.
                calling a. ${a()}
            </%def>
        
            ${b()}
""")
        assert flatten_result(t.render()) == "this is b. x is 9. calling a. this is a. x is 5."
    
    def test_scope_five(self):
        """test that variables are pulled from 'enclosing' scope before context."""
        # same as test four, but adds a scope around it.
        t = Template("""
            <%def name="enclosing()">
            <%
                x = 5
            %>
            <%def name="a()">
                this is a. x is ${x}.
            </%def>

            <%def name="b()">
                <%
                    x = 9
                %>
                this is b. x is ${x}.
                calling a. ${a()}
            </%def>

            ${b()}
            </%def>
            ${enclosing()}
""")
        assert flatten_result(t.render()) == "this is b. x is 9. calling a. this is a. x is 5."

    def test_scope_six(self):
        """test that the initial context counts as 'enclosing' scope, for plain defs"""
        t = Template("""

        <%def name="a()">
            a: x is ${x}
        </%def>

        <%def name="b()">
            <%
                x = 10
            %>
            b. x is ${x}.  ${a()}
        </%def>

        ${b()}
    """)
        assert flatten_result(t.render(x=5)) == "b. x is 10. a: x is 5"

    def test_scope_seven(self):
        """test that the initial context counts as 'enclosing' scope, for nested defs"""
        t = Template("""
        <%def name="enclosing()">
            <%def name="a()">
                a: x is ${x}
            </%def>

            <%def name="b()">
                <%
                    x = 10
                %>
                b. x is ${x}.  ${a()}
            </%def>

            ${b()}
        </%def>
        ${enclosing()}
    """)
        assert flatten_result(t.render(x=5)) == "b. x is 10. a: x is 5"

    def test_scope_eight(self):
        """test that the initial context counts as 'enclosing' scope, for nested defs"""
        t = Template("""
        <%def name="enclosing()">
            <%def name="a()">
                a: x is ${x}
            </%def>

            <%def name="b()">
                <%
                    x = 10
                %>
                
                b. x is ${x}.  ${a()}
            </%def>

            ${b()}
        </%def>
        ${enclosing()}
    """)
        assert flatten_result(t.render(x=5)) == "b. x is 10. a: x is 5"

    def test_scope_nine(self):
        """test that 'enclosing scope' doesnt get exported to other templates"""
        
        l = lookup.TemplateLookup()
        l.put_string('main', """
        <%
            x = 5
        %>
        this is main.  <%include file="secondary"/>
""")

        l.put_string('secondary', """
        this is secondary.  x is ${x}
""")

        assert flatten_result(l.get_template('main').render(x=2)) == "this is main. this is secondary. x is 2"
        
    def test_scope_ten(self):
        t = Template("""
            <%def name="a()">
                <%def name="b()">
                    <%
                        y = 19
                    %>
                    b/c: ${c()}
                    b/y: ${y}
                </%def>
                <%def name="c()">
                    c/y: ${y}
                </%def>

                <%
                    # we assign to "y".  but the 'enclosing scope' of "b" and "c" is from the "y" on the outside
                    y = 10
                %>
                a/y: ${y}
                a/b: ${b()}
            </%def>

            <%
                y = 7
            %>
            main/a: ${a()}
            main/y: ${y}
    """)
        assert flatten_result(t.render()) == "main/a: a/y: 10 a/b: b/c: c/y: 10 b/y: 19 main/y: 7"

    def test_scope_eleven(self):
        t = Template("""
            x is ${x}
            <%def name="a(x)">
                this is a, ${b()}
                <%def name="b()">
                    this is b, x is ${x}
                </%def>
            </%def>
            
            ${a(x=5)}
""")
        assert result_lines(t.render(x=10)) == [
            "x is 10",
            "this is a,", 
            "this is b, x is 5"
        ]

    def test_unbound_scope(self):
        t = Template("""
            <%
                y = 10
            %>
            <%def name="a()">
                y is: ${y}
                <%
                    # should raise error ?
                    y = 15
                %>
                y is ${y}
            </%def>
            ${a()}
""")
        try:
            print t.render()
            assert False
        except UnboundLocalError:
            assert True

    def test_unbound_scope_two(self):
        t = Template("""
            <%def name="enclosing()">
            <%
                y = 10
            %>
            <%def name="a()">
                y is: ${y}
                <%
                    # should raise error ?
                    y = 15
                %>
                y is ${y}
            </%def>
            ${a()}
            </%def>
            ${enclosing()}
""")
        try:
            print t.render()
            assert False
        except UnboundLocalError:
            assert True

    def test_canget_kwargs(self):
        """test that arguments passed to the body() function are accessible by top-level defs"""
        l = lookup.TemplateLookup()
        l.put_string("base", """
        
        ${next.body(x=12)}
        
        """)
        
        l.put_string("main", """
            <%inherit file="base"/>
            <%page args="x"/>
            this is main.  x is ${x}
            
            ${a()}
            
            <%def name="a(**args)">
                this is a, x is ${x}
            </%def>
        """)
        
        # test via inheritance
        #print l.get_template("main").code
        assert result_lines(l.get_template("main").render()) == [
            "this is main. x is 12",
            "this is a, x is 12"
        ]

        l.put_string("another", """
            <%namespace name="ns" file="main"/>
            
            ${ns.body(x=15)}
        """)
        # test via namespace
        assert result_lines(l.get_template("another").render()) == [
            "this is main. x is 15",
            "this is a, x is 15"
        ]

class NestedDefTest(unittest.TestCase):
    def test_nested_def(self):
        t = Template("""

        ${hi()}
        
        <%def name="hi()">
            hey, im hi.
            and heres ${foo()}, ${bar()}
            
            <%def name="foo()">
                this is foo
            </%def>
            
            <%def name="bar()">
                this is bar
            </%def>
        </%def>
""")
        assert flatten_result(t.render()) == "hey, im hi. and heres this is foo , this is bar"

    def test_nested_2(self):
        t = Template("""
            x is ${x}
            <%def name="a()">
                this is a, x is ${x}
                ${b()}
                <%def name="b()">
                    this is b: ${x}
                </%def>
            </%def>
            ${a()}
""")
        
        assert flatten_result(t.render(x=10)) == "x is 10 this is a, x is 10 this is b: 10"
        
    def test_nested_with_args(self):
        t = Template("""
        ${a()}
        <%def name="a()">
            <%def name="b(x, y=2)">
                b x is ${x} y is ${y}
            </%def>
            a ${b(5)}
        </%def>
""")
        assert flatten_result(t.render()) == "a b x is 5 y is 2"
        
    def test_nested_def_2(self):
        template = Template("""
        ${a()}
        <%def name="a()">
            <%def name="b()">
                <%def name="c()">
                    comp c
                </%def>
                ${c()}
            </%def>
            ${b()}
        </%def>
""")
        assert flatten_result(template.render()) == "comp c"

    def test_nested_nested_def(self):
        t = Template("""
        
        ${a()}
        <%def name="a()">
            a
            <%def name="b1()">
                a_b1
            </%def>
            <%def name="b2()">
                a_b2 ${c1()}
                <%def name="c1()">
                    a_b2_c1
                </%def>
            </%def>
            <%def name="b3()">
                a_b3 ${c1()}
                <%def name="c1()">
                    a_b3_c1 heres x: ${x}
                    <%
                        y = 7
                    %>
                    y is ${y}
                </%def>
                <%def name="c2()">
                    a_b3_c2
                    y is ${y}
                    c1 is ${c1()}
                </%def>
                ${c2()}
            </%def>
            
            ${b1()} ${b2()}  ${b3()}
        </%def>
""")
        assert flatten_result(t.render(x=5, y=None)) == "a a_b1 a_b2 a_b2_c1 a_b3 a_b3_c1 heres x: 5 y is 7 a_b3_c2 y is None c1 is a_b3_c1 heres x: 5 y is 7"
    
    def test_nested_nested_def_2(self):
        t = Template("""
        <%def name="a()">
            this is a ${b()}
            <%def name="b()">
                this is b
                ${c()}
            </%def>
            
            <%def name="c()">
                this is c
            </%def>
        </%def>
        ${a()}
""" )
        assert flatten_result(t.render()) == "this is a this is b this is c"

    def test_outer_scope(self):
        t = Template("""
        <%def name="a()">
            a: x is ${x}
        </%def>

        <%def name="b()">
            <%def name="c()">
            <%
                x = 10
            %>
            c. x is ${x}.  ${a()}
            </%def>
            
            b. ${c()}
        </%def>

        ${b()}
        
        x is ${x}
""")
        assert flatten_result(t.render(x=5)) == "b. c. x is 10. a: x is 5 x is 5"
            
class ExceptionTest(unittest.TestCase):
    def test_raise(self):
        template = Template("""
            <%
                raise Exception("this is a test")
            %>
    """, format_exceptions=False)
        try:
            template.render()
            assert False
        except Exception, e:
            assert str(e) == "this is a test"
    def test_handler(self):
        def handle(context, error):
            context.write("error message is " + str(error))
            return True
            
        template = Template("""
            <%
                raise Exception("this is a test")
            %>
    """, error_handler=handle)
        assert template.render().strip() == """error message is this is a test"""
        

if __name__ == '__main__':
    unittest.main()
