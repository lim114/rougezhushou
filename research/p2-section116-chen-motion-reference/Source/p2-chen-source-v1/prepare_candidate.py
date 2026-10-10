"""Source-only preparation; never imports/runs project or edits tracked files."""
from pathlib import Path
import ast, hashlib, json
ROOT=Path('/workspace/rougezhushou')
OUT=Path('/workspace/.continuation/p2-chen-source-v1')
CAND=OUT/'candidate'
blocks=[]

def edit(path,before,after):
    p=ROOT/path
    original=p.read_bytes()
    nl='\r\n' if b'\r\n' in original else '\n'
    a=before.replace('\n',nl).encode();b=after.replace('\n',nl).encode()
    destination=CAND/path
    old=destination.read_bytes() if destination.exists() else original
    if old.count(a)!=1:raise ValueError('Source anchor not unique: '+path)
    composed=old.replace(a,b)
    compile(composed,str(destination),'exec')
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(composed)
    blocks.append({'path':path,'baseline_sha256':hashlib.sha256(original).hexdigest(),
                   'before':before,'after':after,'newline':repr(nl),
                   'before_sha256':hashlib.sha256(a).hexdigest(),'after_sha256':hashlib.sha256(b).hexdigest()})

def add(path,source):
    if (ROOT/path).exists():raise ValueError('new path exists')
    raw=source.encode();compile(raw,str(CAND/path),'exec')
    p=CAND/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)

add('rouge/chen_motion_reference.py', '''"""Inspect Chen's pinned original motions without placing combat events.

Names, lengths and animation events are resource facts. They do not establish
which action runs, how often it loops, damage/collision timing or skill end.
The opt-in orientation only changes presentation; numeric selectors stay closed.
"""
from copy import deepcopy

from .animation_reference import references

OPERATOR = 'char_1050_chen3'
ACTIONS = {
    1: (('Skill_1_Begin', '开启动作条目'),
        ('Skill_1_Loop', '循环动作条目'), ('Skill_1_End', '结束动作条目')),
    2: (('Skill_2_Begin', '开启动作条目'),
        ('Skill_2_Disappear', '消失动作条目'), ('Attack', '普攻动作条目')),
    3: (('Skill_3_Begin', '开启动作条目'),
        ('Skill_3_Loop', '循环动作条目'), ('Skill_3_End', '结束动作条目')),
}


def chen_motion_reference(scenario):
    """Return a detached resource reference for an explicit Front/Back choice."""
    if scenario.get('operator') != OPERATOR:
        return None
    orientation = scenario.get('chen_motion_orientation')
    if orientation is None:
        return None
    if type(orientation) is not str or orientation not in ('Front', 'Back', 'both'):
        raise ValueError('陈原版阶段资料面向需要为Front、Back或both；留空不显示。')
    skill = scenario.get('skill')
    if type(skill) is not int or skill not in ACTIONS:
        raise ValueError('陈原版阶段资料仅适用于一、二、三技能。')
    catalog = references()
    source = catalog['operators'][OPERATOR]['records']
    faces = ('Front', 'Back') if orientation == 'both' else (orientation,)
    motions = []
    for face in faces:
        for name, label in ACTIONS[skill]:
            record = next(r for r in source
                          if r['orientation'] == face and r['animation'] == name)
            # Preserve every original representation and event in source order.
            motions.append({'label': label, **deepcopy(record)})
    return {
        'operator': OPERATOR, 'skill': skill, 'orientation': orientation,
        'source_commit': catalog['source_commit'], 'fps': catalog['fps'],
        'frame_normalization_tolerance': catalog['frame_normalization_tolerance'],
        'motions': motions, 'numeric_schedule_changed': False,
        'runtime_motion_selection_verified': False,
        'damage_event_binding_verified': False,
        'actual_damage_times_seconds': None, 'actual_skill_end_seconds': None,
        'actual_slash_end_seconds': None, 'actual_wave_collision_seconds': None,
        'phase_duration_sum_permitted': False,
    }
''')

