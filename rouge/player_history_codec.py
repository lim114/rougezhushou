"""A small whitelist codec for private snapshots, without executable objects.

JSON alone folds adjacent surrogate code units and does not qualify nonfinite
numbers. Keep opaque historical evidence intact; player views qualify numbers.
"""
import json
import struct

def encode(value, stack=None):
    stack=set()if stack is None else stack
    kind=type(value)
    if value is None:return ['null']
    if kind is bool:return ['bool',value]
    if kind is int:return ['int',hex(value)]
    if kind is float:return ['float64',struct.pack('>d',value).hex()]
    if kind is str:
        return ['codepoints',[ord(c)for c in value]]if any(0xd800<=ord(c)<=0xdfff for c in value)else['text',value]
    if kind not in(dict,list,tuple):raise ValueError('当前记录含无法无损归档的内容，本局未改动。')
    identity=id(value)
    if identity in stack:raise ValueError('当前记录含循环内容，未归档或重置。')
    stack.add(identity)
    try:
        if kind is dict:return ['object',[[encode(k,stack),encode(v,stack)]for k,v in value.items()]]
        return ['array'if kind is list else'tuple',[encode(item,stack)for item in value]]
    finally:stack.remove(identity)

def decode(value):
    if not isinstance(value,list)or not value or not isinstance(value[0],str):raise ValueError('历史内容类型无法核对。')
    tag=value[0]
    if tag=='null'and len(value)==1:return None
    if len(value)!=2:raise ValueError('历史内容长度无法核对。')
    raw=value[1]
    if tag=='bool'and type(raw)is bool:return raw
    if tag=='int'and type(raw)is str:
        number=int(raw,16)
        if hex(number)!=raw:raise ValueError('历史整数格式无法核对。')
        return number
    if tag=='float64'and type(raw)is str and len(raw)==16:
        binary=bytes.fromhex(raw)
        if len(binary)!=8 or binary.hex()!=raw:raise ValueError('历史数值格式无法核对。')
        return struct.unpack('>d',binary)[0]
    if tag=='text'and type(raw)is str and not any(0xd800<=ord(c)<=0xdfff for c in raw):return raw
    if tag=='codepoints'and type(raw)is list and all(type(n)is int and 0<=n<=0x10ffff for n in raw):
        return ''.join(chr(n)for n in raw)
    if tag in('array','tuple')and type(raw)is list:
        result=[decode(item)for item in raw];return tuple(result)if tag=='tuple'else result
    if tag=='object'and type(raw)is list:
        result={}
        for pair in raw:
            if type(pair)is not list or len(pair)!=2:raise ValueError('历史字段格式无法核对。')
            key=decode(pair[0])
            try:
                if key in result:raise ValueError('历史字段重复，未覆盖。')
                result[key]=decode(pair[1])
            except TypeError as error:raise ValueError('历史字段名称无法核对。')from error
        return result
    raise ValueError('历史内容类型不受支持。')

def bytes_for(value):
    return json.dumps(encode(value),ensure_ascii=True,separators=(',',':'),allow_nan=False).encode('ascii')
