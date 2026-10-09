"""SOURCE-only transport addition; never imported or called by this author.

Keep the five historical native/byte functions whole. Apply this narrow envelope
to their full native graph before saving evidence, and invert it after reading.
Python str codepoints include surrogate ordinals. They are not all interoperable
Unicode scalar values. JSON-encoding a native adjacent pair directly is lossy.
Root must bind actual095 save and completed096, admit the concrete FINAL source,
and run the declared controls before relying on this evidence transport.
"""

PENDING_SOURCE_ONLY = True
if PENDING_SOURCE_ONLY:
    raise SystemExit('Pending097: source-only envelope; root FINAL admission and actual095/096 prerequisites required')


def _graph_header(graph, schema):
    if type(graph) is not dict or set(graph) != {'schema', 'root', 'nodes'}:
        raise ValueError('Exact full native graph header required')
    if graph['schema'] != schema or type(graph['nodes']) is not list:
        raise ValueError('Unsupported full native graph schema')
    root = graph['root']
    if type(root) is not int or not 0 <= root < len(graph['nodes']):
        raise ValueError('Invalid native graph root')
    return len(graph['nodes'])


def _whole_nonstring_node(node, count):
    """Copy every old nonstring node field; preserve reference indexes/order."""
    if type(node) is not dict:
        raise ValueError('Native node must be an object')
    kind = node.get('type')
    if kind in ('NoneType', 'bool', 'int'):
        if set(node) != {'type', 'value'}:
            raise ValueError('Unexpected primitive native node fields')
        expected = {'NoneType': type(None), 'bool': bool, 'int': int}[kind]
        if type(node['value']) is not expected:
            raise ValueError('Native primitive type mismatch')
        return dict(node)
    if kind in ('float', 'bytes'):
        if set(node) != {'type', 'hex'} or type(node['hex']) is not str or not node['hex'].isascii():
            raise ValueError('Exact ASCII native hex node required')
        return dict(node)
    if kind not in ('dict', 'list', 'tuple') or set(node) != {'type', 'items'} or type(node['items']) is not list:
        raise ValueError('Unexpected nonstring native node')
    def reference(value):
        if type(value) is not int or not 0 <= value < count:
            raise ValueError('Invalid native node reference')
        return value
    if kind == 'dict':
        items = []
        for pair in node['items']:
            if type(pair) is not list or len(pair) != 2:
                raise ValueError('Exact native dict key/value pair required')
            items.append([reference(pair[0]), reference(pair[1])])
    else:
        items = [reference(value) for value in node['items']]
    return {'type': kind, 'items': items}


def envelope_native_strings(graph):
    """Full flat graph -> JSON-safe ord-array string nodes; no value mutation."""
    count = _graph_header(graph, 'flat-typed-graph-v1')
    nodes = []
    for node in graph['nodes']:
        if type(node) is dict and node.get('type') == 'str':
            if set(node) != {'type', 'value'} or type(node['value']) is not str:
                raise ValueError('Exact native string node required')
            nodes.append({'type': 'str', 'codepoints': [ord(point) for point in node['value']]})
        else:
            nodes.append(_whole_nonstring_node(node, count))
    return {'schema': 'flat-typed-graph-v1-string-codepoints097', 'root': graph['root'], 'nodes': nodes}


def inverse_native_strings(envelope):
    """Envelope -> entire old graph; range accepts Python surrogate ordinals."""
    count = _graph_header(envelope, 'flat-typed-graph-v1-string-codepoints097')
    nodes = []
    for node in envelope['nodes']:
        if type(node) is dict and node.get('type') == 'str':
            if set(node) != {'type', 'codepoints'} or type(node['codepoints']) is not list:
                raise ValueError('Exact codepoint string node required')
            points = node['codepoints']
            if any(type(point) is not int or not 0 <= point <= 0x10ffff for point in points):
                raise ValueError('Python str ordinal must be an integer in 0..0x10ffff')
            nodes.append({'type': 'str', 'value': ''.join(chr(point) for point in points)})
        else:
            nodes.append(_whole_nonstring_node(node, count))
    return {'schema': 'flat-typed-graph-v1', 'root': envelope['root'], 'nodes': nodes}
