PENDING097 = True
if PENDING097:
    raise SystemExit('Pending account097 support: actual095 publication, completed096 and independent FINAL Source admission required')
ROOT_PRESEAL_BINDING_SHA256 = None

import ast
import gzip
import hashlib
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import traceback

def digest(data):return hashlib.sha256(data).hexdigest()

# HISTORICAL_FIVE_CODECS_SOURCE_INSERTION

# WHOLE_STRING_ENVELOPE_SOURCE_INSERTION

def ref097(path):
    path=Path(path);raw=path.read_bytes()
    return {'path':str(path),'bytes':len(raw),'sha256':digest(raw)}

def verify_ref097(reference):
    assert type(reference) is dict and set(reference)=={'path','bytes','sha256'}
    assert type(reference['bytes']) is int and reference['bytes']>=0
    actual=ref097(reference['path']);assert actual==reference,('Exact reference mismatch',reference,actual)
    return Path(reference['path']).read_bytes()

def pointer097(value,path):
    assert path=='' or type(path) is str and path.startswith('/')
    for part in path.split('/')[1:]:
        part=part.replace('~1','/').replace('~0','~')
        value=value[int(part)] if type(value) is list else value[part]
    return value

def native097(value):
    graph=flat_native(value);restored=native_inverse(graph)
    assert flat_native(restored)==graph,'Full historical canonical inverse required'
    return envelope_native_strings(graph)

def snapshot097(value):return native097(value)

def restore097(envelope):
    graph=inverse_native_strings(envelope);restored=native_inverse(graph)
    assert flat_native(restored)==graph,'Whole graph canonical/inverse exact, including aliases and order'
    assert envelope_native_strings(flat_native(restored))==envelope
    return restored

