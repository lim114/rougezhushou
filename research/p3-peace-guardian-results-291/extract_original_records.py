"""Cache candidate: recheck complete pinned public source before selection."""
import argparse
import hashlib
import json
from pathlib import Path

SHA256='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    raw=args.source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA256:raise ValueError('Complete original public table changed.')
    topic=json.loads(raw)['details']['rogue_6']
    selected={'schema_version':1,
        'source':{'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/roguelike_topic_table.json',
                  'sha256':SHA256,'bytes':len(raw),'commit':COMMIT},
        'field_root':'$.details.rogue_6',
        'choices':{key:topic['choices'][key] for key in (
            'choice_ro6_task1_1','choice_ro6_task1_2','choice_ro6_task1_3','choice_ro6_task1_4')},
        'choiceScenes':{key:topic['choiceScenes'][key] for key in (
            'scene_ro6_task1_enter','scene_ro6_task1_1','scene_ro6_task1_2')},
        'scope':'Full original objects after complete-source SHA check; no source-scene script, nearest rule or current battle completion inferred.'}
    output=(json.dumps(selected,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    path=Path(__file__).with_name('original-records.json')
    if args.check:
        if path.read_bytes()!=output:raise ValueError('Selected original records no longer reproduce.')
    else:
        with path.open('xb') as stream:stream.write(output)
    print(json.dumps({'checked_existing':args.check,'full_source_bytes':len(raw),'full_source_sha256':SHA256,
        'selected_choices':4,'selected_scenes':3,'selected_sha256':hashlib.sha256(output).hexdigest()}))


if __name__=='__main__':main()
