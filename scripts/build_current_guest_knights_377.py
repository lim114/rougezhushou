"""Check the complete compiled current reference/source pins; never run game/Qt."""
from pathlib import Path
import argparse,json,sys
R=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 if not a.check:raise ValueError('Compiled public source evidence is immutable; explicit --check required')
 sys.path.insert(0,str(R));from rouge import current_guest_knights as model
 d=model.packet()
 if d is None:raise ValueError('Compiled current bindings or full source evidence differ')
 for sid,binding in d['data']['bindings'].items():
  r=model.reference(sid)
  if r is None or len(r['rows'])!=len(binding['rows']):raise ValueError('Exact current binding differs')
 print(json.dumps({'section':377,'passed':True,'source_check_only':True,'exact_configs':len(d['data']['bindings']),
  'exact_references':sum(len(v['rows'])for v in d['data']['bindings'].values()),'manifest_sha256':model.MANIFEST_SHA256,
  'tests_or_windows_started':False},ensure_ascii=False))
if __name__=='__main__':main()
