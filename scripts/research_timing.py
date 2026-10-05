"""Download versioned public timing references only; never execute remote code."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import sys

DEST=Path(__file__).resolve().parents[1]/'.cache/research/timing'
DEST.mkdir(parents=True,exist_ok=True)

def read(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rouge-timing-research'}),timeout=25).read()

def tree(repo):
    j=json.loads(read('https://api.github.com/repos/'+repo+'/git/trees/HEAD?recursive=1'))
    (DEST/(repo.split('/')[-1]+'-tree.json')).write_text(json.dumps(j),encoding='utf-8')
    paths=[x['path'] for x in j['tree'] if x['type']=='blob']
    print(repo,j['sha'],[p for p in paths if any(k in p.lower() for k in ('anim','attack','duration','readme','spec'))][:45])

def probe(pair):
    index,url=pair
    try:
        data=read(url);j=json.loads(data)
        if not isinstance(j,dict):raise ValueError('Not animation mapping')
        (DEST/('latest-animation-'+str(index)+'.json')).write_bytes(data)
        return {'url':url,'profiles':len(j),'present':[k for k in ('char_1052_kalts2','char_1045_svash2','char_4230_mcnist') if k in j]}
    except Exception as exc:return {'url':url,'status':'unavailable','reason':str(exc)[:120]}

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='probe':
        urls=['https://viktorlab.cn/akdata/dps_anim.json',
            'https://viktorlab.cn/akdata/resources/customdata/dps_anim.json',
            'https://arkdps.cn/resources/customdata/dps_anim.json']
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            result=list(pool.map(probe,enumerate(urls)))
        (DEST/'additional-source-probe.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False))
    elif len(sys.argv)>1:
        repo=sys.argv[1]
        info=json.loads((DEST/(repo.split('/')[-1]+'-tree.json')).read_text())
        for name in sys.argv[2:]:
            data=read('https://raw.githubusercontent.com/'+repo+'/'+info['sha']+'/'+name)
            target=DEST/repo.split('/')[-1]/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
            print(name,len(data),hashlib.sha256(data).hexdigest())
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(tree,['xulai1001/arkdps_data_collection','xulai1001/arkdps_base','Ray144165154/arkdps']))
