"""Read public aggregate counts only. No account, run, image or upload input exists."""
from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import json,re,urllib.request
SITE='https://www.lubiao.wiki'
PAGE=SITE+'/tools/blackstream-route'
LABELS={'combat':'作战','emergency-combat':'紧急作战','danger-enemy':'险路恶敌','rogue-trader':'诡意行商','secret-trader':'秘境行商','encounter':'不期而遇','wish':'得偿所愿','settlement':'“居民”据点','forest-clearing':'林间空地','empty':'林间空地','start':'起点','end':'险路尽头','safe-house':'安全的角落','recruit':'应急助力','duel':'狭路相逢','safe-corner':'安全的角落','gain-loss':'失与得','first-step':'先行一步','narrow-meet':'狭路相逢','emergency-aid':'应急助力','fate-choice':'命运所指','danger-end':'险路尽头','danger-path':'险路小径','overlook':'羽瞰点','winding-path':'曲折密道','wrong-turn':'误入奇境','resident-mark':'居民标记'}
DEFAULT=Path(__file__).resolve().parents[1]/'research/public-statistics-388/nodes.json'

def _object(text,start):
    depth=0;quote=None;escaped=False
    for i in range(start,min(len(text),start+500000)):
        char=text[i]
        if quote:
            if escaped:escaped=False
            elif char=='\\':escaped=True
            elif char==quote:quote=None
        elif char in ('"',"'",'`'):quote=char
        elif char=='{':depth+=1
        elif char=='}':
            depth-=1
            if depth==0:return text[start:i+1],i+1
    raise ValueError('公开统计格式已变化，不能读取旧结构。')

def _literal(text):
    # A restricted data conversion, never JS evaluation or execution.
    text=re.sub(r'`([^`$\\]*)`',lambda m:json.dumps(m[1]),text)
    text=re.sub(r'([{,]\s*)([A-Za-z_$][A-Za-z0-9_$]*|[0-9]+)\s*:',lambda m:m[1]+json.dumps(m[2])+':',text)
    def pairs(items):
        out={}
        for key,value in items:
            if key in out:raise ValueError('统计包含重复项。')
            out[key]=value
        return out
    return json.loads(text,object_pairs_hook=pairs)

def parse_counts(script,source_url):
    marker='sourceSchemaVersion:`merged-node-distance@1`';pos=script.find(marker)
    if pos<0 or script.find(marker,pos+1)>=0:raise ValueError('未找到唯一的已支持统计口径。')
    start=script.rfind('{',0,pos);raw,end=_object(script,start);meta=_literal(raw)
    match=re.match(r',\s*[A-Za-z_$][A-Za-z0-9_$]*=',script[end:])
    if not match:raise ValueError('统计表入口已变化。')
    raw,_=_object(script,end+match.end());counts=_literal(raw)
    result={'schema':'rouge-public-node-frequency-v1','provider':'路标档案馆','source_url':PAGE,
        'dataset_url':source_url,'retrieved_at':datetime.now(timezone.utc).isoformat(),
        'source_sha256':sha256(script.encode()).hexdigest(),'metadata':meta,'counts':counts,
        'scope':'历史主地图节点与距入口步数的联合计数；不是当前地图完整条件下的后验概率。'}
    validate(result);return result

def validate(data):
    if data.get('schema')!='rouge-public-node-frequency-v1':raise ValueError('不支持的统计文件。')
    meta=data['metadata'];counts=data['counts']
    if meta.get('sourceSchemaVersion')!='merged-node-distance@1' or not isinstance(meta.get('updatedAt'),str):raise ValueError('统计口径未确认。')
    datetime.fromisoformat(meta['updatedAt'].replace('Z','+00:00'))
    if not isinstance(counts,dict)or not 1<=len(counts)<=80:raise ValueError('统计类别数量异常。')
    for name,floors in counts.items():
        if not isinstance(name,str)or not isinstance(floors,dict):raise ValueError('统计类别异常。')
        for floor,buckets in floors.items():
            if floor not in ('0','1','2','3','4','remembrance')or not isinstance(buckets,dict):raise ValueError('楼层口径异常。')
            for distance,count in buckets.items():
                if not distance.isdigit()or not 0<=int(distance)<=100 or type(count)is not int or not 0<=count<=100000000:raise ValueError('统计计数异常。')
    total=sum(n for key,floors in counts.items()if key!='start'for buckets in floors.values()for n in buckets.values())
    if type(meta.get('sampleCount'))is not int or total!=meta['sampleCount']:raise ValueError('统计总计与分项不一致。')
    return data

def fetch():
    def get(url):
        if not url.startswith(SITE+'/' )or not(url==SITE+'/'or re.fullmatch(re.escape(SITE)+r'/_nuxt/[A-Za-z0-9_.-]+\.js',url)):raise ValueError('统计地址不在公开读取范围内。')
        request=urllib.request.Request(url,headers={'User-Agent':'rougezhushou-public-statistics/1.0','Accept':'text/html,application/javascript'})
        with urllib.request.urlopen(request,timeout=15)as response:
            if not response.geturl().startswith(SITE+'/'):raise ValueError('统计转向了其他站点。')
            raw=response.read(3000001)
        if len(raw)>3000000:raise ValueError('统计文件过大。')
        return raw.decode('utf8')
    home=get(SITE+'/');entry=re.search(r'<script[^>]+src="(/_nuxt/[A-Za-z0-9_.-]+\.js)"',home)
    if not entry:raise ValueError('公开统计网页入口已变化。')
    source=get(SITE+entry[1]);route=re.search(r'name:`tools-blackstream-route`.*?import\(`\./([A-Za-z0-9_.-]+\.js)`',source)
    if not route:raise ValueError('公开节点统计入口已变化。')
    url=SITE+'/_nuxt/'+route[1];return parse_counts(get(url),url)

def load(path=DEFAULT):return validate(json.loads(Path(path).read_text('utf8')))

def frequency_rows(data,floor,distance):
    validate(data)
    if floor not in ('0','1','2','3','4','remembrance')or type(distance)is not int or not 0<=distance<=100:raise ValueError('请选择资料覆盖的楼层和距入口步数。')
    values=[(name,buckets.get(floor,{}).get(str(distance),0))for name,buckets in data['counts'].items()]
    total=sum(n for _,n in values)
    if not total:return []
    # Denominator is all observed node types at this floor/distance, not maps or all distances.
    return [{'type':key,'name':LABELS.get(key,key),'count':n,'total':total,'frequency':n/total}for key,n in values if n>0]
