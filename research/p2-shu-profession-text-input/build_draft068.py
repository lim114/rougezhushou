from pathlib import Path
import shutil, hashlib, json, datetime

base=Path(__file__).parent
draft=base/'draft068'
if not draft.exists():
    shutil.copytree(base/'baseline',draft,ignore=shutil.ignore_patterns('__pycache__'))
name='rouge/operator_engine.py'
raw=(base/'baseline'/name).read_bytes()
text=raw.decode().replace('\r\n','\n')
needle="            if self.s.get('four_sui'):"
insert="""            if '天有四时' in self.tv:
                for field in ('three_professions','three_same_profession'):
                    if isinstance(self.s.get(field),str):
                        raise ValueError(field+' 不接受文本条件；请使用布尔值。')
            if self.s.get('four_sui'):"""
assert text.count(needle)==1
text=text.replace(needle,insert)
assert raw.count(b'\r\n')==raw.count(b'\n')
path=draft/name
path.write_bytes(text.replace('\n','\r\n').encode())
receipt={
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'baseline_commit':'0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb',
    'changes':{name:{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}},
    'only_selected_tian_you_si_shi_strings_rejected':True,
    'after_existing_four_sui_062_string_guard':True,
    'no_predicate_math_source_value_or_other_owner_change':True,
}
(base/'draft-receipt068.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
