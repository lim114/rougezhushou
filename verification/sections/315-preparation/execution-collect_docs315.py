from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
from html import unescape
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json,re,urllib.request,urllib.parse
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.cache/p3-current-rewards-315';OUT.mkdir(exist_ok=True)
NAMES={'enemy_2001_duckmi':'鸭爵','enemy_2002_bearmi':'高普尼克','enemy_2034_sythef':'流泪小子','enemy_2085_skzjxd':'圆仔','enemy_2125_dylnpp':'小八界','enemy_2152_shezlc':'恶笼草'}
class Text(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in('script','style'):self.skip+=1
 def handle_endtag(self,tag):
  if tag in('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,data):
  if not self.skip:self.rows.append(data)
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def fetch(pair):
 key,name=pair;url='https://m.prts.wiki/w/'+urllib.parse.quote(name);attempts=[]
 for attempt in range(1,4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 rougezhushou-readonly-reward-documentation'}),timeout=30)as r:assert r.status==200;raw=r.read()
   html=raw.decode('utf8');parser=Text();parser.feed(html);flat=re.sub(r'\s+','',''.join(parser.rows));rev=re.search(r'wgRevisionId["\s:]+(\d+)',html);assert rev,'Revision missing'
   # Only the short documented reward condition is extracted; no timing inferred.
   matches=list(re.finditer(r'级别([012])',flat));grades={}
   for pos,m in enumerate(matches):
    end=matches[pos+1].start()if pos+1<len(matches)else len(flat);part=flat[m.end():end]
    target='被击倒时战斗结束后额外获得10源石锭；到达路径终点时战斗结束后扣除10源石锭'if key=='enemy_2152_shezlc'else'被击倒后，在战斗结算时掉落1件收藏品'
    if target in part:grades[m[1]]={'quote':target,'quantity':10 if key=='enemy_2152_shezlc'else 1,'resource':'gold'if key=='enemy_2152_shezlc'else'random_relic'}
   (OUT/(key+'.html')).write_bytes(raw);attempts.append({'attempt':attempt,'HTTP_success':True,'grades_extracted':sorted(grades)})
   return key,{'name':name,'url':url,'revision':rev[1],'fixed_url':'https://prts.wiki/index.php?title='+urllib.parse.quote(name)+'&oldid='+rev[1],'download_sha256':sha256(raw).hexdigest(),'download_bytes':len(raw),'grades':grades,'all_three_grades_verified':set(grades)=={'0','1','2'},'attempts':attempts,'entire_html_publicly_archived':False,'actual_current_server_verified':False},None
  except Exception as e:attempts.append({'attempt':attempt,'HTTP_success':False,'error':type(e).__name__+': '+str(e)})
 return key,None,{'name':name,'url':url,'attempts':attempts,'deferred':True}
records={};failures={}
with ThreadPoolExecutor(max_workers=3)as pool:
 for key,record,error in pool.map(fetch,NAMES.items()):
  if error:failures[key]=error
  else:records[key]=record
out={'observedUTC':datetime.now(timezone.utc).isoformat(),'source_type':'PRTS community mechanics, not an official game API','license':'PRTS CC BY-NC-SA 4.0; game text Hypergryph copyright','records':records,'failures':failures,'source_only_not_actual_game_reward':True};(OUT/'documented-rewards.json').write_bytes(enc(out));print(json.dumps({'records':{k:{'revision':v['revision'],'grades':list(v['grades'])}for k,v in records.items()},'failures':failures},ensure_ascii=False),flush=True)
