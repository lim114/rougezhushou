"""Explicitly named acquisitions from existing complete event readers, never a pool."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import importlib,json,re
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-named-rewards-347';DATA='rouge/data/current-named-reward-origins.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='51cb261cae8d2911d8d9d2e106195c10c6b1201c539a5ab776081baf05818f2c'
PROVIDER_MODULES={'resources':'current_resource_events','encounters':'current_encounters','peace':'current_peace','ritual':'current_ritual_reference','reconstruction':'current_reconstruction','resting':'current_resting','shadow':'current_shadow'}
SELECTIONS=(('resources','choice_ro6_relic1_1','rogue_6_relic_fight_11'),('resources','choice_ro6_relic1_2','rogue_6_relic_legacy_142'),('resources','choice_ro6_relic1_3','rogue_6_relic_legacy_141'),('resources','choice_ro6_relic2_1','rogue_6_relic_fight_18'),('resources','choice_ro6_relic2_2','rogue_6_relic_fight_19'),('encounters','choice_ro6_normal2_1','rogue_6_relic_cargo_12'),('peace','choice_ro6_task1_1','rogue_6_relic_cargo_11'),('ritual','choice_ro6_chimera2_1','rogue_6_relic_final_4'),('reconstruction','choice_ro6_sacrifice2_21','rogue_6_relic_final_6'),('resting','choice_ro6_surprise_1','rogue_6_relic_cargo_13'),('shadow','choice_ro6_normal4_26','rogue_6_relic_artifact_4'))
ITEM_IDS=frozenset(v[2]for v in SELECTIONS)
def providers():return{k:importlib.import_module('.'+v,__package__)for k,v in PROVIDER_MODULES.items()}
def source_rows(packets,current,modules):
    rows=[]
    for reader,cid,iid in SELECTIONS:
        d=packets[reader]['data'];original=d['originals']['choices'][cid];item=current['items'][iid]
        if original!=current['choices'][cid]or item['type']!='RELIC':raise ValueError('Exact current reward source required')
        text=version._plain(original['description']);match=re.search(r'(?:^|，)获得收藏品(.+)$',text)
        if match is None:raise ValueError('Reward must be explicitly named in full description')
        pointer=original['displayData']['itemId'];name=match[1]
        if pointer is None:
            unique=[k for k,v in current['items'].items()if v['type']=='RELIC'and v['name']==name]
            if unique!=[iid]:raise ValueError('Unique full literal name required for missing pointer')
            basis='unique_full_literal_name_missing_original_pointer'
        else:
            if pointer!=iid or name.strip('“”')!=item['name'].strip('“”'):raise ValueError('Exact pointer and full reward name must agree except outer quotes')
            basis='explicit_original_item_pointer_and_full_name'
        target=modules[reader].locate('choices',cid)
        if target is None:raise ValueError('Existing exact original-choice entry required')
        if 'event'in d:event=d['event']
        else:
            events=d['events'];event=events[target['event_id']]if type(events)is dict else next(v for v in events if v['id']==target['event_id'])
        if iid in d['originals']['items']and d['originals']['items'][iid]!=item:raise ValueError('Reader item record differs')
        rows.append({'key':'named347:'+cid,'reader':'named347','reader_key':reader,'event_title':event['title'],'event_id':event['id'],'scene_id':target.get('scene_id','source-choice'),'choice_id':cid,'item_id':iid,'item':deepcopy(item),'choice':deepcopy(original),'target':deepcopy(target),'binding_basis':basis,'original_item_pointer':pointer,'actual_quantity':None,'actual_received':None,'actual_eligible':None,'reader_source_identity':json.loads(json.dumps(packets[reader]['source_identity']))})
    if len(rows)!=11 or len({r['item_id']for r in rows})!=11:raise ValueError('Keep11 distinct newly linked named acquisitions')
    return rows
def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);mods=providers();expected={DATA,PACK+'/source-notes.json'}|{v.DATA for v in mods.values()}|{v.MANIFEST for v in mods.values()}
        if m['schema']!='current_named_rewards_347_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
        for name,pin in m['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            p=ROOT.joinpath(*rel.parts)
            if p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):return None
            if any(a.is_symlink()for a in p.parents if a!=ROOT and ROOT in a.parents):return None
            content=p.read_bytes()
            if len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
        d=json.loads((ROOT/DATA).read_bytes());packets={k:v.packet()for k,v in mods.items()};current=version.packet()
        if current is None or any(p is None for p in packets.values()):return None
        if d['schema']!='current_named_rewards_347_v1'or d['game_commit']!=version.NEW_COMMIT or d['complete_acquisition_pool']is not False:return None
        if d['rows']!=source_rows(packets,current['current']['details'],mods):return None
        return {'data':d,'source_identity':(MANIFEST_SHA256,tuple((k,p['source_identity'])for k,p in packets.items())),'actual_received':None,'actual_eligible':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError,StopIteration):return None
def reference(category,item_id):
    if type(category)is not str or type(item_id)is not str or category!='relics'or item_id not in ITEM_IDS:return None
    p=packet()
    if p is None:return None
    rows=[deepcopy(r)for r in p['data']['rows']if r['item_id']==item_id];detail=version.detail(category,item_id)
    if not rows or detail is None or any(detail['row']['value']['item']!=r['item']for r in rows):return None
    return{**p,'kind':'named_acquisition_347','category':category,'item_id':item_id,'item':deepcopy(rows[0]['item']),'rows':rows,'complete_acquisition_pool':False,'actual_quantity':None}
def player_text(result,key=None):
    lines=['【取得方式资料】'+result['item']['name'],'这里只列已经逐条核对的具名领取选项，不是全部掉落方式；没有列出不等于不能获得。','','已核对'+str(len(result['rows']))+'条领取选项；不同选项、事件和阶段不合并领取。']
    row=next((r for r in result['rows']if r['key']==key),None)
    if row:
        lines+=['','【相关事件资料】'+row['event_title'],'【查看的选项】'+row['choice']['title'],'【本项代价与奖励原文】',version._plain(row['choice']['description']),'','【数量与实际获得】原文没有独立写明件数，本局是否可选、实际扣除与领取尚未核对；不补成1件，也不写入本局。']
        reader=row['reader_key']
        if reader=='encounters':lines+=['','【别混淆】此项奖励是猎印；持有笼控器是条件，不等于本项会领取笼控器，也不证明笼控器被消耗。']
        if reader=='reconstruction':lines+=['','【前后步骤分开】本项是“等待结果”领取焚毁“文明”；前一步复原“文明”才写随机消耗2件自然物。不能在本项再扣一次，也不能仅凭原项编号认定实际父情景或资格。']
        if reader=='resting':lines+=['','【源私钥的对应范围】领取原项只写名称，没有给出物品编号；按当前唯一同名物品显示。其说明中的99源石锭与另一事件领取项的99关系未证，不能合计198或推定重复领取。']
        if reader=='peace':lines+=['','【取得与生效时点分开】这是接取悬赏的取得选项；不等于已经前往、完成作战或累计胜利后的攻速。']
        if reader=='shadow':lines+=['','【与另一结果分开】犬植浆和行动力分别查阅，不当成同时得到；第八圈后的实际抽取、重复及停止规则仍待核对。']
        if reader=='ritual':lines+=['','【全部源石锭】倾囊资助写明消耗全部源石锭；零余额时是否可选及实际发放仍未知，不能当作免费保证领取。']
        if reader=='resources':lines+=['','【各选项分开】血衣之下和擒与缚中的不同领取选项分别阅读；不是把多个互斥奖励合在一起获得。']
        lines+=['','【继续查阅】点击“查看这条选项的条件与后续”，打开这条准确选项对应的现有事件资料；条件默认未知，原件前置未证时不会补出父菜单。']
    else:lines+=['','请选择一条领取选项，再查看它自己的条件、代价和后续。']
    lines+=['','【范围与未知】本清单不包含仅持有、交付或消耗该物品的其它选项；图片提示也不单独当作领取证明。完整获取池、服务器出现资格、实际件数及本局领取仍未知。','仅局外查阅，不扣资源、不领取、不改本局记忆或计算；不推荐路线或给生成概率。']
    return '\n'.join(lines)
