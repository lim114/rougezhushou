from pathlib import Path
import ast
root=Path(__file__).resolve().parents[1]
src=(root/'.cache/run_section_292_window.py').read_text(encoding='utf8')
raw=src.replace('292','293').replace('verify_event_preview_filters_window_293.py','verify_resting_corner_window_293.py').encode('utf8')
ast.parse(raw)
target=root/'.cache/run_section_293_window.py';assert not target.exists();target.write_bytes(raw)
print('Prepared owned293 window runner; supervisor behavior unchanged except section label.')
