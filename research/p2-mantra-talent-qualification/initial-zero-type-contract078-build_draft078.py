from pathlib import Path
import datetime,hashlib,json,shutil
base=Path(__file__).parent
draft=base/'draft078'
assert not draft.exists()
shutil.copytree(base/'baseline',draft,ignore=shutil.ignore_patterns('__pycache__'))
name='rouge/operator_engine.py'
raw=(base/'baseline'/name).read_bytes()
old="                emit('麻痹触发天赋',attack*self.talent('噤声限域','atk_scale'),'elemental',triggers)\r\n".encode()
new="                emit('麻痹触发天赋',attack*self.talent('噤声限域','atk_scale'),'elemental',triggers if '噤声限域' in self.tv else 0)\r\n".encode()
assert raw.count(old)==1
edited=raw.replace(old,new)
(draft/name).write_bytes(edited)
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':'225cb66dc89143a3cd3a884bd6c62f47ed9d36bc','changed_file':name,'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(edited).hexdigest(),'original_CRLF_preserved':True,'only_actual_selected_talent_effective_emit_count':True,'raw_declared_count_parsing_range_rows_and_old_errors_unchanged':True,'global_palsy_source_possible_semantics_S3_overflow_and_eligible_zero_attack_unknown_unchanged':True,'77_patch_not_included':True}
(base/'draft-receipt078.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(out)
