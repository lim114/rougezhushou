from pathlib import Path
import hashlib,json,shutil,subprocess
r=Path(__file__).resolve().parents[1]
assert subprocess.check_output(['git','branch','--show-current'],cwd=r,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()=='8ae63bf9e5eb39be22bc5f706cf6f75e35c691f2'
b=json.loads((r/'.cache/section283-main-integration/before-model.json').read_bytes())
for p,d in b['source_sha256'].items():assert hashlib.sha256((r/p).read_bytes()).hexdigest()==d,p
dest=r/'rouge/panel_native_bridge.py';assert not dest.exists();shutil.copyfile(r/'.cache/panel_native_bridge_283.py',dest)
def edit(p,old,new,count=1):
 s=(r/p).read_text();assert s.count(old)==count,(p,old,s.count(old));(r/p).write_bytes(s.replace(old,new).encode('utf8'))
p='rouge/relic_attributes.py'
edit(p,'    original_attack = scenario[\'base_attack\']','    cultivated = dict(attributes)\n    original_attack = scenario[\'base_attack\']')
edit(p,"    scenario['_attribute_attack_speed'] = attributes['attack_speed']\n", "    scenario['_attribute_attack_speed'] = attributes['attack_speed']\n    from .panel_native_bridge import prepare as prepare_native_panels\n    prepare_native_panels(scenario, cultivated, attributes, runes)\n")
p='rouge/estimate.py'
edit(p,"    return {'base_stats':stats,**({'sp_events':sp_events} if sp_events else {}),'skill':{", "    from .panel_native_bridge import normal_terms, first_three_skill_terms\n    native_normal=normal_terms(attributes,scenario['base_attack'],\n        hp_multiplier=hp_bonus+total('hp_pct'),attack_multiplier=total('attack_pct'),\n        defense_multiplier=defense_bonus+total('defense_pct'),defense_flat=defense_flat,\n        resistance_addition=total('resistance_flat'),\n        attack_speed_addition=sum(e['value'] for e in effects if e['kind']=='attack_speed'))\n    native_skill=first_three_skill_terms(scenario,attributes,effects)\n    return {'_panel_native_terms':{'normal':native_normal,'skill':native_skill},\n        'base_stats':stats,**({'sp_events':sp_events} if sp_events else {}),'skill':{")
p='rouge/operator_engine.py'
edit(p,"            'block_count':attributes['block_count']}\n", "            'block_count':attributes['block_count']}\n        from .panel_native_bridge import normal_terms\n        self.native_normal_terms=normal_terms(attributes,self.base,\n            hp_multiplier=self.hp_bonus,attack_multiplier=self.atk_bonus,attack_flat=self.atk_flat,\n            defense_multiplier=self.def_bonus,resistance_addition=self.res_bonus,\n            attack_speed_addition=self.as_bonus)\n")
edit(p,"        result['estimate']={'base_stats':self.stats,", "        from .panel_native_bridge import unknown_skill_terms\n        result['estimate']={'_panel_native_terms':{'normal':self.native_normal_terms,'skill':unknown_skill_terms()},\n            'base_stats':self.stats,")
p='rouge/relics.py'
old="    result['estimate']['base_stats']['defense']+=sum(r['value'] for r in rules if r['kind']=='defense_flat' and not r.get('token_only'))"
new="    defense_flat_reference=sum(r['value'] for r in rules if r['kind']=='defense_flat' and not r.get('token_only'))\n    result['estimate']['base_stats']['defense']+=defense_flat_reference\n    from .panel_native_bridge import add_final_term\n    add_final_term(result['estimate'],'normal','defense','final_addition',defense_flat_reference)"
edit(p,old,new)
edit(p,"        stats['attack_speed_reference']=permanent+active", "        add_final_term(result['estimate'],'normal','attack_speed','addition',active)\n        add_final_term(result['estimate'],'skill','attack_speed','addition',skill_bonus)\n        stats['attack_speed_reference']=permanent+active")
p='rouge/damage.py'
edit(p,"    finish_mei_module_reference(scenario,result)\n    from .reporting import build_report", "    finish_mei_module_reference(scenario,result)\n    from .panel_native_bridge import finish as finish_native_panels\n    finish_native_panels(scenario,result)\n    from .reporting import build_report")
p='rouge/calibration.py'
edit(p,"            'rune_sources':deepcopy(resolved.get('_attribute_runes',[])),", "            'rune_sources':deepcopy(resolved.get('_attribute_runes',[])),\n            'native_panel_reference':deepcopy(result['panel_native_finalization']),")
p='rouge/reporting.py'
edit(p,"    sections.extend(current_output_breakdown_sections(result))", "    from .panel_native_bridge import report_section as native_panel_section\n    native_panel=native_panel_section(result)\n    if native_panel is not None:sections.append(native_panel)\n    sections.extend(current_output_breakdown_sections(result))")
p='rouge/offline_tools_view.py'
start=(r/p).read_text();idx=start.index("        elif command == 'panel':")
anchor="        elif command == 'panel':"
renderer='''def _native_panel_tables(data):
    from .panel_native_bridge import PHASE_NAMES,LABELS,conditional_value
    parts=[_h('同一主结果 · 原生算式与精度核验'),
        _p('来源核验：'+_text(data['source_valid'])+'；各层使用独立名义快照，不推断保护值编码/解码相等。')]
    for phase,label in PHASE_NAMES.items():
        rows=[row for row in data['fields'] if row['phase']==phase]
        if rows:
            parts += [_h(label),_table(['属性','现有模型值','条件算式/编码前参考','数值条件已闭合','完整原生值'],
                [(LABELS[row['field']],row['model_value'],conditional_value(row),row['conditional_complete'],None) for row in rows])]
    parts += [_p('藏品层为类型写回前参考；常态/技能层为固定名义参数的重算参考。'),
        _p('实际注册与范围覆盖、缓存、反射目标、当前热更新和原生完整面板：未知。')]
    return parts


'''
edit(p,'def _sp_recovery_attribute_tables(data):',renderer+'def _sp_recovery_attribute_tables(data):')
s=(r/p).read_text();begin=s.index(anchor);end=s.index('        elif ',begin+len(anchor))
block=s[begin:end]
block += "            parts += _native_panel_tables(data['native_panel_reference'])\n"
s=s[:begin]+block+s[end:];(r/p).write_bytes(s.encode('utf8'))
w='<!-- section283-active:start -->\n## 第283节进行中 · 主面板接入五属性原生算式与精度资格\n\n已有培养/符文/天赋/技能层不重复计功，保留现有名义模型与支持范围。新增共享五属性finalizer：同一源选择供主线，首三人normal/skill按已有primitive直接构造，不从结果相除推输入；符文3桶与普通4桶分开，五范围/typed写回/全RC条件数值与actual分离。培养与后层独立名义basis不借codec回环；其余技能native基值未闭合时保留未知但旧模型不降级。四层校准和主报告复用主求值，不另加独立query。\n\n验收：33公开旧模型冻结对照、同主结果四层/五属性、9技能、已证参数与完整未知并列、三态read/write/manager前缀与sourcefresh反例、当前Windows面板/刷新保留及私人状态不变。最新full275历史不冒充当前283，下一290/final300。\n<!-- section283-active:end -->\n\n'
(r/'WORK_IN_PROGRESS.md').write_bytes((w+(r/'WORK_IN_PROGRESS.md').read_text()).encode('utf8'))
print('283 main-path bridge integrated; formal validation and publication pending')
