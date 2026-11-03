"""Public design cases; list construction performs no API, GUI or state reads."""
def cases075(squads):
    rows=[]
    def add(section,owner,number,elite,level,rank,mode,**extra):
        args={'operator':owner,'skill':number,'elite':elite,'level':level,'skill_rank':rank,
              'potential':1,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':10,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[]}
        args.update(extra);rows.append({'section':section,'input':args})
    modes=('frames','continuous')
    for record in squads.values():
        for mode in modes:
            for flag in (False,True):
                add(71,'silverash',3,2,90,10,mode,run_config={'squad':{
                    'id':record['id'],'name':record['name'],'level':record['bandLevel'],'effect_verified':flag}})
    for sid,gate in (('rogue_6_band_2',3),('rogue_6_band_5',6),('rogue_6_band_7',9)):
        record=squads[sid]
        for grade in (gate-1,gate):
            for mode in modes:
                add(71,'silverash',3,2,90,10,mode,run_config={'squad':{
                    'id':sid,'name':record['name'],'level':1,'effect_verified':True},
                    'difficulty':{'value':grade,'modeDifficulty':'NORMAL'}})
    record=squads['rogue_6_band_22']
    for elite,level,rank in ((0,50,4),(1,80,7),(2,90,10)):
        for mode in modes:
            add(71,'mechanist',1,elite,level,rank,mode,run_config={'squad':{
                'id':record['id'],'name':record['name'],'level':1,'effect_verified':True}})
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,90,10,(1,2,3))):
        for potential in (1,6):
            interval={(1,1):30,(1,6):26,(2,1):20,(2,6):16}.get((elite,potential))
            # Existing option QDoubleSpinBox has two decimal places.
            ages=(0,59,60,120,3600) if interval is None else (0,interval-.01,interval,3*interval-.01,3*interval,3600)
            for number in numbers:
                for mode in modes:
                    for warmup in (0,100):
                        for age in ages:
                            add(72,'char_1038_whitw2',number,elite,level,rank,mode,potential=potential,
                                deployment_elapsed_seconds=age,drone_warmup_hits=warmup)
    for elite,level,rank in ((1,60,7),(2,39,7),(2,40,10)):
        for stage in (1,2,3):
            for number in (1,2):
                for mode in modes:
                    for horizon in (0,10):
                        add(73,'char_133_mm',number,elite,level,rank,mode,module_id='uniequip_002_mm',
                            module_level=stage,window_seconds=horizon)
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,1,1,(1,2,3)),(2,90,10,(1,2,3))):
        for stage in ((0,1,2,3) if elite==2 and level==90 else (0,)):
            for number in numbers:
                for mode in modes:
                    for ghosts,casts,horizon in ((0,0,10),(1,2,10),(3,0,0)):
                        add(74,'char_1035_wisdel',number,elite,level,rank,mode,
                            module_id='uniequip_002_wisdel' if stage else None,module_level=stage,
                            ghost_count=ghosts,ghost_casts=casts,window_seconds=horizon)
    return rows

def preview_cases075(stages):
    return [{'section':75,'stage_id':sid,'enemy_id':enemy['id'],'level':enemy['level'],'technical':technical}
        for sid in ('ro6_n_3_6','ro6_e_3_6') for enemy in stages[sid]['enemies'] for technical in (False,True)]