helper='''def chen_motion_reference_sections(scenario):
    """Expose original motion facts, keeping them outside numeric scheduling."""
    from .chen_motion_reference import chen_motion_reference
    reference=chen_motion_reference(scenario)
    if reference is None:return []
    blocks=[]
    for face in ('Front','Back'):
        motions=[r for r in reference['motions'] if r['orientation']==face]
        if not motions:continue
        rows=[];notes=[
            '这些是原版资源中的独立动作条目；排列便于查看，不代表实际执行顺序、循环次数或当前皮肤动作选择。',
            '每个事件的偏移以该动作资源自身起点为0；不是技能开启后的实际命中或碰撞时刻。',
            '原始秒数和浮点帧保留原值；30帧/秒归一化仅处理资源表示误差，不证明游戏帧取整或客户端相位。',
            '参考只改变资料展示，不排程多事件伤害，不替换攻击模板，也不将动作长度相加作为技能持续时间。']
        for index,motion in enumerate(motions):
            prefix='motion_'+str(index);duration=motion['duration'];label=motion['label']
            rows.extend([
                metric(prefix+'_duration',label+' · 资源时长',repr(duration['seconds']),'秒（原值）'),
                metric(prefix+'_raw_frames',label+' · 原始浮点帧',repr(duration['raw_frames_30hz']),'帧'),
                metric(prefix+'_strict_ceil',label+' · 严格向上取整帧',duration['strict_ceil_frames_30hz'],'帧'),
                metric(prefix+'_normalized',label+' · 归一化参考帧',duration['ceil_frames_30hz'],'帧'),
                metric(prefix+'_events',label+' · 命名事件数量',len(motion['events']),'个')])
            for event_index,event in enumerate(motion['events']):
                event_prefix=prefix+'_event_'+str(event_index)
                event_label=label+' · 第'+str(event_index+1)+'个命名事件'
                rows.extend([
                    metric(event_prefix+'_seconds',event_label+' · 原始偏移',repr(event['seconds']),'秒（动作内）'),
                    metric(event_prefix+'_raw_frames',event_label+' · 原始浮点帧',repr(event['raw_frames_30hz']),'帧'),
                    metric(event_prefix+'_strict_ceil',event_label+' · 严格向上取整帧',event['strict_ceil_frames_30hz'],'帧'),
                    metric(event_prefix+'_normalized',event_label+' · 归一化参考偏移',event['ceil_frames_30hz'],'帧')])
                notes.append(event_label+'名称：'+event['name']+'；原名不等于已核验的实际伤害绑定。')
            notes.append(label+'资源动作原名：'+motion['animation']+'；来源：'+motion['source']['url']+
                         '；资源SHA-256：'+motion['source']['sha256'])
        rows.extend([metric('actual_damage','实际命中时刻',None,'秒'),
                     metric('actual_end','实际技能结束时刻',None,'秒')])
        if reference['skill']==2:
            rows.extend([metric('slash_end','实际斩击结束时刻',None,'秒'),
                         metric('strengthening_start','实际强化起点',None,'秒')])
            notes.append('普攻动作仅列资源参照，未证明它用于斩击后强化；消失动作长度不等于斩击持续时间。')
        elif reference['skill']==3:
            rows.append(metric('wave_collision','实际剑气碰撞时刻',None,'秒'))
            notes.append('循环动作的三个命名事件不补齐剑气碰撞、开启交接、实际循环次数或结束时刻。')
        else:
            notes.append('循环动作的两个命名事件仅列原始偏移，未绑定实际两段伤害或开启、结束交接。')
        blocks.append(section('chen_motion_'+face.lower(),'陈 · 原版阶段资料 · '+
                              {'Front':'正面','Back':'背面'}[face],rows,notes))
    return blocks


'''
edit('rouge/reporting.py','def build_report(scenario,result):\n',helper+'def build_report(scenario,result):\n')
edit('rouge/reporting.py','    chen_phase=result.get(\'chen_phase_reference\')\n',
     '    sections.extend(chen_motion_reference_sections(scenario))\n    chen_phase=result.get(\'chen_phase_reference\')\n')
edit('rouge/app.py',
'''        self.timing_scenario=QPlainTextEdit()
''',
'''        self.chen_motion_orientation=QComboBox()
        self.chen_motion_orientation.addItem('不显示原版阶段资料',None)
        self.chen_motion_orientation.addItem('正面原版动作资料','Front')
        self.chen_motion_orientation.addItem('背面原版动作资料','Back')
        self.chen_motion_orientation.addItem('正背面原版动作对照','both')
        self.chen_motion_preview_key=None;self.chen_motion_previews={}
        form.addRow('陈原版阶段资料',self.chen_motion_orientation)
        form.setRowVisible(self.chen_motion_orientation,False)
        self.chen_motion_orientation.setToolTip('仅显示当前技能的原版动作资源长度与全部命名事件；不排程多段伤害，不补齐斩击结束、剑气碰撞或技能结束。连续与逐帧模式均可查看，不写入培养或本局记忆。')
        self.chen_motion_orientation.currentIndexChanged.connect(lambda:self.calculate())
        self.timing_scenario=QPlainTextEdit()
''')
edit('rouge/app.py',
'''            if self.frame_timing.isChecked():
                for field,widget in (('normal_animation_reference',self.normal_animation_reference),
''',
'''            if op=='char_1050_chen3' and self.chen_motion_orientation.currentData() is not None:
                scenario['chen_motion_orientation']=self.chen_motion_orientation.currentData()
            if self.frame_timing.isChecked():
                for field,widget in (('normal_animation_reference',self.normal_animation_reference),
''')
edit('rouge/app.py',
'''        for widget in widgets:
            self.damage_form.setRowVisible(widget,self.frame_timing.isChecked() and widget.count()>1)

    def sync_target_buffs(self,op):
''',
'''        for widget in widgets:
            self.damage_form.setRowVisible(widget,self.frame_timing.isChecked() and widget.count()>1)
        if key!=self.chen_motion_preview_key:
            if self.chen_motion_preview_key is not None:
                self.chen_motion_previews[self.chen_motion_preview_key]=self.chen_motion_orientation.currentData()
            self.chen_motion_orientation.blockSignals(True)
            found=self.chen_motion_orientation.findData(self.chen_motion_previews.get(key))
            self.chen_motion_orientation.setCurrentIndex(max(0,found))
            self.chen_motion_orientation.blockSignals(False)
            self.chen_motion_preview_key=key
        self.damage_form.setRowVisible(self.chen_motion_orientation,op=='char_1050_chen3' and skill in (1,2,3))

    def sync_target_buffs(self,op):
''')
edit('scripts/verify_cloud.py','MODULES = (\n','MODULES = (\n    "tests.test_chen_motion_reference",\n')
(OUT/'transport.json').write_text(json.dumps({'kind':'SOURCE_ONLY_LOCAL_ANCHOR_TRANSPORT_NOT_APPLIED','blocks':blocks,'new_files':['rouge/chen_motion_reference.py','tests/test_chen_motion_reference.py']},ensure_ascii=False,indent=2)+'\n')
print('Source-only local blocks',len(blocks),'compile-noexec done')
