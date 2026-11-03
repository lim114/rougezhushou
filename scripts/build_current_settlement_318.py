"""Current unambiguous base gold; historical XP mode splits stay historical."""
from pathlib import Path
from hashlib import sha256
from urllib.parse import unquote
import argparse,json,re,sys
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-settlement-318';DATA='rouge/data/current-settlement-reference.json'
sys.path.insert(0,str(ROOT))
FLOORS={'Ⅰ':'floor1','Ⅱ':'floor2','Ⅲ':'floor3','Ⅳ':'floor4','Ⅴ':'floor5','0':'source0'}
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def quantity(text):
    if text in('——','?'):return None
    m=re.fullmatch(r'(\d+)(?:~(\d+))?',text);assert m,text
    low,high=int(m[1]),int(m[2]or m[1]);assert high>=low;return {'minimum':low,'maximum':high}
def links(text):
    result=[]
    for m in re.finditer(r'\]\((/w/ISW-(?:NO|DF)_[^\s]+)\s+"(ISW-(?:NO|DF)) ([^"]+)"\)',text):
        url,code,name=m.groups();assert unquote(url).split('_',1)==['/w/'+code,name];result.append({'code':code,'name':name,'url':'https://prts.wiki'+url})
    return result
def parse(text):
    assert '多个指挥经验加成之间乘算叠加，最终结果向下取整'in text
    main={};special=[];previous=None;portal=False
    for index,line in enumerate(text.splitlines()):
        if not line.startswith('|'):continue
        cells=[x.strip()for x in line.split('|')[1:-1]]
        if cells and cells[0]in FLOORS:
            assert len(cells)==9;main[FLOORS[cells[0]]]={kind:{'experience_collapsed_token':cells[1+i*2],'base_gold':quantity(cells[2+i*2]),'source_line_index':index,'column_kind':kind,'original_floor_label':cells[0]}for i,kind in enumerate(('normal','emergency','boss','boss_pursuit'))};continue
        if cells and cells[0]=='/':assert cells[1]=='与战斗节点所属层/特殊战斗一致'and all(not x or x=='——'for x in cells[2:]);portal=True;continue
        related=links(cells[0])if cells else[]
        compact=[c for c in cells if c]
        if related:
            assert len(compact)==3;previous={'label':cells[0],'links':related};token,gold=compact[-2:];difficulty='NORMAL'
        elif previous and compact and compact[0].startswith('紧急作战版本适用此掉落 '):
            assert len(compact)==2;token=compact[0].removeprefix('紧急作战版本适用此掉落 ');gold=compact[1].removeprefix('紧急作战版本适用此掉落 ');difficulty='FOUR_STAR'
        else:continue
        special.append({**previous,'difficulty':difficulty,'experience_collapsed_token':token,'base_gold':quantity(gold),'source_line_index':index})
    assert set(main)==set(FLOORS.values())and len(special)==18 and portal
    return main,special
def historical_xp(token,old):
    if old and old['source_text']==token:return {'base':old['base'],'full_technology':old.get('full_technology_reference'),'source_revision':'433770','applied_to_current':False,'current_modes_verified':False}
    return None
def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes())
    for name,pin in receipt['excerpt_files'].items():
        raw=(root/PACK/name).read_bytes();assert sha256(raw).hexdigest()==pin['sha256']and len(raw)==pin['bytes']
    text=(root/PACK/'settlement-441984-excerpt.md').read_text('utf8');main,special=parse(text)
    pursuit=(root/PACK/'ordinary_pursuit-441984-excerpt.md').read_text('utf8');assert '一张招募券'in pursuit and'没有任何指挥经验、源石锭和收藏品报酬'in pursuit and'险路恶敌追猎通关时则会正常掉落奖励'in pursuit
    old=json.loads((root/'rouge/data/base-settlement-reference.json').read_bytes());assert old['source']['revision']=='433770'
    from scripts.build_base_settlement_reference import build as historical_build
    assert historical_build(root)==old
    assert '额外获得一个随机收藏品'in(root/'research/p3-ending-events-316/topic-441984-excerpt.md').read_text('utf8')
    for floor,columns in main.items():
        oldfloor='6'if floor=='source0'else floor.removeprefix('floor')
        for kind,row in columns.items():row['historical_experience_reference']=historical_xp(row['experience_collapsed_token'],old['main_floor_table'][oldfloor][kind]['experience']);row['current_experience']=None
    for row in special:
        candidates=[x for x in old['special_battle_table']if x['difficulty']==row['difficulty']and{v['title']for v in x['links']}=={v['code']+' '+v['name']for v in row['links']}]
        assert len(candidates)==1;row['historical_experience_reference']=historical_xp(row['experience_collapsed_token'],candidates[0]['experience']);row['current_experience']=None
    data={'schema':'current_settlement_318_v1','source':receipt,'main_floor_table':main,'special_battle_table':special,'ordinary_pursuit':{'current_experience':0,'base_gold':{'minimum':0,'maximum':0},'recruit_ticket_reference':1,'actual_received':None},'current_nonzero_experience_modes_verified':False,'hidden_i_row_absent_is_not_zero':True,'complete_reward_pool_known':False,'actual_run_updated':False}
    raw=enc(data);names=['research/p3-ending-events-316/topic-441984-excerpt.md',PACK+'/source-receipt.json',PACK+'/settlement-441984-excerpt.md',PACK+'/ordinary_pursuit-441984-excerpt.md',PACK+'/original-download-failures.json','rouge/data/base-settlement-reference.json','research/p3-base-settlement/current-main.html'];files={n:{'bytes':(root/n).stat().st_size,'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(raw),'sha256':sha256(raw).hexdigest()}
    return raw,enc({'schema':'current_settlement_318_manifest_v1','files':files,'current_stage_directory_required':True,'current_nonzero_experience_verified':False})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();raw,manifest=build()
    for name,value in((DATA,raw),(PACK+'/runtime-manifest.json',manifest)):
        if a.write:(ROOT/name).write_bytes(value)
        if a.check:assert(ROOT/name).read_bytes()==value
    print(json.dumps({'manifest_sha256':sha256(manifest).hexdigest(),'main_rows':6,'special_rows':18,'current_nonzero_experience_verified':False}))
