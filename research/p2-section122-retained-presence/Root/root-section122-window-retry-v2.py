"""Root second actual122 GUI attempt, exact corrected public producer fixture only."""
import argparse,copy,hashlib,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source-manifest-sha256',required=True);a=p.parse_args()
B=Path('/workspace/.continuation');R=Path('/workspace/rougezhushou');old=B/'section122-window-source-v1';new=B/'section122-window-source-v2';guard=B/'section122-candidate-source-v1.json'
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
assert (B/'section122-window-actual-v1.exit-code').read_bytes()==b'1\n'
w=json.loads((B/'section122-window-actual-v1/receipt.json').read_bytes());assert w['failure']['type']=='KeyError' and w['failure']['message']=="'rogue_6_active_tool_5'" and w['source_drift']==[]
assert w['runner_sha256']==sha(old/'window122.py') and w['cases_sha256']==sha(old/'cases.json') and w['native_helper_sha256']==sha(old/'native_evidence.py')
assert sha(new/'MANIFEST.json')==a.source_manifest_sha256
subprocess.run(['python3',str(B/'root-verify-sealed-source-v2.py'),str(new/'MANIFEST.json'),'--sha256',a.source_manifest_sha256],check=True)
v=json.loads((old/'cases.json').read_bytes());expected=copy.deepcopy(v);packet=expected['string_ingress'][1];assert packet['id']=='held_bar';ids=packet['observed']['relics']['ids'];assert ids==['rogue_6_relic_legacy_15','rogue_6_relic_legacy_103','rogue_6_active_tool_5'];ids.remove('rogue_6_active_tool_5')
assert json.loads((new/'cases.json').read_bytes())==expected
assert (new/'window122.py').read_bytes().replace(sha(new/'cases.json').encode(),sha(old/'cases.json').encode())==(old/'window122.py').read_bytes()
g=json.loads(guard.read_bytes());actual=dict(sorted((q.relative_to(R).as_posix(),sha(q)) for d in ('rouge','tests','scripts') for q in (R/d).rglob('*') if q.is_file() and q.suffix in ('.py','.json') and '__pycache__' not in q.parts));assert actual==g['source_sha256'] and all(sha(R/q)==v for q,v in g['source_additional_sha256'].items())
assert g['section']==122 and w['source_guard_sha256']==sha(guard)
assert w['source_before']==w['source_after']==g['source_sha256'] and w['source_count']==len(actual)
assert w['source_additional_before']==w['source_additional_after']==g['source_additional_sha256']
def win(q):return 'Z:'+str(q).replace('/','\\')
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['ROUGE_TEST_CJK_FONT']=r'Z:\usr\share\fonts\opentype\noto\NotoSansCJK-Regular.ttc'
subprocess.run(['python3',str(B/'root-run-primary-v1.py'),'--prefix',str(B/'section122-window-actual-v2'),'--','/workspace/.compat/run-wine-python.sh',win(new/'window122.py'),'--root',win(R),'--guard',win(guard),'--out',win(B/'section122-window-actual-v2'),'--source-count',str(len(actual))],cwd=R,env=env,check=True)
assert (B/'section122-window-actual-v2.exit-code').read_bytes()==b'0\n'
