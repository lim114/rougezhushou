from pathlib import Path
import datetime, hashlib, json, shutil

base = Path(__file__).parent
draft = base / 'draft077'
assert not draft.exists()
shutil.copytree(base / 'baseline', draft, ignore=shutil.ignore_patterns('__pycache__'))
name = 'rouge/operator_engine.py'
raw = (base / 'baseline' / name).read_bytes()
old = b"            regular('magic',extra,name='\xe9\xa3\x98\xe6\xb5\xae\xe5\xa4\xa7\xe5\x9c\xb0\xe4\xb9\x8b\xe4\xb8\x8a')\r\n"
new = "            regular('magic',extra,times=1 if '飘浮大地之上' in self.tv else 0,name='飘浮大地之上')\r\n".encode()
assert raw.count(old) == 1
edited = raw.replace(old, new)
(draft / name).write_bytes(edited)
receipt = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'baseline_commit': '225cb66dc89143a3cd3a884bd6c62f47ed9d36bc',
           'changed_file': name, 'before_sha256': hashlib.sha256(raw).hexdigest(),
           'after_sha256': hashlib.sha256(edited).hexdigest(), 'original_CRLF_preserved': True,
           'only_selected_talent_gate_on_additional_event_multiplicity': True,
           'weight_validation_formula_static_attributes_and_unknown_clocks_unchanged': True,
           'zero_component_shape_and_original_owner_attack_timeline_retained': True}
(base / 'draft-receipt077.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(receipt)
