from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent
FREEZE='verification/full-335/source-freeze-binding-recheck2.json';PIN='a428e10af9cadc6acafcae044524308ada1f7816e7512a4346c59efc74b71815'
def read(p):return json.loads(p.read_bytes())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def guard():
 assert sha(ROOT/FREEZE)==PIN
 data=read(ROOT/FREEZE);old=read(ROOT/'verification/full-335/source-freeze-attempt1.json');repair=read(ROOT/'verification/full-335/binding-repair/repair-scope.json')
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==old['parent_commit']
 assert set(data['source_sha256'])==set(old['source_sha256']) and data['selectors']==old['selectors'] 
 changed={k for k in old['source_sha256']if data['source_sha256'][k]!=old['source_sha256'][k]}
 assert changed=={r['file']for r in repair['files']}==set(data['only_changed_source_files'])and not repair['production_changed']and all(r['complete_AST_outside_binding_and_one_parser_option_identical']for r in repair['files'])
 assert set(data['supplemental_public_inputs_sha256'])==set(old['supplemental_public_inputs_sha256'])
 for n,h in old['supplemental_public_inputs_sha256'].items():assert n in changed or data['supplemental_public_inputs_sha256'][n]==h
 for group in ('source_sha256','supplemental_public_inputs_sha256'):
  for n,h in data[group].items():assert sha(ROOT/n)==h,n
 return data
