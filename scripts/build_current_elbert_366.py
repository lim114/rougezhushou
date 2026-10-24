"""Freeze complete mechanism cards and current exact stage/entity references."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
import argparse,importlib.util,json,re,sys

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-elbert-366'


def encode(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')


class Visible(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.skip=0;self.card_count=0
    def handle_starttag(self,tag,attrs):
        if 'prts-enemy-level-card'in(dict(attrs).get('class')or'').split():self.card_count+=1
        if tag in('style','script'):self.skip+=1
        if tag in('p','div','br','li','td','th'):self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in('style','script'):self.skip-=1
    def handle_data(self,text):
        if not self.skip:self.parts.append(text)
    def text(self):return '\n'.join(line.strip()for line in ''.join(self.parts).splitlines()if line.strip())


def complete_card(html,profile):
    start=html.index('<section class="mf-section-1');end=html.index('</section>',start)+len('</section>')
    raw=html[start:end]
    parser=Visible();parser.feed(raw);text=parser.text()
    if raw.count('<section')!=1 or parser.card_count!=1:raise ValueError('One complete unique visible enemy card section required')
    if profile=='firebrand':required=('登场10秒后自身退场','10秒内由最大值线性降低至0','每秒变化一次','根据关卡配置可改为由0线性提升至最大值','2.0 / 1000 / 200','半径0.25','中点判定','不受迷彩','随后自身退场')
    else:required=('仅未被阻挡时可触发','下个路径点','普通攻击为持续攻击','所在地块中心','以自身路径召唤1个','取决于','在关卡内的配置','退场后在自身所在位置','半径20.0','攻击速度+50','移动速度最终提升至150%','同名效果不叠加')
    if any(term not in text for term in required):raise ValueError('Complete mechanism qualification missing:'+profile)
    return{'profile':profile,'complete_section_character_span':[start,end],'full_html':raw,
           'full_visible_text':text,'section_sha256':sha256(raw.encode('utf8')).hexdigest(),
           'one_complete_current_visible_card_and_legacy_table_retained':True,'qualifying_phrases':list(required)}


def build(source_root=ROOT,artifact_root=ROOT):
    source_root,artifact_root=Path(source_root),Path(artifact_root);sys.path.insert(0,str(source_root))
    spec=importlib.util.spec_from_file_location('rouge._elbert_builder_366',ROOT/'rouge/current_elbert_reference.py')
    model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    source=json.loads((source_root/'research/p3-expansion-313/current-topic.json').read_bytes())
    inputs=json.loads((source_root/'research/p3-current-battle-314/source-inputs.json').read_bytes())
    profiles={};cards={};downloads={}
    for name,title,revision,cooldown,recovery in(('elbert','埃尔伯特',442860,30,'0.5'),('heretic','“异端”埃尔伯特',442859,75,'0.33'),('firebrand','“火种”',435364,None,None)):
        raw=(artifact_root/PACK/(name+'-page.html')).read_bytes();download=json.loads((artifact_root/PACK/(name+'-download.json')).read_bytes());html=raw.decode('utf8')
        if download['http_status']!=200 or download['full_original_html_archived']is not True or len(raw)!=download['bytes']or sha256(raw).hexdigest()!=download['sha256']or re.findall(r'"wgRevisionId":(\d+)',html)!=[str(revision)]:raise ValueError('Actual complete successful source required:'+name)
        card=complete_card(html,name)
        if name!='firebrand'and(('后摇'+recovery+'秒')not in card['full_visible_text']or('\n闪现\n0\n'+str(cooldown)+'\n/\n')not in card['full_visible_text']):raise ValueError('Exact distinct blink recovery and cold-start table required')
        profiles[name]={'title':title,'revision':revision,'url':download['url'],'blink_cooldown':cooldown,'blink_recovery_text':recovery,'card_key':name}
        cards[name]=card;downloads[name]=download
    active=model.battle.packet()
    if active is None:raise ValueError('Current exact battle reference required')
    stage_rows=model.source_rows(source,inputs)
    for stage in stage_rows.values():
        for row in stage['entities']:
            cfg=row['declared_configuration'];values={r['key']:r['value']for r in cfg['talentBlackboard']}
            if len(values)!=len(cfg['talentBlackboard']):raise ValueError('Duplicate mechanism key')
            if row['kind']=='boss':
                wanted={'Die.attack_speed':50.0,'Die.move_speed':1.5,'Die.projectile_range':20.0}
                if any(values.get(k)!=v for k,v in wanted.items()):raise ValueError('Staff description differs from exact current configuration')
                if cfg['skills']!=[{'prefabKey':'Blink','priority':0,'cooldown':float(profiles[row['profile']]['blink_cooldown']),'initCooldown':0.0,'spCost':0,'blackboard':None}]:raise ValueError('Blink source differs from documentary reference')
            else:
                independent=row['constructor']=='independent'
                wanted={'DamageAura.range_radius':0.25,'DamageAura.interval':1.0,'DamageAura.value':500.0 if independent else 1000.0,
                        'DamageAura.ep_value':200.0,'DamageAura.circle':1.5 if independent else 2.0,
                        'DamageAura.duration':6.0 if independent else 10.0,'Passive.duration':6.0 if independent else 10.0}
                if any(values.get(k)!=v for k,v in wanted.items()):raise ValueError('Exact firebrand independent/default source differs')
    data={'schema':'current_elbert_366_v1','game_commit':model.battle.version.NEW_COMMIT,
          'stages':stage_rows,'profiles':profiles,'complete_cards':cards,
          'battle_identity':active['identity'],'current_server_verified':False,
          'actual_fire_direction':None,'actual_staff_position':None,'actual_damage':None,
          'actual_clock':None,'run_updated':False,'numerical_model_applied':False}
    notes={'section':366,'candidate_preparation_only':True,'game_commit':model.battle.version.NEW_COMMIT,
           'actual_new_downloads':downloads,'complete_unique_visible_cards':3,'exact_current_stage_configs':4,
           'exact_current_entity_references':8,
           'new_scope':'Current four exact stage configurations get a full two-boss/independent-firebrand/staff mechanism reader and exact entity/location source guard. Not re-counting older auxiliary firebrand parameter references.',
           'old_scope_reused':'auxiliary_enemy_mechanisms already documents default-vs-independent firebrand in two old stages. Retain old module and its source bounds; not called from current reference and not claimed migrated wholesale.',
           'independent_entity_rule':'Complete boss cards explicitly bind intensity change to Firebrand stage configuration, not boss title. Keep original handbook distance summary separately; do not calculate intensity by distance.',
           'current_firebrand_sources':'Normal and DLC1normal useDb true with grade0 DB. Alternate and DLC1alternate useDb false with full independent6s/500/1.5 configuration; no DB default inheritance.',
           'undefined_override_identity':'ro6_b_3 contains complete override wrappers with every m_defined=false, not a null override; each wrapper is reviewed as undefined and retained verbatim. No placeholder name/prefab/attribute is applied. A true unreviewed DB override is rejected rather than merged silently.',
           'direction_limit':'Independent sp flags are retained raw, not decoded into a growth curve without semantic script evidence. Matching boss name is not a rule selector.',
           'staff_scope':'Both complete source cards state post-exit staff, radius20, attackSpeed+50, finalmoveSpeed150%, same-name nonstack. Only documentary reference; no actual received buff, coverage or final panel.',
           'timing_scope':'Documentary cooldown0/30vs0/75and recovery0.5vs0.33 retained. No automatic absolute spawn/collision/blink/staff/tick clock or final damage calculation.',
           'unknown':['actual stage instance','actual source spawn/branch','firebrand growth rule active in current instance','first tick/collision/end clocks','actual staff position/coverage','current server execution','numeric environment corrections'],
           'excluded':['365 Hanko/smoke','old boss309-312 workflows','combat control','game/chat/private state','tests/native acceptance'],
           'licensing':'PRTS complete public cards and attribution retained; community prose follows source-site CC BY-NC-SA and game content retains rightsholder copyright.'}
    output={model.DATA:encode(data),PACK+'/complete-cards.json':encode(cards),PACK+'/source-notes.json':encode(notes)}
    names={model.DATA,PACK+'/source-notes.json',PACK+'/complete-cards.json','research/p3-expansion-313/current-topic.json',
           'research/p3-current-battle-314/source-inputs.json','research/p3-current-battle-314/source-selection.json',
           'research/p3-current-battle-314/runtime-manifest.json'}
    names.update(PACK+'/'+name+suffix for name in profiles for suffix in('-page.html','-download.json'))
    files={}
    for name in sorted(names):
        raw=output.get(name)
        if raw is None:raw=((artifact_root if name.startswith(PACK+'/')else source_root)/name).read_bytes()
        files[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    output[model.MANIFEST]=encode({'schema':'current_elbert_366_manifest_v1','game_commit':model.battle.version.NEW_COMMIT,'files':files})
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--source-root',type=Path,default=ROOT);p.add_argument('--output-root',type=Path,default=ROOT);args=p.parse_args();output=build(args.source_root,args.output_root)
    for name,raw in output.items():
        path=args.output_root/name
        if args.check:
            if path.read_bytes()!=raw:raise ValueError('Build differs:'+name)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    print(json.dumps({'prepared_only':True,'stages':4,'enemy_references':8,'complete_cards':3,'manifest_sha256':sha256(output[PACK+'/runtime-manifest.json']).hexdigest()}))
