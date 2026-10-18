"""Independent source reading only; never mutates the frozen research package."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,re

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
SOURCE=ROOT/'.cache/p3-310-boss-research'
spec=importlib.util.spec_from_file_location('public_dom_reader',ROOT/'scripts/build_choice_annotations_307.py')
dom=importlib.util.module_from_spec(spec);spec.loader.exec_module(dom)

class Document(dom.Document):
 def handle_starttag(self,tag,attrs):
  where=self.getpos();super().handle_starttag(tag,attrs)
  self.nodes[-1].position=where

def visible(n,include_hidden=False):
 if isinstance(n,str):return n
 if n.tag in('script','style'):return''
 if not include_hidden and 'display:none' in n.attrs.get('style','').replace(' ',''):return''
 if n.tag=='br':return'\n'
 return ''.join(visible(c,include_hidden) for c in n.children)+('\n' if n.tag in('p','li','dt','dd','tr') else '')

def subtree(n):
 yield n
 for c in n.children:
  if isinstance(c,dom.Node):yield from subtree(c)

def pin(p):return{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def dump(name,obj):
 p=OUT/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return pin(p)
frozen=json.loads((SOURCE/'HANDOFF.json').read_text(encoding='utf-8'))
before={n:pin(SOURCE/n) for n in frozen['files']}
assert before==frozen['files']
source_records=json.loads((SOURCE/'http-source-records.json').read_text(encoding='utf-8'))
cards=[];module=None;global_notes=[]
for source in source_records[:3]:
 raw=(SOURCE/source['file']).read_text(encoding='utf-8');doc=Document(raw)
 lines=raw.splitlines(keepends=True);starts=[0]
 for line in lines:starts.append(starts[-1]+len(line))
 def loc(n):
  ln,col=n.position;offset=starts[ln-1]+col
  return{'line':ln,'column':col,'character_offset':offset,'byte_offset_utf8':len(raw[:offset].encode('utf-8'))}
 def tips(n):
  result=[]
  for child in subtree(n):
   if 'display:none' in child.attrs.get('style','').replace(' ',''):
    result.append({'location':loc(child),'text_including_nested_tooltips':visible(child,True).strip(),
     'attributes':child.attrs})
  return result
 url='https://m.prts.wiki/w/'+source['title'].replace(' ','_')+'?oldid='+source['revision']
 sref={'file':'.cache/p3-310-boss-research/'+source['file'],'revision':source['revision'],
  'sha256':source['sha256'],'url':url}
 for n in doc.nodes:
  if n.attrs.get('id')=='talent-intro-base':
   global_notes.append({'actor_page':source['title'],'source':sref,'location':loc(n),'selector':'#talent-intro-base',
    'kind':'generic_documentation_convention_not_this_boss_specific_difficulty_rule',
    'complete_text_including_hidden':visible(n,True).strip()})
 nodes=[n for n in doc.nodes if dom.cls(n,'ak-card__body') and dom.cls(n,'skill_card')]
 for index,n in enumerate(nodes):
  title=next((c for c in n.children if isinstance(c,dom.Node)and dom.cls(c,'ak-card__title')),None)
  header=visible(title).strip()if title else None
  paragraphs=[c for c in n.children if isinstance(c,dom.Node)and c.tag=='p']
  cards.append({'actor':source['title'],'card_index':index,'kind':'skill'if title else'ability',
   'source_selector':'.ak-card__body.skill_card['+str(index)+']','source':sref,'location':loc(n),
   'complete_visible_header':header,'documented_mode_labels':re.findall(r'\[([^\[\]]+)\]',header or''),
   'complete_visible_body':'\n'.join(visible(c).strip()for c in paragraphs),
   'complete_visible_card':visible(n).strip(),
   'paragraphs':[{'paragraph_index':i,'location':loc(c),'text':visible(c).strip()}for i,c in enumerate(paragraphs)],
   'tooltips':tips(n)})
 if source['file']=='module-complete.html':
  tables=[n for n in doc.nodes if n.tag=='table'and dom.cls(n,'wikitable')and'源阶方模块'in visible(n)and'装置机制'in visible(n)]
  assert len(tables)==1
  t=tables[0]
  module={'name':source['title'],'source':sref,'source_selector':'table.wikitable containing 源阶方模块 and 装置机制',
   'location':loc(t),'complete_visible_table':visible(t).strip(),
   'table_rows':[{'row_index':i,'location':loc(n),'text':visible(n).strip()}for i,n in enumerate(subtree(t))if n.tag=='tr'],
   'tooltips':tips(t),'trap_id_occurrences':[]}
  skills=[n for n in doc.nodes if n.tag=='table'and dom.cls(n,'wikitable')and'全域信息失真'in visible(n)]
  assert len(skills)==1
  module['skill_tables']=[{'source_selector':'section#mf-section-2 table.wikitable containing 全域信息失真',
   'location':loc(n),'complete_visible_table':visible(n).strip(),
   'paragraphs':[{'location':loc(p),'text':visible(p).strip()}for p in subtree(n)if p.tag=='p'],
   'tooltips':tips(n)}for n in skills]
  for m in re.finditer('trap_324_shmbmb',raw):
   module['trap_id_occurrences'].append({'character_offset':m.start(),'line':raw[:m.start()].count('\n')+1,
    'literal_HTML_context':raw[max(0,m.start()-180):m.end()+180]})
assert len(cards)==9 and sum(c['kind']=='skill'for c in cards)==7
assert module is not None
dump('complete-visible-cards-and-tooltips.json',{'kind':'SOURCE_READING_ONLY','cards':cards,'module':module,
 'global_documentation_notes':global_notes,
 'visible_body_excludes_display_none_tooltips':True,'tooltips_are_separate_context_not_extra_boss_skills':True})
dump('frozen-source-pins-before.json',before)
after={n:pin(SOURCE/n)for n in frozen['files']};assert before==after
dump('frozen-source-pins-after.json',after)
for c in cards:
 print(c['actor'],c['card_index'],c['kind'],repr(c['complete_visible_header']),len(c['tooltips']))
print('\nMODULE COMPLETE VISIBLE TABLE\n'+module['complete_visible_table'])
print('\nMODULE COMPLETE VISIBLE SKILL TABLE\n'+module['skill_tables'][0]['complete_visible_table'])
print('FROZEN_SOURCE_UNCHANGED',len(after))