def durable097(value):
    envelope=native097(value);raw=json.dumps(envelope,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode('ascii')
    loaded=json.loads(raw.decode('ascii'))
    assert native097(restore097(loaded))==envelope
    return raw

def write_case097(output,case_id,value):
    assert type(case_id) is str and case_id and all(c.isalnum() or c in '-_' for c in case_id)
    path=Path(output)/(case_id+'.json.gz');raw=durable097(value);compressed=gzip.compress(raw,mtime=0)
    with path.open('xb') as f:f.write(compressed)
    saved=path.read_bytes();decoded=gzip.decompress(saved)
    assert saved==compressed and decoded==raw
    assert native097(restore097(json.loads(decoded.decode('ascii'))))==native097(value)
    return {'id':case_id,'file':ref097(path),'decoded_bytes':len(raw),'decoded_sha256':digest(raw),
            'full_native_durable_inverse_verified':True}

def exception097(error):
    return {'type':type(error).__module__+'.'+type(error).__qualname__,'message':str(error),
            'args':error.args,'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}

def file097(path):
    path=Path(path)
    try:info=path.lstat()
    except FileNotFoundError:return {'exists':False,'kind':'absent','raw_bytes':byte_evidence(None)}
    row={'exists':True,'mode':stat.S_IFMT(info.st_mode),'size':info.st_size}
    if stat.S_ISLNK(info.st_mode):
        row.update(kind='symlink',link=os.readlink(path));return row
    if stat.S_ISDIR(info.st_mode):
        row.update(kind='directory',children=tree097(path));return row
    assert stat.S_ISREG(info.st_mode),'Unqualified public fixture filesystem entry'
    raw=path.read_bytes();row.update(kind='file',raw_bytes=byte_evidence(raw))
    try:row['decoded']=json.loads(raw.decode('utf-8'))
    except (ValueError,UnicodeError) as error:row['decode_error']=exception097(error)
    return row

def tree097(folder):
    folder=Path(folder);rows=[]
    if not folder.exists():return {'exists':False,'entries':[]}
    def visit(path):
        for child in sorted(path.iterdir(),key=lambda p:p.name):
            info=child.lstat();rel=child.relative_to(folder).as_posix()
            if stat.S_ISDIR(info.st_mode):rows.append({'path':rel,'kind':'directory'});visit(child)
            else:rows.append({'path':rel,'evidence':file097(child)})
    visit(folder);return {'exists':True,'entries':rows}

def guard097(root):
    root=Path(root);rows={}
    for group in ('rouge','tests','scripts'):
        base=root/group;assert base.is_dir()
        for path in sorted(base.rglob('*')):
            if path.suffix in ('.py','.json') and path.is_file():
                assert not path.is_symlink(),'Source symlink outside sealed guard is not admitted'
                raw=path.read_bytes();rows[path.relative_to(root).as_posix()]={'bytes':len(raw),'sha256':digest(raw)}
    return rows

def load_binding097(binding_path,admission_path,runner_file,mode):
    assert mode in ('baseline','candidate')
    assert type(ROOT_PRESEAL_BINDING_SHA256) is str and len(ROOT_PRESEAL_BINDING_SHA256)==64
    raw=Path(binding_path).read_bytes();assert digest(raw)==ROOT_PRESEAL_BINDING_SHA256
    binding=json.loads(raw)
    assert binding['format']=='ACCOUNT097_ROOT_ACTUAL_PRESEAL_V1'
    assert binding['root_runtime_authorized'] is True and binding['actual_future_prerequisites_bound'] is True
    required={'actual095_publication','actual096_completed_scope','actual096_expected_old_exact'}
    assert {g['name'] for g in binding['required_actual_gates']}==required
    for gate in binding['required_actual_gates']:
        observed=json.loads(verify_ref097(gate['file']))
        assert pointer097(observed,gate['pass_pointer'])==gate['pass_value']
        assert gate['actual_primary_captured'] is True and type(gate['actual_primary_exit']) is int and gate['actual_primary_exit']==0
        assert verify_ref097(gate['raw_exit_file']).strip()==b'0'
    platform_key='windows' if os.name=='nt' else 'linux'
    admission=json.loads(Path(admission_path).read_bytes())
    assert admission['format']=='ACCOUNT097_ROOT_FINAL_SOURCE_ADMISSION_V1'
    assert admission['root_authorized'] is True and admission['runtime_executed'] is False
    assert admission['preseal_binding']['sha256']==ROOT_PRESEAL_BINDING_SHA256
    assert verify_ref097(admission['preseal_binding'])==raw
    review=json.loads(verify_ref097(admission['independent_final_source_review']['file']))
    assert pointer097(review,admission['independent_final_source_review']['pass_pointer']) is True
    assert pointer097(review,admission['independent_final_source_review']['runtime_pointer']) is False
    reviewed=pointer097(review,admission['independent_final_source_review']['reviewed_sources_pointer'])
    for row in admission['final_sources']:
        reference={'path':row['paths'][platform_key],'bytes':row['bytes'],'sha256':row['sha256']}
        verify_ref097(reference);assert reviewed[row['name']]==row['sha256']
    resolved=Path(runner_file).resolve();support=Path(__file__).resolve()
    assert all(any(Path(r['paths'][platform_key]).resolve()==p for r in admission['final_sources']) for p in (resolved,support))
    source=Path(binding['mode_roots'][mode]['paths'][platform_key]).resolve()
    expected=json.loads(verify_ref097(binding['mode_roots'][mode]['whole_source_guard']))
    assert guard097(source)==expected,'Actual completed096/integrated097 entire Source exact'
    actual_account=expected['rouge/account_cache.py']['sha256']
    assert actual_account==binding['expected_source_inputs'][mode]['account_cache_sha256']
    assert expected['rouge/app.py']['sha256']==binding['expected_source_inputs']['future096_app_sha256']
    verify_ref097(binding['shared_plan']);verify_ref097(binding['candidate_code_manifest'])
    assert binding['declared_public_fixture_only'] is True and binding['default_private_paths_forbidden'] is True
    return binding,source,expected,admission

class ExactSourceFinder097(importlib.abc.MetaPathFinder):
    def __init__(self,root,expected):self.root=Path(root);self.expected=expected;self.actual_imports=[]
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0]!='rouge':return None
        stem=self.root.joinpath(*fullname.split('.'));file=stem.with_suffix('.py');package=False
        if not file.is_file():file=stem/'__init__.py';package=True
        if not file.is_file():return None
        key=file.relative_to(self.root).as_posix();raw=file.read_bytes()
        assert key in self.expected and {'bytes':len(raw),'sha256':digest(raw)}==self.expected[key]
        outer=self
        class Loader097(importlib.abc.Loader):
            def create_module(self,spec):return None
            def exec_module(self,module):
                current=file.read_bytes();assert current==raw
                module.__file__=str(file);outer.actual_imports.append({'module':fullname,'relative_path':key,'bytes':len(raw),'sha256':digest(raw)})
                exec(compile(current,str(file),'exec',dont_inherit=True),module.__dict__)
        return importlib.util.spec_from_file_location(fullname,file,loader=Loader097(),submodule_search_locations=[str(stem)] if package else None)

def install_source097(root,expected):
    assert not any(name=='rouge' or name.startswith('rouge.') for name in sys.modules),'Fresh interpreter required'
    sys.dont_write_bytecode=True;sys.path.insert(0,str(root));finder=ExactSourceFinder097(root,expected);sys.meta_path.insert(0,finder)
    return finder

def cache_state097(cache):
    return {'records':cache.records,'issues':cache.issues,'load_issue':cache.load_issue,
            'preserve_original':cache.preserve_original,
            'save_issue_present':hasattr(cache,'save_issue'),'save_issue':getattr(cache,'save_issue',None)}

class Calls097:
    def __init__(self,root):self.root=str(Path(root).resolve()).replace('\\','/').lower();self.rows=[];self.counts={};self.active={};self.scope='before-import'
    def trace(self,frame,event,arg):
        path=frame.f_code.co_filename.replace('\\','/').lower()
        if not path.startswith(self.root+'/rouge/'):return None
        key=path[len(self.root)+1:]+':'+frame.f_code.co_qualname
        if event=='call':
            self.counts[key]=self.counts.get(key,0)+1
            forbidden={'GameCapture.connect','GameCapture.set_collecting','GameCapture.capture','MainWindow.sample_now','DesktopBackend.start','DesktopBackend.request','ScreenReader.analyze','ScreenReader.read'}
            assert frame.f_code.co_qualname not in forbidden,('Unrequested external action',key)
            name=frame.f_code.co_name;qual=frame.f_code.co_qualname
            targeted=(path.endswith('/rouge/damage.py') or path.endswith('/rouge/account_cache.py') and qual in {'AccountCache.observe','AccountCache.save','AccountCache.view','AccountCache.notice'} or path.endswith('/rouge/run_state.py') and name=='apply' or path.endswith('/rouge/app.py') and qual in {'MainWindow.calculate','MainWindow.apply_operator_observation','MainWindow.apply_run_observation','MainWindow.show_observed_operator','MainWindow.update_operator','MainWindow.current_operator_state','MainWindow.account_training_status','MainWindow.render_damage'})
            if targeted:
                argc=frame.f_code.co_argcount+frame.f_code.co_kwonlyargcount;names=list(frame.f_code.co_varnames[:argc]);extra=argc
                if frame.f_code.co_flags&4:names.append(frame.f_code.co_varnames[extra]);extra+=1
                if frame.f_code.co_flags&8:names.append(frame.f_code.co_varnames[extra])
                caller={name:frame.f_locals[name] for name in names if name!='self' and name in frame.f_locals}
                row={'sequence':len(self.rows)+1,'scope':self.scope,'key':key,'caller_before':native097(caller),'exception_events':[],'outcome':'pending'}
                if 'self' in frame.f_locals:
                    obj=frame.f_locals['self'];row['self_type']=type(obj).__module__+'.'+type(obj).__qualname__
                    if path.endswith('/rouge/account_cache.py'):row['cache_before']=native097({'caller':caller,'cache':cache_state097(obj)})
                self.rows.append(row);self.active[id(frame)]=(row,caller)
            return self.trace
        if id(frame) in self.active:
            row,caller=self.active[id(frame)]
            if event=='exception':row['exception_events'].append(native097(exception097(arg[1])))
            elif event=='return':
                row['caller_after']=native097(caller);row['caller_unchanged']=row['caller_before']==row['caller_after']
                row['return_value']=native097(arg);row['caller_and_returned']=native097({'caller':caller,'returned':arg})
                row['outcome']='observed_return_event';row['return_none_with_exception_events']=arg is None and bool(row['exception_events'])
                if frame.f_code.co_name=='_prepare_damage':row['prepared_exit_scenario']=native097(frame.f_locals.get('scenario'))
                if path.endswith('/rouge/account_cache.py'):row['cache_after']=native097({'caller':caller,'cache':cache_state097(frame.f_locals['self'])})
                del self.active[id(frame)]
        return self.trace

def common_math097(cache,trace):
    from rouge.damage import calculate_damage
    from rouge.estimate import format_estimate
    from rouge.reporting import format_report
    view=cache.view('mechanist');fields=view.get('fields',{});ranks=view.get('skill_ranks',{})
    scenario={'operator':'mechanist','skill':1,'skill_rank':ranks.get('1',7),'enemy_defense':0,'enemy_resistance':0,'relic_ids':[],
              'elite':fields.get('elite',2),'level':fields.get('level',1),'trust':fields.get('trust',100),
              'potential':fields.get('potential',1),'module_id':fields.get('module_id'),'module_level':fields.get('module_level',0)}
    before=native097(scenario);start=len(trace.rows);counts=dict(trace.counts);result=calculate_damage(scenario)
    texts={'estimate':format_estimate(result),'general':format_report(result),'technical':format_report(result,technical=True),
           'JSON':json.dumps({'scenario':scenario,'result':result},ensure_ascii=False,indent=2)}
    assert native097(scenario)==before
    return {'scenario_before':before,'scenario_after':native097(scenario),'result':result,'all_report_texts':texts,
            'actual_entries':trace.rows[start:],'actual_count_delta':{k:v-counts.get(k,0) for k,v in trace.counts.items() if v!=counts.get(k,0)}}
