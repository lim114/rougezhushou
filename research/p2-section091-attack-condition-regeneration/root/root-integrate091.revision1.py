"""Root-only exact integration and maintained-source check; no project imports."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
BASE = '2cbc45f03f99ed4f04b9c7e2612b58542f909168'
UI = LOCAL / 'p2-continuous-attack-controls-091-ui-candidate'
DEEP = LOCAL / 'p2-section091-deepcolor-regeneration-notes-author'
META = LOCAL / 'root-integration-plan091.json'
SHA = lambda b: hashlib.sha256(b).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def snapshot():
    return {p.relative_to(ROOT).as_posix(): SHA(p.read_bytes())
            for folder in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}

def write_new(path, obj):
    with path.open('xb') as f:
        f.write((json.dumps(obj, ensure_ascii=False, indent=2)+'\n').encode())

def packets():
    out = []
    for folder, name, expected, schema in (
        (UI, 'ui-author-public-manifest091.json', '2b286f356a0d10da925f269f6e303c731adfcf9674efc18eef22363e092a7b53', 'ui'),
        (DEEP, 'public-artifacts-manifest-final.json', 'cfedb0ab204f413d77fe695c614f6667df92886320abc23d5a6d99c9963ece73', 'deep'),
        (LOCAL/'p2-continuous-attack-control-091-independent', 'public-artifacts-manifest-final-independent091.json', '2d3e90c9b8341e6399d5b21611d27cca111eab2b1ea7331c2122a8658f0ce6e7', 'ui'),
    ):
        mf = folder/name
        raw = mf.read_bytes()
        assert SHA(raw) == expected, mf
        d = json.loads(raw)
        if schema == 'ui':
            assert d['format_version'] == 1
            rows = d['files']
            count, total = d['file_count'], d['total_bytes']
        else:
            assert d['schema_version'] == 1
            rows = d['artifacts']
            count, total = d['artifact_count'], d['artifact_bytes']
        assert len(rows) == count and sum(r['bytes'] for r in rows) == total
        names = set()
        for row in rows:
            name = row['archive_path'] if schema == 'ui' else row['path']
            relative = Path(name)
            assert not relative.is_absolute() and '..' not in relative.parts and name not in names
            names.add(name)
            source = Path(row['source_path']) if schema == 'ui' else folder/relative
            local = folder/relative
            assert source.resolve().is_relative_to(LOCAL.resolve()), source
            assert local.resolve().is_relative_to(folder.resolve())
            assert local.read_bytes() == source.read_bytes(), local
            b = source.read_bytes()
            assert len(b) == row['bytes'] and SHA(b) == row['sha256'], source
        out.append({'path': str(mf), 'sha256': expected, 'files': count, 'bytes': total})
    return out

phase = sys.argv[1]
assert git('branch','--show-current').decode().strip() == 'codex/p2-development'
assert git('rev-parse','HEAD').decode().strip() == BASE
if phase == 'prepare':
    assert not git('status','--porcelain').strip()
    checked = packets()
    specs = [
        ('rouge/app.py', UI/'candidate/rouge/app.py', '6a107fa37d2c21b9160131aa8c901fc2342ef7a422c3134dc0579ea24f4b56a2', 'fa27d6eceaf88f8caf1bc4e994641c6d110884ee9fbf673ab7d46a355cc41143'),
        ('scripts/verify_damage_ui.py', UI/'candidate/scripts/verify_damage_ui.py', '3b8ff41400002ff8616cb99690e47dcea9793b32bcdaa3ceb2bea20150fa396b', '0b0dcbcade07f0ff11b2bdcba7c7598a696ff4ece3418bc296312ce97c2a2d54'),
        ('rouge/operator_engine.py', DEEP/'draft-tree/rouge/operator_engine.py', None, 'f50e6b992525da0cb3daedb16a3cd4cd45f80052b063007224bd63ac8de93f50'),
        ('rouge/reporting.py', DEEP/'draft-tree/rouge/reporting.py', None, 'b71dec77a7cb7ba88da7324982be6f4fd59c02ae8cd91bce44fe92f3546f5d01'),
    ]
    rows=[]
    for name, source, oldsha, newsha in specs:
        before=git('show', f'{BASE}:{name}')
        after=source.read_bytes()
        assert (ROOT/name).read_bytes() == before
        assert (oldsha is None or SHA(before)==oldsha) and SHA(after)==newsha, name
        if name.endswith('.py'): ast.parse(after.decode(), filename=name)
        assert (b'\r\n' in before)==(b'\r\n' in after), name
        rows.append({'target_path':name,'source_path':str(source),'original_sha256':SHA(before),'new_sha256':newsha,'bytes':len(after)})
    policies=json.loads((LOCAL/'section091-policy-updates.json').read_bytes())
    assert policies['actual_base']==BASE and policies['applied'] is False
    for row in policies['updates']:
        source=Path(row['draft_source_path']);before=(ROOT/row['target_path']).read_bytes();after=source.read_bytes()
        assert before==git('show', f"{BASE}:{row['target_path']}")
        assert SHA(before)==row['original_sha256'] and SHA(after)==row['new_sha256']
        assert (b'\r\n' in before)==(b'\r\n' in after)
        rows.append({**row,'source_path':str(source),'bytes':len(after)})
    before=snapshot();assert len(before)==730
    write_new(META, {'format_version':1,'status':'PREPARED_NOT_APPLIED_PENDING_DEEP_INDEPENDENT_FINAL', 'base':BASE,'packets':checked,'changes':rows,'before_maintained_sha256':before,'project_calls':0})
    print(json.dumps({'prepared':True,'files':len(rows),'maintained':len(before),'project_calls':0}))
elif phase == 'apply':
    assert not git('status','--porcelain').strip()
    plan=json.loads(META.read_bytes());assert plan['base']==BASE and snapshot()==plan['before_maintained_sha256']
    packets()
    ind_path=Path(sys.argv[2]);ind=json.loads(ind_path.read_bytes())
    assert SHA(ind_path.read_bytes())==sys.argv[3]
    assert 'PASS' in ind['status'], ind['status']
    # All candidates are checked before the first tracked write.
    for row in plan['changes']:
        assert SHA((ROOT/row['target_path']).read_bytes())==row['original_sha256']
        b=Path(row['source_path']).read_bytes();assert len(b)==row['bytes'] and SHA(b)==row['new_sha256']
    for row in plan['changes']:
        (ROOT/row['target_path']).write_bytes(Path(row['source_path']).read_bytes())
    write_new(LOCAL/'root-integration-applied091.json', {'format_version':1,'status':'APPLIED_PENDING_ROOT_CHECKS_WINDOW_ARCHIVE','base':BASE,'changes':plan['changes'],'Deep_independent':{'path':str(ind_path),'sha256':sys.argv[3]},'project_calls':0})
    print(json.dumps({'applied':True,'files':len(plan['changes']),'project_calls':0}))
elif phase == 'source':
    plan=json.loads(META.read_bytes());after=snapshot();before=plan['before_maintained_sha256']
    expected={row['target_path'] for row in plan['changes'] if row['target_path'] in before}
    assert set(after)==set(before) and len(after)==730
    drift={n for n in after if after[n]!=before[n]};assert drift==expected,drift
    for row in plan['changes']:
        b=(ROOT/row['target_path']).read_bytes();assert SHA(b)==row['new_sha256'] and len(b)==row['bytes']
    result={'format_version':1,'passed':True,'base':BASE,'old_maintained':730,'current_maintained':730,'unchanged_maintained':730-len(drift),'changed_maintained':sorted(drift),'source_sha256_after':after,'frozen_candidate_and_policy_bytes_exact':True,'project_calls':0}
    write_new(LOCAL/'root-source-091.json',result)
    print(json.dumps({'passed':True,'current':730,'unchanged':730-len(drift),'changed':sorted(drift),'project_calls':0}))
else:
    raise ValueError(phase)
