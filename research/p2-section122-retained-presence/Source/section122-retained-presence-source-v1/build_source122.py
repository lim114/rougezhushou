from pathlib import Path
import json,hashlib,ast,difflib
P=Path(__file__).parent
blocks={}
def change(rel,old,new):
    rows=blocks.setdefault(rel,[])
    rows.append({'old_lf':old,'new_lf':new,'old_lf_sha256':hashlib.sha256(old.encode()).hexdigest(),'new_lf_sha256':hashlib.sha256(new.encode()).hexdigest()})

r='rouge/run_state.py'
change(r,'from .catalog import catalog,operator_profiles,tactical_tools\n','from .catalog import catalog,operator_profiles,tactical_tools\nfrom .record_flags import (record_flag,active_record,unconfirmed_record_ids,unconfirmed_item_ids,\n    memory_has_unconfirmed_items,metadata_mask,RUN_METADATA_KEYS,RECIPIENT_KEYS)\n')
change(r,"            if (member.get('scope')!='run' or member.get('present') is not True\n", "            if (member.get('scope')!='run' or member.get('present') is not True\n                    or metadata_mask(member).intersection(('recruitment_kind',*RECIPIENT_KEYS))\n")
change(r,"            if record.get('held', True) and identity not in known:reject()\n","            if active_record(record, 'held') and identity not in known:reject()\n")
change(r,"        if not signature or type(count) is not int or len(signature)!=count:return\n        icons=[]\n", "        if not signature or type(count) is not int or len(signature)!=count:return\n        # A historical slot cannot overrule an unqualified possession flag.\n        unknown=set(unconfirmed_item_ids(self.state))\n        if any(unknown.intersection(candidates) for candidates in signature):return\n        icons=[]\n")
change(r,"                if rid in self.state['relics'] and self.state['relics'][rid].get('held',True)]\n","                if rid in self.state['relics'] and active_record(self.state['relics'][rid],'held')]\n")
change(r,"        memory=copy.deepcopy(state.get('relic_icon_memory'))\n", "        retained_memory=state.get('relic_icon_memory')\n        suspended=memory_has_unconfirmed_items(state,retained_memory)\n        memory=None if suspended else copy.deepcopy(retained_memory)\n")
change(r,"        else:state['relic_icon_memory']=None\n", "        elif not (suspended and count is None and not icons and not current_ids and not tools):\n            state['relic_icon_memory']=None\n        # A metadata-only read leaves suspended raw memory intact; it cannot\n        # replay or silently delete that historical possession evidence.\n")
change(r,"                if record.get('held',True) and record.get('source')=='held_icon_and_run_difficulty':\n", "                if active_record(record,'held') and record.get('source')=='held_icon_and_run_difficulty':\n")
change(r,'    def apply(self,observed,captured_at):\n', '''    def confirm_record_flag(self,kind,identity,record,key,value,captured_at):
        """Retain an unknown raw flag when fresh direct evidence qualifies it.

        Qualification is not an acquisition, departure or recruitment event.
        The caller supplies the already established observation's bool; this
        method cannot infer a game lifecycle from an invalid old JSON value.
        """
        if record_flag(record,key) is None:
            self.state['history'].append({'at':captured_at,'kind':'state_flag_reconfirmed',
                'record_kind':kind,'id':identity,'field':key,
                'previous_value':copy.deepcopy(record[key]),'value':value,
                'previous_record':copy.deepcopy(record)})
            if kind=='operator' and key=='present':
                record['unconfirmed_run_metadata']=sorted(metadata_mask(record)|set(RUN_METADATA_KEYS))
                record['qualified_char_buff_ids']=[]

    def apply(self,observed,captured_at):
''')
change(r,"        prior_held=set(self.held_relic_ids())\n", "        prior_held=set(self.held_relic_ids())\n        prior_unknown_held=set(unconfirmed_record_ids(state['relics'],'held'))\n")
change(r,"            if rid not in state['relics'] or not state['relics'][rid].get('held',True):\n                state['history'].append({'at':captured_at,'kind':'relic_confirmed','id':rid})\n", "            prior=state['relics'].get(rid,{})\n            if rid not in state['relics'] or record_flag(prior,'held') is False:\n                state['history'].append({'at':captured_at,'kind':'relic_confirmed','id':rid})\n            self.confirm_record_flag('relic',rid,prior,'held',True,captured_at)\n")
change(r,"            if tid not in state['tactical_tools'] or not state['tactical_tools'][tid].get('held',True):\n                state['history'].append({'at':captured_at,'kind':'tool_confirmed','id':tid})\n", "            prior=state['tactical_tools'].get(tid,{})\n            if tid not in state['tactical_tools'] or record_flag(prior,'held') is False:\n                state['history'].append({'at':captured_at,'kind':'tool_confirmed','id':tid})\n            self.confirm_record_flag('tactical_tool',tid,prior,'held',True,captured_at)\n")
change(r,"                if rid not in incoming and record.get('held',True):\n                    record['held']=False\n                    state['history'].append({'at':captured_at,'kind':'relic_no_longer_held','id':rid})\n", "                if rid not in incoming and record_flag(record,'held') is not False:\n                    prior=record_flag(record,'held')\n                    self.confirm_record_flag('relic',rid,record,'held',False,captured_at)\n                    record['held']=False\n                    if prior is True:\n                        state['history'].append({'at':captured_at,'kind':'relic_no_longer_held','id':rid})\n")
change(r,"                if tid not in incoming_tools and record.get('held',True):\n                    record['held']=False\n                    state['history'].append({'at':captured_at,'kind':'tool_no_longer_held','id':tid})\n", "                if tid not in incoming_tools and record_flag(record,'held') is not False:\n                    prior=record_flag(record,'held')\n                    self.confirm_record_flag('tactical_tool',tid,record,'held',False,captured_at)\n                    record['held']=False\n                    if prior is True:\n                        state['history'].append({'at':captured_at,'kind':'tool_no_longer_held','id':tid})\n")
change(r,"            previous=state['operators'].get(member['id'],{})\n", "            previous=state['operators'].get(member['id'],{})\n            prior_presence=record_flag(previous,'present')\n            prior_metadata_mask=metadata_mask(previous)\n")
change(r,"            changed_origin=origin is not None and previous.get('recruitment_kind') is not None and origin!=previous['recruitment_kind']\n", "            changed_origin=prior_presence is not None and 'recruitment_kind' not in prior_metadata_mask and origin is not None and previous.get('recruitment_kind') is not None and origin!=previous['recruitment_kind']\n")
change(r,"            corrected=(origin is not None and isinstance(origin_source,dict)\n", "            corrected=(prior_presence is not None and 'recruitment_kind' not in prior_metadata_mask and origin is not None and isinstance(origin_source,dict)\n")
change(r,"            if ((type(prior_elite) is int and type(current_elite) is int and current_elite>prior_elite)\n                    or previous.get('advanced') is False and member.get('advanced') is True):\n", "            elite_qualified=not ('unconfirmed_run_metadata' in previous and 'elite' in previous.get('invalid_fields',[]))\n            if (prior_presence is not None and ((elite_qualified and type(prior_elite) is int and type(current_elite) is int and current_elite>prior_elite)\n                    or 'advanced' not in prior_metadata_mask and previous.get('advanced') is False and member.get('advanced') is True)):\n")
change(r,"            returned=bool(previous) and not previous.get('present',True)\n", "            returned=bool(previous) and prior_presence is False\n            if prior_presence is None:\n                # Keep old leaves, but an identity re-read does not reconfirm\n                # the historical cultivation hidden by an unknown presence.\n                invalid.update(previous.get('fields',{}))\n                invalid_ranks.update(previous.get('skill_ranks',{}))\n            self.confirm_record_flag('operator',member['id'],previous,'present',True,captured_at)\n")
change(r,"            if fields!=previous.get('fields') or ranks!=previous.get('skill_ranks') or not previous.get('present',True) or advanced_changed:\n", "            if fields!=previous.get('fields') or ranks!=previous.get('skill_ranks') or prior_presence is False or advanced_changed:\n")
change(r,"            from .recipient_state import merge_recipient_evidence\n", """            merged=state['operators'][member['id']]
            mask=metadata_mask(merged)
            if mask:
                if origin is not None:mask.discard('recruitment_kind')
                if 'advanced' in member:mask.discard('advanced')
                if 'char_buff_ids' in member:
                    if member.get('char_buffs_complete') is True:
                        mask.difference_update(RECIPIENT_KEYS)
                        merged.pop('qualified_char_buff_ids',None)
                    elif mask.intersection(RECIPIENT_KEYS):
                        prior=[] if changed_origin or returned else previous.get('qualified_char_buff_ids',[])
                        if type(prior) is not list or any(type(bid) is not str for bid in prior):prior=[]
                        merged['qualified_char_buff_ids']=list(dict.fromkeys(prior+member['char_buff_ids']))
                merged['unconfirmed_run_metadata']=sorted(mask)
            from .recipient_state import merge_recipient_evidence
""")
change(r,"                if key not in current and member.get('present',True):\n                    member['present']=False\n                    state['history'].append({'at':captured_at,'kind':'operator_no_longer_present','id':key})\n", "                if key not in current and record_flag(member,'present') is not False:\n                    prior=record_flag(member,'present')\n                    self.confirm_record_flag('operator',key,member,'present',False,captured_at)\n                    member['present']=False\n                    if prior is True:\n                        state['history'].append({'at':captured_at,'kind':'operator_no_longer_present','id':key})\n")
change(r,"        invalidate_recipient_absence(state,members,set(self.held_relic_ids())-prior_held,promoted_ids,captured_at)\n", "        invalidate_recipient_absence(state,members,set(self.held_relic_ids())-prior_held-prior_unknown_held,promoted_ids,captured_at)\n")
change(r,"        complete=_inventory_confirmation_flag(self.state['inventory_verified']) and count is not None and known+tools==count\n        return {'source':'run_capture','complete':complete,\n", "        complete=_inventory_confirmation_flag(self.state['inventory_verified']) and count is not None and known+tools==count\n        unknown=unconfirmed_item_ids(self.state)\n        if complete and unknown:complete=False\n        return {**({'unconfirmed_item_ids':unknown} if unknown else {}),'source':'run_capture','complete':complete,\n")
change(r,"        return sorted(tid for tid,record in self.state['tactical_tools'].items() if record.get('held',True))\n", "        return sorted(tid for tid,record in self.state['tactical_tools'].items() if active_record(record,'held'))\n")
change(r,"        return sorted(rid for rid,record in self.state['relics'].items() if record.get('held',True))\n", "        return sorted(rid for rid,record in self.state['relics'].items() if active_record(record,'held'))\n")
change(r,"        names=[operator_profiles()[key]['name']+('（已离队，保留记录）' if not member.get('present',True) else '')\n", "        names=[operator_profiles()[key]['name']+('（在场状态未确认，保留记录）' if record_flag(member,'present') is None else\n                '（已离队，保留记录）' if record_flag(member,'present') is False else '')\n")
change(r,"               +('（已进阶）' if member.get('advanced') else '')\n", "               +('（已进阶）' if record_flag(member,'present') is not None and 'advanced' not in metadata_mask(member) and member.get('advanced') else '')\n")
change(r,"               +('（应急雇佣，仅一次作战）' if member.get('recruitment_kind')=='emergency_hire' else '')\n", "               +('（应急雇佣，仅一次作战）' if record_flag(member,'present') is not None and 'recruitment_kind' not in metadata_mask(member) and member.get('recruitment_kind')=='emergency_hire' else '')\n")
change(r,"        present=sum(bool(member.get('present',True)) for member in state['operators'].values())\n", "        present=sum(active_record(member,'present') for member in state['operators'].values())\n")
change(r,"            resources or '源石锭/零件数尚未确认',\n", "            resources or '源石锭/零件数尚未确认',\n            *(['部分记录的持有状态未确认；原记录保留，暂不自动套用对应持有效果与层数。'] if status.get('unconfirmed_item_ids') else []),\n")

