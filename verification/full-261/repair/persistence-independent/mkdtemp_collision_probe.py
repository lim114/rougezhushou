"""Actual directory creation under forced public name collisions; no mocks of IO."""
import hashlib,json,os,platform,tempfile
from pathlib import Path
from unittest.mock import patch

rows=[]
for kind in ('regular','directory','live_directory_symlink','dangling_directory_symlink'):
    with tempfile.TemporaryDirectory(prefix='public-mkdir-contract-') as folder:
        parent=Path(folder);collision=parent/'.rouge-record-collision';fresh=parent/'.rouge-record-fresh'
        target=parent/'public-target-directory'
        if kind=='regular':collision.write_bytes(b'PUBLIC ORIGINAL FILE')
        elif kind=='directory':
            collision.mkdir();(collision/'original.txt').write_bytes(b'PUBLIC ORIGINAL DIRECTORY CHILD')
        elif kind=='live_directory_symlink':
            target.mkdir();(target/'original.txt').write_bytes(b'PUBLIC ORIGINAL TARGET CHILD')
            collision.symlink_to(target.name,target_is_directory=True)
        else:collision.symlink_to(target.name,target_is_directory=True)
        def snapshot():
            value={'collision_is_symlink':collision.is_symlink(),'target_exists':target.exists()}
            if collision.is_symlink():value['link_text']=str(collision.readlink())
            elif collision.is_file():value['collision_bytes_hex']=collision.read_bytes().hex()
            elif collision.is_dir():value['collision_children']={p.name:p.read_bytes().hex() for p in collision.iterdir() if p.is_file()}
            if target.is_dir():value['target_children']={p.name:p.read_bytes().hex() for p in target.iterdir() if p.is_file()}
            return value
        before=snapshot();allocated=None;error=None
        try:
            with patch('tempfile._get_candidate_names',return_value=iter(('collision','fresh'))):
                directory=tempfile.TemporaryDirectory(dir=parent,prefix='.rouge-record-')
            allocated=Path(directory.name)
            assert allocated==fresh, (kind,str(allocated))
            assert allocated.is_dir() and not allocated.is_symlink()
            (allocated/'public-owned-fd-test.txt').write_bytes(b'PUBLIC NEW DIRECTORY CONTENT')
            directory.cleanup()
        except BaseException as exc:error={'type':type(exc).__name__,'message':str(exc)}
        after=snapshot()
        rows.append({'collision_kind':kind,'allocated_fresh_name':allocated==fresh if allocated else False,
                     'original_before':before,'original_after':after,'original_unchanged':before==after,'error':error})
result={'platform':platform.system(),'os_name':os.name,'actual_tempfile_file':tempfile.__file__,
        'forced_candidate_names_only':True,'os_mkdir_or_file_IO_mocked':False,'rows':rows,
        'passed':all(row['allocated_fresh_name'] and row['original_unchanged'] and row['error'] is None for row in rows),
        'private_state_accessed':False,'game_actions':0,'chat_requests':0}
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if result['passed'] else 1)
