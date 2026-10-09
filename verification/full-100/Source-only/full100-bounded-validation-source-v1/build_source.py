"""Source-only transport of the archived healthy full090 GUI suite.

This builder reads text and compiles text without importing or executing targets.
The generated runner is for Root's fresh actual full100 validation only.
"""
from pathlib import Path
import ast
import hashlib
import json

PACKET = Path(__file__).resolve().parent
BASE = Path('/workspace/rougezhushou/verification/full-090/wine-ui-runner.py')
BASE_SHA = '9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9'
base_bytes = BASE.read_bytes()
assert hashlib.sha256(base_bytes).hexdigest() == BASE_SHA
base = base_bytes.decode('utf-8')
source = '\n'.join(base.splitlines()[16:]) + '\n'
operations = []

def replace_once(old, new, purpose):
    global source
    assert source.count(old) == 1, (purpose, source.count(old))
    source = source.replace(old, new, 1)
    operations.append({'purpose': purpose,
                       'old_sha256': hashlib.sha256(old.encode()).hexdigest(),
                       'new_sha256': hashlib.sha256(new.encode()).hexdigest()})

prefix = r'''"""Fresh bounded actual full100 Wine Qt validation; no runtime result yet."""
import argparse, functools, hashlib, json, os, sys, threading, time
from pathlib import Path

_parser100 = argparse.ArgumentParser()
_parser100.add_argument('--root', required=True)
_parser100.add_argument('--guard', required=True)
_parser100.add_argument('--out', required=True)
_args100 = _parser100.parse_args()
ROOT = Path(_args100.root).resolve()
OUT = Path(_args100.out).resolve()
if OUT == ROOT or OUT.is_relative_to(ROOT):
    raise ValueError('The fresh evidence directory must be outside the repository')
_guard_bytes100 = Path(_args100.guard).read_bytes()
_guard100 = json.loads(_guard_bytes100)
_expected100 = _guard100['source_sha256']
_additional100 = _guard100['source_additional_sha256']
if not isinstance(_expected100, dict) or not _expected100:
    raise ValueError('A real completed100 maintained Source map is required')
if not isinstance(_additional100, dict) or 'CORE_0.70_VERIFICATION.json' not in _additional100:
    raise ValueError('Completed100 additional Source map must include CORE registration')

def maintained_source100():
    result = {}
    for name in ('rouge', 'tests', 'scripts'):
        folder = ROOT / name
        if not folder.is_dir():
            raise ValueError('Missing maintained Source folder: ' + name)
        for path in sorted(folder.rglob('*')):
            relative = path.relative_to(ROOT)
            if '__pycache__' in relative.parts or path.suffix not in ('.py', '.json'):
                continue
            if path.is_symlink():
                raise ValueError('Source symlink refused: ' + str(relative))
            if path.is_file():
                result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))

def additional_source100():
    result = {}
    for relative in _additional100:
        path = ROOT / relative
        if (not isinstance(relative, str) or Path(relative).is_absolute()
                or '..' in Path(relative).parts or path.is_symlink()
                or not path.resolve().is_relative_to(ROOT)):
            raise ValueError('Invalid supplemental Source path: ' + str(relative))
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))

if maintained_source100() != _expected100:
    raise AssertionError('Completed100 maintained Source drift before project imports')
if additional_source100() != _additional100:
    raise AssertionError('Completed100 supplemental Source drift before project imports')
OUT.mkdir(parents=True, exist_ok=False)
(OUT / 'source100-guard-input.json').write_bytes(_guard_bytes100)
_started100 = time.perf_counter()
_deadline100 = _started100 + 600
_restorations100 = []
_count_enabled100 = False

def _deadline_check100():
    if time.perf_counter() >= _deadline100:
        raise TimeoutError('Fresh full100 deadline of600 seconds reached')

def _hard_timeout100():
    record = {'passed': False, 'scope': 'actual full100 hard deadline',
              'deadline_seconds': 600, 'elapsed_seconds': time.perf_counter()-_started100,
              'guard_sha256': hashlib.sha256(_guard_bytes100).hexdigest(),
              'full_function_vector_measured': False}
    try:
        (OUT / 'hard-timeout-100.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
        print(json.dumps({'passed': False, 'hard_deadline': 600}), flush=True)
    finally:
        os._exit(124)

_timer100 = threading.Timer(600, _hard_timeout100)
_timer100.daemon = True
_timer100.start()

def _replace_binding100(owner, name, replacement):
    original = getattr(owner, name)
    _restorations100.append((owner, name, original))
    setattr(owner, name, replacement)

def _increment100(key):
    _deadline_check100()
    if _count_enabled100:
        entry_counts090[key] = entry_counts090.get(key, 0) + 1

def _install_narrow_observers100():
    # Every wrapper calls its actual original; no return, input, or state substitution.
    import rouge.damage as damage100
    import rouge.estimate as estimate100
    import rouge.reporting as reporting100
    import rouge.run_state as run100
    import rouge.operator_engine as engine100

    def instrument(owner, name, key):
        original = getattr(owner, name)
        @functools.wraps(original)
        def passthrough(*args, **kwargs):
            _increment100(key)
            return original(*args, **kwargs)
        _replace_binding100(owner, name, passthrough)

    instrument(damage100, 'calculate_damage', 'calculate_damage')
    instrument(estimate100, 'format_estimate', 'format_estimate')
    original_report100 = reporting100.format_report
    @functools.wraps(original_report100)
    def report100(result, *, technical=False):
        _increment100('format_report_technical' if technical else 'format_report_default')
        return original_report100(result, technical=technical)
    _replace_binding100(reporting100, 'format_report', report100)
    for name in ('__init__', 'apply', 'load'):
        if hasattr(run100.RunState, name):
            instrument(run100.RunState, name, 'RunState.' + name)

    original_plan100 = engine100.Combat.plan
    @functools.wraps(original_plan100)
    def plan100(self, normal=False, window=None):
        _deadline_check100()
        selected = _count_enabled100 and profile_case090 is not None and normal is True
        if selected:
            profile_trace090.append({'event':'actual_same_call_normal_plan_entry','normal':True})
        returned = original_plan100(self, normal=normal, window=window)
        if selected:
            profile_trace090.append({'event':'actual_same_call_normal_plan_return',
                                     'returned_not_none': returned is not None})
        return returned
    _replace_binding100(engine100.Combat, 'plan', plan100)
    original_calculate100 = engine100.Combat.calculate
    @functools.wraps(original_calculate100)
    def calculate100(self):
        _deadline_check100()
        returned = original_calculate100(self)
        if (_count_enabled100 and profile_case090 is not None
                and self.s['operator']=='char_4182_oblvns'
                and profile_case090['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal'):
            actual_plan_returns = [row for row in profile_trace090
                                  if row['event']=='actual_same_call_normal_plan_return']
            profile_trace090.append({'event':'actual_same_call_Combat_calculate_return',
                'normal_plan_return_not_none': len(actual_plan_returns)==1
                    and actual_plan_returns[0]['returned_not_none'] is True,
                'actual_ranged_condition_consumed':self.ranged_attack_condition_consumed,
                'actual_selected_note_max_cnt':self.tv['颂乐音符']['max_cnt']})
        return returned
    _replace_binding100(engine100.Combat, 'calculate', calculate100)

'''

