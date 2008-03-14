"""loads Markdown files, converts each one to HTML and parses the HTML into an ElementTree structure.
The collection of ElementTrees are further parsed to generate a table of contents structure, and are  
 manipulated to replace various markdown-generated HTML with specific Mako tags before being written
 to Mako templates, which then re-access the table of contents structure at runtime.

Much thanks to Alexey Shamrin, who came up with the original idea and did all the heavy Markdown/Elementtree 
lifting for this module."""
import sys, re, os
from toc import TOCElement

try:
    import elementtree.ElementTree as et
except:
    raise "This module requires ElementTree to run (http://effbot.org/zone/element-index.htm)"

import markdown

def dump_tree(elem, stream):
    if elem.tag.startswith('MAKO:'):
        dump_mako_tag(elem, stream)
    else:
        if elem.tag != 'html':
            if len(elem.attrib):
                stream.write("<%s %s>" % (elem.tag, " ".join(["%s=%s" % (key, repr(val)) for key, val in elem.attrib.iteritems()])))
            else:
                stream.write("<%s>" % elem.tag)
        if elem.text:
            stream.write(elem.text)
        for child in elem:
            dump_tree(child, stream)
            if child.tail:
                stream.write(child.tail)
        stream.write("</%s>" % elem.tag)

def dump_mako_tag(elem, stream):
    tag = elem.tag[5:]
    params = ','.join(['%s=%s' % i for i in elem.items()])
    stream.write('<%%call expr="%s(%s)">' % (tag, params))
    if elem.text:
        stream.write(elem.text)
    for n in elem:
        dump_tree(n, stream)
        if n.tail:
            stream.write(n.tail)
    stream.write("</%call>")

def create_toc(filename, tree, tocroot):
    title = [None]
    current = [tocroot]
    level = [0]
    def process(tree):
        while True:
            i = find_header_index(tree)
            if i is None:
                return
            node = tree[i]
            taglevel = int(node.tag[1])
            start, end = i, end_of_header(tree, taglevel, i+1)
            content = tree[start+1:end]
            description = node.text.strip()
            if title[0] is None:
                title[0] = description
            name = node.get('name')
            if name is None:
                name = description.split()[0].lower()
            
            taglevel = node.tag[1]
            if taglevel > level[0]:
                current[0] = TOCElement(filename, name, description, current[0])
            elif taglevel == level[0]:
                current[0] = TOCElement(filename, name, description, current[0].parent)
            else:
                current[0] = TOCElement(filename, name, description, current[0].parent.parent)

            level[0] = taglevel

            tag = et.Element("MAKO:formatting.section", path=repr(current[0].path), paged='paged', extension='extension', toc='toc')
            tag.text = (node.tail or "") + '\n'
            tag.tail = '\n'
            tag[:] = content
            tree[start:end] = [tag]

            process(tag)

    process(tree)
    return (title[0], tocroot.get_by_file(filename))

def index(parent, item):
    for n, i in enumerate(parent):
        if i is item:
            return n

def find_header_index(tree):
    for i, node in enumerate(tree):
        if is_header(node):
            return i

def is_header(node):
    t = node.tag
    return (isinstance(t, str) and len(t) == 2 and t[0] == 'h' 
            and t[1] in '123456789')

def end_of_header(tree, level, start):
    for i, node in enumerate(tree[start:]):
        if is_header(node) and int(node.tag[1]) <= level:
            return start + i
    return len(tree)

def process_rel_href(tree):
    parent = get_parent_map(tree)
    for a in tree.findall('.//a'):
        m = re.match(r'(bold)?rel\:(.+)', a.get('href'))
        if m:
            (bold, path) = m.group(1,2)
            text = a.text
            if text == path:
                tag = et.Element("MAKO:nav.toclink", path=repr(path), extension='extension', paged='paged', toc='toc')
            else:
                tag = et.Element("MAKO:nav.toclink", path=repr(path), description=repr(text), extension='extension', paged='paged', toc='toc')
            a_parent = parent[a]
            if bold:
                bold = et.Element('strong')
                bold.tail = a.tail
                bold.append(tag)
                a_parent[index(a_parent, a)] = bold
            else:
                tag.tail = a.tail
                a_parent[index(a_parent, a)] = tag

def replace_pre_with_mako(tree):
    parents = get_parent_map(tree)

    for precode in tree.findall('.//pre/code'):
        reg = re.compile(r'\{(python|mako|html|ini)(?: title="(.*?)"){0,1}\}(.*)', re.S)
        m = reg.match(precode[0].text.lstrip())
        if m:
            code = m.group(1)
            title = m.group(2)
            precode[0].text = m.group(3)
        else:
            code = title = None
            
        tag = et.Element("MAKO:formatting.code")
        if code:
            tag.attrib["syntaxtype"] = repr(code)
        if title:
            tag.attrib["title"] = repr(title)
        tag.text = precode.text
        [tag.append(x) for x in precode]
        pre = parents[precode]
        tag.tail = pre.tail
        
        pre_parent = parents[pre]
        pre_parent[reverse_parent(pre_parent, pre)] = tag
        
def safety_code(tree):
    parents = get_parent_map(tree)
    for code in tree.findall('.//code'):
        tag = et.Element('%text')
        if parents[code].tag != 'pre':
            tag.attrib["filter"] = "h"
        tag.text = code.text
        code.append(tag)
        code.text = ""

def reverse_parent(parent, item):
    for n, i in enumerate(parent):
        if i is item:
            return n

def get_parent_map(tree):
    return dict([(c, p) for p in tree.getiterator() for c in p])

def header(toc, title, filename):
    return """# -*- coding: utf-8 -*-
<%%inherit file="content_layout.html"/>
<%%page args="toc, extension, paged"/>
<%%namespace  name="formatting" file="formatting.html"/>
<%%namespace  name="nav" file="nav.html"/>
<%%def name="title()">%s - %s</%%def>
<%%!
    filename = '%s'
%%>
## This file is generated.  Edit the .txt files instead of this one.
""" % (toc.root.doctitle, title, filename)
  
class utf8stream(object):
    def __init__(self, stream):
        self.stream = stream
    def write(self, str):
        self.stream.write(str.encode('utf8'))
        
def parse_markdown_files(toc, files):
    for inname in files:
        infile = 'content/%s.txt' % inname
        if not os.access(infile, os.F_OK):
            continue
        html = markdown.markdown(file(infile).read())
        tree = et.fromstring("<html>" + html + "</html>")
        (title, toc_element) = create_toc(inname, tree, toc)
        safety_code(tree)
        replace_pre_with_mako(tree)
        process_rel_href(tree)
        outname = 'output/%s.html' % inname
        print infile, '->', outname
        outfile = utf8stream(file(outname, 'w'))
        outfile.write(header(toc, title, inname))
        dump_tree(tree, outfile)
    
    