r='rouge/training_view.py'
change(r,'from .account_cache import _record_issue\n','from .account_cache import _record_issue\nfrom .catalog import operator_profiles\nfrom .record_flags import record_flag,active_record,metadata_mask,projected_run_metadata\n')
change(r,"    if (not enabled or not member or not member.get('present', True)\n", "    if (not enabled or not member or not active_record(member, 'present')\n")
change(r,"    if not member or not member.get('present', True):\n        return {'state': account, 'notice': '', 'selection': 'account'}\n", "    if not member or record_flag(member, 'present') is False:\n        return {'state': account, 'notice': '', 'selection': 'account'}\n    if record_flag(member, 'present') is None:\n        return {'state': account,\n                'notice': '本局记录的在场标记未确认；暂用标注的账号参考或档案预览，不自动确认该成员的本局培养与强化，原记录保留。',\n                'selection': 'account_after_unconfirmed_presence'}\n")
change(r,"    return member\n", "    return projected_run_metadata(member)\n")
change(r,"    current = {key: value for key, value in member.get('fields', {}).items()\n", "    member = projected_run_metadata(member)\n    current = {key: value for key, value in member.get('fields', {}).items()\n")
change(r,"    try:\n        return format_operator_observation({**member, 'id': op})\n", """    try:
        if record_flag(member,'present') is None:
            return (f'干员：{operator_profiles()[op]["name"]}\\n'
                    '本局记录的在场状态未确认；原培养、来源与强化仅作保留记录，请重新读取相应页面确认。')
        view=projected_run_metadata(member)
        text=format_operator_observation({**view, 'id': op})
        if metadata_mask(member):
            text+='\\n部分保留的来源或强化资格尚未确认；仅使用此次重新读取的明确字段与强化。'
        return text
""")