replace_once("ROOT=Path(r'Z:\\workspace\\rougezhushou')\nOUT=Path(r'Z:\\workspace\\.compat')\n", '', 'Use fresh CLI paths; never the historical mutable output directory')
start = source.index('def profile090(frame,event,value):\n')
end = source.index('\ndef projection090(result):', start)
replace_once(source[start:end], '', 'Remove global frame profile and local-variable inspection')
old_hash = "def source_hashes():\n    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()\n            for folder in (ROOT/'rouge',) for p in sorted(folder.rglob('*'))\n            if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}\n"
replace_once(old_hash, "def source_hashes():\n    return maintained_source100()\n", 'Whole maintained Root100 set rather than historical126-source snapshot')
replace_once('    import rouge.app as module\n', '    _install_narrow_observers100()\n    import rouge.app as module\n', 'Install targeted original-call observers before application imports')
replace_once('        previous_profile090=sys.getprofile();sys.setprofile(profile090)\n', '        _count_enabled100=True\n', 'Count actual startup entries without global profiling')
replace_once('        sys.setprofile(previous_profile090)\n', '        _count_enabled100=False\n', 'Close startup observation scope')
replace_once('        previous090=sys.getprofile()\n        sys.setprofile(profile090)\n', '        previous090=_count_enabled100\n        _count_enabled100=True\n', 'Narrow counters only in inherited86-89 verification group')
replace_once("                        assert returned090[0]['normal_not_none'] is True\n", "                        assert returned090[0]['normal_plan_return_not_none'] is True\n", 'Check actual normal plan return; do not claim frame-local normal observation')
replace_once('            profile_case090=None;sys.setprofile(previous090)\n', '            profile_case090=None;_count_enabled100=previous090\n', 'Restore observer scope without touching sys profile')
replace_once("        receipt['actual_source090_commit']='5e2ff697402d06e78b239e01f0b4307b50dd5633'\n        receipt['maintained_actual_source_files090']=730\n", "        receipt['inherited_expected_projection_source090_commit']='5e2ff697402d06e78b239e01f0b4307b50dd5633'\n        receipt['maintained_actual_source_files100']=len(before)\n", 'Separate expected historical projections from actual100 Source')
replace_once("    receipt['passed']=True\n", "    required_png100=['wine-sown-tile-control-100.png','wine-movement-reference-100.png',\n                     'wine-medical-trait-100.png','wine-window-100.png']\n    receipt['screenshots100']=[{'file':name,'bytes':(OUT/name).stat().st_size,\n        'sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest()} for name in required_png100]\n    assert len(receipt['screenshots100'])==4 and all(row['bytes']>0 for row in receipt['screenshots100'])\n    receipt['passed']=True\n", 'Four real existing GUI screenshots with actual byte receipts; Root must view')
replace_once("    after=source_hashes();drift=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]\n", "    after=source_hashes();drift=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]\n    additional_after100=additional_source100()\n    additional_drift100=[n for n in sorted(set(_additional100)|set(additional_after100))\n                         if _additional100.get(n)!=additional_after100.get(n)]\n    receipt['source_additional_sha256']=_additional100\n    receipt['source_additional_sha256_after']=additional_after100\n    receipt['source_additional_drift']=additional_drift100\n    if additional_drift100:receipt['passed']=False;receipt['complete_ui_validation']=False\n", 'Require supplemental Root100 Source agreement after actual window closes')
replace_once("    print(json.dumps(receipt,ensure_ascii=False))\n    sys.exit(0 if receipt['passed'] else 1)\n", "    for owner100,name100,original100 in reversed(_restorations100):\n        setattr(owner100,name100,original100)\n    _timer100.cancel()\n    print(json.dumps({'passed':receipt['passed'],'total_actual_checks':receipt.get('total_actual_checks'),\n          'elapsed_seconds':receipt['elapsed_seconds'],'receipt':'wine-ui-100.json'},ensure_ascii=False))\n    sys.exit(0 if receipt['passed'] else 1)\n", 'Small stdout and original binding restoration; no giant invocation output')
replace_once("    with tempfile.TemporaryDirectory() as folder:\n", "    with tempfile.TemporaryDirectory(prefix='rouge-full100-') as folder:\n", 'Fresh real native temporary runtime storage')
replace_once("         'checks':checks,'passed':False,'complete_ui_validation':False,'plain_text_normalization':'QPlainTextEdit converts non-breaking spaces to ordinary spaces'}\n", "         'checks':checks,'passed':False,'complete_ui_validation':False,'plain_text_normalization':'QPlainTextEdit converts non-breaking spaces to ordinary spaces',\n         'source100_guard_sha256':hashlib.sha256(_guard_bytes100).hexdigest(),\n         'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),\n         'deadline_seconds':600,'global_profile_or_trace_used':False,\n         'old095_complete_function_vector_measured':False,\n         'old090_frame_local_normal_observed':False,\n         'normal_plan_original_return_observed_instead':True,\n         'specialist96_100_validation_in_this_runner':False,\n         'scope_note100':'Healthy maintained full090 functional suite transported to actual100. Separate96-100 receipts required. No old095 complete invocation vector, native Windows, capture or chat certification.'}\n", 'Honest fresh bounded scope, Source identity and explicit unmeasured vectors')
for old, new in [('wine-ui-report-difference-090.json','wine-ui-report-difference-100.json'),
                 ('wine-sown-tile-control-090.png','wine-sown-tile-control-100.png'),
                 ('wine-movement-reference-090.png','wine-movement-reference-100.png'),
                 ('wine-medical-trait-090.png','wine-medical-trait-100.png'),
                 ('wine-window-090.png','wine-window-100.png'),
                 ('wine-ui-failure-090.png','wine-ui-failure-100.png'),
                 ('wine-ui-new-states-090.json.gz','wine-ui-new-states-100.json.gz'),
                 ('wine-ui-090.json','wine-ui-100.json')]:
    assert old in source, old
    source = source.replace(old,new)
    operations.append({'purpose':'Fresh evidence filename', 'old':old,'new':new})
