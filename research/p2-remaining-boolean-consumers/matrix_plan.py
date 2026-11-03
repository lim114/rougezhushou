"""Unique, bounded scenarios; never regenerates the old 36 source probes."""
import math

ACTIVE=(
 ('char_4228_closur',2,'reinforcement_blocks_target'),('char_437_mizuki',2,'enemy_below_half'),
 ('char_206_gnosis',3,'frozen_at_skill_end'),('char_4087_ines',3,'ines_first_deployment'),
 ('char_4182_oblvns',2,'ranged_attack'),('char_4182_oblvns',2,'organ_mode'),('char_4182_oblvns',2,'fever'),
 ('char_1048_orchd2',1,'power_coating'),('char_1048_orchd2',1,'double_charge'),
 ('char_1041_angel2',2,'steal_success'),('char_1041_angel2',3,'delivery_coordinate'),('char_1035_wisdel',2,'overload'))


def typed(v):
 if isinstance(v,dict):return {'type':'dict','items':[[typed(k),typed(x)] for k,x in v.items()]}
 if isinstance(v,(list,tuple)):return {'type':type(v).__name__,'items':[typed(x) for x in v]}
 if isinstance(v,float):return {'type':'float','hex':v.hex()}
 return {'type':type(v).__name__,'value':v}


