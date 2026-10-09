"""Independent standard-library SOURCE review; never execute reviewed code."""
from pathlib import Path
import ast
import base64
import hashlib
import json
import sys
import platform
from datetime import datetime, timezone

BASE = Path('/workspace/.continuation')
OUT = BASE / 'full095-ui-cache-retry-independent-review-v1'
ORIGINAL = BASE / 'full095-ui-final-v1/wine-full-ui-095-final.py'
CACHE = BASE / 'full095-ui-lineno-cache-source-pending-v1/wine-full-ui-095-lineno-cache-pending.py'
PENDING = BASE / 'full095-ui-migration-pending-v3/wine-full-ui-095-pending.py'
ANCESTOR = BASE / 'ui-090-final-gate-revision/wine-ui-smoke-090-final-gate-revision.py'
GUARD = BASE / 'root-source-095-v2.json'
PACKAGE = BASE / 'full095-ui-cache-retry-source-v1'
RUNNER = PACKAGE / 'wine-full-ui-095-cache-retry.py'
MANIFEST = PACKAGE / 'public-artifacts-manifest-cache-retry095.json'
SEALED_MANIFEST_SHA = 'd9b2c86141a36faf0c3600051690ce0fffc55c0bf1d2248bffeb14ab02402c85'
SEALED_RUNNER_SHA = 'e5dec2d704cecbde56762cf7c2f92016f5123b592633fae12840a892869e6bc5'
EXPECTED = {
    ORIGINAL: '83c412ce7e456109dc32a6415f7a61526955d48b01d25dbb72198870e6cf18ee',
    CACHE: '1a6ac7f0db3096de170a9e0d035148bfbad372cc58f704bb7ad39da6cb7cfb6d',
    PENDING: '8b2bf2bad7b0fe0b9467fe8616847ce7f751ad6b9e5d400787ceb86eaad19bf8',
    ANCESTOR: '9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9',
    GUARD: '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab',
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def ref(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': sha(data)}

def parse_source(path):
    data = path.read_bytes()
    source = data.decode('utf-8')
    tree = ast.parse(source, filename=str(path))
    lines = data.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))
    def span(node):
        return (starts[node.lineno-1] + node.col_offset,
                starts[node.end_lineno-1] + node.end_col_offset)
    def segment(node):
        a, z = span(node)
        return data[a:z]
    return data, source, tree, span, segment

def named_assign(tree, name):
    matches = [n for n in tree.body if isinstance(n, ast.Assign)
               and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
               and n.targets[0].id == name]
    if len(matches) != 1:
        raise AssertionError((name, len(matches)))
    return matches[0]

def func(tree, name):
    matches = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(matches) != 1:
        raise AssertionError((name, len(matches)))
    return matches[0]

def assert_vector(tree, segment):
    nodes = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Assert)),
                   key=lambda n:(n.lineno,n.col_offset))
    return [segment(n).decode('utf-8') for n in nodes]

def vector_sha(vector):
    return sha(json.dumps(vector, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))