source = prefix + source
assert 'sys.setprofile' not in source and 'sys.settrace' not in source
compile(source, str(PACKET/'window.py'), 'exec')
ast.parse(source)
(PACKET/'window.py').write_text(source, encoding='utf-8')
contract = {'format_version':1,'status':'Source only; no runtime result',
    'origin_file':str(BASE),'origin_bytes':len(base_bytes),'origin_sha256':BASE_SHA,
    'archived_passed_functional_check_count':4283,
    'origin_static_assert_count':sum(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(base))),
    'generated_static_assert_count':sum(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(source))),
    'old_source_guard_removed':True,'old_profile_function_removed':True,
    'inherited_assertion_expression_change':{'old':"returned090[0]['normal_not_none'] is True",
        'new':"returned090[0]['normal_plan_return_not_none'] is True",
        'reason':'Real original plan return is observed; frame-local normal is not inspected.'},
    'other_inherited_product_assertions_changed':False,
    'old_false_pending_blocks_removed':True,
    'source_compilation_only':True,'target_modules_imported':False,
    'old095_invocation_vector_unmeasured':True,
    'future_root100_guard_required':True,'future_runtime_results':None,
    'operations':operations}
(PACKET/'source-contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'Source-only compile succeeded','runner_bytes':len(source.encode()),
    'runner_sha256':hashlib.sha256(source.encode()).hexdigest(),
    'static_asserts':contract['generated_static_assert_count']},ensure_ascii=False))
