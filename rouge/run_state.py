"""Separate current exploration evidence from permanent account profiles."""
import json
import time
import uuid
import copy
import math
from collections import Counter
from pathlib import Path
from .catalog import catalog,operator_profiles,tactical_tools
from .relic_recognition import resolve_owned_icons,resolve_difficulty_icons,difficulty_families

def _validate_saved_containers(saved):
    """Qualify the shapes consumed by restart and views before installing data.

    Unknown extra fields remain opaque. A rejected file is never repaired or
    replaced: the existing unreadable-file guard owns the fallback state.
    This is a consumer boundary, not a complete game-state schema.
    """
    def reject():
        raise ValueError('Invalid exploration record')

    def mapping(record, key):
        value = record.get(key, {})
        if not isinstance(value, dict):reject()
        return value

    def sequence(record, key, item_type=dict):
        value = record.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, item_type) for item in value):reject()
        return value

    def optional_mapping(record, key):
        if key in record and record[key] is not None and not isinstance(record[key], dict):reject()

    def content(record, key):
        optional_mapping(record, key)
        value = record.get(key)
        if not value:return
        if not isinstance(value.get('title'), str):reject()
        sequence(value, 'scene_candidates', str)
        for option in sequence(value, 'visible_options'):
            if not isinstance(option.get('title'), str):reject()

    def text_sequence(value):
        # The original formatter also handles a string (characters) or JSON
        # object (its string keys). Do not replace those safe old semantics.
        if not isinstance(value, (str, list, dict)):reject()
        if any(not isinstance(item, str) for item in value):reject()

    for key in ('operators', 'relics', 'maps', 'resources', 'tactical_tools'):
        records = mapping(saved, key)
        if any(not isinstance(record, dict) for record in records.values()):reject()
    config = mapping(saved, 'config')
    for key in ('difficulty', 'squad', 'zone'):mapping(config, key)
    history = sequence(saved, 'history')
    sequence(saved, 'node_contents')
    content(saved, 'last_node_content')
    profiles = operator_profiles()
    for oid, member in saved['operators'].items():
        if oid not in profiles:reject()
        for key in ('fields', 'skill_ranks', 'sources', 'field_times', 'skill_times'):
            mapping(member, key)
        for key in ('char_buff_ids', 'char_buff_absent_ids', 'char_buff_pending_ids', 'missing_fields'):
            sequence(member, key, str)
        for key in ('invalid_fields', 'invalid_skill_ranks'):
            sequence(member, key, (str, int))
        optional_mapping(member, 'recipient_buffs')
        popup = member.get('recipient_buffs')
        if popup is not None:sequence(popup, 'ids', str)
    known_relics = catalog()['relics']
    known_tools = tactical_tools()
    for key, known in (('relics', known_relics), ('tactical_tools', known_tools)):
        for identity, record in saved.get(key, {}).items():
            if record.get('held', True) and identity not in known:reject()
            mapping(record, 'icon_evidence')
            label = record.get('icon_evidence', {}).get('tier_label')
            if label is not None and not isinstance(label, str):reject()
    for record in saved.get('resources', {}).values():
        if 'value' not in record or 'captured_at' not in record:reject()
        at = record['captured_at']
        try:
            # Keep the formatter's existing accepted timestamp values,
            # including bool. Inventory counts have a separate permission
            # boundary; that policy does not redefine resource timestamps.
            time.strftime('%H:%M:%S', time.localtime(at))
        except (OverflowError, OSError, TypeError, ValueError):reject()
    difficulty = config.get('difficulty', {})
    if difficulty and 'value' not in difficulty:reject()
    squad = config.get('squad', {})
    if 'name' in squad and not isinstance(squad['name'], str):reject()
    zone = config.get('zone', {})
    if zone and not isinstance(zone.get('name'), str):reject()
    if zone.get('id') is not None and not isinstance(zone['id'], str):reject()
    for zid, graph in saved.get('maps', {}).items():
        nodes = sequence(graph, 'nodes')
        if 'grid' in graph:mapping(graph, 'grid')
        for node in nodes:
            for key in ('remembered_type', 'observed_type', 'template_type'):
                if key in node and node[key] is not None and not isinstance(node[key], str):reject()
            for key in ('content', 'remembered_content'):content(node, key)
            optional_mapping(node, 'prediction')
            sequence(node, 'content_history')
            prediction = node.get('prediction')
            if prediction is not None:
                if prediction and 'candidates' not in prediction:reject()
                sequence(prediction, 'candidates', str)
                for key in ('reason', 'notice'):
                    if prediction.get(key) and not isinstance(prediction[key], str):reject()
            if node.get('remembered_type') == '林间空地' and not isinstance(node.get('id'), str):reject()
        # A partial opaque graph remains acceptable while it has no visible
        # consumer. Matched or selected graphs need the fields the real window
        # indexes, before that graph can reach rendering or route consumers.
        if graph and (graph.get('status') == 'matched' or zid == zone.get('id')):
            if not isinstance(graph.get('template_id'), str):reject()
            grid = mapping(graph, 'grid')
            if any(type(grid.get(key)) is not int or grid[key] < 1 for key in ('rows', 'cols')):reject()
            for node in nodes:
                if not isinstance(node.get('id'), str):reject()
                if any(type(node.get(key)) is not int for key in ('row', 'col')):reject()
                if not 0 <= node['row'] < grid['rows'] or not 0 <= node['col'] < grid['cols']:reject()
                if 'distance' not in node:reject()
            if 'edges' not in graph:reject()
            for edge in sequence(graph, 'edges', list):
                if len(edge) != 2 or any(not isinstance(identity, str) for identity in edge):reject()
            if not isinstance(mapping(graph, 'source').get('url'), str):reject()
            text_sequence(graph.get('limitations', []))
            candidates = {name for node in nodes for name in
                          (node.get('prediction') or {}).get('candidates', [])}
            budget = graph.get('generation_budget', {})
            if budget:
                if not isinstance(budget, dict):reject()
                for name, record in budget.items():
                    if not isinstance(record, dict) or 'known_total' not in record:reject()
                    required = set()
                    if record['known_total']:required.update(('fixed', 'source_max', 'random_eligible'))
                    if name in candidates:required.update(('fixed', 'source_max', 'revealed_additional'))
                    if not required <= record.keys():reject()
                text_sequence(graph.get('generation_limitations', []))
            elif candidates:
                # format_node tests each candidate's membership even in an
                # empty budget. Preserve empty dict/list/string when safe.
                if not isinstance(budget, (dict, list, str)):reject()
                if isinstance(budget, str) and '' in candidates:reject()
            if graph.get('constraint_conflicts'):text_sequence(graph['constraint_conflicts'])
    for event in history:
        if event.get('kind') == 'map_node_revealed':
            for key in ('previous', 'type'):
                if key in event and event[key] is not None and not isinstance(event[key], str):reject()
    signature = saved.get('bar_signature')
    if signature is not None:
        if not isinstance(signature, list):reject()
        for candidates in signature:
            if not isinstance(candidates, list) or any(not isinstance(identity, str) for identity in candidates):reject()
    memory = saved.get('relic_icon_memory')
    if memory is not None:
        if not isinstance(memory, dict):reject()
        if memory and 'icons' not in memory:reject()
        for icon in sequence(memory, 'icons'):
            if not isinstance(icon.get('id'), str):reject()
            if 'candidates' not in icon:reject()
            sequence(icon, 'candidates', str)


