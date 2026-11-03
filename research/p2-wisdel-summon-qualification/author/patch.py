import difflib,hashlib,json,pathlib
p=pathlib.Path(__file__).resolve().parent
files=['rouge/operator_engine.py','rouge/reporting.py','rouge/wisdel_summon_qualification.py','rouge/data/wisdel-summon-qualification-reference.json','tests/test_wisdel_summon_qualification_reference.py'];hunks=[];hashes={}
for rel in files:
 before=(p/'frozen70'/rel).read_bytes() if (p/'frozen70'/rel).exists() else b'';after=(p/'draft'/rel).read_bytes();hashes[rel]={'before':hashlib.sha256(before).hexdigest() if before else None,'after':hashlib.sha256(after).hexdigest()}
 hunks.append('diff --git a/'+rel+' b/'+rel+'\n')
 if not before:hunks.append('new file mode 100644\n')
 hunks.extend(difflib.unified_diff(before.decode().splitlines(keepends=True),after.decode().splitlines(keepends=True),fromfile='a/'+rel if before else '/dev/null',tofile='b/'+rel,n=3))
blob=''.join(hunks).encode();(p/'section74.patch').write_bytes(blob);receipt={'baseline_head':'552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9','sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob),'files':hashes,'engine_newlines':'CRLF preserved','test_newlines':'LF','scope':'two pinned original owner summon-route cultivation source facts and report only; all declared counts, numeric results, controls and error gates unchanged','tracked_root_edits':0}
(p/'patch-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt))
