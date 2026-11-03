from pathlib import Path
from hashlib import sha256
import json
r=Path(__file__).resolve().parents[1];p=r/'.cache/first_fit_ground_297.py';raw=p.read_bytes()
d=r/'.cache/p3-297-ground-candidate'
assert not (d/'original-first-fit-producer.py').exists()
(d/'original-first-fit-producer.py').write_bytes(raw)
(d/'preparation-error.json').write_bytes((json.dumps({
 'kind':'ACTUAL_ROOT_CACHE_INPUT_SCHEMA_ERROR_NOT_MECHANISM_OR_PRODUCT_FAILURE',
 'actual_tool_exit':1,'error':'ValueError: too many values to unpack (expected 4)',
 'call':'Existing fit expects four anchor numeric fields; root passed an extra cue string. Error before cv2 fit or any result.',
 'root_producer_sha256':sha256(raw).hexdigest(),'production_or_private_changed':False,
 'observed_coordinates_changed':False,
 'first_revision_preparation_shell_failed_before_execution':'PowerShell nested quote caused Python SyntaxError; no producer, fit or file change from that attempt.'},indent=2)+'\n').encode())
text=raw.decode('utf8').replace('p3-297-ground-candidate/research','p3-297-ground-candidate-revision2/research')
old="*p['observed_pixel'],p['cue']]for p in author"
new="*p['observed_pixel']]for p in author"
assert text.count(old)==1
text=text.replace(old,new)
target=r/'.cache/first_fit_ground_297_revision2.py';assert not target.exists();target.write_bytes(text.encode())
print('First-fit revision2 prepared; source coordinates preserved and unreadable points remain excluded before any fit.')
