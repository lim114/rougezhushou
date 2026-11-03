"""Only public temporary files; reproduce unsafe fixed temporary-path writes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--source-root',type=Path,default=ROOT)
args=parser.parse_args();SOURCE=args.source_root.resolve()
sys.path.insert(0,str(SOURCE))
from rouge.account_cache import AccountCache
from rouge.run_state import RunState

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
source_paths=[SOURCE/'rouge/account_cache.py',SOURCE/'rouge/run_state.py',SOURCE/'rouge/persistence_install.py']
before_source={str(p.relative_to(SOURCE)):digest(p) for p in source_paths}
rows=[]
for owner in ('run','cache'):
    for link_kind in ('live_symlink','dangling_symlink','hardlink'):
        for raced_destination in (False,True):
            with tempfile.TemporaryDirectory(prefix='public-tmp-repro-',dir=HERE) as folder:
                folder=Path(folder);destination=folder/(owner+'.json')
                record=RunState(destination) if owner=='run' else AccountCache(destination,{})
                temporary=destination.with_suffix('.tmp');target=folder/'public-unrelated-target.txt'
                if link_kind!='dangling_symlink':target.write_bytes(b'PUBLIC ORIGINAL MUST REMAIN')
                target_before=digest(target)
                target_bytes_before=target.read_bytes().hex() if target.exists() else None
                if link_kind=='hardlink':
                    import os
                    os.link(target,temporary)
                else:temporary.symlink_to(target.name)
                if raced_destination:destination.write_bytes(b'PUBLIC LATER DESTINATION MUST REMAIN')
                destination_before=digest(destination)
                destination_bytes_before=destination.read_bytes().hex() if destination.exists() else None
                saved=record.save()
                protected_changed=digest(target)!=target_before
                destination_after=digest(destination)
                if raced_destination:
                    assert not saved and destination_after==destination_before
                    assert record.save_issue is not None
                    assert not record.save()
                rows.append({'owner':owner,'temporary_kind':link_kind,'raced_destination':raced_destination,
                    'save_returned':saved,'protected_target_created_or_changed':protected_changed,
                    'target_sha256_before':target_before,'target_sha256_after':digest(target),
                    'target_bytes_before_hex':target_bytes_before,
                    'target_bytes_after_hex':target.read_bytes().hex() if target.exists() else None,
                    'destination_bytes_before_hex':destination_bytes_before,
                    'destination_bytes_after_hex':destination.read_bytes().hex() if destination.exists() else None,
                    'destination_protected_on_collision':destination_after==destination_before if raced_destination else None,
                    'failure_latched':record.save_issue is not None,
                    'destination_is_symlink_after':destination.is_symlink()})
after_source={str(p.relative_to(SOURCE)):digest(p) for p in source_paths}
assert before_source==after_source
result={'scope':'Necessary isolated public-file reproduction only, not full suite or private state',
        'source_root':str(SOURCE),'actual_loaded_run_module':sys.modules[RunState.__module__].__file__,
        'actual_loaded_cache_module':sys.modules[AccountCache.__module__].__file__,
        'source_sha256':before_source,'source_drift':[],'rows':rows,
        'protected_target_changes':sum(row['protected_target_created_or_changed'] for row in rows),
        'old_first_install_destination_guard_still_holds':all(row['destination_protected_on_collision'] for row in rows if row['raced_destination']),
        'production_source_written':False,'private_state_accessed':False}
print(json.dumps(result,ensure_ascii=False,indent=2))
