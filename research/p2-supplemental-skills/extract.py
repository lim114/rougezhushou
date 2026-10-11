"""Reproduce the seven pinned skill fragments from original JSON files."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--source-directory',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    catalog=json.loads((root/'rouge/data/catalog.json').read_text(encoding='utf-8'))
    source={key:catalog['source'][key] for key in ('repository','commit','files')}
    originals={}
    for name in ('character_table','skill_table'):
        raw=(args.source_directory/(name+'.json')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['files'][name]['sha256']:
            raise ValueError('Original source SHA256 mismatch: '+name)
        originals[name]=json.loads(raw)
    operators={}
    for identity,kind in [('char_208_melan','attack_boost'),('char_123_fang','dp'),
                          ('char_124_kroos','double_physical'),('char_210_stward','magic_strike'),
                          ('char_209_ardign','self_heal'),('char_122_beagle','defense_boost'),
                          ('char_120_hibisc','heal_boost')]:
        character=originals['character_table'][identity];skill=character['skills'][0]['skillId']
        operators[identity]={'name':character['name'],'kind':kind,'character_selector':identity,
                             'skill_id':skill,'talents':character['talents'],
                             'levels':originals['skill_table'][skill]['levels'][:7]}
    data={'schema':1,'source':source,'operators':operators}
    with args.output.open('x',encoding='utf-8') as output:
        output.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
