import hashlib,json,unittest
from pathlib import Path
from rouge.animation_reference import choices,descriptor,label,references
from rouge.damage import calculate_damage
from rouge.timing import AttackTimeline
from scripts.build_original_animation_048 import frames

ROOT=Path(__file__).resolve().parents[1]


class OriginalAnimation048Tests(unittest.TestCase):
    def test_all_sources_match_pinned_skeleton_bytes_and_git_blob(self):
        data=references();self.assertEqual(data['counts']['source_skeletons'],64)
        sources={r['source']['url']:r['source'] for p in data['operators'].values() for r in p['records']}
        downloads=json.loads((ROOT/'.cache/research/timing-048/skeleton-downloads.json').read_text(encoding='utf-8'))
        self.assertEqual(len(sources),64)
        for item in downloads:
            raw=(ROOT/'.cache/research/timing-048'/item['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),item['sha256'])
            self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),item['git_blob'])
            self.assertEqual(len(raw),item['bytes'])
            if item['url'] in sources:self.assertEqual(sources[item['url']]['sha256'],item['sha256'])

    def test_zero_events_loops_and_transitions_never_become_conventional_choices(self):
        data=references();self.assertEqual(len(data['operators']),32)
        for p in data['operators'].values():
            for r in p['records']:
                if not r['selectable_as_conventional_reference']:continue
                self.assertEqual(len(r['events']),1);self.assertEqual(r['events'][0]['name'],'OnAttack')
                self.assertGreater(r['events'][0]['seconds'],0)
                self.assertLess(r['events'][0]['seconds'],r['duration']['seconds'])
                self.assertNotIn('Loop',r['animation']);self.assertFalse(r['runtime_binding_verified'])
                self.assertNotIn('Deploy',r['animation'])
        zero=next(r for r in data['operators']['char_1042_phatm2']['records'] if r['animation']=='Skill_3_Loop')
        self.assertFalse(zero['selectable_as_conventional_reference'])
        self.assertEqual(zero['events'][0]['ceil_frames_30hz'],0)

    def test_orientation_difference_is_preserved(self):
        selected=[r for r in choices('kaltsit',3) if r['animation']=='Skill_3_Attack']
        self.assertEqual({r['orientation']:r['preview']['windup_frames'] for r in selected},{'Front':12,'Back':13})

    def test_recovered_back_sources_are_not_filled_from_the_other_side(self):
        p=references()['operators']['char_196_sunbr']
        self.assertEqual(p['missing_sources'],[])
        back=[r for r in p['records'] if r['orientation']=='Back']
        self.assertEqual([r['animation'] for r in back],['Attack','Default','Idle','Skill','Start'])
        self.assertEqual(len([r for r in p['records'] if r['orientation']=='Front']),9)
        self.assertTrue(all(r['source']['sha256']=='09526db9b53f6fa54ac51219ce31e6cd3903e618d9a47781f230bf68de3edfb2'
                            for r in back))

    def test_representation_error_is_disclosed_without_hiding_real_fractional_frames(self):
        f=frames(.4+1e-8)
        self.assertEqual(f['strict_ceil_frames_30hz'],13);self.assertEqual(f['ceil_frames_30hz'],12)
        self.assertEqual(frames(.4001)['ceil_frames_30hz'],13)

    def test_reference_cannot_leak_to_another_operator_or_skill(self):
        ref=next(r for r in choices('kaltsit',3) if r['animation']=='Skill_3_Attack')['id']
        for op,skill in (('mechanist',3),('kaltsit',2)):
            with self.assertRaises(ValueError):AttackTimeline({'operator':op,'skill':skill,'timing':{'animation_reference':ref}})

    def test_explicit_reference_drives_first_release_and_both_faces_remain_optional(self):
        for face,expected in (('Front',12),('Back',13)):
            ref=next(r for r in choices('kaltsit',3) if r['animation']=='Skill_3_Attack' and r['orientation']==face)
            r=calculate_damage({'operator':'kaltsit','skill':3,'timing':{'animation_reference':ref['id']}})
            stream=r['timing']['streams'][0]
            self.assertEqual(stream['release_frames'][0],expected)
            self.assertFalse(stream['exact_binding'])
            self.assertEqual(stream['original_animation_reference']['original_orientation'],face)
            self.assertFalse(stream['original_animation_reference']['overridden_by_preview'])

    def test_no_reference_preserves_unknown_default_and_overrides_remain_explicit(self):
        r=calculate_damage({'operator':'kaltsit','skill':3})
        self.assertFalse(r['timing']['streams'][0]['known_animation'])
        self.assertNotIn('original_animation_reference',r['timing']['streams'][0])
        ref=choices('kaltsit',3)[0]['id']
        stream=calculate_damage({'operator':'kaltsit','skill':3,
            'timing':{'animation_reference':ref,'windup_frames':6,'recovery_frames':9}})['timing']['streams'][0]
        self.assertEqual(stream['release_frames'][0],6)
        self.assertTrue(stream['original_animation_reference']['overridden_by_preview'])

    def test_normal_reference_applies_to_attack_sp_initial_charge(self):
        ref=choices('mechanist',1,normal=True)[0]['id']
        r=calculate_damage({'operator':'mechanist','skill':1,'timing':{'normal_animation_reference':ref}})
        self.assertEqual(r['estimate']['skill']['initial_seconds'],(13+6*36+1)/30)
        self.assertNotIn('original_animation_reference',r['timing']['streams'][0])

    def test_reference_uses_existing_movement_and_half_open_window_clock(self):
        ref=choices('mechanist',1,normal=True)[0]['id']
        timeline=AttackTimeline({'operator':'mechanist','skill':2,'timing':{
            'animation_reference':ref,'movement_windows':[[.2,.5]]}})
        stream=timeline.attacks(1,1.2)
        self.assertEqual(stream['release_frames'],[28]);self.assertEqual(stream['impact_frames'],[28])
        self.assertEqual(timeline.attacks(28/30,1.2)['release_frames'],[])


if __name__=='__main__':unittest.main()
