"""Pure static extraction of complete public documents and fixed primary records."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,re
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('source_dom',ROOT/'scripts/build_choice_annotations_307.py');dom=importlib.util.module_from_spec(spec);spec.loader.exec_module(dom)
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def write(n,v):(OUT/n).write_bytes(encoded(v))
def pin(p):
 p=Path(p);raw=p.read_bytes();return{'file':p.relative_to(ROOT).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
class Document(dom.Document):
 def __init__(self,text):
  self.original=text;self.line_starts=[0]+[m.end()for m in re.finditer('\n',text)];super().__init__(text)
 def handle_starttag(self,tag,attrs):
  super().handle_starttag(tag,attrs);n=self.nodes[-1];line,col=self.getpos();offset=self.line_starts[line-1]+col;n.location={'line':line,'column':col,'character_offset':offset,'byte_offset_utf8':len(self.original[:offset].encode('utf8'))}
def visible(n):
 if isinstance(n,str):return n
 if n.tag in('script','style')or'display:none'in n.attrs.get('style','').replace(' ',''):return''
 return''.join(visible(c)for c in n.children)+('\n'if n.tag in('p','li','dt','dd','tr','br')else'')
def serial(n):return n if isinstance(n,str)else{'tag':n.tag,'attributes':n.attrs,'location':getattr(n,'location',None),'children':[serial(c)for c in n.children]}
def descend(n):
 for c in n.children:
  if isinstance(c,dom.Node):yield c;yield from descend(c)
sources=json.loads((OUT/'http-source-records.json').read_bytes());assert len(sources)==5 and all(x['status']==200 and not x.get('error')for x in sources)
complete={}
for src in sources:
 raw=(OUT/src['file']).read_bytes();assert sha256(raw).hexdigest()==src['sha256'];doc=Document(raw.decode('utf8'));cards=[]
 for n in doc.nodes:
  if not(dom.cls(n,'ak-card__body')and dom.cls(n,'skill_card')):continue
  header=next((c for c in n.children if isinstance(c,dom.Node)and dom.cls(c,'ak-card__title')),None)
  headertext=visible(header).strip()if header else None
  paragraphs=[{'text':visible(c).strip(),'location':getattr(c,'location',None),'complete_DOM':serial(c)}for c in n.children if isinstance(c,dom.Node)and c.tag=='p']
  tooltipnodes=[{'location':c.location,'attributes':c.attrs,'complete_visible_text':visible(c),'complete_DOM':serial(c)}for c in descend(n)if any(('tooltip'in k or'tippy'in k or k=='data-content')for k in c.attrs)]
  cards.append({'card_index':len(cards),'kind':'skill'if headertext else'ability','complete_visible_header':headertext,'documented_modes_from_complete_header':re.findall(r'\[([^\[\]]+)\]',headertext or''),'unlabelled_mode_means':'文献未限定，不代表所有状态适用或没有能力','location':n.location,'paragraphs':paragraphs,'complete_visible_card':visible(n).strip(),'tooltip_nodes':tooltipnodes,'complete_DOM':serial(n)})
 tables=[{'table_index':i,'location':n.location,'complete_visible_text':visible(n).strip(),'complete_DOM':serial(n)}for i,n in enumerate([n for n in doc.nodes if n.tag=='table'and dom.cls(n,'wikitable')])]
 complete[src['title']]={'source':src,'cards':cards,'complete_wikitables':tables}
write('complete-document-cards.json',{'schema':'section311_complete_documentary_cards_v1','documents':complete,'DOM_parser':pin(ROOT/'scripts/build_choice_annotations_307.py'),'notes':['Headers are read in full, not split to first line.','Every source HTML remains complete raw original.','No mode inferred from absent label; no time/state or phase calculations.']})
bpath=ROOT/'rouge/data/battle-previews.json';battle=json.loads(bpath.read_bytes());spath=ROOT/'rouge/data/enemy-skill-references.json';skills=json.loads(spath.read_bytes());dbpath=ROOT/'.cache/game-data/levels/enemydata/enemy_database.json';dbraw=dbpath.read_bytes();assert sha256(dbraw).hexdigest()==battle['source']['enemy_database']['sha256'];db=json.loads(dbraw)
ids=['enemy_2145_cadejo','enemy_2146_cadesd','enemy_2137_shsdgo','enemy_2146_cadesd_2','enemy_2146_cadesd_3']
original={'schema':'section311_selected_complete_original_records_v1','source_files':[pin(bpath),pin(spath),pin(dbpath)],'complete_canonical_stages':{},'complete_original_levels':{},'complete_stage_enemyDbRefs':{},'complete_original_enemy_records':{eid:[row for row in db['enemies']if row['Key']==eid]for eid in ids},'complete_skill_definitions':{eid:skills['definitions'].get(eid)for eid in ids},'complete_skill_bindings':{}}
for sid in ['ro6_b_4','ro6_b_4_b']:
 stage=battle['stages'][sid];p=ROOT/'.cache/game-data/levels'/stage['level_source']['url'].split('/levels/',1)[1];raw=p.read_bytes();assert sha256(raw).hexdigest()==stage['level_source']['sha256'];level=json.loads(raw)
 original['source_files'].append(pin(p));original['complete_canonical_stages'][sid]=stage;original['complete_original_levels'][sid]=level;original['complete_stage_enemyDbRefs'][sid]=[row for row in level['enemyDbRefs']if row['id']in ids];original['complete_skill_bindings'][sid]={key:value for key,value in skills['bindings'][sid].items()if key.split('@')[0]in ids}
write('selected-original-records.json',original)
covered={('ro6_b_6','enemy_2150_shchmr',0):309,('ro6_b_5','enemy_2147_shophm',0):310,('ro6_b_5','enemy_2148_shorbb',0):310}
rows=[]
for sid,stage in battle['stages'].items():
 for e in stage['enemies']:
  if e.get('level_type')=='BOSS':
   identity=(sid,e['id'],e['level']);rows.append({'identity':list(identity),'stage_name':stage['name'],'fixed_name':e['name'],'complete_boss_reader_section':covered.get(identity),'has_only_generic_reference':identity not in covered,'stage_level_source':stage['level_source']})
write('fixed-boss-inventory.json',{'schema':'section311_fixed_BOSS_identity_inventory_v1','source':pin(bpath),'rows':rows,'scope':'Only current fixed battle-previews BOSS-labelled references; not an exhaustive server boss catalogue.','existing_dedicated_readers':[pin(ROOT/n)for n in ['rouge/enemy_form_reference.py','rouge/boss_phase_reference.py','rouge/boss_cycle_reference.py','rouge/battle_view.py']],'306_scope':'空值体伪装/现身，不是本组三主体完整技能/能力阅读。','total_fixed_identity_rows':len(rows),'unique_enemy_ids':len({x['identity'][1]for x in rows}),'reader_covered_identity_rows':sum(x['complete_boss_reader_section']is not None for x in rows)})
print(json.dumps({'document_revisions':[(s['title'],s['revision'])for s in sources],'complete_card_counts':{name:{'skills':sum(c['kind']=='skill'for c in v['cards']),'abilities':sum(c['kind']=='ability'for c in v['cards'])}for name,v in complete.items()},'selected_primary_bytes':(OUT/'selected-original-records.json').stat().st_size,'inventory_rows':len(rows),'output_pins':{n:pin(OUT/n)for n in ['complete-document-cards.json','selected-original-records.json','fixed-boss-inventory.json']}},ensure_ascii=False))
