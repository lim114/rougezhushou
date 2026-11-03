"""Separate API aliases/text errors; none of these are Qt control submissions."""
import gzip,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;PACKAGE=P/'public-schema-70'
sys.path.insert(0,str(PACKAGE));sys.dont_write_bytecode=True
from rouge.damage import calculate_damage
from rouge.reporting import format_report
def hashes():
    return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((PACKAGE/'rouge').rglob('*'))if p.is_file()and p.suffix in('.py','.json')}
before=hashes();records=[];calls=0
def strict(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False)
def outcome(args):
    global calls
    calls+=1;original=strict(args)
    try:
        result=calculate_damage(args)
        row={'status':'returned','result':result,'human_report':format_report(result)}
    except (ValueError,TypeError)as error:
        row={'status':'raised','exception':{'type':type(error).__name__,'message':str(error)}}
    assert strict(args)==original;return row
def pair(section,raw,numeric):
    left=outcome(raw);right=outcome(numeric)
    assert strict(left)==strict(right)
    records.append({'section':section,'scope':'API-only alias/inactive pair, never actual Qt','raw_input':raw,
                    'numeric_or_absent_control':numeric,'raw_outcome':left,'control_outcome':right,'whole_strict_json_equal':True})
def error(section,args,message):
    actual=outcome(args)
    assert actual=={'status':'raised','exception':{'type':'ValueError','message':message}}
    records.append({'section':section,'scope':'API-only exact error, never actual checkbox/spinbox','input':args,'outcome':actual})
for mode in ('frames','continuous'):
    for number in (1,2,3):
        wisdel={'operator':'char_1035_wisdel','skill':number,'timing_mode':mode,'window_seconds':10}
        for ghosts,casts,rawghosts,rawcasts in ((0,0,'0.0','bad'),(1,1,'1.0','1e0'),(3,2,'3e0','2.0')):
            pair(66,{**wisdel,'ghost_count':rawghosts,'ghost_casts':rawcasts},
                    {**wisdel,'ghost_count':ghosts,'ghost_casts':casts})
        phatm={'operator':'char_1042_phatm2','skill':number,'timing_mode':mode,'window_seconds':10}
        for alias in ('1.0','1e0'):
            pair(67,{**phatm,'enemy_attack_count':alias},{**phatm,'enemy_attack_count':1})
    shu={'operator':'char_2025_shu','skill':3,'timing_mode':mode,'window_seconds':10}
    for field in ('three_professions','three_same_profession'):
        error(68,{**shu,field:'false'},field+' 不接受文本条件；请使用布尔值。')
    error(68,{**shu,'four_sui':'false','three_professions':'false','three_same_profession':'false'},
          'four_sui 不接受文本条件；请使用布尔值。')
    silver={'operator':'silverash','skill':3,'timing_mode':mode,'window_seconds':10,'preexisting_fragile':False}
    error(69,{**silver,'cooperative':'false'},'cooperative不接受字符串，请提供明确的布尔条件。')
    error(69,{**silver,'cooperative':'false','preexisting_fragile':'false'},
          'preexisting_fragile不接受字符串，请提供明确的布尔条件。')
    error(70,{**shu,'enemy_on_sown_tile':'false'},'enemy_on_sown_tile 不接受文本条件；请使用布尔值。')
    error(70,{**shu,'elite':1,'skill_rank':7,'enemy_on_sown_tile':'false'},
          '当前精英阶段尚未开放所选技能或专精。')
    for number in (1,2):
        plain={**shu,'skill':number}
        pair(70,{**plain,'enemy_on_sown_tile':'false'},plain)
    error(66,{'operator':'char_1035_wisdel','skill':1,'timing_mode':mode,'ghost_count':True},
          'ghost_count需要范围内的有限非负整数。')
    error(67,{'operator':'char_1042_phatm2','skill':2,'timing_mode':mode,'enemy_attack_count':True},
          'enemy_attack_count需要范围内的有限非负整数。')
assert hashes()==before
receipt={'scope':'Public API-only alias and exact text/bool error design evidence, distinct from all actual Qt checks',
         'calls':calls,'whole_result_pairs':sum('raw_input'in r for r in records),
         'expected_error_checks':sum('input'in r for r in records),
         'source_drift':[],'gui_executed':False,'wine_executed':False,'records':records}
raw=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
(P/'api-text-contracts.json.gz').write_bytes(raw)
summary={k:v for k,v in receipt.items()if k!='records'}
summary['full_gzip_sha256']=hashlib.sha256(raw).hexdigest()
(P/'api-text-contract-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
