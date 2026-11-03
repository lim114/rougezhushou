def calculate(self):
        if self._calculation_batch_depth:
            self._calculation_requested = True
            return
        if hasattr(self,'charge_timeline_button'):self.charge_timeline_button.setEnabled(False)
        if hasattr(self,'shield_timeline_button'):self.shield_timeline_button.setEnabled(False)
        if hasattr(self,'healing_budget_button'):self.healing_budget_button.setEnabled(False)
        if hasattr(self,'skill_upgrade_button'):self.skill_upgrade_button.setEnabled(False)
        if hasattr(self,'enemy_comparison_button'):self.enemy_comparison_button.setEnabled(False)
        if hasattr(self,'scenario_library_button'):self.scenario_library_button.setEnabled(False)
        if hasattr(self,'damage_budget_button'):self.damage_budget_button.setEnabled(False)
        self.damage_result=None
        if hasattr(self,'relic_context'):self.damage_form.setRowVisible(self.relic_context,False)
        op=self.operator.currentData()
        self.sync_player_tools(op,self.skill.currentData())
        self.sync_animation_references(op,self.skill.currentData())
        if hasattr(self,'target_buff_list'):
            self.sync_target_buffs(op)
        self.sync_scenario_previews(op,self.skill.currentData())
        if op is None:
            self.show_damage_text('本局总览暂无已确认招募干员。请选择职业分支进行局外预览。')
            return
        if op not in catalog()['operators']:
            state=self.current_operator_state() or {'id':op,'fields':{},'skill_ranks':{}}
            text=format_operator_observation({**state,'id':op},self.training_conditions())
            if not state.get('fields'):text+='\n未读取培养状态，以上为明确的档案预览条件。'
            self.show_damage_text(text+'\n\n此干员可读取培养档案；技能伤害规则尚未实现，不将未知伤害显示为零。')
            return
        if self.skill.currentData() is None:
            self.show_damage_text('该精英阶段尚无已实现的技能，请选择已开放的计算档案。')
            return
        ids = [self.relic_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.relic_list.count())
               if self.relic_list.item(i).checkState() == Qt.CheckState.Checked]
        scenario = {'operator':self.operator.currentData(),'skill':self.skill.currentData(),
            **self.training_conditions(),'deployment_elapsed_seconds':self.deployment_elapsed.value(),
            'healing_targets':self.healing_targets.value(),'continuous_attacks':self.continuous_attacks.isChecked(),
            'skill_rank':self.skill_rank_value(),
            'enemy_defense':self.defense.value(),'enemy_resistance':self.resistance.value(),
            'cooperative':self.cooperative.isChecked(),'preexisting_fragile':self.fragile.isChecked(),
            'charge_count':self.charge_count.value(),'shield_break_count':self.shield_breaks.value(),
            'activation_count':self.activation_count.value(),'companion_attack':self.companion_attack.value(),
            'deployment_stacks':self.stacks.value(),'relic_ids':ids}
        for owner,key,skills,widget in self.model_option_widgets:
            if owner==op and self.skill.currentData() in skills:
                if owner=='mechanist' and key=='mechanist_module_static_reference':
                    from .mechanist_module_reference import qualification
                    if not qualification(scenario)['qualified']:continue
                if owner=='char_133_mm' and key=='mei_module_static_reference':
                    from .mei_module_static_reference import qualification
                    if not qualification(scenario)['qualified']:continue
                if owner=='char_4202_haruka' and key=='haruka_module_target_static_reference':
                    from .haruka_target_static_reference import qualification
                    if not qualification(scenario)['qualified']:continue
                scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()
        state=self.current_operator_state()
        run_state=self.current_run_operator_state()
        scenario['recruitment_kind']=run_state.get('recruitment_kind') if run_state.get('scope')=='run' else None
        scenario['char_buff_ids']=run_state.get('char_buff_ids',[]) if run_state.get('scope')=='run' else []
        scenario['char_buffs_complete']=run_state.get('char_buffs_complete') is True if run_state.get('scope')=='run' else False
        scenario['char_buff_absent_ids']=list(run_state.get('char_buff_absent_ids',[])) if run_state.get('scope')=='run' else []
        scenario['char_buff_pending_ids']=list(run_state.get('char_buff_pending_ids',[])) if run_state.get('scope')=='run' else []
        if self.target_buff_test.isChecked():
            scenario['char_buff_ids']=list(dict.fromkeys(scenario['char_buff_ids']+[
                self.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.target_buff_list.count())
                if self.target_buff_list.item(i).checkState()==Qt.CheckState.Checked]))
            scenario['char_buff_absent_ids']=[bid for bid in scenario['char_buff_absent_ids'] if bid not in scenario['char_buff_ids']]
            scenario['char_buff_pending_ids']=[bid for bid in scenario['char_buff_pending_ids'] if bid not in scenario['char_buff_ids']]
        fields=state.get('fields',{})
        scenario['unconfirmed_training']=[label for key,label in [('elite','精英阶段'),('trust','信赖'),
            ('potential','潜能'),('module_id','模组'),('module_level','模组阶段')] if key not in fields]
        known_ranks=state.get('skill_ranks',{})
        if self.skill_rank_selection()['manual_reference_applied']:
            scenario['unconfirmed_training'].append('所选技能等级（已选账号参考，局外模拟）')
        elif self.skill_rank_selection().get('common_reference_applied'):
            scenario['unconfirmed_training'].append('所选技能等级（已选本局公共等级来源参考，未直接读取）')
        elif str(self.skill.currentData()) not in known_ranks and self.skill.currentData() not in known_ranks:
            scenario['unconfirmed_training'].append('所选技能等级')
        if 'level' not in fields and not self.level_override:scenario['unconfirmed_training'].append('当前等级')
        if fields and state.get('scope')!='run':
            scenario['unconfirmed_training'].append('本局实际培养（当前为干员详情档案）')
        if state.get('scope')=='run':
            confirmed=state['run_confirmed_fields']
            scenario['unconfirmed_training'] += [label+'（账号参考）' for key,label in
                [('level','本局等级'),('elite','本局精英阶段'),('trust','本局信赖'),('potential','本局潜能'),
                 ('module_id','本局模组'),('module_level','本局模组阶段')] if key in fields and key not in confirmed]
        scenario['inventory_status']=self.run.inventory_status() if self.auto_relics.isChecked() else {
            'source':'manual_test','complete':True,'recognized':len(ids),'expected_count':None}
        if self.auto_relics.isChecked():scenario['relic_history_context']=self.run.relic_history_context()
        scenario['run_config']=self.run.state.get('config',{})
        target=self.target_enemy.currentData()
        self.defense.setEnabled(target is None);self.resistance.setEnabled(target is None)
        if target:
            scenario['target_enemy']=dict(target)
            if target['enemy_id']=='enemy_2148_shorbb':scenario['target_enemy']['orb_mode']=self.orb_mode.currentData()
        if self.limit_window.isChecked():
            scenario['window_seconds'] = self.window_seconds.value()
        if self.operator.currentData()=='mechanist' and self.skill.currentData()==2 and self.shield_duration_known.isChecked():
            scenario['skill_duration_seconds']=self.shield_duration.value()
        try:
            profile=catalog()['operators'][op]
            needed=set()
            for rid in ids:
                for effect in active_effects(mechanics()['relics'][rid],rid):
                    if effect.get('target_enemy_id') and target and target['enemy_id']!=effect['target_enemy_id']:continue
                    if matches(effect,profile) or any(matches(effect,t,token=True) for t in profile.get('tokens',{}).values()):
                        if effect.get('condition') and effect['condition']!='emergency_hire':needed.add(effect['condition'])
                        if effect.get('recipient_condition'):needed.add(effect['recipient_condition'])
                        if effect.get('loss_pending_condition'):needed.add(effect['loss_pending_condition'])
                        if effect.get('unit_condition') and profile.get('tokens'):needed.add('token_conditions')
                        if effect.get('enemy_level'):needed.add('enemy_level_type')
            if op=='mechanist' and scenario.get('mechanist_module_static_reference'):
                needed.add('mechanist_target_blocker')
            if op=='char_133_mm' and scenario.get('mei_module_static_reference'):
                needed.add('mei_target_motion')
            self.damage_form.setRowVisible(self.relic_context,bool(needed))
            self.damage_form.labelForField(self.relic_context).setText('局外情景条件（测试）' if needed & {'mechanist_target_blocker','mei_target_motion'} else '当前藏品条件（测试）')
            examples={'mei_target_motion':'fly','mechanist_target_blocker':'own_token','gold':25,'parts_count':3,'empty_slots':4,'current_hp_ratio':.65,'deployed_casters':2,'adjacent_allies':1,
                'skill_cast_stacks':1,'altar_stacks':3,'chitin_recipient':1,'battle_start_shields':1,'blocked_enemies':1,
                'probe_stacks':2,'fire_rod_stacks':3,'deployment_hp_ratio':.65,'deployment_loss_unused':1,'enemy_level_type':'ELITE',
                'grudge_stacks':100,'deployed_seconds':80,'near_protection_point':1,'enemy_first_damage_unused':1,
                'entered_zone_count':2,'active_other_aura_sources':1,'mercenary_recipient':1,'mercenary_stacks':1,
                'token_conditions':{tid:{'blocked_enemies':1} for tid in profile.get('tokens',{})}}
            labels={'mechanist_target_blocker':'当前目标阻挡身份：self本体、own_token所属召唤物、other其他单位、none未阻挡、unknown未确认；不能用人数代替。此值仅来自手动局外声明。','parts_count':'当前零件箱实有零件数量（不是容量或估价）；悲伤的红计数上限99',
                'mei_target_motion':'fly声明当前目标满足原生FLY_ONLY；not_fly不满足；unknown未确认。只接受手动局外声明，不由敌人基础分类或浮空参数推断。',
                'altar_stacks':'圆石祭坛实际层数（非战斗次数，最多10）','chitin_recipient':'当前干员是否获得几丁质刺刃（0/1）',
                'battle_start_shields':'开战时的对局护盾值（不是屏障）','blocked_enemies':'本体实际阻挡敌人数（不是阻挡上限）',
                'probe_stacks':'探测先锋实际层数（最多99）','token_conditions':'各召唤物独立阻挡条件（不继承本体）'}
            labels.update(empty_slots='零件箱空栏数（容量减已持有数量，不能以零件数代替）',
                grudge_stacks='仇名录实际击杀叠层（独立乘算，最多999；不由战斗次数推断）',
                deployed_seconds='当前干员已在场秒数（局外条件，不读取实时站位）',
                near_protection_point='当前干员位于蓝色目标点周围八格（0/1，局外条件）',
                enemy_first_damage_unused='当前技能开始时，该干员对本目标的首次伤害尚未触发（0/1）',
                entered_zone_count='已累计进入的新区域计数（非当前主楼层；不能用楼层号替代）',
                active_other_aura_sources='犬植浆当前生效的其他干员光环数，已排除自身及阻挡失效条件（局外情景）',
                mercenary_recipient='当前干员是否为佣兵饰物的实际受益者（0/1）',
                mercenary_stacks='佣兵饰物当前总层数，包含初始1层，最多10层；不是额外完美作战次数',
                fire_rod_stacks='厄运火杆实际层数，0–99；不能由楼层或任意战斗胜利次数推断',
                deployment_hp_ratio='他缚本次部署损血事件前生命比例（0–1，独立局外参考，不读取实时生命）',
                deployment_loss_unused='本次部署他缚损血是否尚未触发（0/1）；重算不推进此状态，退场后新部署需重新确认情景')
            self.relic_context.setPlaceholderText('局外情景示例（不会自动套用）：'+json.dumps({k:examples.get(k,0) for k in sorted(needed)},ensure_ascii=False))
            self.relic_context.setToolTip('只使用当前适用藏品或已选模组参考的条件；留空保持未确认，测试值不写入本局记忆。\n'+
                '\n'.join(k+'：'+labels.get(k,'当前藏品所需的明确计算条件') for k in sorted(needed)))
            resources=self.run.calculation_resources()
            context={name:r['value'] for name,r in resources.items() if name in needed and name not in ('mechanist_target_blocker','mei_target_motion')}
            parts=resources.get('parts_count',{})
            if 'empty_slots' in needed and isinstance(parts.get('capacity'),int) and isinstance(parts.get('value'),int):
                context['empty_slots']=parts['capacity']-parts['value']
            if needed and self.relic_context.toPlainText().strip():
                preview=parse_preview_object(self.relic_context.toPlainText(),'藏品测试条件')
                context.update({k:v for k,v in preview.items() if k in needed})
            if 'enemy_level_type' in context:scenario['enemy_level_type']=context.pop('enemy_level_type')
            scenario['relic_context']=context
            scenario['relic_context_source']='本局最近确认的计数；测试条件仅用于预览'
            scenario['timing_mode']='frames' if self.frame_timing.isChecked() else 'continuous'
            if self.timing_scenario.toPlainText().strip():
                scenario['timing']=parse_preview_object(self.timing_scenario.toPlainText(),'战斗时序情景')
            if op=='char_1050_chen3' and self.chen_motion_orientation.currentData() is not None:
                scenario['chen_motion_orientation']=self.chen_motion_orientation.currentData()
            if self.frame_timing.isChecked():
                for field,widget in (('normal_animation_reference',self.normal_animation_reference),
                                     ('animation_reference',self.skill_animation_reference)):
                    if widget.currentData() is not None:
                        scenario.setdefault('timing',{})[field]=widget.currentData()
            result = calculate_damage(scenario)
            apply_relic_history_notice(scenario,result)
            if self.target_buff_test.isChecked():
                result['estimate']['notes'].insert(0,'当前启用个人强化测试；测试选项不代表从本局画面读取到的强化，也不写入记忆。')
            self.damage_result = {'scenario':scenario,'result':result}
            if hasattr(self,'offline_tools'):self.offline_tools.set_scenario(scenario)
            if hasattr(self,'paired_calibration'):self.paired_calibration.set_scenario(scenario)
            if hasattr(self,'attack_state_sequence'):self.attack_state_sequence.set_context(scenario)
            if hasattr(self,'timing_calibration'):self.timing_calibration.set_scenario(scenario)
            if hasattr(self,'bounded_calibration'):self.bounded_calibration.set_scenario(scenario)
            if hasattr(self,'calibration_experiment'):self.calibration_experiment.set_scenario(scenario)
            if hasattr(self,'recipient_native_ratio'):self.recipient_native_ratio.set_context(scenario)
            if hasattr(self,'relic_order_precision'):self.relic_order_precision.set_context(scenario)
            self.charge_timeline_button.setEnabled(op=='mechanist' and scenario['skill']==3)
            self.shield_timeline_button.setEnabled(op=='mechanist' and scenario['skill']==2)
            from .healing_budget import healing_sources
            self.healing_budget_button.setEnabled(bool(healing_sources(result)))
            self.skill_upgrade_button.setEnabled(True)
            self.enemy_comparison_button.setEnabled(True)
            self.scenario_library_button.setEnabled(True)
            from .damage_budget import damage_sources
            self.damage_budget_button.setEnabled(bool(damage_sources(result)))
            self.render_damage()
        except Exception as error:
            self.damage_result=None
            self.show_damage_text(str(error))
