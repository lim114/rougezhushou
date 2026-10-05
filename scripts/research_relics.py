"""Read public, pinned game tables before implementing collectible rules."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'.cache/research/relics'
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rouge-relic-research'}),timeout=40) as response:return response.read()
def main():
    DEST.mkdir(parents=True,exist_ok=True)
    receipt={}
    repo='Kengxxiao/ArknightsGameData'
    try:
        commits=json.loads(fetch(f'https://api.github.com/repos/{repo}/commits?path=zh_CN/gamedata/excel/roguelike_topic_table.json&per_page=1'))
        commit=commits[0]['sha']
        url=f'https://raw.githubusercontent.com/{repo}/{commit}/zh_CN/gamedata/excel/roguelike_topic_table.json'
        payload=fetch(url);current=json.loads(payload)['details']['rogue_6']
        baseline=json.loads((ROOT/'.cache/game-data/roguelike_topic_table.json').read_text(encoding='utf-8'))['details']['rogue_6']
        old={k:v for k,v in baseline['items'].items() if v.get('type')=='RELIC'}
        now={k:v for k,v in current['items'].items() if v.get('type')=='RELIC'}
        changes=[k for k in old if old[k]!=now.get(k) or baseline['relics'].get(k)!=current['relics'].get(k)]
        (DEST/'latest-topic.json').write_bytes(payload)
        receipt['latest_snapshot']={'url':url,'commit':commit,'sha256':hashlib.sha256(payload).hexdigest(),
            'baseline_relics':len(old),'latest_relics':len(now),'changed_existing':changes,'new_ids':sorted(set(now)-set(old))}
    except Exception as exc:receipt['latest_snapshot']={'unavailable':str(exc)[:200]}
    probes=['https://api.github.com/repos/xulai1001/arkdps_data_collection/commits?path=customdata/dps_anim.json&per_page=1',
        'https://api.github.com/repos/Ray144165154/arkdps/git/trees/HEAD?recursive=1']
    def probe(url):
        try:
            payload=fetch(url);j=json.loads(payload)
            name='animation-history.json' if 'commits?' in url else 'arkdps-tree.json'
            (DEST/name).write_bytes(payload)
            return {'url':url,'saved':name,'sha256':hashlib.sha256(payload).hexdigest()}
        except Exception as exc:return {'url':url,'unavailable':str(exc)[:120]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:receipt['timing_probes']=list(pool.map(probe,probes))
    (DEST/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
