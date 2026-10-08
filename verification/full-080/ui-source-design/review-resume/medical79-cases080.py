"""Construct public design cases without API calls or private state reads."""
def cases080():
    rows=[]
    def add(elite,level,rank,number,mode,scope,horizon,timing,**extra):
        args={'operator':'char_4202_haruka','elite':elite,'level':level,'skill_rank':rank,
              'skill':number,'timing_mode':mode,'potential':5,'trust':100,
              'module_id':None,'module_level':0,'window_seconds':horizon,'healing_targets':1,
              'enemy_defense':0,'enemy_resistance':0,'cooperative':False,'preexisting_fragile':False,'relic_ids':[]}
        if timing:args['timing']=timing
        args.update(extra);rows.append({'section':76,'context':scope,'input':args})
    scopes=[('positive',10,{}),('zero_window',0,{}),
            ('zero_lifetime',10,{'target_disappears_seconds':0}),
            ('empty_target_windows',10,{'target_windows':[]})]
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,60,10,(1,2,3))):
        for potential in (4,5):
            for number in numbers:
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for repeat in ((False,True)if number==2 else (False,)):
                            for count in (0,1,10000):
                                opts={'bubble_bursts':count,'potential':potential}
                                if number==2:opts['haruka_repeat']=repeat
                                if number==3:opts['levitate_triggers']=0
                                add(elite,level,rank,number,mode,scope,horizon,timing,**opts)
    for stage in (1,2,3):
        for level in (59,60):
            for mode in ('frames','continuous'):
                for count in (0,1):
                    add(2,level,10,2,mode,'module_unlock_boundary',10,{},bubble_bursts=count,
                        module_id='uniequip_002_haruka',module_level=stage,haruka_repeat=True)
    for elite,level,rank,number in ((0,50,4,1),(1,80,7,2)):
        for mode in ('frames','continuous'):
            for count in (0,1):
                opts={'haruka_repeat':False}if number==2 else {}
                add(elite,level,rank,number,mode,'locked_module_does_not_grant_talent',10,{},bubble_bursts=count,
                    module_id='uniequip_002_haruka',module_level=3,**opts)
    for mode in ('frames','continuous'):
        for trigger in (1,1000):
            for count in (0,1):
                add(2,60,10,3,mode,'independent_levitate_declaration',10,{},bubble_bursts=count,levitate_triggers=trigger)
    for elite,rank in ((1,7),(2,10)):
        for mode in ('frames','continuous'):
            for count in (0,1):
                add(elite,60,rank,2,mode,'zero_declared_friendly_targets',10,{},bubble_bursts=count,
                    healing_targets=0,haruka_repeat=False)
    def aglna(elite,level,rank,number,potential,mode,scope,horizon,timing,weight):
        args={'operator':'char_1015_aglna2','elite':elite,'level':level,'skill_rank':rank,'skill':number,
              'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[],
              'enemy_weight':weight}
        if timing:args['timing']=timing
        rows.append({'section':77,'context':scope,'input':args})
    for elite,numbers in ((0,(1,)),(1,(1,2)),(2,(1,2,3))):
        for number in numbers:
            for potential in (1,3):
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for weight in (0,3,4,100):
                            aglna(elite,1,1,number,potential,mode,scope,horizon,timing,weight)
    for elite,level,rank,number in ((0,50,4,1),(1,80,7,2),(2,90,10,3)):
        for mode in ('frames','continuous'):
            for weight in (0,3,4,100):
                aglna(elite,level,rank,number,3,mode,'readonly_max_cultivation',10,{},weight)
    # Exact public NORMAL roster identities, massLevel3/4. Selection overrides
    # the separate manual reference; declared weight remains genuine Qt input.
    for elite,number in ((0,1),(2,3)):
        for enemy_id,level,mass in (('enemy_10107_mjcdog_2',0,3),('enemy_2002_bearmi',1,4)):
            for mode in ('frames','continuous'):
                for weight in (0,100):
                    aglna(elite,1,1,number,3,mode,'selected_enemy_overrides_manual_weight',10,{},weight)
                    rows[-1]['input']['target_enemy']={'stage_id':'ro6_n_3_6','enemy_id':enemy_id,'level':level}
                    rows[-1]['expected_reference_mass']=mass
    #78 final source is committed; these designs still need final080 preflight.
    def mantra(elite,level,rank,number,potential,mode,scope,horizon,timing,count,**extra):
        args={'operator':'char_4204_mantra','elite':elite,'level':level,'skill_rank':rank,'skill':number,
              'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[],
              'palsy_triggers':count}
        if number==3:args['palsy_overflow_hits']=0
        if timing:args['timing']=timing
        args.update(extra)
        rows.append({'section':78,'context':scope,'input':args})
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,90,10,(1,2,3))):
        for number in numbers:
            for potential in (4,5):
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for count in (0,1,10000):
                            mantra(elite,level,rank,number,potential,mode,scope,horizon,timing,count)
    for mode in ('frames','continuous'):
        for scope,horizon,timing in scopes:
            for overflow in (1,10000):
                for count in (0,1):
                    mantra(2,90,10,3,5,mode,'separate_overflow_'+scope,horizon,timing,count,palsy_overflow_hits=overflow)
    for number in (1,2,3):
        for mode in ('frames','continuous'):
            for count in (0,1):
                mantra(2,90,10,number,5,mode,'elemental_immunity_does_not_bind_clock',10,{},count,
                    enemy_elemental_resistance=100.0)
    for stage in (1,2,3):
        for level in (59,60):
            for mode in ('frames','continuous'):
                for count in (0,1):
                    mantra(2,level,10,2,5,mode,'readonly_module_boundary',10,{},count,
                        module_id='uniequip_002_mantra',module_level=stage)
    for mode in ('frames','continuous'):
        for count in (0,1):
            mantra(0,50,4,1,5,mode,'locked_module_does_not_grant_talent',10,{},count,
                module_id='uniequip_002_mantra',module_level=3)
    #79 medical form only. No assumed account form-unlock or unavailable HP0.
    def medical(elite,level,rank,number,potential,mode,scope,horizon,timing,**extra):
        args={'operator':'char_1037_amiya3','elite':elite,'level':level,'skill_rank':rank,
              'skill':number,'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[]}
        if number==2:args['amiya_hit_targets']=1
        if timing:args['timing']=timing
        args.update(extra);rows.append({'section':79,'context':scope,'input':args})
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,70,7,(1,2)),(2,80,10,(1,2))):
        for number in numbers:
            for potential in (1,6):
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for count in ((1,5,100)if number==2 else (None,)):
                            opts={'amiya_hit_targets':count}if count is not None else {}
                            medical(elite,level,rank,number,potential,mode,scope,horizon,timing,**opts)
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,70,7,(1,2)),(2,49,10,(1,2)),(2,50,10,(1,2))):
        for number in numbers:
            for stage in (1,2,3):
                for mode in ('frames','continuous'):
                    medical(elite,level,rank,number,1,mode,'readonly_INC_X_boundary',10,{},
                        module_id='uniequip_002_amiya3',module_level=stage)
    for elite,numbers in ((0,(1,)),(1,(1,2)),(2,(1,2))):
        for number in numbers:
            for mode in ('frames','continuous'):
                for targets in ((0,2)if number==1 else (0,1)):
                    medical(elite,1,1,number,1,mode,'own_regeneration_independent_of_friendly_count',10,{},
                        healing_targets=targets)
        for mode in ('frames','continuous'):
            medical(elite,1,1,1,1,mode,'readonly_talent_minimum_level',10,{})
    return rows
