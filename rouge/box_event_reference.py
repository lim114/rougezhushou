"""Current box-event reference; document links are not actual game eligibility."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version

ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-box-event-322';DATA='rouge/data/box-event-reference.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='bca118ed7906b81b67ab68532f2d45bfe0afb96bdf807de1c3e431a1c5323e5a'
UNAVAILABLE='窥视箱中的资料暂时无法核对，旧对话、选项和作战入口已清除；恢复后请重新选择。'
SUPPORTED_SCENES=frozenset(('scene_ro6_end2_enter','scene_ro6_end2_1','scene_ro6_end2_2','scene_ro6_end2_3'))
SUPPORTED_CHOICES=frozenset('choice_ro6_end2_'+str(n)for n in range(1,8))


def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-table.html','research/p3-expansion-313/current-topic.json'}
        if manifest['schema']!='box_event_322_manifest_v1'or manifest['game_commit']!=version.NEW_COMMIT or set(manifest['files'])!=expected:return None
        values={}
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
            values[name]=content
        data=json.loads(values[DATA]);current=version.packet()
        if current is None or data['schema']!='box_event_322_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('stages','stages'),('items','items')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_variant':None,'actual_received':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None


def reference(event_id='box',has_covenant=None):
    if type(event_id)is not str or event_id!='box':return None
    if has_covenant is not None and type(has_covenant)is not bool:raise ValueError('持有状态应为是、否或未知。')
    ref=packet()
    if ref is None:return None
    data=ref['data'];return {**ref,'event':deepcopy(data['event']),'scenes':deepcopy(data['scenes']),'choices':deepcopy(data['choices']),'declared_has_covenant':has_covenant,'condition_is_manual_reference_only':True}


def locate(category,key):
    if type(category)is not str or type(key)is not str:return None
    # Exact inventory membership only avoids loading this packet for unrelated rows.
    # It never admits a row without the source-verified packet below.
    if not ((category=='scenes'and key in SUPPORTED_SCENES)or(category=='choices'and key in SUPPORTED_CHOICES)):return None
    ref=packet()
    if ref is None:return None
    data=ref['data']
    if category=='scenes'and key in data['scenes']:return {'event_id':'box','scene_id':key,'choice_id':None}
    if category=='choices':
        matches=[v for v in data['choices'].values()if key in v['variant_ids']]
        if len(matches)==1:return {'event_id':'box','scene_id':matches[0]['scene_id'],'choice_id':matches[0]['id']}
    return None


def scene_label(result,sid):
    if sid==result['event']['entry_scene_id']:return '最初对话 · 窥视箱中'
    labels={'scene_ro6_end2_1':'拒绝后的对话','scene_ro6_end2_2':'保护证据后的对话','scene_ro6_end2_3':'黑色石板出现异状后的对话'}
    return labels.get(sid,'请选择对话')


def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    scene=result['scenes'].get(sid);choice=result['choices'].get(cid)
    if scene is None or choice is None or cid not in scene['choice_ids']or choice['scene_id']!=sid:return None
    out=deepcopy(choice);out['listed_condition_match']=result['declared_has_covenant']if choice['requires_covenant']else None;return out


def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择要查阅的对话；这里不表示本局已进行到这一步。'
    data=result['data'];scene=result['scenes'][sid];c=choice_reference(result,sid,cid)
    status={None:'尚未确认',True:'按你用于对照的条件：持有',False:'按你用于对照的条件：未持有'}[result['declared_has_covenant']]
    lines=['【正在查阅】窥视箱中',scene_label(result,sid),'','【关键藏品】祭日之契：'+status,'这只是本页的条件对照，不会修改本局持有记录。','','【当前对话】',version._plain(data['originals']['scenes'][sid]['description'])]
    if c:
        lines+=['','【查看的选项】'+c['title'],'【原文写明】',version._plain(c['description'])]
        if c['requires_covenant']:
            message=('尚未确认持有祭日之契，不能认定本局有这个选项；下方只可查资料。'if c['listed_condition_match']is None else'符合原文列出的持有条件；完整游戏前置仍待核验。'if c['listed_condition_match']else'不满足原文列出的持有条件；本页不会把它当可走的分支，后续和作战按钮不可用。')
            lines+=['','【这个选项的已知条件】',message]
        if len(c['variant_ids'])>1:lines+=['','【同文案的不同记录】','游戏资料有三份同文案记录，均写明同一段后续对话。它们的作用方式并不完全相同，实际使用哪份仍未知；这里保留全部，不替你选定。']
        if c['next_scene_id']:lines+=['','【明确的后续对话】',scene_label(result,c['next_scene_id']),'下方按钮仅继续查阅，不会在游戏中选择。']
        if c['stage_ids']:
            lines+=['','【文献明确关联的作战】',*[data['originals']['stages'][s]['name']for s in c['stage_ids']],'可查看固定地图、敌人和出怪资料；这是关联资料，不能当作已经进入或满足全部条件。']
        if c['id']=='covenant':lines+=['这条原选项先指向黑色石板的后续对话。文献在此注明“失恒常量”，不把查图按钮当成实际进入战斗的步骤。']
        if c['battle_destination_unbound']:lines+=['','【作战去向尚未绑定】','文献将“打印”怪物这一项另列为选项四，但没有在这一格写明作战名称。它与黑色石板对话的实际父子关系及具体战斗尚未核验，不借用相邻选项的地图。']
    elif scene['choice_ids']:lines+=['','请选择本段文献列出的选项；不代表本局全部可选。']
    else:lines+=['','文献没有为这段对话明确列出专属后续选项；不把别处的确认选项自动接在这里。']
    lines+=['','【范围与未知】','原事件表仍标记“调查中”。只对照国服10月16日固定资料和修订352356的文献，不证明服务器的出现条件、完整选项或实际结局。','不提供生成概率或路线建议，不操作游戏，不记录领取、选择或战斗，也不改变本局记忆。']
    return '\n'.join(lines)
