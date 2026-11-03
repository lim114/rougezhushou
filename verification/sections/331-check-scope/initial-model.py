"""Current rest/travel references; original text aliases preserve provenance only."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-rest-travel-331';DATA='rouge/data/current-rest-travel.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='d87bd2056a8d76227b7e88b6c22e66461888e242d98216263274a2fd04f71be6'
UNAVAILABLE='休憩与换区资料暂时无法核对，旧对话、选项及后续入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-tables.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json'}
        if m['schema']!='current_rest_travel_331_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
        values={}
        for name,pin in m['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            path=ROOT.joinpath(*rel.parts)
            if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):return None
            for parent in path.parents:
                if parent==ROOT:break
                if parent.is_symlink():return None
            content=path.read_bytes()
            if len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
            values[name]=content
        data=json.loads(values[DATA]);current=version.packet()
        if current is None or data['schema']!='current_rest_travel_331_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id,source_request=None):
    if type(event_id)is not str:return None
    ref=packet()
    if ref is None or event_id not in ref['data']['events']:return None
    d=ref['data'];e=d['events'][event_id]
    if source_request is not None:
        if type(source_request)is not dict or set(source_request)!={'category','key'}:return None
        cat=source_request['category'];key=source_request['key']
        if type(cat)is not str or type(key)is not str or cat not in('scenes','choices')or d['lookup'][cat].get(key,{}).get('event_id')!=event_id:return None
    return {**ref,'event':deepcopy(e),'scenes':{k:deepcopy(d['scenes'][k])for k in e['scene_ids']},'choices':{k:deepcopy(d['choices'][k])for k in e['choice_ids']},'source_request':deepcopy(source_request),'actual_menu':None,'actual_background':None,'actual_departed':None,'actual_received':None}


def locate(category,key):
    if type(category)is not str or type(key)is not str or category not in('scenes','choices'):return None
    prefixes=('scene_ro6_rest_','scene_ro6_evacuate')if category=='scenes'else('choice_ro6_rest_','choice_ro6_evacuate')
    if not key.startswith(prefixes):return None
    ref=packet()
    if ref is None:return None
    t=ref['data']['lookup'][category].get(key)
    return {**deepcopy(t),'source_request':{'category':category,'key':key}}if t is not None else None


def scene_label(result,sid):
    scene=result['scenes'].get(sid)
    if scene is None:return '请选择查阅对话'
    label='最初对话 · '+result['event']['title']if sid==result['event']['entry_scene_id']else'文献中的后续对话'
    predecessors=[c for c in result['choices'].values()if c['next_scene_id']==sid]
    if len(predecessors)==1:label='选择“'+predecessors[0]['title']+'”后的对话'
    if len(scene['original_scene_ids'])>1:label+='（三种画面共用此段文字）'
    return label


def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    scene=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(scene and c and cid in scene['choice_ids']and c['scene_id']==sid):return None
    return deepcopy(c)


def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择要查阅的对话；不表示本局已经到达或已领取。'
    c=choice_reference(result,sid,cid);lines=['【正在查阅】'+result['event']['title'],scene_label(result,sid),'','【当前对话】',version._plain(result['scenes'][sid]['description'])]
    if result['event']['id']=='金色凝滞':lines+=['','【选项目录不等于当前菜单】','资料收录7条说明，原注写“随机3个”。留存招募券的求援是否与其它项共用这三项名额，仍未核验。','可逐条查阅，但不把7项当成本局同时出现，也不把各项收益相加。']
    else:lines+=['','【同一句话的三种画面】','文献记载三张画面，当前同文对话合并阅读，全部原始记录仍保留；不按画面编号猜资格或分支。']
    if c:
        effect=c['effect_reference'];lines+=['','【查看的选项】'+c['title'],'【原文写明】',version._plain(c['description'])]
        if effect:
            resource=effect['resource'];qty=effect['quantity']
            if resource=='加工品':
                lines+=['','【明确的奖励说明】1件珍贵加工品','加工品不等于收藏品，具体名单、完整候选池和实际领取未知。','原文同时写明保留目前行动力并直接进入下一区域；这里不执行换区，也不把行动力转为希望。']
                if c['display_item_includes_none']and c['display_item_ids']:lines+=['部分同文记录附带的展示物品指向生命上限；展示标记不能证明额外生命奖励，本页只列原文明示加工品。']
            elif resource=='高级物资配给券':
                item=next(i for i in result['data']['originals']['items'].values()if i['name']==resource);lines+=['','【具名奖励说明】高级物资配给券','原文未单列领取张数，不自动补1张。','','【该券的作用资料】',version._plain(item['usage']),'不等于已经获得、已经进阶或选定了干员。']
            elif resource=='使用留存招募券':lines+=['','【这是使用已有留存券】','不是获得新券。具体可用券、取出数量及培养结果尚未确认；这里不执行招募，也不反推本项是否属于随机三项。']
            elif resource=='进入下一区域':lines+=['','【换区说明】保留行动力，进入下一区域','原记录没有指定下一段对话；不假造下一关、下一层或地图节点，不执行移动和资源转换。','文献把本项放在“自己找路”后的对话，不自动接到“接受提议”后，也不假定两分支共用确认。']
            else:
                lines+=['','【明确的本次变化】'+resource+' +'+str(qty),'这是文献中的变化量，不是已经结算后的本局数值。']
                if resource=='目标生命值上限':lines+=['指探索的目标生命值上限，不是干员生命；是否同时回复当前目标生命值不能据此额外断定。']
                elif resource=='可携带干员数':lines+=['指可携带上限，不等于新招募1名干员或增加全队已招募人数。']
                elif resource=='零件箱容量':lines+=['指容量上限，不是获得1件零件。']
        if len(c['variant_ids'])>1:lines+=['','【相同文案的多份记录】'+str(len(c['variant_ids']))+'份','全部保留供核对，不当多次领取；本局实际使用哪份仍未确认。']
        if c['next_scene_id']:lines+=['','【明确对应的后续文案】',scene_label(result,c['next_scene_id']),'只继续查资料，不执行游戏选项或领取。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择本段文献列出的选项；不表示本局全部可选。']
    else:lines+=['','资料未列本段的专属后续选项，不自动返回最初菜单或接入其它换区确认。']
    if result['source_request']:lines+=['','你从一份指定的原始资料进入本页；这仅保留来源定位，不表示本局采用该记录。']
    lines+=['','【范围与未知】','固定版本的资料查阅。完整出现资格、菜单抽取、父关系、换区执行和实际奖励仍待核验。','不修改本局资源、培养、留存券或地图，不提供路线推荐或概率。']
    return '\n'.join(lines)
