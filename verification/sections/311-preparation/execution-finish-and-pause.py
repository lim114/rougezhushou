from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, runpy
ROOT = Path(__file__).resolve().parents[1]
def enc(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')
receipt = ROOT / 'verification/sections/311-preparation/finish-current-and-pause.json'
receipt.write_bytes(enc({'section': 311, 'kind': 'direct_latest_user_instruction',
    'instruction': '完成此节后收尾，不再进行下一节',
    'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'meaning': 'Finish311 validation, requirements/index, ordinary push and actual remote verification; then pause. Do not start312.'}))
path = ROOT / 'DEVELOPMENT_CHECKPOINT.json'
cp = json.loads(path.read_bytes())
assert cp['completed_sections'] == 311 and cp['next_section'] == 312
cp['policy'].update(pause_after_active_section_requested=True, new_functional_sections_paused=False,
    stop_after_section=311, current_user_batch_target_section=311, current_user_batch_completed=False,
    latest_pause_instruction_receipt=receipt.relative_to(ROOT).as_posix())
cp['batch_target_section'] = 311
cp['current_batch'].update(end=311, next_section_started=False)
cp['next_action'] = '311本地验收完成；按用户最新要求完成本节普通推送与远端核对后暂停，312不启动，等待用户恢复。'
path.write_bytes(enc(cp))
marker = '<!-- section311-publication-pending -->'
instruction = '用户最新要求：完整完成第311节的提交、要求/索引同步与真实远端核对后暂停本批，不启动312，等待用户明确恢复。'
for name in ('AGENTS.md', 'PROJECT_COMPLETED.md', 'WORK_IN_PROGRESS.md', 'PROJECT_REQUIREMENTS.md', 'CLOUD_HANDOFF.md'):
    path = ROOT / name
    text = path.read_text('utf8')
    assert text.count(marker) == 1
    if instruction not in text:
        text = text.replace(marker, instruction + '\n\n' + marker, 1)
    if name == 'AGENTS.md':
        if '继续P3，312未启动；' in text:
            assert text.count('继续P3，312未启动；') == 1
            text = text.replace('继续P3，312未启动；', '本节完整发布核对后按用户要求暂停，312不启动；', 1)
        else:
            assert text.count('本节完整发布核对后按用户要求暂停，312不启动；') == 1
    path.write_text(text, encoding='utf8')
runpy.run_path(str(ROOT / 'scripts/update_cloud_index.py'))['update'](ROOT)
metadata = (ROOT / '.cache/metadata311.py').read_text('utf8')
metadata = metadata.replace("cp['batch_status']='P3_SECTION311_PUBLISHED'", "cp['batch_status']='P3_SECTION311_PUBLISHED_PAUSED_BY_USER'")
anchor = "cp['current_batch'].update(status=cp['batch_status'],batch_closed=True,next_section=312,next_section_started=False)"
assert metadata.count(anchor) == 1
metadata = metadata.replace(anchor, anchor + "\ncp['policy'].update(development_paused_by_latest_user_request=True,pause_after_active_section_requested=True,new_functional_sections_paused=True,current_user_batch_completed=True)")
metadata = metadata.replace('继续P3剩余节点/敌人/固定地图事项；下一定期全量320，312未启动。', '本批按用户最新要求暂停，312未启动，等待用户明确恢复；下一定期全量320仅在恢复后适用。')
metadata = metadata.replace("'development_paused':False", "'development_paused':True")
metadata = metadata.replace('继续P3，312未启动，下一定期全量320。', '本批按用户要求暂停，312未启动，等待明确恢复；下一定期全量320仅恢复后适用。')
(ROOT / '.cache/metadata311.py').write_text(metadata, encoding='utf8')
publisher = (ROOT / '.cache/publish311.py').read_text('utf8')
anchor = "assert cp['policy']['development_paused_by_latest_user_request'] is False"
assert publisher.count(anchor) == 1
publisher = publisher.replace(anchor,
    "if phase=='functional':assert cp['policy']['development_paused_by_latest_user_request'] is False\n"
    "else:assert cp['policy']['development_paused_by_latest_user_request'] is True and cp['cloud_publication_closeout']['development_paused'] is True\n"
    "assert cp['policy']['pause_after_active_section_requested'] is True and cp['policy']['stop_after_section']==311\n"
    "assert read(cp['policy']['latest_pause_instruction_receipt'])['instruction']=='完成此节后收尾，不再进行下一节'")
(ROOT / '.cache/publish311.py').write_text(publisher, encoding='utf8')
finalizer = (ROOT / '.cache/finalize311_final.py').read_text('utf8')
finalizer = finalizer.replace('311-index-validation-final', '311-index-validation-pause')
(ROOT / '.cache/finalize311_pause.py').write_text(finalizer, encoding='utf8')
(ROOT / 'verification/sections/311-preparation/execution-finish-and-pause.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'finish_section': 311, 'next312_will_not_start': True, 'goal_pause_after_verified_publication': True}))