def check_inverse_ancestry():
    originals = {}
    for path, expected in EXPECTED.items():
        data = path.read_bytes()
        if sha(data) != expected:
            raise AssertionError(('source_hash', str(path), sha(data), expected))
        originals[path] = data
    cache_ledger_path = BASE/'full095-ui-lineno-cache-source-pending-v1/exact-inverse-cache095.json'
    cache_ledger = json.loads(cache_ledger_path.read_text())
    recovered = originals[CACHE].decode('utf-8')
    for op in reversed(cache_ledger['changes']):
        if op['kind'] == 'exact_origin_line_replacement':
            if recovered.count(op['new']) != 1:
                raise AssertionError(('cache_unique_replacement', op['kind']))
            recovered = recovered.replace(op['new'], op['old'], 1)
        else:
            new = op['insert'] + op['anchor'] if op['kind']=='unique_helper_insert' else op['anchor'] + op['insert']
            if recovered.count(new) != 1:
                raise AssertionError(('cache_unique_insert', op['kind']))
            recovered = recovered.replace(new, op['anchor'], 1)
    if recovered.encode('utf-8') != originals[ORIGINAL]:
        raise AssertionError('cache_inverse_whole_bytes')

    original_data,_, original_tree, original_span, original_segment = parse_source(ORIGINAL)
    pending_data,_, pending_tree, _, pending_segment = parse_source(PENDING)
    substitutions = []
    for name in ['PENDING095', 'BINDING095']:
        a,z = original_span(named_assign(original_tree,name))
        substitutions.append((a,z,pending_segment(named_assign(pending_tree,name))))
    recovered = original_data
    for a,z,replacement in sorted(substitutions,reverse=True):
        recovered = recovered[:a]+replacement+recovered[z:]
    if recovered != pending_data:
        raise AssertionError('final_to_pending_whole_bytes')

    pending_ledger_path = BASE/'full095-ui-migration-pending-v3/exact-inverse-ledger095.json'
    pending_ledger = json.loads(pending_ledger_path.read_text())
    operations = pending_ledger['operations']
    chunks = []
    cursor = 0
    for op in sorted(operations,key=lambda x:x['pending_byte_start']):
        start=op['pending_byte_start']; end=start+op['pending_byte_count']
        if start < cursor or sha(pending_data[start:end]) != op['pending_sha256']:
            raise AssertionError(('pending_slice',op['category']))
        before=base64.b64decode(op['before_base64'],validate=True)
        if len(before)!=op['original_byte_count'] or sha(before)!=op['original_sha256']:
            raise AssertionError(('original_inverse_slice',op['category']))
        chunks.extend([pending_data[cursor:start],before]);cursor=end
    chunks.append(pending_data[cursor:]); recovered=b''.join(chunks)
    if recovered != originals[ANCESTOR] or len(recovered)!=729181:
        raise AssertionError('pending_to_original729181_whole_bytes')
    return {
        'cache_to_final_byteexact':True,
        'final_to_pending_byteexact':True,
        'final_binding_replacements':len(substitutions),
        'pending_to_original729181_byteexact':True,
        'pending_inverse_operations':len(operations),
        'original729181_sha256':sha(recovered),
        'references':[ref(p) for p in [ORIGINAL,CACHE,PENDING,ANCESTOR,GUARD,cache_ledger_path,pending_ledger_path]],
    }

def reverse_operations(data, operations):
    # New retry stages record coordinates after each sequential forward edit.
    # Reverse the ordered operations and update the source after every edit.
    for op in reversed(operations):
        a=op['pending_byte_start'];z=a+op['pending_byte_count']
        if sha(data[a:z])!=op['pending_sha256']:
            raise AssertionError(('inverse_slice',op['category'],a))
        old=base64.b64decode(op['before_base64'],validate=True)
        data=data[:a]+old+data[z:]
    return data

