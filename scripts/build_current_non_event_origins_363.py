"""Build ten exact named non-event source links, with explicit timing boundaries."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
import argparse,importlib.util,json,re,sys

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-non-event-origins-363'
MAIN='research/p3-current-recruit-tickets-354/topic-page.html'
DOWNLOAD='research/p3-current-recruit-tickets-354/source-download.json'


def encode(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')


class Visible(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in('style','script'):self.skip+=1
        if tag in('br','td','th','li','p'):self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in('style','script'):self.skip-=1
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)
    def text(self):return ' '.join(''.join(self.parts).split())


def documented_rows(html,rows,observations):
    originals=[]
    for match in re.finditer(r'<tr\b[^>]*>.*?</tr>',html,re.S):
        visible=Visible();visible.feed(match[0]);originals.append((visible.text(),match[0],match.start(),match.end()))
    result={}
    for row in rows:
        source_id=row['source_id']
        if row['kind']=='squad':
            candidates=[r for r in originals if re.sub(r'^NEW\s+','',r[0]).startswith(row['source_name']+' ')]
            if len(candidates)!=1:raise ValueError('One complete named squad row required:'+source_id)
            text,raw,start,end=candidates[0]
            name=row['item_name'].strip('“”')
            if name not in text or '初始携带' not in text:raise ValueError('Named initial-carry documentation required')
            result[source_id]={'source_kind':'complete_current_topic_squad_row','revision':442954,
                               'visible_text':text,'full_html':raw,'html_character_span':[start,end],
                               'timing':'initial','timing_basis':'explicit_initial_carry_in_same_named_squad_row_not_blackboard_key',
                               'item_name_comparison':'full_literal_name_only_outer_curly_quotes_removed',
                               'original_usage_also_explicit':name in row['source_item']['usage']and'初始携带'in row['source_item']['usage'],
                               'actual_execution':None}
        else:
            name=row['source_name'];page=next(v for v in observations['pages']if v['name']==name)
            result[source_id]={'source_kind':'fixed_game_item_usage_with_actual_web_observation',
                               'url':page['url'],'revision':page['revision'],
                               'visible_text':row['source_item']['usage'],'timing':'unspecified',
                               'timing_basis':'Current_topic_callback_timing_not_proven; old_Mizuki_note_not_transferred',
                               'full_original_page_html_archived':False,'actual_execution':None}
    return result


def build(source_root=ROOT,artifact_root=ROOT):
    source_root,artifact_root=Path(source_root),Path(artifact_root);sys.path.insert(0,str(source_root))
    spec=importlib.util.spec_from_file_location('rouge._non_event_builder_363',ROOT/'rouge/current_non_event_origins.py')
    model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    current=json.loads((source_root/'research/p3-expansion-313/current-topic.json').read_bytes())['details']
    page=(source_root/MAIN).read_bytes();download=json.loads((source_root/DOWNLOAD).read_bytes())
    if download['http_status']!=200 or len(page)!=download['bytes']or sha256(page).hexdigest()!=download['sha256']:
        raise ValueError('Actual complete354 download required')
    html=page.decode('utf8')
    if re.findall(r'"wgRevisionId":(\d+)',html)!=['442954']:raise ValueError('Pinned source revision differs')
    observations=json.loads((artifact_root/PACK/'web-observations.json').read_bytes())
    if observations['full_original_html_archived']is not False or observations['current_topic_timing_proven']is not False:
        raise ValueError('Do not promote rendered excerpts or old-theme timing into current original proof')
    from rouge import current_recruit_tickets as recruits
    recruit_packet=recruits.packet()
    if recruit_packet is None:raise ValueError('Existing354 exact recruitment reader required')
    rows=model.source_rows(current);documents=documented_rows(html,rows,observations)
    for row in rows:
        if row['item_category']=='recruit_tickets':
            ref=recruits.reference(row['item_id'])
            if ref is None or ref['selected']['original_item']!=row['item']:raise ValueError('Exact existing voucher required')
    data={'schema':'current_non_event_origins_363_v1','game_commit':model.version.NEW_COMMIT,
          'rows':rows,'documents':documents,
          'recruit_source_identity':json.loads(json.dumps(recruit_packet['source_identity'])),
          'complete_acquisition_pool':False,'actual_eligible':None,'actual_source_active':None,
          'actual_quantity':None,'actual_received':None,'actual_candidate':None,
          'actual_cultivation':None,'actual_cost':None,'run_updated':False,'calculation_applied':False}
    notes={'section':363,'preparation_only':True,'game_commit':model.version.NEW_COMMIT,
           'source_fields':['details.items','details.relics','details.bandRef','details.init','details.recruitTickets'],
           'new_scope':'Ten exact non-event reverse source entries: eight named squad grants and two recruitment-voucher grants. Does not rediscover source mechanisms or replace event-origin coverage.',
           'excluded_existing_scopes':['360 eight new-training upgrade tickets','361 cross-run startup assistance','338/347/349 seventeen event reward items','354 existing47 recruitment/stashing pairs'],
           'primary_pointer_scope':'Exactly one named-item immediate_reward per selected source; preserve full parent item/effect, index and blackboard. Resource and unexpanded pool entries excluded.',
           'timing_scope':'Eight squad timing claims are supported by complete named squad rows in actual PRTS442954 HTML. The key immediate_reward alone is not used as proof of real callback timing.',
           'source_difference':'Geological-survey item usage lacks initial-carry wording; current full community squad row explicitly names its initial notebook. Both are retained separately.',
           'literal_name_scope':'Time-of-end item has literal outer curly quotes in its item name, while the squad source uses decorative brackets. Strip only outer curly quotes for this full-name comparison; full original item/name preserved, no approximate title matching.',
           'squad_text_difference':'Current community squad rows also contain effects/notes beyond this frozen game usage. Only exact named initial-carry clauses corroborate this feature; other changed effects are not merged into calculations.',
           'relic_timing':'Both current-topic item usages establish random upgraded temporary recruitment but no callback timestamp. Silver item obtain-time note is located under the old Mizuki theme; do not transfer it to the current black-flow topic.',
           'counts':'All nine other records count1; multilateral-trade strengthened band27 count3 initially. Separate per-shop count1 and other random-pool entries are not added.',
           'initial_range_scope':'Exact initialBandRelic membership is retained per mode/grade/predefined identity. It is source configuration inclusion, not account unlock, selected active variant or full server eligibility.',
           'failed_original_item_downloads':'Two actual urllib TLS EOF failures retained. Web tool excerpts have no inferred HTTP status or original HTML byte claim.',
           'unknown':['actual source activation','account unlock and technology','actual inventory and receipt','current-topic relic grant callbacks',
                      'random operator identity/cultivation','complete acquisition pools','live server eligibility'],
           'not_performed':['formal tests','Qt/native UI','game operation','capture','chat','private-state read/write'],
           'licensing':'Full PRTS source attribution retained; community prose under source-site CC BY-NC-SA and original game material under rightsholder copyright.'}
    output={model.DATA:encode(data),PACK+'/documented-source-rows.json':encode(documents),PACK+'/source-notes.json':encode(notes)}
    names={model.DATA,PACK+'/source-notes.json',PACK+'/documented-source-rows.json',
           PACK+'/web-observations.json',PACK+'/failed-downloads.json',MAIN,DOWNLOAD,
           'research/p3-expansion-313/current-topic.json','rouge/data/current-recruit-tickets.json',
           'research/p3-current-recruit-tickets-354/runtime-manifest.json'}
    files={}
    for name in sorted(names):
        raw=output.get(name)
        if raw is None:raw=((artifact_root if name.startswith(PACK+'/')else source_root)/name).read_bytes()
        files[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    output[model.MANIFEST]=encode({'schema':'current_non_event_origins_363_manifest_v1','game_commit':model.version.NEW_COMMIT,'files':files})
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--source-root',type=Path,default=ROOT);p.add_argument('--output-root',type=Path,default=ROOT)
    args=p.parse_args();output=build(args.source_root,args.output_root)
    for name,raw in output.items():
        target=args.output_root/name
        if args.check:
            if target.read_bytes()!=raw:raise ValueError('Build differs:'+name)
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    print(json.dumps({'prepared_only':True,'rows':10,'timing_documented_initial':8,'timing_unknown':2,
                      'manifest_sha256':sha256(output[PACK+'/runtime-manifest.json']).hexdigest()}))
