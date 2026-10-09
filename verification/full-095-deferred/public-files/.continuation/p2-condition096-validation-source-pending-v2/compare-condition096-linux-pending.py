PENDING_PREPARATION = True
if PENDING_PREPARATION:raise SystemExit('Pending096: root-authorized actual isolated gold/candidate data and final source admission required')
import gzip,hashlib,json,sys
from pathlib import Path
def flat_native(value):
    nodes=[];todo=[];seen={}
    def reference(v):
        kind=type(v)
        if kind in (dict,list,tuple) and id(v) in seen:return seen[id(v)]
        index=len(nodes);nodes.append(None);todo.append((index,v))
        if kind in (dict,list,tuple):seen[id(v)]=index
        return index
    root=reference(value)
    while todo:
        index,v=todo.pop();kind=type(v)
        if v is None or kind in (bool,int,str):node={'type':kind.__name__,'value':v}
        elif kind is float:node={'type':'float','hex':v.hex()}
        elif kind is bytes:node={'type':'bytes','hex':v.hex()}
        elif kind in (list,tuple):node={'type':kind.__name__,'items':[reference(x) for x in v]}
        elif kind is dict:node={'type':'dict','items':[[reference(k),reference(x)] for k,x in v.items()]}
        else:raise TypeError(('unsupported evidence value',kind.__name__))
        nodes[index]=node
    return {'schema':'flat-typed-graph-v1','root':root,'nodes':nodes}


def native_inverse(graph):
    assert graph['schema']=='flat-typed-graph-v1'
    nodes=graph['nodes'];values={};active=set();stack=[(graph['root'],False)]
    while stack:
        index,finish=stack.pop()
        if index in values:continue
        node=nodes[index];kind=node['type']
        if kind in ('NoneType','bool','int','str'):values[index]=node['value'];continue
        if kind=='float':values[index]=float.fromhex(node['hex']);continue
        if kind=='bytes':values[index]=bytes.fromhex(node['hex']);continue
        if not finish:
            assert index not in active,'Public evidence graph must be acyclic'
            active.add(index);stack.append((index,True))
            children=[x for pair in node['items'] for x in pair] if kind=='dict' else node['items']
            stack.extend((child,False) for child in reversed(children) if child not in values)
        else:
            active.remove(index)
            if kind=='dict':values[index]={values[k]:values[v] for k,v in node['items']}
            elif kind=='list':values[index]=[values[x] for x in node['items']]
            elif kind=='tuple':values[index]=tuple(values[x] for x in node['items'])
            else:raise ValueError(('invalid flat type',kind))
    return values[graph['root']]


def clone(value):return native_inverse(flat_native(value))


def snapshot(value):
    graph=flat_native(value);restored=native_inverse(graph)
    assert flat_native(restored)==graph,'Lossless native inverse must reproduce exact flat graph'
    return {'native':graph,'JSON_projection':restored,'native_inverse_verified':True}


def delta(before,after):return {k:after.get(k,0)-before.get(k,0) for k in sorted(set(before)|set(after))}


def digest(data):return hashlib.sha256(data).hexdigest()


def filesystem(folder):
    rows=[]
    for path in sorted(folder.rglob('*')):
        rel=path.relative_to(folder).as_posix()
        if path.is_dir():rows.append({'path':rel,'kind':'directory'});continue
        data=path.read_bytes();row={'path':rel,'kind':'file','bytes':len(data),'sha256':digest(data),'raw_hex':data.hex()}
        try:row['decoded']=snapshot(json.loads(data.decode('utf-8')))
        except (UnicodeDecodeError,ValueError) as error:row['decode_error']={'type':type(error).__name__,'message':str(error)}
        rows.append(row)
    return rows


def file_bytes(path):return path.read_bytes() if path.exists() else None


def byte_evidence(data):
    assert data is None or type(data) is bytes,'Only an existing raw file byte string or explicit absent file'
    graph=flat_native(data);restored=native_inverse(graph)
    assert type(restored) is type(data) and restored==data and flat_native(restored)==graph,'Lossless raw-byte native inverse must preserve exact original value'
    return {'schema':'raw-file-bytes-evidence-v1','native':graph,'native_inverse_verified':True,
        'JSON_safe_raw_bytes':{'file_exists':data is not None,'raw_hex':data.hex() if data is not None else None,
            'byte_count':len(data) if data is not None else None,'sha256':digest(data) if data is not None else None}}


assert len(sys.argv)==4
old=json.loads(Path(sys.argv[1]).read_text());new=json.loads(Path(sys.argv[2]).read_text());out=Path(sys.argv[3]);assert not out.exists()
assert old['passed'] is new['passed'] is True and old['workflow_complete'] is new['workflow_complete'] is True
assert old['mode']=='gold' and new['mode']=='candidate' and old['plan_sha256']==new['plan_sha256']
assert old['source_drift']==new['source_drift']==[]
assert [r['id'] for r in old['records']]==[r['id'] for r in new['records']]
def read(row):
    compressed=Path(row['path']).read_bytes();assert len(compressed)==row['bytes'] and digest(compressed)==row['sha256'];raw=gzip.decompress(compressed);assert len(raw)==row['decoded_bytes'] and digest(raw)==row['decoded_sha256'];return json.loads(raw)
checks=[]
for a,b in zip(old['records'],new['records']):
    x=read(a);y=read(b)
    assert x==y,('Full old native/error/call-order/all-three-text/math-vector difference; no field removal',a['id'])
    checks.append({'id':a['id'],'full_record_byte_value_exact':True,'original_numeric_vector_exact':True,'three_texts_exact':True})
proof={'format_version':1,'passed':True,'kind':'SAVED_ONLY_ACTUAL_ISOLATED_LINUX_CONDITION096_PAIRS','project_calls_in_comparator':0,'checks':checks,'gold_receipt_sha256':digest(Path(sys.argv[1]).read_bytes()),'candidate_receipt_sha256':digest(Path(sys.argv[2]).read_bytes()),'completed_section_increment':0}
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
