from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
original=ROOT/'.cache/promote_section_297.py';raw=original.read_bytes();text=raw.decode()
old="""for name,raw in files.items():
 dest=ROOT/name
 if name in existing:assert sha256(dest.read_bytes()).hexdigest()==scope['before_existing_sources'][name]['sha256']
 else:assert not dest.exists(),name
for name,raw in files.items():
 target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
"""
new="""# The interrupted producer already wrote exactly these18 sources. Revalidate,
# do not overwrite them or hide the original archival-path failure.
for name,raw in files.items():
 assert (ROOT/name).read_bytes()==raw,name
"""
assert text.count(old)==1;text=text.replace(old,new)
assert text.count("'first-real-backend-tests'")==1
text=text.replace("'first-real-backend-tests'","'first-real-pure-api-tests'")
dest=ROOT/'verification/sections/297-preparation/promotion-archive-path-correction';dest.mkdir(exist_ok=False)
(dest/'original-producer.py').write_bytes(raw)
(dest/'correction.json').write_bytes((json.dumps({'kind':'ACTUAL_ROOT_PROMOTION_ARCHIVE_PATH_ERROR_AFTER_SOURCE_COPY',
 'actual_tool_exit':1,'error':'AssertionError: first-real-backend-tests',
 'actual_archive_directory':'first-real-pure-api-tests',
 'source_paths_already_copied':18,'archive_writes_before_failure':0,
 'resume_revalidates_all18_current_bytes_against_frozen_candidates_before_archiving':True,
 'resume_source_rewrites':False,'necessary_or_native_tests_executed':False,
 'original_producer_sha256':sha256(raw).hexdigest()},ensure_ascii=False,indent=2)+'\n').encode())
target=ROOT/'.cache/promote_section_297_resume.py';assert not target.exists();target.write_bytes(text.encode())
print('Exact-byte resume prepared; no sources modified by this preparation.')
