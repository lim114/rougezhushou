"""Rebuild documented real-domain directory from exact, public fixed sources."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
import argparse, importlib.util, json, re, sys

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-real-domain-357'


def encode(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')


class Cells(HTMLParser):
    """Visible cell text; style/script/footnote markers are not game prose."""
    VOID={'img','br','hr','input','meta','link','source','wbr','area','base','embed','param','track'}
    def __init__(self):super().__init__();self.current=None;self.rows=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if self.skip:
            if tag not in self.VOID:self.skip+=1
            return
        if tag in('style','script','sup'):self.skip=1;return
        if tag in('td','th'):self.current=[]
        if tag=='br'and self.current is not None:self.current.append('\n')
    def handle_data(self,data):
        if not self.skip and self.current is not None:self.current.append(data)
    def handle_endtag(self,tag):
        if self.skip:self.skip-=1;return
        if tag in('td','th')and self.current is not None:
            self.rows.append(re.sub(r'[ \t]+',' ',''.join(self.current)).strip());self.current=None


def extract(database,main,snapshot):
    start=database.rfind('<div class="mw-heading',0,database.index('id="实托邦·理念"'))
    end=database.rfind('<div class="mw-heading',0,database.index('id="乌托邦"'))
    section=database[start:end]
    tables=re.findall(r'<table class="wikitable fieldeff".*?</table>',section,re.S)
    if len(tables)!=14:raise ValueError('Complete10 ideology and4 policy tables required')
    weather=snapshot['modules']['weather'];by_name={}
    for group in('mainWeatherData','subWeatherData'):
        for row in weather[group].values():by_name[row['name']]=row['type']
    if len(by_name)!=14:raise ValueError('Unique exact names required')
    documented={}
    for index,table in enumerate(tables):
        parser=Cells();parser.feed(table);cells=[cell for cell in parser.rows if cell]
        headline=cells[0].splitlines();name=headline[0]
        if name not in by_name or by_name[name]in documented:raise ValueError('Full documented exact-name match required')
        idea=by_name[name].startswith('rogue_6_weather_')
        stages={}
        if idea:
            for level,label in((1,'早期 I'),(2,'中期 II'),(3,'晚期 III')):
                slot=cells.index(label);stages[str(level)]=cells[slot+1]
        notes=[line.strip()for cell in cells for line in cell.splitlines()if line.strip().startswith('※')]
        documented[by_name[name]]={'name':name,'lore':'\n'.join(headline[1:]),'notes':notes,
            'stages':stages,'function':None if idea else cells[-1],
            'source_table':index+1,'source_table_sha256':sha256(table.encode('utf8')).hexdigest(),
            'complete_table':True,'text_excludes_noncontent_style_script_and_note_markers':True}
    position=main.index('理想域：实托邦')
    mstart=main.rfind('<div class="AKCollapse-title"',0,position)
    mend=main.index('<div class="AKCollapse-title"',position)
    overview=main[mstart:mend]
    for phrase in('理念','方针','理想源','紧急作战','保密等级·6+','保密等级·12+'):
        if phrase not in overview:raise ValueError('Complete overview qualification missing:'+phrase)
    return documented,section.encode('utf8'),overview.encode('utf8'),{'database':[start,end],'main':[mstart,mend]}


def build(source_root=ROOT,artifact_root=ROOT):
    source_root,artifact_root=Path(source_root),Path(artifact_root);sys.path.insert(0,str(source_root))
    spec=importlib.util.spec_from_file_location('rouge._real_domain_builder_357',ROOT/'rouge/current_real_domain.py')
    model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    snapshot=json.loads((source_root/'research/p3-expansion-313/current-topic.json').read_bytes())
    html={};downloads={}
    for name,revision in(('database',442947),('main',442954)):
        raw=(artifact_root/PACK/(name+'-page.html')).read_bytes();download=json.loads((artifact_root/PACK/(name+'-download.json')).read_bytes())
        if download['http_status']!=200 or download['revision']!=revision or download['bytes']!=len(raw)or download['sha256']!=sha256(raw).hexdigest():raise ValueError('Actual source download differs')
        text=raw.decode('utf8')
        if re.findall(r'"wgRevisionId":(\d+)',text)!=[str(revision)]:raise ValueError('Actual page revision differs')
        html[name]=text;downloads[name]=download
    documented,section,overview,spans=extract(html['database'],html['main'],snapshot)
    rows=model.source_rows(snapshot,documented)
    from rouge import current_vine_events as vine,current_resting as resting
    providers={'vine':vine,'resting':resting};links={};details=snapshot['details']
    for key,(provider,category,identity,type_id)in model.LINKS.items():
        module=providers[provider];p=module.packet();target=module.locate(category,identity)
        if p is None or target is None:raise ValueError('Exact existing event reader required')
        original=details['choices'if category=='choices'else'choiceScenes'][identity]
        if key.startswith('red_')and'“希望的沃土”'not in original['description']:raise ValueError('Exact named future effect required')
        links[key]={'key':key,'reader':provider,'source_category':category,'source_id':identity,
            'type':type_id,'original':original,'target':target,
            'label':('呼吸的红苔：'+original['title']+'（下一地区原文）')if category=='choices'else'安眠一隅原场景（具体触发选项未知）',
            'source_identity':json.loads(json.dumps(p['source_identity'])),
            'binding_basis':'explicit_original_named_future_effect'if provider=='vine'else'community_named_event_reference_not_actual_trigger_choice',
            'actual_trigger':None,'actual_eligible':None}
    data={'schema':'current_real_domain_357_v1','game_commit':model.version.NEW_COMMIT,
          'rows':rows,'documented':documented,'links':links,
          'difficulties':{str(r['grade']):r for r in details['difficulties']if r['modeDifficulty']=='NORMAL'},
          'squads':{key:{'item':details['items'][key],'relic':details['relics'][key]}for key in model.SQUADS},
          'actual_combination':None,'actual_affected_nodes':None,'actual_eligible':None,
          'calculation_applied':False,'complete_generation_script':False,'run_updated':False}
    notes={'section':357,'candidate_only':True,'game_commit':model.version.NEW_COMMIT,
        'database_revision':442947,'overview_revision':442954,'complete_section_character_spans':spans,
        'source_game_fields':['modules.weather.mainWeatherData','modules.weather.subWeatherData','details.difficulties','details.items','details.relics','details.choices','details.choiceScenes'],
        'complete_ideology_records':30,'complete_policy_records':4,
        'new_coverage_scope':'Old future_region_effects300 already supplies3 hope phases. This group adds a complete current34-record directory, the other27 ideology records and4 policies, condition/coupling explanations and exact existing-event links. No duplicate claim for the old3.',
        'text_difference_scope':'Storage original game text names two merchants; current community explicitly adds emergency support and explains a correction. Preserve both original and documented descriptions without rewriting the game source.',
        'coupling_scope':'Hope and Gain are mutually restricted by the community document. Other arbitrary combinations are not proven. Gain documents an exception for the civilization squad immunity.',
        'phase_scope':'Pinned NORMAL2 adds natural generation,6 medium+policies,12 late+range extension. This is a documentary ordinary-generation comparison, not a claim that forced sources or preexisting states obey every natural-generation prerequisite.',
        'exact_event_scope':'Two original red-moss choices explicitly name hope in the next region. Resting is only a named community event association to the exact original entry scene; no actual triggering choice is restored.',
        'memory_tree_limit':'Existing memory-tree documentation mentions hope and beautiful new earth after recall, while the current database describes hope as only from red moss. Their precise applicability has not been resolved; do not use recall to infer current hope generation.',
        'actual_conditions':'Manual page declarations only. Mode/difficulty/layer/node coverage/enter-vs-pass/squad/paired effect are explained separately; no game capture or automatic activation.',
        'source_urls':{k:v['resolved_url']for k,v in downloads.items()},
        'unknown':['actual weather/phase/covered nodes','complete server generation/combination script',
                   'storage rounding and minimum slots','actual cold and freeze event clock',
                   'actual squad unlock/active state','exact sleeping trigger choice','random reward pool/quantity and actual receipt',
                   'current numerical modifier layers and actual combat consequences'],
        'not_performed':['game operation','live placement analysis','capture','chat','credentials','private-state read/write','calculation mutation']}
    output={model.DATA:encode(data),PACK+'/source-notes.json':encode(notes),
            PACK+'/documented-real-domain.html':section,PACK+'/documented-domain-overview.html':overview}
    names=set(output)|{PACK+'/'+n for n in('database-page.html','main-page.html','database-download.json','main-download.json')}|{
        'research/p3-expansion-313/current-topic.json','rouge/data/current-vine-events.json','rouge/data/current-resting.json',
        'research/p3-current-vine-events-333/runtime-manifest.json','research/p3-current-resting-345/runtime-manifest.json'}
    files={}
    for name in sorted(names):
        raw=output.get(name)
        if raw is None:raw=((artifact_root if name.startswith(PACK+'/')else source_root)/name).read_bytes()
        files[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    output[model.MANIFEST]=encode({'schema':'current_real_domain_357_manifest_v1','game_commit':model.version.NEW_COMMIT,'files':files})
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--source-root',type=Path,default=ROOT);p.add_argument('--output-root',type=Path,default=ROOT);a=p.parse_args();output=build(a.source_root,a.output_root)
    for name,raw in output.items():
        path=a.output_root/name
        if a.check:
            if path.read_bytes()!=raw:raise ValueError('Build differs:'+name)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    print(json.dumps({'candidate_only':True,'ideology_records':30,'policies':4,'manifest_sha256':sha256(output[PACK+'/runtime-manifest.json']).hexdigest()}))