r='rouge/recipient_state.py'
change(r,'from .relics import mechanics\n','from .relics import mechanics\nfrom .record_flags import active_record,metadata_mask,RECIPIENT_KEYS\n')
change(r,"    absent = set() if new_recruitment or not previous else absent_buffs(previous)\n", "    if metadata_mask(merged).intersection(RECIPIENT_KEYS) and 'char_buff_ids' not in observed:\n        return  # Retain raw popup evidence; identity-only reads cannot renew it.\n    absent = set() if new_recruitment or not previous else absent_buffs(previous)\n")
change(r,"    held = {rid for rid, record in state['relics'].items() if record.get('held', True)}\n", "    held = {rid for rid, record in state['relics'].items() if active_record(record, 'held')}\n")
change(r,"        if member.get('scope') != 'run' or not member.get('present', True):\n", "        if (member.get('scope') != 'run' or not active_record(member, 'present')\n                or metadata_mask(member).intersection(RECIPIENT_KEYS)):\n")

r='rouge/relic_counter_semantics.py'
change(r,'from .relics import mechanics\n','from .relics import mechanics\nfrom .record_flags import active_record\n')
change(r,'    losses={}\n', '    losses={};qualification_cutoffs={}\n')
change(r,"        at=event.get('at')\n        if rid and type(at) in (int,float) and math.isfinite(at):\n", "        at=event.get('at')\n        if (event.get('kind')=='state_flag_reconfirmed' and event.get('record_kind')=='relic'\n                and event.get('field')=='held' and type(event.get('value')) is bool\n                and isinstance(event.get('id'),str) and type(at) in (int,float) and math.isfinite(at)):\n            identity=event['id']\n            qualification_cutoffs[identity]=max(qualification_cutoffs.get(identity,float('-inf')),at)\n        if rid and type(at) in (int,float) and math.isfinite(at):\n")
change(r,"                or not state['relics'][rid].get('held',True)\n                or losses.get(rid,float('-inf'))>=at):continue\n", "                or not active_record(state['relics'][rid],'held')\n                or losses.get(rid,float('-inf'))>=at\n                or qualification_cutoffs.get(rid,float('-inf'))>at):continue\n")

