import copy,json,unittest
from pathlib import Path
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.haruka_target_static_reference import FLAG,MODULE,OP,qualification,rule

def scenario(**extra):
    return {'operator':OP,'skill':2,'skill_rank':7,'elite':2,'level':60,'module_id':MODULE,
            'module_level':1,'base_attack':1000,'healing_targets':3,'window_seconds':10,FLAG:True,**extra}
def body(r):return next(c for c in r['components'] if c['name']=='护佑者普通治疗')

class HarukaTargetStaticReferenceTests(unittest.TestCase):
    def test_default_off_preserves_two_known_and_unplaced_third(self):
        for mode in ('frames','continuous'):
            r=calculate_damage(scenario(**{FLAG:False,'timing_mode':mode}))
            self.assertNotIn(FLAG,r)
            self.assertEqual(r['haruka_healing_reference']['modeled_target_limit_reference'],2)
            self.assertTrue(any(c['name']=='护佑者额外目标治疗（组合待核验）' for c in r['components']))
            self.assertGreater(r['known_healing_subtotals']['window_healing'],0)
            self.assertFalse(r['haruka_healing_reference']['native_composition_verified'])

    def test_three_stages_ten_ranks_all_skill_selectors_use_bound_sources(self):
        for stage in (1,2,3):
            for skill in (1,2,3):
                for rank in range(1,11):
                    s=scenario(skill=skill,skill_rank=rank,module_level=stage)
                    r=calculate_damage(s);ref=r[FLAG];limit=2+int(skill==2 and rank>=7)
                    self.assertEqual(ref['selector_limit_reference'],limit)
                    self.assertEqual(ref['modeled_potential_recipients'],limit)
                    self.assertEqual(ref['selector_key'],'max_target_heal_add' if skill==2 else 'max_target_heal')
                    self.assertEqual(r['haruka_healing_reference']['legacy_modeled_target_limit_reference'],2)
                    self.assertEqual(ref['qualification']['native_skill_index'],skill-1)
                    self.assertTrue(ref['native_static_binding_verified']);self.assertTrue(ref['native_static_composition_verified'])
                    self.assertFalse(ref['runtime_binding_verified']);self.assertFalse(ref['current_hotfix_equivalence_verified'])
                    self.assertFalse(r['haruka_healing_reference']['native_attachment_verified'])
                    self.assertFalse(any('组合待核验' in c['name'] for c in r['components']))

    def test_s2_third_is_one_body_budget_not_old_extra_source(self):
        for mode in ('frames','continuous'):
            one=calculate_damage(scenario(healing_targets=1,timing_mode=mode))
            three=calculate_damage(scenario(timing_mode=mode));ref=three[FLAG]
            self.assertEqual(body(three)['hits'],body(one)['hits']*3)
            self.assertEqual(body(three)['total'],body(one)['total']*3)
            self.assertEqual(ref['packets'][0]['modeled_body_attempt_count'],body(one)['hits'])
            self.assertEqual(ref['conditional_window_body_healing_reference'],body(three)['total'])
            self.assertEqual(ref['packets'][1]['conditional_window_subtotal'],ref['packets'][0]['conditional_window_subtotal']*2)
            self.assertIsNone(ref['packets'][1]['actual_adjacent_enemy_coverage'])

    def test_declarations_clamp_to_source_cap_without_inventing_friend_events(self):
        for skill,rank,cap in ((1,7,2),(2,6,2),(2,7,3),(3,10,2)):
            for count in (0,1,2,3,100):
                r=calculate_damage(scenario(skill=skill,skill_rank=rank,healing_targets=count))
                self.assertEqual(r[FLAG]['modeled_potential_recipients'],min(cap,count))
                self.assertEqual(r[FLAG]['declared_potential_recipients'],count)
                self.assertIsNone(r[FLAG]['actual_target_count'])
            one=calculate_damage(scenario(skill=skill,skill_rank=rank,healing_targets=1))
            maximum=calculate_damage(scenario(skill=skill,skill_rank=rank,healing_targets=100))
            self.assertEqual(body(maximum)['total'],body(one)['total']*cap)

    def test_static_selection_does_not_promote_actual_totals_or_clock(self):
        for skill in (1,2,3):
            r=calculate_damage(scenario(skill=skill));ref=r[FLAG]
            for k in ('actual_target_limit','actual_target_count','actual_acquisition_times_seconds',
                      'actual_full_cast_healing','actual_window_healing','actual_cycle_healing'):
                self.assertIsNone(ref[k])
            for k in ('total_healing','phase_healing','window_healing','window_hps','cycle_healing','cycle_hps'):
                self.assertIsNone(r['estimate']['skill'][k])
            self.assertIsNone(r['total_healing']);self.assertIsNone(body(r)['actual_total'])
            self.assertIn('preview',body(r)['timing_reference'])
            self.assertFalse(r['complete']);self.assertFalse(r['estimate']['complete'])
            if skill==2:self.assertIsNone(r['total_damage'])

    def test_zero_preview_scopes_and_no_enemy_keep_friend_budget_independent(self):
        for extra in ({'healing_targets':0},{'window_seconds':0},
                      {'timing':{'interrupt_windows':[[0,60]]}}):
            r=calculate_damage(scenario(**extra))
            self.assertEqual(r[FLAG]['conditional_window_body_healing_reference'],0)
            self.assertIsNone(r[FLAG]['actual_window_healing'])
        r=calculate_damage(scenario(timing={'target_disappears_seconds':0}))
        self.assertGreater(r[FLAG]['packets'][0]['conditional_window_subtotal'],0)
        self.assertEqual(r[FLAG]['packets'][1]['conditional_window_subtotal'],0)
        r=calculate_damage(scenario(timing={'target_windows':[]}))
        self.assertGreater(r[FLAG]['packets'][0]['conditional_window_subtotal'],0)
        self.assertIsNone(r[FLAG]['actual_target_count'])

    def test_healing_and_resistance_multipliers_apply_once_after_count(self):
        base=calculate_damage(scenario());scaled=calculate_damage(scenario(relic_ids=['rogue_6_relic_legacy_81']))
        self.assertEqual(scaled[FLAG]['packets'][0]['per_recipient_heal_reference'],900)
        self.assertEqual(scaled[FLAG]['conditional_window_body_healing_reference'],16200)
        self.assertEqual(scaled[FLAG]['conditional_window_body_healing_reference'],base[FLAG]['conditional_window_body_healing_reference']*1.2)
        self.assertEqual(scaled[FLAG]['packets'][0]['before_covered_healing_factors']['total'],13500)
        self.assertEqual(scaled[FLAG]['packets'][1]['conditional_window_subtotal'],base[FLAG]['packets'][1]['conditional_window_subtotal'])
        resist=calculate_damage(scenario(enemy_resistance=50))
        self.assertEqual(resist[FLAG]['packets'][0],base[FLAG]['packets'][0])
        self.assertEqual(resist[FLAG]['packets'][1]['conditional_window_subtotal'],base[FLAG]['packets'][1]['conditional_window_subtotal']/2)

    def test_first_and_repeat_attack_references_remain_separate(self):
        first=calculate_damage(scenario());repeat=calculate_damage(scenario(haruka_repeat=True))
        self.assertGreater(repeat[FLAG]['packets'][0]['per_recipient_heal_reference'],first[FLAG]['packets'][0]['per_recipient_heal_reference'])
        self.assertIsNone(repeat[FLAG]['actual_full_cast_healing'])
        self.assertIsNone(repeat['estimate']['skill']['cycle_healing'])

    def test_bubbles_and_levitate_are_not_multiplied_by_body_recipient_count(self):
        for skill in (1,2,3):
            one=calculate_damage(scenario(skill=skill,healing_targets=1,bubble_bursts=2,levitate_triggers=1))
            many=calculate_damage(scenario(skill=skill,healing_targets=3,bubble_bursts=2,levitate_triggers=1))
            self.assertEqual(one['external_event_reference']['conditional_components'],many['external_event_reference']['conditional_components'])
            self.assertEqual(one['external_event_reference']['window_reference']['conditional_components'],many['external_event_reference']['window_reference']['conditional_components'])

    def test_gates_and_strict_flag_do_not_enable_other_modules_or_cultivation(self):
        for extra in ({'level':59},{'elite':1,'level':80},{'module_id':None}):
            s=scenario(**extra)
            self.assertFalse(qualification(s)['qualified'])
            self.assertNotIn(FLAG,calculate_damage(s))
        for extra in ({'module_level':0},{'module_level':4},{'module_id':'original'},{'module_level':True}):
            self.assertFalse(qualification(scenario(**extra))['qualified'])
            with self.assertRaises(ValueError):calculate_damage(scenario(**extra))
        for value in (1,0,'true','false',None,[],{}):
            with self.assertRaises(ValueError):calculate_damage(scenario(**{FLAG:value}))
        self.assertNotIn(FLAG,calculate_damage({'operator':'silverash','skill':1,FLAG:True}))

    def test_report_connects_final_budget_and_source_to_actual_unknowns(self):
        r=calculate_damage(scenario(relic_ids=['rogue_6_relic_legacy_81']))
        text=format_estimate(r)
        for word in ('明确选择的静态治疗人数上限：3 名','单名受疗治疗条件参考：900',
                     '观察窗口普通治疗条件小计：16,200','实际同时受疗人数：未知','观察窗口治疗：未知','TRAIT_DATA_ONLY'):
            self.assertIn(word,text)
        self.assertIn('research/p2-haruka-targets-current/receipt.json',r[FLAG]['source']['receipt'])
        self.assertIn('/haruka_module_target_static_reference',r['report']['selected_module_source_reference']['existing_coverage']['native_paths'])

    def test_native_receipt_and_current_prefab_paths_cover_source_composition(self):
        folder=Path(__file__).resolve().parents[1]/'research/p2-haruka-targets-current'
        receipt=json.loads((folder/'receipt.json').read_text(encoding='utf-8'))
        self.assertTrue(receipt['physical_validation']['all_instruction_bytes_match'])
        self.assertEqual(receipt['physical_validation']['limits'],[])
        self.assertEqual(len(receipt['asset_validation']),3)
        self.assertIn('mainSkillIndex1',receipt['data_flow_binding'])
        self.assertIn('No additional previous target',receipt['data_flow_binding'])
        generic=json.loads((folder/'targeted-generic-methods.json').read_text(encoding='utf-8'))
        self.assertEqual([(x['method'],x['class_args'],x['method_args']) for x in generic['rows']],
                         [('TryGetValue',['System.String','Torappu.TalentData'],[]),
                          ('set_Item',['System.String','Torappu.TalentData'],[]),
                          ('ContainsItem',[],['System.Int32'])])
        binding=json.loads((folder/'catalog-binding.json').read_text(encoding='utf-8'))
        for stage in binding['module']['levels']:
            part=next(p for p in stage['parts'] if p['target']=='TRAIT_DATA_ONLY')
            self.assertIsNone(part['resKey']);self.assertEqual(part['overrideTraitDataBundle']['candidates'][0]['prefabKey'],'-1')
        self.assertTrue((folder/'first-generic-method-spec-check.json').exists())

    def test_repeated_calculation_does_not_mutate_catalog_scenario_or_rule(self):
        s=scenario();s0=copy.deepcopy(s);c0=copy.deepcopy(catalog()['operators'][OP]);rules=copy.deepcopy(rule())
        first=calculate_damage(s);second=calculate_damage(s)
        self.assertEqual(first[FLAG],second[FLAG]);self.assertEqual(s,s0)
        self.assertEqual(catalog()['operators'][OP],c0);self.assertEqual(rule(),rules)
        first[FLAG]['source']['catalog_commit']='modified'
        self.assertEqual(calculate_damage(s)[FLAG]['source'],second[FLAG]['source'])

if __name__=='__main__':unittest.main()
