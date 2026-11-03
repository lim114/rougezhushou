from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'.cache/run_section_296_window.py';text=p.read_text()
text=text.replace('verify_battle_entry_references_window_296.py','verify_expedition_results_window_297.py')
text=text.replace('296','297')
target=ROOT/'.cache/run_section_297_window.py';assert not target.exists();target.write_bytes(text.encode())
print('Only section/native executable labels adapted; reviewed owned supervisor retained.')