r='rouge/app.py'
change(r,'from .run_state import RunState\n','from .run_state import RunState\nfrom .record_flags import active_record\n')
change(r,"            available=[key for key,member in self.run.state['operators'].items() if key in catalog()['operators'] and member.get('present',True)]\n", "            available=[key for key,member in self.run.state['operators'].items() if key in catalog()['operators'] and active_record(member,'present')]\n")
change(r,"                     if key in operator_profiles() and member.get('present',True) and member.get('scope')!='account')\n", "                     if key in operator_profiles() and active_record(member,'present') and member.get('scope')!='account')\n")

r='rouge/run_metadata_view.py'
change(r,'\n\ndef format_run_buff_status(state, buffs):\n','\nfrom .record_flags import record_flag,active_record,metadata_mask,projected_run_metadata,RECIPIENT_KEYS\n\n\ndef format_run_buff_status(state, buffs):\n')
change(r,"    current = state.get('scope') == 'run'\n", """    if state.get('scope')=='run' and record_flag(state,'present') is None:
        return '本局记录的在场状态未确认；原强化记录保留，暂不自动套用。'
    qualified=projected_run_metadata(state)
    if (state.get('scope')=='run' and active_record(state,'present')
            and metadata_mask(state).intersection(RECIPIENT_KEYS) and not qualified.get('char_buff_ids')):
        return '保留的个人强化资格尚未重新确认；原记录保留，暂不自动套用。'
    retained=metadata_mask(state).intersection(RECIPIENT_KEYS)
    state=qualified
    current = state.get('scope') == 'run' and active_record(state,'present')
""")
change(r,"    return text\n", "    if current and retained:text+='；其他保留的个人强化资格尚未重新确认。'\n    return text\n")

