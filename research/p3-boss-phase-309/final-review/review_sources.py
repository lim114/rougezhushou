from pathlib import Path
from hashlib import sha256
import json,re,importlib.util

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;SOURCE=ROOT/'.cache/p3-309-boss-lifecycle-research'
spec=importlib.util.spec_from_file_location('read_existing_dom',ROOT/'scripts/build_choice_annotations_307.py')
dom=importlib.util.module_from_spec(spec);spec.loader.exec_module(dom)
def visible(node):
 if isinstance(node,str):return node
 if node.tag in('script','style')or'display:none'in node.attrs.get('style','').replace(' ',''):return''
 if node.tag=='br':return'\n'
 return''.join(visible(child)for child in node.children)+('\n'if node.tag in('p','li','dt','dd')else'')
def digest(path):return sha256(path.read_bytes()).hexdigest()
handoff=json.loads((SOURCE/'HANDOFF.json').read_text(encoding='utf-8'))
before={name:digest(SOURCE/name)for name in handoff['files']}
assert all(before[name]==pin['sha256']for name,pin in handoff['files'].items())
doc=dom.Document((SOURCE/'boss-complete.html').read_text(encoding='utf-8'))
nodes=[n for n in doc.nodes if dom.cls(n,'ak-card__body')and dom.cls(n,'skill_card')]
assert len(nodes)==7
cards=[]
for index,node in enumerate(nodes):
 titles=[child for child in node.children if isinstance(child,dom.Node)and dom.cls(child,'ak-card__title')]
 header=visible(titles[0]).strip()if titles else None
 effects=[child for child in node.children if isinstance(child,dom.Node)and child.tag=='p']
 modes=re.findall(r'\[([^\[\]]+)\]',header or'')
 cards.append({'card_index':index,'source_selector':'.ak-card__body.skill_card['+str(index)+']',
  'complete_visible_header':header,'documented_mode_labels':modes,
  'complete_visible_effect':'\n'.join(visible(child).strip()for child in effects),
  'complete_visible_card':visible(node).strip()})
original=json.loads((SOURCE/'selected-original-records.json').read_text(encoding='utf-8'))
record=original['current_skill_definition_complete']['0']
data=json.loads((SOURCE/'player-reading-data-candidate.json').read_text(encoding='utf-8'))
assert len(data['skills'])==6
corrections=[]
for skill,card in zip(data['skills'],cards[:6]):
 corrections.append({'skill_id':skill['skill_id'],'name':skill['name'],
  'old_documented_modes':skill['documented_modes'],'correct_documented_modes':card['documented_mode_labels'],
  'source_selector':card['source_selector'],'complete_visible_header':card['complete_visible_header']})
output={'kind':'INDEPENDENT_SOURCE_REVIEW_NO_FROZEN_SOURCE_EDITS','source_revision':'435612',
 'source_page_sha256':digest(SOURCE/'boss-complete.html'),'cards':cards,'mode_correction_proposal':corrections,
 'frozen_inputs_before':before}
(OUT/'seven-complete-visible-cards.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert before=={name:digest(SOURCE/name)for name in handoff['files']}
for row in cards:print(row['card_index'],repr(row['complete_visible_header']),row['documented_mode_labels'])
print('FROZEN_SOURCE_UNCHANGED',len(before))
