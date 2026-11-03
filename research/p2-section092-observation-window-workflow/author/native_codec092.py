"""Lossless built-in native value trees; stdlib-only, never imports project code."""
import json


def encode(value):
    t=type(value)
    if value is None:return ['none']
    if t is bool:return ['bool',value]
    if t is int:return ['int',str(value)]
    if t is float:return ['float',value.hex()]
    if t is str:return ['str',value]
    if t is list:return ['list',[encode(v) for v in value]]
    if t is tuple:return ['tuple',[encode(v) for v in value]]
    if t is dict:return ['dict',[[encode(k),encode(v)] for k,v in value.items()]]
    if t in (set,frozenset):return ['set' if t is set else 'frozenset',sorted([encode(v) for v in value],key=canonical)]
    if t is bytes:return ['bytes',value.hex()]
    raise TypeError('Unsupported actual native type: '+t.__module__+'.'+t.__qualname__)


def decode(tree):
    tag=tree[0]
    if tag=='none':return None
    if tag=='bool':return tree[1]
    if tag=='int':return int(tree[1])
    if tag=='float':return float.fromhex(tree[1])
    if tag=='str':return tree[1]
    if tag=='list':return [decode(x) for x in tree[1]]
    if tag=='tuple':return tuple(decode(x) for x in tree[1])
    if tag=='dict':return {decode(k):decode(v) for k,v in tree[1]}
    if tag=='set':return {decode(x) for x in tree[1]}
    if tag=='frozenset':return frozenset(decode(x) for x in tree[1])
    if tag=='bytes':return bytes.fromhex(tree[1])
    raise ValueError('Unsupported saved tree tag: '+str(tag))


def canonical(tree):return json.dumps(tree,ensure_ascii=False,separators=(',',':'),allow_nan=False)
