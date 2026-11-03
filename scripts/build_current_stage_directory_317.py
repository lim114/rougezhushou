"""Exact current stage identities linked to documented directory groupings."""
from pathlib import Path
from hashlib import sha256
from urllib.parse import unquote
import re,json,argparse
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-stage-directory-317';DATA='rouge/data/current-stage-directory.json'
GROUPS={'ISW-NO 一般作战 & 紧急作战':'normal','ISW-NO & ISW-DF 险路恶敌':'boss','ISW-NO 鸭爵与雇员':'duck','ISW-NO 狭路相逢':'duel','ISW-NO 特殊挑战':'challenge','ISW-NO 流窜“居民” & “居民”据点':'resident','ISW-NO 坎诺特的挑战':'shop','ISW-NO & ISW-DF 追猎':'pursuit'}
FLOORS={'Ⅰ':'floor1','Ⅱ':'floor2','Ⅲ':'floor3','Ⅳ':'floor4','Ⅴ':'floor5','0':'special0','*i*':'speciali'}
KINDS={'normal':'普通作战与紧急作战','boss':'险路恶敌','duck':'鸭爵与雇员','duel':'狭路相逢','challenge':'特殊挑战','resident':'流窜居民与据点','shop':'坎诺特的挑战','pursuit':'追猎','unknown':'来源分类未确认'}
FLOOR_LABELS={'floor1':'第一层','floor2':'第二层','floor3':'第三层','floor4':'第四层','floor5':'第五层','floor6':'第六层','unknown':'层数未确认'}

def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def parse(text):
    assert 'ISW-NO 一般作战 & 紧急作战'in text and'部分随机'in text
    group=None;floor=None;rows=[]
    for index,token in enumerate(text.split('|')):
        token=token.strip()
        if token in GROUPS:group=GROUPS[token];floor=None;continue
        if token in FLOORS:floor=FLOORS[token];continue
        for match in re.finditer(r'\]\((/w/ISW-(?:NO|DF)_[^\s]+)\s+"(ISW-(?:NO|DF)) ([^"]+)"\)',token):
            url,code,name=match.groups();assert unquote(url).split('_',1)==['/w/'+code,name]
            assert group is not None
            rows.append({'name':name,'code':code,'kind':group,'floor':floor or'unknown','source_token_index':index,'source_url':'https://prts.wiki'+url,'reference_only':True})
    assert len(rows)==len({(r['code'],r['name'])for r in rows})
    assert all(r['floor']=='unknown'for r in rows if r['kind']in('duck','duel','challenge','resident','shop'))
    return rows

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());excerpt=(root/PACK/'stage-table-441984-excerpt.md').read_bytes()
    assert sha256(excerpt).hexdigest()==receipt['excerpt_sha256']and len(excerpt)==receipt['excerpt_bytes']and receipt['revision_from_actual_scraped_fixed_link']=='441984'
    headers=json.loads((root/PACK/'region-label-excerpts.json').read_bytes());assert headers=={'special0':'cero(O)  \n源流交汇处  \n(VI) Bestia Aristócrata','speciali':'imaginario(i)  \n盲目者所见  \n(VI) ojo'}
    entries=parse(excerpt.decode('utf8'));table=json.loads((root/'research/p3-expansion-313/current-topic.json').read_bytes())['details']['stages'];mapped={}
    for sid,stage in table.items():
        references=[r for r in entries if r['name']==stage['name']and r['code']==stage['code']]
        assert len(references)<=1
        ref=references[0]if references else None
        floor=ref['floor']if ref else'unknown';region={'special0':'源流交汇处','speciali':'盲目者所见'}.get(floor,'主要区域'if floor.startswith('floor')else'具体区域未确认');floor='floor6'if floor in('special0','speciali')else floor
        kind=ref['kind']if ref else'unknown'
        if kind=='normal':
            assert stage['isBoss']==0 and stage['isElite']in(0,1);play_kind='emergency'if stage['isElite']==1 else'normal'
        else:play_kind=kind
        mapped[sid]={'id':sid,'name':stage['name'],'code':stage['code'],'kind':ref['kind']if ref else'unknown','floor':floor,'region':region,'play_kind':play_kind,'documented_entry':ref,'original_stage':stage,'actual_generation_eligible':None,'whole_variant_pool_proven':False}
    data={'schema':'current_stage_directory_317_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','rows':mapped,'documented_entries':entries,'source':receipt,'region_headers':headers,'same_name_variants_not_collapsed':True,'directory_is_current_generation_pool':False,'floor_grouping_is_original_numeric_ID':False,'actual_current_server_verified':False}
    raw=enc(data);names=[PACK+'/region-label-excerpts.json',PACK+'/source-receipt.json',PACK+'/stage-table-441984-excerpt.md','research/p3-expansion-313/current-topic.json'];files={n:{'sha256':sha256((root/n).read_bytes()).hexdigest(),'bytes':(root/n).stat().st_size}for n in names};files[DATA]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    manifest=enc({'schema':'current_stage_directory_317_manifest_v1','game_commit':data['game_commit'],'files':files,'current_version_packet_required':True})
    return raw,manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args();data,manifest=build()
    for name,raw in((DATA,data),(PACK+'/runtime-manifest.json',manifest)):
        if args.check:assert(ROOT/name).read_bytes()==raw
        if args.write:(ROOT/name).write_bytes(raw)
    result=json.loads(data);print(json.dumps({'manifest_sha256':sha256(manifest).hexdigest(),'stage_refs':len(result['rows']),'documented_entries':len(result['documented_entries']),'unmatched_stage_refs':[k for k,r in result['rows'].items()if not r['documented_entry']]},ensure_ascii=False))