def review_retry():
    ancestry=check_inverse_ancestry()
    checks=[]
    def check(name, condition, evidence):
        checks.append({'name':name,'passed':bool(condition),'evidence':evidence})
        if not condition:
            raise AssertionError(name)
    check('sealed_manifest',sha(MANIFEST.read_bytes())==SEALED_MANIFEST_SHA,ref(MANIFEST))
    manifest=json.loads(MANIFEST.read_text())
    check('sealed_runner',sha(RUNNER.read_bytes())==SEALED_RUNNER_SHA,ref(RUNNER))
    for name,item in manifest['artifacts'].items():
        actual=ref(PACKAGE/name)
        check('manifest_artifact_'+name,actual['bytes']==item['bytes'] and actual['sha256']==item['sha256'],actual)
    contract_path=PACKAGE/'source-contract-cache-retry095.json'
    inverse_path=PACKAGE/'exact-inverse-cache-retry095.json'
    launch_path=PACKAGE/'exact-launch-contract-cache-retry095.json'
    handoff_path=PACKAGE/'handoff-cache-retry095.json'
    contract=json.loads(contract_path.read_text());inverse=json.loads(inverse_path.read_text())
    launch=json.loads(launch_path.read_text());handoff=json.loads(handoff_path.read_text())
    retry_data,retry_source,retry_tree,retry_span,retry_segment=parse_source(RUNNER)
    cache_data,cache_source,cache_tree,_,cache_segment=parse_source(CACHE)
    original_data,original_source,original_tree,_,original_segment=parse_source(ORIGINAL)
    pairs=inverse['output_rebindings']
    declared={(p['original'],p['retry']):p['occurrences'] for p in pairs}
    ops=inverse['reverse_stages'][0]['operations']
    observed={p:0 for p in declared}
    intermediate=retry_data
    for op in reversed(ops):
        a=op['pending_byte_start'];z=a+op['pending_byte_count']
        check('output_op_slice_%d'%a,sha(intermediate[a:z])==op['pending_sha256'],
              {'byte_start':a,'sha256':sha(intermediate[a:z]),
               'coordinates':'source state after this forward operation; inverse updates source at every step'})
        old_literal=base64.b64decode(op['before_base64'],validate=True)
        old=ast.literal_eval(old_literal.decode('utf-8'))
        new=ast.literal_eval(intermediate[a:z].decode('utf-8'))
        check('output_op_%d'%a,op['category']=='declared_output_literal' and (old,new) in declared,
              {'byte_start':a,'old':old,'new':new})
        observed[(old,new)]+=1
        intermediate=intermediate[:a]+old_literal+intermediate[z:]
    check('only_exact_declared_output_literals',observed==declared,
          {'declared':pairs,'operation_count':len(ops)})
    recovered=reverse_operations(retry_data,ops)
    check('retry_to_cache_entire_bytes',recovered==cache_data,
          {'bytes':len(recovered),'sha256':sha(recovered)})
    recovered=reverse_operations(recovered,inverse['reverse_stages'][1]['operations'])
    check('ledger_cache_to_final_entire_bytes',recovered==original_data,
          {'bytes':len(recovered),'sha256':sha(recovered)})
    for stage in inverse['reverse_stages']:
        for endpoint in ['from','to']:
            actual=ref(Path(stage[endpoint]['path']))
            check('inverse_endpoint_'+endpoint+'_'+Path(actual['path']).name,
                  actual==stage[endpoint],actual)
    check('contract_inverse_output_declarations_equal',contract['output_rebindings']==pairs,pairs)

    original_asserts=assert_vector(original_tree,original_segment)
    cache_asserts=assert_vector(cache_tree,cache_segment)
    retry_asserts=assert_vector(retry_tree,retry_segment)
    normalized=[]
    for assertion in retry_asserts:
        for old,new in declared:
            assertion=assertion.replace(repr(new),repr(old))
        normalized.append(assertion)
    changed=[{'ordinal':i,'original':a,'retry':b} for i,(a,b) in enumerate(zip(original_asserts,retry_asserts)) if a!=b]
    check('907_assertions_preserved',len(original_asserts)==len(cache_asserts)==len(retry_asserts)==907
          and original_asserts==cache_asserts and normalized==original_asserts,
          {'original_count':len(original_asserts),'cache_count':len(cache_asserts),'retry_count':len(retry_asserts),
           'original_and_cache_source_vector_sha256':vector_sha(original_asserts),
           'retry_source_vector_sha256':vector_sha(retry_asserts),'wholetext_unchanged':907-len(changed),
           'only_changed_assertions':changed})
    check('three_screenshot_assertion_literal_deltas',len(changed)==3 and all(
          'grab().save' in d['original'] and d['retry'].replace('-cache-retry-v1','')==d['original'] for d in changed),changed)
    binding_node=named_assign(retry_tree,'BINDING095')
    binding=ast.literal_eval(binding_node.value)
    original_binding=ast.literal_eval(named_assign(original_tree,'BINDING095').value)
    original_binding_path=BASE/'full095-ui-final-v1/root-bound-input095.json'
    binding_path=PACKAGE/'root-bound-input095.json'
    check('binding_wholetext_and_file_byteexact',retry_segment(binding_node)==original_segment(named_assign(original_tree,'BINDING095'))
          and binding==original_binding and binding_path.read_bytes()==original_binding_path.read_bytes()
          and json.loads(binding_path.read_text())==binding,
          {'original':ref(original_binding_path),'retry':ref(binding_path),'cases_count':len(binding['cases']),
           'guard':binding['source_guard'],'actual94_guard':binding['actual94_guard'],
           'actual94_receipt_declared_ref':binding['actual94_receipt'],
           'baseline_receipt_declared_ref':binding['baseline_receipt'],
           'baseline_files_declared_refs':binding['baseline_files'],
           'case_ids':[c['id'] for c in binding['cases']]})
    check('actual95_guard_preserved',binding['source_guard']['sha256']==EXPECTED[GUARD]
          and manifest['root_source_guard_sha256']==EXPECTED[GUARD],ref(GUARD))
    check('all_binding95_states_remain_uncompleted',binding['actual95_section_completed'] is False
          and binding['section_completed'] is False,{'actual95_section_completed':False,'section_completed':False})

    helper=retry_segment(func(retry_tree,'_runner_line095')).decode('utf-8')
    expected_helper="def _runner_line095(cursor):\n    code=cursor.f_code;key=(id(code),cursor.f_lasti)\n    cached=_runner_line_cache095.get(key)\n    if cached is not None:return cached[1]\n    line=cursor.f_lineno\n    _runner_line_cache095[key]=(code,line)\n    return line"
    check('cache_exact_helper_semantics',helper==expected_helper,
          {'line':func(retry_tree,'_runner_line095').lineno,'source':helper,
           'key':'(id(code),cursor.f_lasti)','value':'(code,line)','strong_code_reference':True,
           'cache_miss_f_lineno_reads':1,'cache_hit_f_lineno_reads':0,'None_preserved':True,
           'no_default_or_coercion':True,'no_code_object_key_hash':True})
    cache_assign=named_assign(retry_tree,'_runner_line_cache095')
    check('cache_fresh_global_dictionary',ast.literal_eval(cache_assign.value)=={},
          {'line':cache_assign.lineno,'source':retry_segment(cache_assign).decode('utf-8')})
    check('origin_entire_cache_source_preserved',retry_segment(func(retry_tree,'_origin095'))==cache_segment(func(cache_tree,'_origin095')),
          {'line':func(retry_tree,'_origin095').lineno,'source':retry_segment(func(retry_tree,'_origin095')).decode('utf-8')})
    old_origin=original_segment(func(original_tree,'_origin095')).decode('utf-8')
    new_origin=retry_segment(func(retry_tree,'_origin095')).decode('utf-8')
    original_statement="            origin={'runner_line':cursor.f_lineno,'function':cursor.f_code.co_qualname}\n            if cursor.f_lineno<=len(_source_lines095):origin['source']=_source_lines095[cursor.f_lineno-1]"
    cache_statement="            line=_runner_line095(cursor)\n            origin={'runner_line':line,'function':cursor.f_code.co_qualname}\n            if line<=len(_source_lines095):origin['source']=_source_lines095[line-1]"
    check('original_stack_walk_and_phase_algorithm_preserved',new_origin.replace(cache_statement,original_statement)==old_origin,
          {'only_changed_origin_statement':cache_statement,'parent_phase_and_classification_preserved':True})
    check('trace_scope_preserved',retry_segment(func(retry_tree,'_trace095'))==original_segment(func(original_tree,'_trace095')),
          {'source':retry_segment(func(retry_tree,'_trace095')).decode('utf-8')})
    assigned_lineno=[n for n in ast.walk(retry_tree) if isinstance(n,ast.Attribute)
                     and n.attr in ['f_lineno','co_linetable'] and isinstance(n.ctx,ast.Store)]
    dynamic_line_writes=[n for n in ast.walk(retry_tree) if isinstance(n,ast.Call)
                        and isinstance(n.func,ast.Name) and n.func.id in ['setattr','delattr']
                        and len(n.args)>1 and isinstance(n.args[1],ast.Constant)
                        and n.args[1].value in ['f_lineno','co_linetable']]
    check('no_runner_line_or_linetable_writes',not assigned_lineno and not dynamic_line_writes,
          {'direct_attribute_stores':len(assigned_lineno),'literal_setattr_delattr':len(dynamic_line_writes),
           'scope':'This harness; no generic debugger equivalence claimed.'})
    compile(retry_source,str(RUNNER),'exec')
    check('host_source_compilation_without_execution',True,
          {'compiler':platform.python_version(),'reviewed_code_objects_executed':0,
           'actual_Windows_target_bytecode_verified':False})

    expected_argv=['/workspace/.compat/run-wine-python.sh',
                   'Z:\\workspace\\.continuation\\full095-ui-cache-retry-source-v1\\wine-full-ui-095-cache-retry.py']
    expected_cwd='/workspace/rougezhushou'
    check('exact_argv_and_cwd',launch['argv']==contract['execution_argv']==contract['exact_argv']==handoff['execution_argv']==expected_argv
          and launch['cwd']==contract['execution_cwd']==contract['cwd']==handoff['cwd']==expected_cwd
          and contract['script_arg_index']==1,
          {'argv':expected_argv,'cwd':expected_cwd,'script_arg_index':1,'execution_performed':False})
    wrapper=ref(Path(launch['wrapper']['path']))
    check('wrapper_current_hash_matches_launch',wrapper==launch['wrapper'],wrapper)
    prior_review_path=BASE/'full095-ui-final-independent-review-v1/formal-source-review-full095-ui-FINAL-v1.json'
    prior_review=json.loads(prior_review_path.read_text())
    check('129_guard_source_keys_preserved',contract['source_keys']==prior_review['source_keys'] and len(contract['source_keys'])==129,
          {'count':len(contract['source_keys']),'prior_review':ref(prior_review_path),
           'current_repository_reads_performed':0,'current_maintained735_readiness':'Root prelaunch must verify; this review proves preservation.'})
    check('fresh_output_contract_consistent',contract['output_plan']==handoff['output_plan'],contract['output_plan'])
    output_paths=list(contract['replacement_output_paths'].values())+contract['fresh_evidence_directories']
    output_status=[{'path':p,'exists':Path(p).exists(),'is_symlink':Path(p).is_symlink()} for p in output_paths]
    check('no_retry_output_reuse_at_source_review',all(not p['exists'] and not p['is_symlink'] for p in output_status),output_status)
    prior_outputs=prior_review['runtime_output_contract']
    check('fresh_receipt_native_and_screenshot_namespaces',
          contract['output_plan']['receipt']!=prior_outputs['receipt']
          and contract['output_plan']['native_directory']!=prior_outputs['fresh_native_directory']
          and all(p not in prior_outputs['four_required_screenshots'] for p in contract['output_plan']['pngs']),
          {'retry':contract['output_plan'],'prior_receipt':prior_outputs['receipt'],
           'prior_native_directory':prior_outputs['fresh_native_directory']})
    check('source_unrun_claims_consistent',contract['runtime_pass'] is False and contract['execution_ready'] is False
          and launch['actual_execution_performed'] is False and manifest['runtime_calls']==0,
          {'runtime_pass':False,'execution_ready':False,'actual_execution_performed':False})
    cpdir=BASE/'full095-cpython-lineno-source-diagnosis-v1'
    cmanifest_path=cpdir/'public-artifacts-manifest-lineno095.json'
    cmanifest=json.loads(cmanifest_path.read_text())
    crefs=[]
    for filename in ['Objects-frameobject.c','Python-frame.c','Objects-codeobject.c','Python-instrumentation.c']:
        actual=ref(cpdir/filename);crefs.append(actual)
        check('CPython_source_hash_'+filename,actual['bytes']==cmanifest[filename]['bytes'] and actual['sha256']==cmanifest[filename]['sha256'],actual)
    csources={f:(cpdir/f).read_text() for f in ['Objects-frameobject.c','Python-frame.c','Objects-codeobject.c','Python-instrumentation.c']}
    check('CPython_line_lookup_source_chain',
          'return PyUnstable_InterpreterFrame_GetLine(f->f_frame);' in csources['Objects-frameobject.c']
          and 'Py_RETURN_NONE;' in csources['Objects-frameobject.c']
          and 'return PyCode_Addr2Line(frame->f_code, addr);' in csources['Python-frame.c']
          and '_PyCode_InitAddressRange(co, &bounds);' in csources['Objects-codeobject.c']
          and 'while (bounds->ar_end <= lasti)' in csources['Objects-codeobject.c']
          and 'frame_obj->f_lineno = line;' in csources['Python-instrumentation.c'],
          {'references':crefs,'conclusion':'For this unmodified runner tracing scope, immutable code and bytecode offset determine the same native line. None is retained. Native runtime speed and UI outcome remain unverified.'})
    check('manifest_stable_after_all_review_reads',sha(MANIFEST.read_bytes())==SEALED_MANIFEST_SHA,ref(MANIFEST))
    check('runner_stable_after_all_review_reads',sha(RUNNER.read_bytes())==SEALED_RUNNER_SHA,ref(RUNNER))
    refs=[ref(PACKAGE/name) for name in sorted(manifest['artifacts'])]+[
          ref(MANIFEST),ref(handoff_path),wrapper,ref(prior_review_path),ref(cmanifest_path),
          ref(BASE/'full095-cpython-lineno-source-diagnosis-v1/source-diagnosis-cpython-lineno095.json'),
          ref(BASE/'full095-cpython-lineno-source-erratum-v1/source-erratum-actual-frame-and-cache095.json')]+crefs
    result={
        'format_version':1,'status':'STOPWRITE_INDEPENDENT_SOURCE_REVIEW_PASSED_RUNTIME_UNRUN',
        'source_gate_passed':True,'runtime_pass':False,'execution_ready':False,
        'runner_sha256':SEALED_RUNNER_SHA,'final_manifest_sha256':SEALED_MANIFEST_SHA,
        'guard_sha256':EXPECTED[GUARD],'source_guard_sha256':EXPECTED[GUARD],
        'binding_sha256':ref(binding_path)['sha256'],
        'source_keys':contract['source_keys'],'execution_argv':expected_argv,
        'actualargv':expected_argv,'exact_argv':expected_argv,'execution_cwd':expected_cwd,
        'actualcwd':expected_cwd,'cwd':expected_cwd,'script_arg_index':1,
        'actualargv_execution_performed':False,
        'review_completed_at_UTC':datetime.now(timezone.utc).isoformat(),
        'review_scope':'Independent SOURCE comparison of the sealed cache/output retry, immutable original/cache/pending/ancestor source chain, preserved binding and exact intended argv/cwd. No project, runner, codec, helper, target bytecode, Qt, Wine, DLL, API, tests or Git was executed; repository files were not read or modified. Current repository readiness and actual Root prelaunch/runtime/saved validation remain separate.',
        'source_artifacts':refs,'independent_standard_library_review':{'checks':len(checks),'passed':len(checks),'blocked':0,'results':checks},
        'whole_SOURCE_inverse':dict(ancestry,retry_to_cache_byteexact=True,
                                    retry_to_original729181_chain_sha256=EXPECTED[ANCESTOR],
                                    retry_stage_coordinate_semantics='Each new retry-stage operation records the source state after its sequential forward edit; inverse processes operations in reverse list order and mutates the recovered source after each individually hash-checked slice. The original pending-v3 ledger separately uses final pending coordinates, reconstructed in source-position order.'),
        'assertion_preservation':{'count':907,'wholetext_unchanged':904,'output_normalized_wholetext_exact':True,'changed_assertions':changed},
        'binding_preservation':{'whole_file_byteexact':True,'BINDING095_wholetext_byteexact':True,'cases_count':len(binding['cases']),
                                'actual95_guard_retained':True,'actual94_baseline_and_case_binding_retained':True},
        'cache_applicability':{'immutable_code_and_offset_native_line_mapping':True,'key':'(id(code),cursor.f_lasti)',
                               'value':'(code,line)','strong_code_reference':True,'None_preserved':True,
                               'original_stack_walk_and_phase_algorithm_preserved':True,
                               'generic_debugger_equivalence_claimed':False,'runtime_speedup_verified':False},
        'runtime_output_contract':contract['output_plan'],'output_absence_observation':output_status,
        'blocking_findings':[],
        'execution_counts':{'project':0,'Wine':0,'Qt':0,'DLL':0,'API':0,'tests':0,'target_bytecode':0,
                            'process_attach_or_signal_or_mutations':0,'Git':0,'tracked_modifications':0,'actual_prelaunch':0},
        'completed_section_increment':0,'full095_runtime_pass':False,'STOPWRITE_after_handoff':True,
        'reviewer_source':ref(Path(__file__)),
    }
    OUT.mkdir(parents=True,exist_ok=True)
    formal_path=OUT/'formal-source-review-cache-retry095.json'
    if formal_path.exists():
        raise AssertionError('formal_review_already_exists_STOPWRITE')
    formal_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'formal_review':ref(formal_path),'checks':len(checks),'source_gate_passed':True,'runtime_pass':False},indent=2))

if __name__ == '__main__':
    if '--retry' in sys.argv:
        review_retry()
    else:
        print(json.dumps(check_inverse_ancestry(),ensure_ascii=False,indent=2))
