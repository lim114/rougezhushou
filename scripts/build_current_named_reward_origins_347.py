"""Build new acquisition entry links from pinned readers, not inferred reward pools."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge import current_named_reward_origins as model
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def build():
    mods=model.providers();packets={k:v.packet()for k,v in mods.items()}
    if any(v is None for v in packets.values()):raise ValueError('All pinned readers required')
    current=model.version.packet();rows=model.source_rows(packets,current['current']['details'],mods)
    notes={'section':347,'source_method':'Reuse complete frozen current327/328/324/343/344/345/346 readers and their original records.11 newly linked named choices only; old338 six choices/three items retained separately.','new_HTML_or_image_download':False,'complete_acquisition_pool':False,'actual_server_or_game_verified':False,'excluded_roles':['持有或交付/消耗物品','只有物品提示图标','随机或未具名收藏品','仅解锁或已返回/胜利的条件','把同物品两份现有阅读器计两次取得'],'missing_pointer':'源私钥：名称全文唯一对应，缺原itemId仍明确保留','name_spelling':'剑锤/翱翼/虬蜕只存在外层中文引号差异，必须同时核对原项明确指针和完整名称，不按序号或模糊匹配','fresh_web_crosschecks':[{'url':'https://prts.wiki/w/剑锤','establishes':'剑锤条目取得方式为血衣之下割下怪花，与固定原件一致；不新增算法。'},{'url':'https://prts.wiki/w/沉沦者的黑流树海/引擎配件目录','establishes':'笼控器两个取得选项属旧338已覆盖，本节不重复计新增。'}],'providers':{k:{'manifest':v.MANIFEST,'manifest_sha256':v.MANIFEST_SHA256}for k,v in mods.items()}}
    out={model.DATA:enc({'schema':'current_named_rewards_347_v1','game_commit':model.version.NEW_COMMIT,'rows':rows,'complete_acquisition_pool':False}),model.PACK+'/source-notes.json':enc(notes)}
    names=set(out)|{v.DATA for v in mods.values()}|{v.MANIFEST for v in mods.values()};files={}
    for n in sorted(names):
        raw=out[n]if n in out else(ROOT/n).read_bytes();files[n]={'bytes':len(raw),'sha256':sha256(raw).hexdigest()}
    out[model.MANIFEST]=enc({'schema':'current_named_rewards_347_manifest_v1','game_commit':model.version.NEW_COMMIT,'files':files});return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();out=build()
    for n,b in out.items():
        f=ROOT/n
        if a.check:
            if f.read_bytes()!=b:raise ValueError('Build differs:'+n)
        else:f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
    h=sha256(out[model.MANIFEST]).hexdigest()
    if a.check and h!=model.MANIFEST_SHA256:raise ValueError('Runtime binding differs')
    print(json.dumps({'new_rows':11,'new_items':11,'providers':7,'manifest_sha256':h}))
