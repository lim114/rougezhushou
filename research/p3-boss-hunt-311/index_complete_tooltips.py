"""Reconstruct the separate tooltip index from the already complete DOM."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
def walk(n):
    if isinstance(n,dict):
        yield n
        for c in n.get('children',[]):yield from walk(c)
def txt(n):
    return n if isinstance(n,str)else ''.join(txt(c)for c in n['children'])+('\n'if n['tag']in ['br','p','li']else '')
def hidden(n):
    return isinstance(n,dict)and n.get('tag')=='span'and 'display:none'in n.get('attributes',{}).get('style','').replace(' ','')
def reconstruct():
    old=json.loads((OUT/'complete-document-cards.json').read_bytes())
    for actor,doc in old['documents'].items():
        for card in doc['cards']:
            tips=[]
            for node in walk(card['complete_DOM']):
                if 'mc-tooltips'in node.get('attributes',{}).get('class','').split():
                    contents=[c for c in node['children']if hidden(c)]
                    tips.append({'location':node['location'],
                        'complete_visible_label':''.join(txt(c)for c in node['children']if c not in contents).strip(),
                        'complete_tooltip_text':'\n'.join(txt(c).strip()for c in contents),'complete_DOM':node})
            card['tooltip_nodes']=tips
    old['notes'].append('Separate tooltip index includes mc-tooltips class containers and complete hidden contents; the first extraction kept them only inside complete_DOM.')
    return (json.dumps(old,ensure_ascii=False,indent=2)+'\n').encode('utf8')
if __name__=='__main__':
    rebuilt=reconstruct()
    actual=(OUT/'complete-document-cards-with-tooltips.json').read_bytes()
    if rebuilt!=actual:raise ValueError('Separate tooltip index differs from the complete original DOM')
    print('Complete tooltip index equals the preserved DOM-derived bytes; no source modified.')