def _inventory_confirmation_flag(value):
    """Qualify a saved confirmation claim without rewriting its raw evidence.

    JSON text/containers cannot stand in for an observed inventory proof.
    Preserve the old numeric/None short-circuit contract; this boundary does
    not redefine inventory counts, resource timestamps or the saved schema.
    """
    return value if type(value) in (bool, int, float, type(None)) else False


class RunState:
    def __init__(self,file):
        self.file=Path(file)
        self.preserve_unreadable=False
        self.save_issue=None
        self.reset(save=False)
        repair_needs_save=False
        try:
            saved=json.loads(self.file.read_text(encoding='utf-8'))
            if not isinstance(saved,dict) or not isinstance(saved.get('operators'),dict) or not isinstance(saved.get('relics'),dict):
                raise ValueError('Invalid exploration record')
            _validate_saved_containers(saved)
            self.state.update(saved)
            if 'relic_icon_memory' not in saved:self.restore_relic_icon_memory()
            self.restore_passed_node_types()
            self.state['notice']='已恢复同一局的记忆；切换另一局时请手动点击“开始新局”。'
            repair_needs_save=self.restore_origin_discovery_buffs()
        except FileNotFoundError:
            # A dangling link or unknown lstat is not a confirmed absent entry.
            confirmed_absent=False
            try:self.file.lstat()
            except FileNotFoundError:confirmed_absent=True
            except OSError:pass
            if not confirmed_absent:
                self.preserve_unreadable=True
                self.state['notice']='原本局记录无法读取；手动重置前不会覆盖原路径。'
        except (OSError,ValueError):
            self.preserve_unreadable=True
            self.state['notice']='原本局记录无法读取，已保留原文件；手动重置前不会覆盖它。'
        # Saving accepted repairs is separate from reading/qualifying the file.
        if repair_needs_save:self.save()

    def restore_passed_node_types(self):
        """Repair old clearing overwrites using this layout's recorded evidence only."""
        from .map_recognition import predict_map
        for zid,graph in self.state['maps'].items():
            changed=False
            for node in graph.get('nodes',[]):
                if node.get('remembered_type')!='林间空地':continue
                node.pop('remembered_type',None);node['visited']=True;changed=True
                for event in reversed(self.state['history']):
                    if event.get('zone_id')!=zid:continue
                    if event.get('kind') in ('map_layout_changed','map_confirmed'):break
                    if event.get('kind')!='map_node_revealed' or event.get('node_id')!=node['id']:continue
                    original=event.get('previous') if event.get('type')=='林间空地' else event.get('type')
                    if original and original!='林间空地' and not original.startswith('未知'):
                        node['remembered_type']=original
                        node['type_recovery_source']='same_run_same_layout_history'
                        break
            if changed:predict_map(graph)

    def reset(self,save=True):
        self.state={'id':str(uuid.uuid4()),'started_at':time.time(),'last_read':None,
            'operators':{},'crew_count':None,'selected_operator':None,'relics':{},'relic_count':None,'bar_signature':None,
            'inventory_verified':False,'inventory_confirmed_at':None,'relic_icon_memory':None,
            'history':[],'resources':{},'tactical_tools':{},'config':{},'maps':{},
            'last_node_content':None,'node_contents':[],
            'notice':'等待本局页面读取；同一局记忆仅在手动开始新局后清空。'}
        if save:
            self.preserve_unreadable=False
            self.save()

    def save(self):
        # A failed session must not retry, including after a manual new run.
        # The explicit reset still clears memory; it cannot make failed IO safe.
        if self.preserve_unreadable or self.save_issue:return False
        text=json.dumps(self.state,ensure_ascii=False,indent=2)
        # Decoding an escaped native high/low pair would fold two Python points.
        # Refuse that lossy write before any directory or temporary-file IO.
        if any(0xd800<=ord(a)<=0xdbff and 0xdc00<=ord(b)<=0xdfff
               for a,b in zip(text,text[1:])):
            self.save_issue='本局记录含暂时无法无损保存的文字，保存未完成'
            return False
        # Escape lone code units after JSON quoting, retaining ordinary Unicode
        # and write_text's original platform newline policy.
        text=text.encode('utf-8',errors='backslashreplace').decode('utf-8')
        try:
            self.file.parent.mkdir(exist_ok=True)
            temporary=self.file.with_suffix('.tmp')
            temporary.write_text(text,encoding='utf-8')
            temporary.replace(self.file)
        except OSError:
            self.save_issue='本局记录保存未完成'
            return False
        return True

    def persistence_notice(self):
        if not self.save_issue:return ''
        return (self.save_issue+'；新的读取及“开始新局”的结果仅在当前运行有效。'
            '重新启动可能恢复磁盘中较早的记录；当前运行不会再次写入或覆盖本局记录。')

    def recognition_context(self):
        return {'run_id':self.state['id'],'config':copy.deepcopy({key:value
            for key,value in self.state['config'].items() if key in ('difficulty','squad')})}

    def calculation_resources(self):
        from .relic_counter_semantics import reusable_resources
        return reusable_resources(self.state)

    def restore_origin_discovery_buffs(self,observed=None,*,repaired_at=None):
        """Repair only the recorded unknown-to-known origin discovery clear.

        This uses current-run history and the retained owned-popup receipt. A
        real recruitment change, departure, fresh complete list or conflicting
        receipt cannot restore anything. Historical events remain untouched.
        """
        history=self.state.get('history',[])
        if not isinstance(history,list):return False
        incoming={m['id']:m for m in (observed or {}).get('operators',[])}
        crew=(observed or {}).get('crew_count')
        full_crew=type(crew) is int and len(incoming)==crew
        changed=False
        from .relics import mechanics
        buffs=mechanics()['char_buffs'];profiles=operator_profiles()
        barriers={'recruitment_changed','classification_corrected','operator_no_longer_present',
                  'char_buffs_origin_discovery_repaired','char_buff_absence_invalidated'}
        for oid,member in self.state['operators'].items():
            if (member.get('scope')!='run' or member.get('present') is not True
                    or member.get('char_buff_ids')!=[] or member.get('char_buffs_complete') is not False
                    or member.get('recruitment_kind') not in ('non_emergency','emergency_hire')):continue
            update=incoming.get(oid,{})
            if (full_crew and oid not in incoming
                    or 'char_buff_ids' in update and update.get('char_buffs_complete') is True
                    or update.get('recruitment_kind') is not None
                       and update['recruitment_kind']!=member['recruitment_kind']):continue
            source=member.get('sources',{}).get('char_buff_ids',{})
            if (not isinstance(source,dict) or source.get('source')!='owned_operator_buff_popup'
                    or type(source.get('complete')) is not bool
                    or source['complete'] and source.get('issues')):continue
            indices=[i for i,event in enumerate(history) if isinstance(event,dict)
                     and event.get('id')==oid and event.get('kind')=='char_buffs_updated']
            if len(indices)<2:continue
            index=indices[-1];clear=history[index]
            ids=clear.get('previous_char_buff_ids')
            if (index==0 or clear.get('char_buff_ids')!=[] or not isinstance(ids,list) or not ids
                    or not all(isinstance(bid,str) for bid in ids) or len(set(ids))!=len(ids)):continue
            origin=history[index-1]
            if (not isinstance(origin,dict) or origin.get('kind')!='recruitment_changed'
                    or origin.get('id')!=oid or 'previous_kind' not in origin
                    or origin['previous_kind'] is not None
                    or origin.get('kind_now')!=member['recruitment_kind']
                    or type(clear.get('at')) not in (int,float) or clear['at']!=origin.get('at')):continue
            positive_index=indices[-2]
            positive=history[positive_index]
            if positive.get('char_buff_ids')!=ids:continue
            positive_at=positive.get('at');clear_at=clear['at'];started_at=self.state.get('started_at')
            if (any(type(at) not in (int,float) or not math.isfinite(at)
                    for at in (positive_at,clear_at,started_at))
                    or not started_at<=positive_at<=clear_at):continue
            # A prior disappearance makes this a return, even if the old
            # recruitment kind happened to be unread. Later observations also
            # supersede this specific historical pair.
            relevant=history[positive_index+1:index-1]+history[index+1:]
            if any(isinstance(event,dict) and event.get('id')==oid and
                   (event.get('kind') in barriers or event.get('kind')=='char_buffs_updated'
                    or event.get('kind')=='operator_updated' and event.get('recruitment_kind') is not None
                       and event['recruitment_kind']!=member['recruitment_kind']) for event in relevant):continue
            popup=member.get('recipient_buffs')
            if popup is not None:
                if (not isinstance(popup,dict) or popup.get('operator_id')!=oid
                        or popup.get('source')!=source['source'] or popup.get('ids')!=ids
                        or popup.get('complete') is not source['complete']):continue
            elif source['complete'] is False:
                # An empty partial re-read need not add a history event. Its
                # retained positive popup is therefore required for partials.
                continue
            profile=profiles.get(oid)
            if not profile or any(bid not in buffs or buffs[bid]['required_profession']
                                  and profile['profession'] not in buffs[bid]['required_profession'].split('|')
                                  for bid in ids):continue
            member['char_buff_ids']=list(ids)
            member['char_buffs_complete']=source['complete']
            for key in ('char_buff_absent_ids','char_buff_pending_ids'):
                if key in member:member[key]=[bid for bid in member[key] if bid not in ids]
            history.append({'at':time.time() if repaired_at is None else repaired_at,
                'kind':'char_buffs_origin_discovery_repaired','id':oid,
                'previous_char_buff_ids':[],'char_buff_ids':list(ids),
                'char_buffs_complete':source['complete'],'cleared_at':clear['at'],
                'source':'same_run_owned_popup_and_origin_discovery_history'})
            changed=True
        return changed

    def restore_relic_icon_memory(self):
        """Migrate recorded full-bar candidates, never invent an unseen slot."""
        signature=self.state.get('bar_signature');count=self.state.get('relic_count')
        known=set(catalog()['relics'])|set(tactical_tools())
        if not signature or type(count) is not int or len(signature)!=count:return
        icons=[]
        for candidates in signature:
            if not isinstance(candidates,list) or not candidates or not all(isinstance(r,str) and r in known for r in candidates):return
            confirmed=[(rid,self.state['relics'][rid]) for rid in candidates
                if rid in self.state['relics'] and self.state['relics'][rid].get('held',True)]
            strong=[(rid,r) for rid,r in confirmed if r.get('icon_evidence',{}).get('name_usage_confirmed')]
            icon={'id':candidates[0],'candidates':list(candidates),'confirmed':len(candidates)==1,
                  'source':'historical_held_bar_signature','observed_at':self.state.get('inventory_confirmed_at')}
            if len(strong)==1:
                rid,record=strong[0];icon.update(id=rid,confirmed=True,source='held_icon_and_usage',name_usage_confirmed=True)
                icon['observed_at']=record.get('captured_at')
            elif len(confirmed)==1 and confirmed[0][1].get('source')=='held_icon_and_run_difficulty':
                rid,record=confirmed[0]
                icon.update(record.get('icon_evidence',{}));icon.update(id=rid,confirmed=True,source=record['source'])
                icon['observed_at']=record.get('captured_at')
            icons.append(icon)
        self.state['relic_icon_memory']={'icons':icons,'count':count,'complete_bar':True,
            'captured_at':self.state.get('inventory_confirmed_at'),'source':'legacy_same_run_signature'}

    def reconcile_relic_icons(self,relics,captured_at,*,observed_tool_ids=()):
        """Keep bounded held-bar evidence and resolve it when grade arrives later."""
        state=self.state;icons=copy.deepcopy(relics.get('icons',[]));count=relics.get('count')
        expected=count if count is not None else state['relic_count']
        memory=copy.deepcopy(state.get('relic_icon_memory'))
        if count is not None and (count==0 or count!=state['relic_count']):memory=None
        # Exact owned tool cards are positive inventory evidence even when
        # their small icons are outside the current crop. A contradicted bar
        # must not reappear when a difficulty label is read on a later page.
        tools=set(observed_tool_ids)&set(tactical_tools())
        if memory and tools and not tools<=set(rid for icon in memory['icons'] for rid in icon['candidates']):
            memory=None
        original_derived={i['id'] for i in icons if i.get('source')=='held_icon_and_run_difficulty'}
        current_ids=set(relics.get('ids',[]))-original_derived
        cards=relics.get('cards',[])
        if icons:
            for icon in icons:icon['observed_at']=captured_at
            signature=lambda rows:sorted(tuple(sorted(i['candidates'])) for i in rows)
            previous=memory['icons'] if memory else []
            # A current partial bar can strengthen matching slots. New artwork
            # invalidates a full historical bar; it cannot prove removals.
            covered=bool(previous) and Counter(signature(icons))<=Counter(signature(previous))
            carried=[]
            if covered:
                carried=[{'id':i['id'],'candidates':[i['id']],'confirmed':True,'source':'held_name_and_usage'}
                         for i in previous if i.get('name_usage_confirmed')]
            icons=resolve_owned_icons(icons,cards+carried)
            icons=resolve_difficulty_icons(icons,state['config'].get('difficulty'))
            full=type(expected) is int and len(icons)==expected
            if covered and not full:
                for icon in icons:
                    slots=[j for j,old in enumerate(previous) if old['candidates']==icon['candidates']]
                    if len(slots)==1:previous[slots[0]]=icon
                memory['icons']=previous
            else:
                memory={'icons':icons,'count':expected,'complete_bar':full,'captured_at':captured_at,'source':'held_bar'}
        elif current_ids and memory and not current_ids<=set(i['id'] for i in memory['icons'] if i.get('confirmed')):
            memory=None
        if memory:
            resolved=resolve_difficulty_icons(resolve_owned_icons(memory['icons'],cards),state['config'].get('difficulty'))
            if resolved!=memory['icons']:
                icons=resolved;relics['memory_replay']=True
                relics['source']='held_bar_memory_and_run_difficulty'
                memory['icons']=resolved
            state['relic_icon_memory']=memory
        else:state['relic_icon_memory']=None
        relics['ids']=sorted(current_ids)
        relics['icons']=icons
        # A correction replaces only previous grade-derived identities. The
        # records and events stay in this run's history.
        groups=difficulty_families()
        for icon in icons:
            if not icon.get('confirmed') or icon['id'] not in groups:continue
            group=groups[icon['id']][0]
            for rid,record in state['relics'].items():
                if rid==icon['id'] or rid not in groups or groups[rid][0]!=group:continue
                if record.get('held',True) and record.get('source')=='held_icon_and_run_difficulty':
                    record['held']=False
                    state['history'].append({'at':captured_at,'kind':'relic_variant_corrected',
                        'previous_id':rid,'current_id':icon['id'],'difficulty':state['config'].get('difficulty',{}).get('value')})
        return relics

    def apply(self,observed,captured_at):
        if not observed or captured_at<max(self.state['started_at'],self.state.get('last_read') or 0):return False
        reused_run=observed.get('config_reuse',{}).get('run_id')
        if reused_run and reused_run!=self.state['id']:return False
        from .relics import mechanics
        for member in observed.get('operators',[]):
            if 'char_buffs_complete' in member:
                if type(member['char_buffs_complete']) is not bool:
                    raise ValueError('个人强化列表完整性必须为布尔值。')
                if 'char_buff_ids' not in member:
                    raise ValueError('个人强化列表完整性必须与明确的强化ID列表一起读取。')
            if 'char_buff_ids' not in member:continue
            ids=member['char_buff_ids'];profile=operator_profiles()[member['id']]
            if member.get('scope')!='run' or not isinstance(ids,list) or not all(isinstance(b,str) for b in ids):
                raise ValueError('强化绑定必须来自本局干员记录，且包含有效ID列表。')
            for bid in ids:
                buff=mechanics()['char_buffs'].get(bid)
                if buff is None or (buff['required_profession'] and profile['profession'] not in buff['required_profession'].split('|')):
                    raise ValueError('强化ID或领取干员职业不符。')
        self.restore_origin_discovery_buffs(observed,repaired_at=captured_at)
        state=self.state;relics=dict(observed.get('relics',{'ids':[],'icons':[],'count':None,'source':'unread'}));count=relics.get('count')
        if isinstance(count,bool):
            count=None;relics['count']=None
        from .run_config import config_data,difficulty_value
        for key,record in observed.get('config',{}).items():
            # Reused records retain their original timestamp and never replace
            # more recent evidence or leak across a manually reset run.
            if record.get('reused_from_run'):continue
            if key=='difficulty':
                if difficulty_value(record) is None:continue
                identity='value'
            elif key=='squad':
                squad=config_data()['squads'].get(record.get('id'))
                if not squad or squad['name']!=record.get('name'):continue
                identity='id'
                previous=state['config'].get(key,{})
                if previous.get('name')==record['name'] and previous.get('effect_verified') and not record.get('effect_verified'):continue
            elif key=='zone':
                zone=config_data()['zones'].get(record.get('id'))
                portal=record.get('id') is None and record.get('hidden') and record.get('candidates') and all(
                    key.startswith('zone_portal_') and config_data()['zones'].get(key,{}).get('name')==record.get('name') for key in record['candidates'])
                if not portal and (not zone or zone['name']!=record.get('name')):continue
                record=dict(record);identity='name' if portal else 'id'
                if not portal and record['id'].split('_')[1].isdigit():record['main_zone_index']=int(record['id'].split('_')[1])
                else:
                    previous=state['config'].get(key,{})
                    record.pop('main_zone_index',None)
                    if previous.get('main_zone_index'):record['main_zone_index']=previous['main_zone_index']
            else:continue
            if state['config'].get(key,{}).get(identity)!=record.get(identity):
                state['history'].append({'at':captured_at,'kind':'config_updated','field':key,
                    'previous':state['config'].get(key),'current':dict(record)})
            state['config'][key]={**record,'captured_at':captured_at}
        self.apply_map(observed.get('map'), captured_at)
        content=observed.get('node_content')
        if content and captured_at>=(state.get('last_node_content') or {}).get('captured_at',0):
            from .node_events import content_identity
            last=state.get('last_node_content')
            location=None;graph=observed.get('map')
            if graph and graph.get('content_binding')=='same_frame_selected_node':
                location={'zone_id':graph['zone_id'],'template_id':graph['template_id'],'node_id':graph['selected_node']}
            record={**copy.deepcopy(content),'captured_at':captured_at,'location':location}
            if content_identity(content)!=content_identity(last) or location!=(last or {}).get('location'):
                state['node_contents'].append(record)
                state['history'].append({'at':captured_at,'kind':'node_content_seen','title':content['title'],'location':location})
            state['last_node_content']=record
        prior_icons=state.get('relic_icon_memory')
        prior_inventory_verified=_inventory_confirmation_flag(state['inventory_verified'])
        prior_held=set(self.held_relic_ids())
        relics=self.reconcile_relic_icons(relics,captured_at,
            observed_tool_ids=observed.get('tactical_tools',{}).get('ids',[]))
        current_icons=state.get('relic_icon_memory')
        displaced_full_inventory=bool(prior_inventory_verified and prior_icons and prior_icons.get('complete_bar')
            and (not current_icons or not current_icons.get('complete_bar')))
        for key,record in observed.get('resources',{}).items():
            if key not in ('gold','parts_count'):
                from .relic_counter_semantics import valid_counter_resource
                if not valid_counter_resource(key,record):continue
            if record.get('value')!=state['resources'].get(key,{}).get('value'):
                state['history'].append({'at':captured_at,'kind':'resource_updated','resource':key,'value':record['value']})
            state['resources'][key]={**record,'captured_at':captured_at}
        signature=sorted([sorted(icon['candidates']) for icon in relics.get('icons',[])])
        previous=state['bar_signature']
        old_count=state['relic_count']
        incoming=set(relics.get('ids',[]))
        incoming_tools=set(observed.get('tactical_tools',{}).get('ids',[])) & set(tactical_tools())
        incoming.update(i['id'] for i in relics['icons'] if i.get('confirmed') and i['id'] in catalog()['relics'])
        incoming_tools.update(i['id'] for i in relics['icons'] if i.get('confirmed') and i['id'] in tactical_tools())
        incoming_items=incoming|incoming_tools
        expected=count if count is not None else old_count
        full_bar=expected is not None and len(signature)==expected
        # An unread or partially visible bar is absence of evidence, not a removal.
        changed=displaced_full_inventory or (full_bar and previous is not None and signature!=previous) or (
            count is not None and old_count is not None and count!=old_count) or (
            _inventory_confirmation_flag(state['inventory_verified']) and bool(incoming_items-set(self.held_relic_ids()+self.held_tool_ids())))
        if changed:
            state['inventory_verified']=False
            state['notice']='持有信息变化，保留本局历史并实时核对当前清单；不会因缺失一帧而遗忘。'
            state['history'].append({'at':captured_at,'kind':'inventory_changed','previous_count':old_count,'count':count})
        if full_bar:state['bar_signature']=signature
        if count is not None:state['relic_count']=count
        for rid in incoming:
            if rid not in state['relics'] or not state['relics'][rid].get('held',True):
                state['history'].append({'at':captured_at,'kind':'relic_confirmed','id':rid})
            evidence=next((i for i in relics['icons'] if i.get('confirmed') and i['id']==rid),{})
            state['relics'][rid]={**state['relics'].get(rid,{}),
                'captured_at':evidence.get('observed_at',captured_at),'resolved_at':captured_at,
                'source':evidence.get('source',relics['source']),'held':True,
                'icon_evidence':{k:v for k,v in evidence.items() if k in ('candidates','score','difficulty','difficulty_group',
                    'difficulty_tier','tier_label','difficulty_source','name_usage_confirmed','difficulty_conflict')}}
        for tid in incoming_tools:
            if tid not in state['tactical_tools'] or not state['tactical_tools'][tid].get('held',True):
                state['history'].append({'at':captured_at,'kind':'tool_confirmed','id':tid})
            state['tactical_tools'][tid]={**state['tactical_tools'].get(tid,{}),
                'captured_at':captured_at,'source':observed.get('tactical_tools',{}).get('source',relics['source']),'held':True}
        # Fully identified current/valid historical slots (or explicit zero)
        # prove removals. A partial observation cannot erase unrelated records.
        if (count==0 and not incoming_items and not relics['icons']) or (isinstance(expected,(int,float)) and expected>0 and len(incoming_items)==expected and
                len(relics['icons'])==expected and all(i.get('confirmed') for i in relics['icons'])):
            for rid,record in state['relics'].items():
                if rid not in incoming and record.get('held',True):
                    record['held']=False
                    state['history'].append({'at':captured_at,'kind':'relic_no_longer_held','id':rid})
            for tid,record in state['tactical_tools'].items():
                if tid not in incoming_tools and record.get('held',True):
                    record['held']=False
                    state['history'].append({'at':captured_at,'kind':'tool_no_longer_held','id':tid})
            state['inventory_verified']=True
            state['inventory_confirmed_at']=(state['relic_icon_memory'] or {}).get('captured_at') if relics.get('memory_replay') else captured_at
        crew=observed.get('crew_count')
        if isinstance(crew,bool):crew=None
        promoted_ids=set()
        if crew is not None:
            state['crew_count']=crew
        for member in observed.get('operators',[]):
            previous=state['operators'].get(member['id'],{})
            fields={**previous.get('fields',{}),**member['fields']}
            ranks={**previous.get('skill_ranks',{}),**{str(k):v for k,v in member.get('skill_ranks',{}).items()}}
            invalid=set(previous.get('invalid_fields',[]))
            invalid_ranks=set(previous.get('invalid_skill_ranks',[]))
            origin=member.get('recruitment_kind')
            changed_origin=origin is not None and previous.get('recruitment_kind') is not None and origin!=previous['recruitment_kind']
            returned=bool(previous) and not previous.get('present',True)
            prior_elite=previous.get('fields',{}).get('elite')
            current_elite=member['fields'].get('elite')
            if ((type(prior_elite) is int and type(current_elite) is int and current_elite>prior_elite)
                    or previous.get('advanced') is False and member.get('advanced') is True):
                promoted_ids.add(member['id'])
            corrected=origin is not None and previous.get('sources',{}).get('recruitment_kind',{}).get('source')=='金色应急雇佣标记'
            if corrected:
                state['history'].append({'at':captured_at,'kind':'classification_corrected','id':member['id'],
                    'previous_kind':previous.get('recruitment_kind'),'kind_now':origin,
                    'reason':'旧识别混淆已进阶金色标记与左侧应急人形/时钟标识；旧分类已作废'})
                changed_origin=False
            if changed_origin or returned:
                state['history'].append({'at':captured_at,'kind':'recruitment_changed','id':member['id'],
                    'previous_kind':previous.get('recruitment_kind'),'kind_now':origin,
                    'previous_fields':previous.get('fields',{}),'previous_skill_ranks':previous.get('skill_ranks',{})})
                invalid.update(fields)
                invalid_ranks.update(ranks)
            old_buffs=previous.get('char_buff_ids',[])
            current_buffs=[] if changed_origin or returned else list(old_buffs)
            if 'char_buff_ids' in member:
                current_buffs=list(dict.fromkeys(member['char_buff_ids'] if member.get('char_buffs_complete') is True
                                                else current_buffs+member['char_buff_ids']))
            if current_buffs!=old_buffs:
                state['history'].append({'at':captured_at,'kind':'char_buffs_updated','id':member['id'],
                    'previous_char_buff_ids':old_buffs,'char_buff_ids':current_buffs})
            if 'elite' in member['fields'] and 'elite' in previous.get('fields',{}) and member['fields']['elite']!=previous['fields']['elite']:
                # Keep historical evidence, but promotion does not prove a module or mastery.
                invalid.update({'level','module_id','module_level','selected_skill'})
                invalid_ranks.update(ranks)
            invalid.difference_update(member['fields'])
            invalid_ranks.difference_update(str(k) for k in member.get('skill_ranks',{}))
            advanced_changed='advanced' in member and member['advanced']!=previous.get('advanced')
            if fields!=previous.get('fields') or ranks!=previous.get('skill_ranks') or not previous.get('present',True) or advanced_changed:
                state['history'].append({'at':captured_at,'kind':'operator_updated','id':member['id'],
                    'fields':member['fields'],'skill_ranks':member.get('skill_ranks',{}),
                    'advanced':member.get('advanced'),'recruitment_kind':origin})
            state['operators'][member['id']]={**previous,**member,
                'fields':fields,'skill_ranks':ranks,
                'char_buff_ids':current_buffs,
                'char_buffs_complete':member.get('char_buffs_complete',False) if 'char_buff_ids' in member else
                                      False if changed_origin or returned else previous.get('char_buffs_complete',False),
                'invalid_fields':sorted(invalid),'invalid_skill_ranks':sorted(invalid_ranks),
                'sources':{**previous.get('sources',{}),**member.get('sources',{})},
                'field_times':{**previous.get('field_times',{}),**{key:captured_at for key in member['fields']}},
                'skill_times':{**previous.get('skill_times',{}),**{str(key):captured_at for key in member.get('skill_ranks',{})}},
                'merged_from_pages':True,
                'captured_at':captured_at if member['fields'] or member.get('skill_ranks') else previous.get('captured_at',captured_at),
                'present':True}
            from .recipient_state import merge_recipient_evidence
            merge_recipient_evidence(previous,member,state['operators'][member['id']],
                                     changed_origin or returned,captured_at)
        members=observed.get('operators',[])
        if observed.get('selected_operator') in {m['id'] for m in members}:
            state['selected_operator']=observed['selected_operator']
        if crew is not None and len({m['id'] for m in members})==crew:
            current={m['id'] for m in members}
            for key,member in state['operators'].items():
                if key not in current and member.get('present',True):
                    member['present']=False
                    state['history'].append({'at':captured_at,'kind':'operator_no_longer_present','id':key})
        from .recipient_state import invalidate_recipient_absence
        invalidate_recipient_absence(state,members,set(self.held_relic_ids())-prior_held,promoted_ids,captured_at)
        state['last_read']=captured_at
        if state['notice'].startswith('等待'):state['notice']='同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'
        self.save()
        return True

    def apply_map(self, graph, captured_at):
        if not graph or graph.get('status') != 'matched': return
        from .map_recognition import map_data, predict_map
        template = next((t for t in map_data()['templates'] if t['id']==graph.get('template_id')
                         and t['zone_id']==graph.get('zone_id')), None)
        if not template or {n['id'] for n in graph.get('nodes', [])}!={n['id'] for n in template['nodes']}: return
        zid = graph['zone_id']; maps = self.state['maps']; previous = maps.get(zid)
        if previous and captured_at < previous.get('captured_at', 0): return
        if previous and previous['template_id'] != graph['template_id']:
            self.state['history'].append({'at':captured_at,'kind':'map_layout_changed','zone_id':zid,
                                          'previous':copy.deepcopy(previous),'current_template':graph['template_id']})
        elif not previous:
            self.state['history'].append({'at':captured_at,'kind':'map_confirmed','zone_id':zid,'template_id':graph['template_id']})
        old = {n['id']:n for n in previous['nodes']} if previous and previous['template_id']==graph['template_id'] else {}
        current = copy.deepcopy(graph)
        difficulty=self.state['config'].get('difficulty',{}).get('value')
        if difficulty is not None:
            current['difficulty_value']=difficulty
            current['difficulty_source']='same_run_confirmed_config'
        for key in ('last_confirmed_current_node','current_node_confirmed_at','vantage_confirmed_visits'):
            if previous and previous['template_id']==graph['template_id'] and key in previous:
                current[key]=previous[key]
        position=current.get('current_node')
        if position and position in {n['id'] for n in template['nodes']}:
            old_position=current.get('last_confirmed_current_node')
            if old_position!=position:
                self.state['history'].append({'at':captured_at,'kind':'map_position_updated','zone_id':zid,
                    'previous':old_position,'current':position})
            current['last_confirmed_current_node']=position
            current['current_node_confirmed_at']=captured_at
        else:current['current_node']=None
        for node in current['nodes']:
            saved = old.get(node['id'], {})
            for key in ('remembered_type','revealed_at','remembered_content','content_confirmed_at','content_history','visited','visited_at'):
                if key in saved: node[key] = saved[key]
            label = node.get('observed_type')
            if label == '林间空地':
                # An empty circle can be native to the layout. Only confirmed
                # prior identity or player presence proves a visit/conversion.
                original=saved.get('remembered_type')
                was_revealed=bool(original and original!='林间空地' and not original.startswith('未知'))
                was_here=node['id'] in (position,current.get('last_confirmed_current_node'),
                    previous.get('last_confirmed_current_node') if previous and previous['template_id']==graph['template_id'] else None)
                if saved.get('visited') or was_revealed or was_here:
                    node['visited'] = True
                    if not saved.get('visited'):
                        self.state['history'].append({'at':captured_at,'kind':'map_node_passed','zone_id':zid,
                            'node_id':node['id'],'original_type':original or node.get('template_type')})
                    node['visited_at'] = saved.get('visited_at', captured_at)
            if label and not label.startswith('未知') and label != '林间空地':
                if label != saved.get('remembered_type'):
                    self.state['history'].append({'at':captured_at,'kind':'map_node_revealed','zone_id':zid,
                        'node_id':node['id'],'previous':saved.get('remembered_type'),'type':label})
                node['remembered_type'] = label; node['revealed_at'] = captured_at
            content=node.get('content')
            if content and content.get('source')=='same_frame_selected_node':
                previous_content=saved.get('remembered_content')
                from .node_events import content_identity
                if content_identity(content)!=content_identity(previous_content):
                    self.state['history'].append({'at':captured_at,'kind':'map_node_content_confirmed','zone_id':zid,
                        'node_id':node['id'],'previous':copy.deepcopy(previous_content),'content':copy.deepcopy(content)})
                    if previous_content:
                        node['content_history']=[*saved.get('content_history',[]),copy.deepcopy(previous_content)]
                node['remembered_content']=copy.deepcopy(content);node['content_confirmed_at']=captured_at
        current['captured_at'] = captured_at
        maps[zid] = predict_map(current)

    def inventory_status(self):
        count=self.state['relic_count'];known=len(self.held_relic_ids())
        tools=len(self.held_tool_ids())
        complete=_inventory_confirmation_flag(self.state['inventory_verified']) and count is not None and known+tools==count
        return {'source':'run_capture','complete':complete,
                'recognized':known,'recognized_tools':tools,'total_badge_count':count,
                'expected_count':count-tools if complete else None if tools else count,'run_id':self.state['id'],
                'confirmed_at':self.state.get('inventory_confirmed_at')}

    def held_tool_ids(self):
        return sorted(tid for tid,record in self.state['tactical_tools'].items() if record.get('held',True))

    def held_relic_ids(self):
        return sorted(rid for rid,record in self.state['relics'].items() if record.get('held',True))

    def relic_history_context(self):
        """Derive retained-growth uncertainty from this run's positive evidence.

        Loss removes current possession, but not already gained Hydra stats.
        Neither history length nor map depth establishes their amount. This
        projection never writes a new state field or repairs missing evidence.
        """
        state=self.state;rid='rogue_6_start_4'
        context={'run_id':state['id'],'persistent_growth_unknowns':[]}
        record=state['relics'].get(rid)
        start=state.get('started_at');last=state.get('last_read')
        if (not isinstance(record,dict) or type(record.get('held')) is not bool
                or any(type(at) not in (int,float) or not math.isfinite(at) for at in (start,last))
                or last<start):return context
        events=[event for event in state.get('history',[]) if isinstance(event,dict)
            and event.get('id')==rid and type(event.get('at')) in (int,float)
            and math.isfinite(event['at']) and start<=event['at']<=last]
        confirmed=[event['at'] for event in events if event.get('kind')=='relic_confirmed']
        if not confirmed:return context
        losses=[event['at'] for event in events if event.get('kind')=='relic_no_longer_held'
                and event['at']>=min(confirmed)]
        context['persistent_growth_unknowns'].append({'id':rid,'name':'襁褓九头蛇',
            'source':'same_run_confirmed_relic_history','currently_held':record['held'],
            'growth_status':'unknown','attack_pct':None,'hp_pct':None,
            'first_confirmed_at':min(confirmed),'last_confirmed_at':max(confirmed),
            'last_loss_confirmed_at':max(losses) if losses else None,
            'mechanism_source':'https://prts.wiki/index.php?title=沉沦者的黑流树海/拟造物质编目&oldid=433329'})
        return context

    def summary(self):
        status=self.inventory_status();state=self.state
        notice=state['notice']
        if self.save_issue:
            notice=notice.replace('持续累积并保存','持续累积')+'\n'+self.persistence_notice()
        count='未确认' if state['relic_count'] is None else str(state['relic_count'])
        crew='未确认' if state['crew_count'] is None else str(state['crew_count'])
        names=[operator_profiles()[key]['name']+('（已离队，保留记录）' if not member.get('present',True) else '')
               +('（已进阶）' if member.get('advanced') else '')
               +('（应急雇佣，仅一次作战）' if member.get('recruitment_kind')=='emergency_hire' else '')
               for key,member in state['operators'].items()]
        from .relics import mechanics
        labels={'numeric':'有数值规则','conditional':'需条件','partial':'部分机制','pending':'机制待接入','non_output':'无输出加成'}
        relics=[catalog()['relics'][rid]['name']+('【'+state['relics'][rid]['icon_evidence']['tier_label']+'】'
                if state['relics'][rid].get('icon_evidence',{}).get('tier_label') else '')
                +'（'+labels[mechanics()['relics'][rid]['status']]+'）' for rid in self.held_relic_ids()]
        conflicts=[catalog()['relics'][rid]['name'] for rid in self.held_relic_ids()
                   if state['relics'][rid].get('icon_evidence',{}).get('difficulty_conflict')]
        from .relic_counter_semantics import RESOURCE_LABELS
        usable=self.calculation_resources()
        resources='、'.join(RESOURCE_LABELS.get(key,key)+f' {record["value"]}（'+
            time.strftime('%H:%M:%S',time.localtime(record['captured_at']))+
            (' 最近确认）' if key in usable else ' 历史值，当前层数待确认）')
            for key,record in state.get('resources',{}).items())
        present=sum(bool(member.get('present',True)) for member in state['operators'].values())
        config=state['config'];difficulty=config.get('difficulty',{}).get('value')
        squad=config.get('squad',{})
        info=('保密等级 '+str(difficulty) if difficulty is not None else '保密等级未确认')+' · '+squad.get('name','分队未确认')
        if squad.get('level') is not None:info+='（强化）' if squad['level']==1 else '（基础）'
        if config.get('zone'):info+=' · '+config['zone']['name']
        return '\n'.join([info,f'本局队伍：当前已识别 {present} / {crew} 人', '、'.join(names) or '成员尚未确认',
            f'本局持有：已识别 {status["recognized"]+status["recognized_tools"]} / {count} 件 · '+('持有清单已核对（本局记录）' if status['complete'] else '变更待核对或尚未读全'),
            '藏品：'+('、'.join(relics) or '身份尚未确认'),
            '战术道具：'+('、'.join(tactical_tools()[tid]['name'] for tid in self.held_tool_ids()) or '未读取到'),
            resources or '源石锭/零件数尚未确认',
            *(['变体依据冲突：'+ '、'.join(conflicts)+'；按已读到的完整持有效果保留，请核对保密等级。'] if conflicts else []),notice])