def json_value(v):
 if isinstance(v,dict):return {k:json_value(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [json_value(x) for x in v]
 if isinstance(v,float) and not math.isfinite(v):return {'saved_nonfinite_float':v.hex()}
 return v


def make_plan():
 rows=[]
 def add(label,expect,op,n,field=None,value=None,**extra):
  s={'operator':op,'skill':n,'base_attack':987,'potential':5,'window_seconds':11,
     'timing_mode':'frames',**extra}
  if field is not None:s[field]=value
  rows.append({'label':label,'expect':expect,'field':field,'input':s})
 for j,(op,n,f) in enumerate(ACTIVE):
  for text in ('false','','0','False'):add(f+'-text-'+repr(text),'changed',op,n,f,text,timing_mode='continuous' if j%2 else 'frames')
  for k,v in enumerate((False,True,0,1,None,[],[0],{}, {'x':False},float('nan'),float('inf'))):
   add(f+'-nonstr-'+str(k),'same',op,n,f,v,timing_mode='continuous' if k%2 else 'frames')
  for op2,n2 in (('mechanist',1),('silverash',3)):add(f+'-other-'+op2,'same',op2,n2,f,'false')
 inactive=[('char_206_gnosis',1,'frozen_at_skill_end',{}),('char_4087_ines',2,'ines_first_deployment',{}),
  ('char_4182_oblvns',1,'organ_mode',{}),('char_4182_oblvns',3,'fever',{}),
  ('char_1048_orchd2',2,'double_charge',{}),('char_1041_angel2',1,'steal_success',{}),
  ('char_1041_angel2',2,'delivery_coordinate',{}),('char_1035_wisdel',1,'overload',{}),
  ('char_437_mizuki',1,'enemy_below_half',{'elite':0,'skill_rank':7}),
  ('char_437_mizuki',2,'enemy_below_half',{'elite':1,'skill_rank':7})]
 for op,n,f,extra in inactive:add(f+'-inactive-'+str(n)+str(extra),'same',op,n,f,'false',**extra)
 for level,modlevel,n,continuous,mode in ((59,2,2,False,'frames'),(60,1,2,False,'frames'),
   (60,2,1,False,'frames'),(60,2,1,True,'frames'),(60,2,2,False,'frames'),(60,2,2,True,'frames'),
   (60,2,3,False,'frames'),(60,2,3,True,'frames'),(60,3,1,True,'frames'),(60,3,2,True,'frames'),
   (60,3,3,False,'frames'),(60,3,3,True,'frames'),(60,2,3,False,'continuous'),(60,2,3,True,'continuous')):
  active=level<60 or modlevel==1 or n==3 and continuous
  add('ranged-module-'+str((level,modlevel,n,continuous,mode)), 'changed' if active else 'same',
      'char_4182_oblvns',n,'ranged_attack','false',elite=2,level=level,module_id='uniequip_002_oblvns',
      module_level=modlevel,continuous_attacks=continuous,timing_mode=mode,
      _oblvns_ranged_attack_consumed=not active)
 for mod,modlevel in (('uniequip_002_mizuki',3),('uniequip_003_mizuki',2),('uniequip_003_mizuki',3),('uniequip_004_mizuki',3)):
  add('mizuki-qualified-'+mod+str(modlevel),'changed','char_437_mizuki',2,'enemy_below_half','0',
      elite=2,level=60,module_id=mod,module_level=modlevel)
 for op,n,f in (('char_206_gnosis',3,'frozen_at_skill_end'),('char_4087_ines',3,'ines_first_deployment')):
  for k,extra in enumerate(({'window_seconds':0},{'timing':{'target_disappears_seconds':0}},
      {'timing':{'target_windows':[]}}, {'timing':{'target_disappears_seconds':1}},
      {'window_seconds':40},{'timing_mode':'continuous','window_seconds':0})):
   add(f+'-source-scope-'+str(k),'changed',op,n,f,'false',**extra)
 errors=[('char_437_mizuki',2,'enemy_below_half',{'potential':True}),
  ('char_4228_closur',2,'reinforcement_blocks_target',{'skill':0}),
  ('char_206_gnosis',3,'frozen_at_skill_end',{'skill_rank':True}),
  ('char_4182_oblvns',2,'organ_mode',{'module_id':'not_a_module','module_level':2}),
  ('char_1048_orchd2',3,'power_coating',{'dragon_arrow_hits':False}),
  ('char_1035_wisdel',2,'overload',{'ghost_count':False}),
  ('char_1035_wisdel',2,'overload',{'ghost_count':1,'ghost_casts':False}),
  ('char_1035_wisdel',2,'overload',{'ghost_count':1,'ghost_casts':1,'window_seconds':0}),
  ('char_206_gnosis',3,'frozen_at_skill_end',{'cold_state':False}),
  ('char_4087_ines',3,'ines_first_deployment',{'stolen_enemy_count':False}),
  ('char_4182_oblvns',2,'fever',{'note_count':False}),
  ('char_1041_angel2',2,'steal_success',{'enemy_resistance':101}),
  ('char_1041_angel2',3,'delivery_coordinate',{'timing':{'windup_frames':float('nan')}}),
  ('char_4228_closur',2,'reinforcement_blocks_target',{'effects':[{'kind':'attack_pct','value':float('inf')}]}),
  ('char_1048_orchd2',1,'double_charge',{'near_previous_deployment':'false'}),
  ('char_437_mizuki',3,'enemy_below_half',{'elite':0,'skill_rank':7})]
 for i,(op,n,f,extra) in enumerate(errors):add('old-error-'+str(i),'old_error',op,n,f,'false',**extra)
 for i,(op,n,f,v,extra) in enumerate((
  ('char_4182_oblvns',3,'ranged_attack',True,{'module_id':'uniequip_002_oblvns','module_level':2,'level':60}),
  ('char_4182_oblvns',3,'ranged_attack','false',{'module_id':'uniequip_002_oblvns','module_level':2,'level':60,'continuous_attacks':False}),
  ('char_1048_orchd2',1,'double_charge',False,{}),('char_1048_orchd2',1,'double_charge','false',{}))):
  for relic in ('rogue_6_relic_legacy_95','rogue_6_relic_legacy_105'):
   expect='same' if not isinstance(v,str) or extra.get('continuous_attacks') is False else 'changed'
   add('multicore-'+str(i)+relic,expect,op,n,f,v,relic_ids=[relic],**extra)
 return rows