r='tests/test_cache_consumers_101.py'
change(r,'''    def test_summary_counts_present_members_with_the_existing_truthiness_gate(self):
        for value, expected in (('yes', 1), (None, 0), ([], 0), ([1], 1), ({}, 0),
                                ({'public': 1}, 1), (False, 0), (True, 1), (0, 0), (1, 1)):
            with self.subTest(value=value):
                run, raw = self.load({'operators': {'mechanist': {'present': value}}})
                text = self.view_unchanged(run, raw, run.summary)
                self.assertIn(f'当前已识别 {expected} /', text)
                self.assertEqual(native(run.state['operators']['mechanist']['present']), native(value))
''','''    def test_summary_counts_only_qualified_presence_and_retains_unknown_raw_flags(self):
        # Section122 intentionally replaces the old non-bool truthiness claim.
        # Boolean controls and the next method's missing-default contract stay.
        for value in ('yes', None, [], [1], {}, {'public': 1}, False, True, 0, 1):
            with self.subTest(value=value):
                run, raw = self.load({'operators': {'mechanist': {'present': value}}})
                text = self.view_unchanged(run, raw, run.summary)
                self.assertIn(f'当前已识别 {int(value is True)} /', text)
                if type(value) is not bool:self.assertIn('在场状态未确认', text)
                self.assertEqual(native(run.state['operators']['mechanist']['present']), native(value))
''')

r='scripts/verify_cloud.py'
change(r,'MODULES = (\n','MODULES = (\n    "tests.test_retained_presence_122",\n')

metadata={}
for rel,rows in blocks.items():
    before=(P/'baseline'/rel).read_bytes();current=before;crlf=b'\r\n' in before
    for row in rows:
        old=row['old_lf'].replace('\n','\r\n').encode() if crlf else row['old_lf'].encode()
        new=row['new_lf'].replace('\n','\r\n').encode() if crlf else row['new_lf'].encode()
        assert current.count(old)==1,(rel,row['old_lf'][:100],current.count(old));current=current.replace(old,new,1)
    q=P/'candidate'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(current)
    tree=ast.parse(current.decode());compile(tree,rel,'exec')
    metadata[rel]={'baseline_bytes':len(before),'baseline_sha256':hashlib.sha256(before).hexdigest(),'candidate_bytes':len(current),'candidate_sha256':hashlib.sha256(current).hexdigest(),'CRLF_preserved':crlf,'blocks':rows}
    patch=''.join(difflib.unified_diff(before.decode().splitlines(True),current.decode().splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
    q=P/'diffs'/(rel.replace('/','__')+'.patch');q.parent.mkdir(exist_ok=True);q.write_text(patch,encoding='utf-8')
(P/'local-transports.json').write_text(json.dumps({'kind':'SOURCE_ONLY_UNEXECUTED_LOCAL_TRANSPORT','planned_section':122,'targets':metadata,'root_application_rule':'Rebind every target and single-match local block against actual section121 Source. Do not replace the full future app or any candidate snapshot. All other bytes and line endings must remain unchanged.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('compiled_only_targets',len(metadata),'blocks',sum(len(v['blocks']) for v in metadata.values()),'project_executions',0)
