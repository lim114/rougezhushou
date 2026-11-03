from pathlib import Path
import shutil,json,hashlib,datetime
base=Path(__file__).parent; root=Path('/workspace/rougezhushou')
draft=base/'draft060'
if not draft.exists():shutil.copytree(base/'baseline',draft,ignore=shutil.ignore_patterns('__pycache__'))
p=draft/'rouge/operator_engine.py'; data=(base/'baseline/rouge/operator_engine.py').read_bytes().decode(); assert '\r\n' in data
text=data.replace('\r\n','\n')
text=text.replace('        self.initial_bonus=0;self.sp_extra=0\n','        self.initial_bonus=0;self.sp_extra=0\n        self.shu_periodic_sp_reference=None\n',1)
old="                self.sp_extra+=self.talent('天有四时','sp')/self.talent('天有四时','interval',4)"
new="""                if self.talent('天有四时','sp')>0:
                    # A discrete talent interval is not a natural SP rate.
                    # The original selector does not establish its first pulse,
                    # owner clock, reset or credit during skill lockout.
                    self.shu_periodic_sp_reference={
                        'interval_seconds_parameter':self.talent('天有四时','interval'),
                        'sp_per_pulse_parameter':self.talent('天有四时','sp'),
                        'attack_bonus_parameter':self.talent('天有四时','atk'),
                        'first_tick_seconds':None,'actual_tick_times_seconds':None,
                        'clock_origin':None,'reset_rule':None,'blocked_credit_rule':None,
                        'native_attachment_verified':False,'clock_verified':False,
                        'events_scheduled':False,
                        'source_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
                        'source_selector':'character_table.char_2025_shu.talents[1].candidates[0]'}"""
assert text.count(old)==1;text=text.replace(old,new)
old="        cycle=duration+recharge if not nonrepeat and duration is not None and recharge is not None else None"
new="""        if self.shu_periodic_sp_reference is not None:
            self.shu_periodic_sp_reference['independent_sp_clock_reference']={
                'initial_seconds':first,'recharge_seconds':recharge,
                'excludes_four_sui_periodic_credit':True}
            first=0.0 if initial>=sp['sp_cost'] else None
            recharge=None
        cycle=duration+recharge if not nonrepeat and duration is not None and recharge is not None else None"""
assert text.count(old)==1;text=text.replace(old,new)
old="        return result\n\n\ndef calculate_extended"
new="""        if self.shu_periodic_sp_reference is not None:
            result['shu_periodic_sp_reference']=self.shu_periodic_sp_reference
            result['timing']['phase_clock_unbound']=True
            result['timing']['resource_and_damage_shared_clock']=False
            result['complete']=result['estimate']['complete']=False
            result['scope']=result['estimate']['scenario_scope']=(
                '所选技能阶段与观察窗口沿用明确情景；四岁周期技力首跳与阻回归属未核验，完整资源回转未知。')
            result['estimate']['notes'].append(
                '四岁条件下保留攻击力加成与4秒获得1点技力原参数；周期首跳、计时起点、重置和阻回期间归属未核验，'
                '不折算成自然回复速度，不用其它来源的充能算例证明完整初动、结束后充能或周期。')
        return result



def calculate_extended"""
assert text.count(old)==1;text=text.replace(old,new)
p.write_bytes(text.replace('\n','\r\n').encode())
p=draft/'rouge/reporting.py';text=(base/'baseline/rouge/reporting.py').read_text()
needle="    received=[r for r in result.get('relic_resolution',{}).get('rules',[]) if r['kind'] in ('received_sp','event_sp') and not r.get('token_only')]"
new="""    shu_sp=result.get('shu_periodic_sp_reference')
    if shu_sp:
        sections.append(section('shu_periodic_sp','天有四时 · 周期技力待核验',[
            metric('interval','周期间隔原参数',shu_sp['interval_seconds_parameter'],'秒'),
            metric('sp','单次周期技力原参数',shu_sp['sp_per_pulse_parameter'],'技力'),
            metric('natural_rate','已计自然技力回复速度',skill['sp_recovery_per_second'],'技力/秒'),
            metric('first_tick','实际周期首跳',shu_sp['first_tick_seconds'],'秒')],
            ['四岁编队条件由当前情景声明；原天赋培养门槛和攻击力加成保持。',
             '4秒获得1点技力是周期原参数，不能当作每秒自然回复+0.25。',
             '周期首跳、计时起点、重置和阻回期间归属尚未核验；未排周期事件，完整初动、充能与回转保持未知。',
             '初始技力已足够时保留0秒就绪；敌方供靶或空观察窗口不取消这一独立友方技力来源。']))
    received=[r for r in result.get('relic_resolution',{}).get('rules',[]) if r['kind'] in ('received_sp','event_sp') and not r.get('token_only')]"""
assert text.count(needle)==1;text=text.replace(needle,new)
text=text.replace("'初动/回转已按模拟帧处理；额外阻回与结束硬直使用明确提供的时序情景。',*reference_notes", "('技能相对窗口保留帧参考；独立技力算例不包含四岁周期来源，完整初动、结束后充能与回转未知。' if shu_sp else '初动/回转已按模拟帧处理；额外阻回与结束硬直使用明确提供的时序情景。'),*reference_notes",1)
p.write_text(text)
(base/'draft-receipt060.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_baseline':'4c5fdc528da191693b325c2569749e5264ed0a15','baseline_engine_equals_current_root56':hashlib.sha256((base/'baseline/rouge/operator_engine.py').read_bytes()).hexdigest()==hashlib.sha256((root/'rouge/operator_engine.py').read_bytes()).hexdigest(),'changed_files':{str(p.relative_to(draft)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':len(p.read_bytes())} for p in [draft/'rouge/operator_engine.py',draft/'rouge/reporting.py']}},ensure_ascii=False,indent=2)+'\n')
print('external draft060 created')
