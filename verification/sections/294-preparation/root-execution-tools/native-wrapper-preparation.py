from pathlib import Path
import ast
root=Path(__file__).resolve().parents[1]
raw=(root/'.cache/run_section_293_window.py').read_text(encoding='utf8')
raw=raw.replace('293','294').replace('verify_resting_corner_window_294.py','verify_direct_map_window_294.py')
raw=raw.replace("'--visible-ms','30000'","'--visible-ms','60000'")
assert "'--visible-ms','60000'" in raw
ast.parse(raw);dest=root/'.cache/run_section_294_window.py';assert not dest.exists();dest.write_bytes(raw.encode('utf8'))
print('Prepared owned294 native runner with explicit60000ms; original supervisor semantics preserved.')
