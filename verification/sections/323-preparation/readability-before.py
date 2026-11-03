"""Current exchange offer flags and explicit amounts, separate from reward pools."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import json
from . import expansion_reference as version

ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-exchange-323';DATA='rouge/data/current-exchange-reference.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='c7f8ae504899efc652d1fa90c5dc721b73ff4fe116c98f3e011cab4be435e440'
RARITIES={'NORMAL':'低稀有度','RARE':'中稀有度','SUPER_RARE':'高稀有度'}
UNAVAILABLE='当前交换资料暂时无法核对，旧物品、数量和条文已清除；恢复后请重新选择。'


def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-table.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json'}
        if manifest['schema']!='current_exchange_323_manifest_v1'or manifest['game_commit']!=version.NEW_COMMIT or set(manifest['files'])!=expected:return None
        blobs={}
        for name,pin in manifest['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            path=ROOT.joinpath(*rel.parts)
            if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):return None
            for parent in path.parents:
                if parent==ROOT:break
                if parent.is_symlink():return None
            content=path.read_bytes()
            if len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
            blobs[name]=content
        data=json.loads(blobs[DATA]);current=version.packet()
        if current is None or data['schema']!='current_exchange_323_v1':return None
        primary=current['current']['details'];old=current['baseline']['details'];actual={k:v for k,v in primary['items'].items()if v['type']=='RELIC'}
        if {r['id']:r['item']for r in data['catalogue']}!=actual:return None
        if any(r['before']!=old['items'].get(r['id'])or type(r['can_offer'])is not bool or r['can_offer']is not r['item']['canSacrifice']for r in data['catalogue']):return None
        if any(primary['choices'].get(k)!=v for k,v in data['original_choices'].items()):return None
        if {k:v for k,v in primary['choiceScenes'].items()if v['title']=='回滚文明'}!=data['related_scenes']:return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_inventory':None,'actual_offer':None,'actual_reward_pool':None,'actual_reward':None,'actual_received_quantity':None,'run_updated':False,'legacy_catalogue_replaced':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None


def catalogue_rows(ref,*,can_offer=None,rarity=None,change=None,query=''):
    if can_offer is not None and type(can_offer)is not bool:raise ValueError('能否交出请选择全部、可交出或不可交出。')
    if rarity not in(None,*RARITIES)or change not in(None,'added','changed','unchanged')or type(query)is not str:raise ValueError('请选择已有的稀有度、更新范围并使用文字检索。')
    if ref is None:return []
    return [deepcopy(r)for r in ref['data']['catalogue']if(can_offer is None or r['can_offer']is can_offer)and(rarity is None or r['rarity']==rarity)and(change is None or r['change']==change)and(not query.strip()or query.strip()in r['name'])]


def target_entry(category,key):
    if type(category)is not str or type(key)is not str or category not in('relics','scenes','choices'):return None
    ref=packet()
    if ref is None:return None
    if category=='relics'and any(r['id']==key for r in ref['data']['catalogue']):return {'tab':'items','item_id':key,'group_id':None}
    if category=='scenes'and key in ref['data']['related_scenes']:return {'tab':'document','item_id':None,'group_id':None}
    if category=='choices':
        rows=[r for r in ref['data']['document_groups']if key in r['primary_candidate_ids']]
        if len(rows)==1:return {'tab':'document','item_id':None,'group_id':rows[0]['id']}
    return None


def item_text(ref,item_id):
    row=next((r for r in ref['data']['catalogue']if r['id']==item_id),None)if ref else None
    if row is None:return '请选择收藏品。这里判断原表是否允许交出，不列可能换到的奖励池。'
    item=row['item'];status='标记为可以交出'if row['can_offer']else'标记为不可交出';change={'added':'本次固定更新新增','changed':'相对旧基准已有改动','unchanged':'相对旧基准未改动'}[row['change']]
    lines=['【收藏品】'+item['name'],'【能否作为提供物】当前原表'+status,'本局是否持有、本次是否会列入选择、实际是否消耗仍未确认。','这项判断只用于交出去，不能说明能否换到它，也不是指定交付或领取。','','【稀有度】'+RARITIES[row['rarity']],'【版本对照】'+change,'','【作用说明】',version._plain(item.get('usage'))or'原表没有独立说明。','','【物品说明】',version._plain(item.get('description'))or'原表没有独立说明。','','【范围与未知】','当前固定物品表共284件收藏品：259件可交出、25件不可交出；不将395条效果定义当成物品数。','这里只读10月16日的固定国服资料，旧272件目录保留；不证明服务器热更新、本局库存、完整交换奖励池或实际奖励，不改变本局记忆。']
    return '\n'.join(lines)


def document_text(ref,group_id):
    row=next((r for r in ref['data']['document_groups']if r['id']==group_id),None)if ref else None
    if row is None:return '请选择交换条文。9组文案来自13处原表记载；相同文案的候选原记录不等于本局已选定记录，也不恢复各个情景的游戏按钮。'
    lines=['【交换条文】'+row['title'],'','【原文说明】',version._plain(row['description'])]
    if row['explicit_reward_quantity']is not None:lines+=['','【明确记载的数量】',str(row['explicit_reward_quantity'])+'件'+row['reward_resource'],'数量来自选项原文；具体物品、档次和完整候选池仍未在此核验，不按提供物稀有度补造。']
    if row['consumption_reference']:lines+=['','【明确记载的消耗】','随机2件自然物；这不是任意2件零件。具体消耗哪两件及本局是否可选未知，这里不会扣除。']
    if row['associated_relic_ids']:
        lines+=['','【明确关联的收藏品】']
        for iid in row['associated_relic_ids']:
            item=next(r['item']for r in ref['data']['catalogue']if r['id']==iid);lines+=[item['name'],version._plain(item.get('usage'))]
        if row['explicit_reward_quantity']is None:lines+=['该具名领取条文未独立写明件数，不自动补成1件；也不表示已经领取。']
    lines+=['','【不同原记录仍需区分】','这条文案有'+str(len(row['primary_candidate_ids']))+'份完整文案相符的当前原记录；保留全部候选，不按编号选定、合并实际来源或推断出现顺序。','通用“离开”记录没有结果说明，未仅凭标题把它绑定到此事件。','','【本局与奖励仍未知】','未恢复真实父情景、首次/再次交换的实际选择与发放脚本；文献重复列出的相同文案不代表可重复领取。','可交出目录不是换入奖励池；不会交付、消耗或记录领取，不给出路线建议，不操作游戏或聊天。']
    return '\n'.join(lines)
