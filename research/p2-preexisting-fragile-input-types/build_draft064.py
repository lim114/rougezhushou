from pathlib import Path
import shutil,hashlib,json,datetime
base=Path(__file__).parent;draft=base/'draft064'
if not draft.exists():shutil.copytree(base/'baseline',draft,ignore=shutil.ignore_patterns('__pycache__'))
p=draft/'rouge/damage.py';data=(base/'baseline/rouge/damage.py').read_bytes().decode();text=data.replace('\r\n','\n')
needle="    # Preserve raw count types before either engine converts them to numbers."
new="""    if scenario['operator']=='silverash' and skill==3 and isinstance(scenario.get('preexisting_fragile'),str):
        raise ValueError('preexisting_fragile不接受字符串，请提供明确的布尔条件。')
    # Preserve raw count types before either engine converts them to numbers."""
assert text.count(needle)==1;text=text.replace(needle,new)
p.write_bytes(text.replace('\n','\r\n').encode())
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':'c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf','changes':{'rouge/damage.py':{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}},'guard_after_training_qualification':True,'strings_active_s3_only':True,'no_math_or_source_value_changes':True}
(base/'draft-receipt064.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(receipt)
