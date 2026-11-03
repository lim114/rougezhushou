from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
def digest(path):
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()
def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

save('source-handoff088.json', {
    'status': 'SOURCE_CONFIRMED_CANDIDATE_NOT_COMPLETED_SECTION88',
    'confirmed_problem': 'Active continuous_attacks strings use Python truthiness without a text guard.',
    'static_literal_gets': 12,
    'actual_source_public_calls': 16,
    'explicit_three_text_requests': 48,
    'formatter_internal_entries_instrumented': False,
    'saved_compare_new_project_calls': 0,
    'tests': 0, 'Qt': 0, 'Wine': 0, 'tracked_mutations': 0,
    'scope': 'Three active controls and one inactive control; other event/periodic/qualification paths need bounded product validation.',
    'unknown': ['Native game clocks', 'All-owner qualification union not inferred from UI or final cycle'],
    'production_hashes_unchanged_during_16_calls': True,
    'original_source16_not_to_be_repeated': True,
    'product_authorization': 'Root separately authorized a frozen proposal and bounded external product draft, after this source seal.',
    'unconfirmed_leads': ['SP multiplication/negative composition', 'Other Wisdel route attachment'],
})
files=[]
for path in sorted(ROOT.iterdir()):
    if path.is_file() and path.name != 'public-artifacts-manifest-source088.json':
        size, sha=digest(path)
        files.append({'source_path':str(path),'archive_path':path.name,'bytes':size,'sha256':sha})
sub=ROOT/'sp-subreview/public-artifacts-manifest-sp088.json'
for row in json.loads(sub.read_text())['files']:
    path=Path(row['source_path']); size,sha=digest(path)
    assert (size,sha)==(row['bytes'],row['sha256'])
    files.append({'source_path':str(path),'archive_path':'sp-subreview/'+row['archive_path'],'bytes':size,'sha256':sha})
size,sha=digest(sub)
files.append({'source_path':str(sub),'archive_path':'sp-subreview/'+sub.name,'bytes':size,'sha256':sha})
save('public-artifacts-manifest-source088.json', {
    'format_version':1, 'status':'FINAL_SOURCE_ONLY', 'files':files,
    'file_count':len(files),'total_bytes':sum(row['bytes'] for row in files),
    'manifest_self_excluded':True,
})
for row in files:
    assert digest(Path(row['source_path'])) == (row['bytes'],row['sha256'])
print(json.dumps({'handoff':digest(ROOT/'source-handoff088.json'), 'manifest':digest(ROOT/'public-artifacts-manifest-source088.json'),'files':len(files),'bytes':sum(row['bytes'] for row in files)}))
