# -----------------------------------------------------------------------------
# amara3.uxml.tree
#
# Basic tree implementation for MicroXML
# 
# -----------------------------------------------------------------------------

#See also: http://www.w3.org/community/microxml/wiki/MicroLarkApi

from amara3.uxml.parser import parse, parser, parsefrags, event
from amara3.util import coroutine


class node(object):
    def xml_encode(self):
        raise ImplementationError

    def xml_write(self):
        raise ImplementationError


class element(node):
    def __init__(self, name, attrs=None, parent=None):#, ancestors=None):
        self.xml_name = name
        self.xml_attributes = attrs or {}
        self.xml_parent = parent
        self.xml_children = []
        #self.xml_ancestors = ancestors or []
        return

    def xml_encode(self):
        strbits = ['<', self.xml_name]
        for aname, aval in self.xml_attrs.items():
            strbits.extend([' ', aname, '="', aval, '"'])
        strbits.append('>')
        for child in self.xml_children:
            if isinstance(child, element):
                strbits.append(child.xml_encode())
            else:
                strbits.append(child)
        strbits.extend(['</', self.xml_name, '>'])
        return ''.join(strbits)

    @property
    def xml_value(self):
        return ''.join(map(lambda x: x.xml_value, self.xml_children))

    def __repr__(self):
        return u'<uxml.element ({0}) "{1}" with {2} children>'.format(hash(self), self.xml_name, len(self.xml_children))

    #def unparse(self):
    #    return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'

class text(node, str):
    def __new__(cls, value, parent):
        self = super(text, cls).__new__(cls, value)
        self.xml_parent = parent
        return self

    def __repr__(self):
        return u'<uxml.text "' + str(self)[:10] + '"...>'

    def xml_encode(self):
        return str(self)

    @property
    def xml_value(self):
        return str(self)

    #def unparse(self):
    #    return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'


class treebuilder(object):
    def __init__(self):
        self._root = None
        self._parent = None

    @coroutine
    def _handler(self):
        while True:
            ev = yield
            if ev[0] == event.start_element:
                new_element = element(ev[1], ev[2], self._parent)
                if self._parent: self._parent.xml_children.append(new_element)
                self._parent = new_element
                if not self._root: self._root = new_element
            elif ev[0] == event.characters:
                new_text = text(ev[1], self._parent)
                if self._parent: self._parent.xml_children.append(new_text)
            elif ev[0] == event.end_element:
                if self._parent.xml_parent:
                    self._parent = self._parent.xml_parent
        return

    def parse(self, doc):
        h = self._handler()
        p = parser(h)
        p.send((doc, False))
        p.send(('', True)) #Wrap it up
        return self._root


def name_test(name):
    def _name_test(ev):
        return ev[0] == event.start_element and ev[1] == name
    return _name_test


def elem_test():
    def _elem_test(ev):
        return ev[0] == event.start_element
    return _elem_test


'''
from amara3.uxml import tree
from amara3.util import coroutine
@coroutine
def sink(accumulator):
    while True:
        e = yield
        accumulator.append(e.xml_value)

values = []
ts = tree.treesequence(('a', 'b'), sink(values))
ts.parse('<a><b>1</b><b>2</b><b>3</b></a>')
values
values = []
ts = tree.treesequence(('a', '*'), sink(values))
ts.parse('<a><b>1</b><c>2</c><d>3</d></a>')
values
'''

class treesequence(object):
    '''
    #tb = tree.treebuilder()
    >>> from amara3.uxml import tree
    >>> from amara3.util import coroutine
    >>> @coroutine
    ... def sink(accumulator):
    ...     while True:
    ...         e = yield
    ...         accumulator.append(e.xml_value)
    ...
    >>> values = []
    >>> ts = tree.treesequence(('a', 'b'), sink(values))
    >>> ts.parse('<a><b>1</b><b>2</b><b>3</b></a>')
    >>> values
    ['1', '2', '3']
    '''
    def __init__(self, pattern, sink):
        self._root = None
        self._parent = None
        self._pattern = pattern
        self._evstack = []
        self._building_depth = 0
        self._sink = sink
        self._prep_pattern()
        self._current = None

    def _prep_pattern(self):
        prepped = []
        for depth, stage in enumerate(self._pattern):
            if isinstance(stage, str):
                if stage == '*':
                    prepped.append(elem_test())
                else:
                    prepped.append(name_test(stage))
            elif isinstance(stage, tuple):
                new_tuple = tuple(( name_test(substage) if isinstance(stage, str) else substage for substage in stage ))
                prepped.append(new_tuple)
            else:
                prepped.append()
        self._pattern = prepped
        return

    def _match_state(self):
        for depth, teststage in enumerate(self._pattern):
            #No match if the pattern isn't completed
            if depth >= len(self._evstack): return False
            if isinstance(teststage, tuple):
                if not any( (substage(self._evstack[depth]) for substage in teststage) ):
                   break 
            elif not teststage(self._evstack[depth]):
                break
        else:
            #Got through the full pattern successfully. Matched.
            return True
        return False

    @coroutine
    def _handler(self):
        while True:
            ev = yield
            if ev[0] == event.start_element:
                self._evstack.append(ev)
                #Keep track of the depth while we're building elements. When we ge back to 0 depth, we're done for this subtree
                if self._building_depth:
                    self._building_depth += 1
                elif self._match_state():
                    self._building_depth = 1
                if self._building_depth:
                    new_element = element(ev[1], ev[2], self._parent)
                    if self._parent: self._parent.xml_children.append(new_element)
                    self._parent = new_element
                    if not self._root: self._root = new_element
            elif ev[0] == event.characters:
                if self._building_depth:
                    new_text = text(ev[1], self._parent)
                    if self._parent: self._parent.xml_children.append(new_text)
            elif ev[0] == event.end_element:
                self._evstack.pop()
                if self._building_depth:
                    self._building_depth -= 1
                    #Done with this subtree
                    if not self._building_depth:
                        self._sink.send(self._parent)
                    #Pop back up in element ancestry
                    if self._parent.xml_parent:
                        self._parent = self._parent.xml_parent
            #print(ev, self._building_depth, self._evstack)
        return

    def parse(self, doc):
        h = self._handler()
        p = parser(h)
        p.send((doc, False))
        p.send(('', True)) #Wrap it up
        return
