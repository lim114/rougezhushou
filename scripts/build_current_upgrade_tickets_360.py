"""Rebuild a public exact upgrade-voucher directory. No game or run-state access."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
import argparse
import importlib.util
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-upgrade-tickets-360'


def encode(value): return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf8')


class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skipping=0
    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'): self.skipping += 1
        if tag in ('p', 'br', 'li', 'dd', 'dt', 'h4'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('style', 'script'): self.skipping -= 1
        if tag in ('p', 'li', 'dd', 'dt', 'h4'): self.parts.append('\n')
    def handle_data(self, text):
        if not self.skipping: self.parts.append(text)
    def text(self): return '\n'.join(line.strip() for line in ''.join(self.parts).splitlines() if line.strip())


def source_sections(html):
    general, tools = html['general'], html['tools']
    start = general.rfind('<div class="mw-heading', 0, general.index('id="3._招募干员"'))
    end = general.rfind('<div class="mw-heading', 0, general.index('id="4._行动奖励"'))
    section = general[start:end]
    parser=Text(); parser.feed(section); visible=parser.text()
    required=('首次招募时','再次招募同一干员','进阶只是解除了能力限制','不会因为进阶使得能力超过普通游戏时的状态',
              '随机直升','阿米娅','临时招募','助战招募')
    if any(term not in visible for term in required): raise ValueError('Complete recruitment qualification required')
    tstart=tools.rfind('<div class="mw-heading',0,tools.index('id="#1初始道具"'))
    # Keep the entire initial-tools group, not only two isolated matching cells.
    tend=tools.rfind('<div class="mw-heading',0,tools.index('id="#2扩展道具"'))
    tool_section=tools[tstart:tend]
    pt=Text(); pt.feed(tool_section); vt=pt.text()
    for term in ('高级物资配给券','临时物资配给券','进阶一个任意干员（不消耗希望）','进阶任意一个5星及以下的干员（不消耗希望）'):
        if term not in vt: raise ValueError('Both complete source item usages required:'+term)
    return section.encode('utf8'), tool_section.encode('utf8'), visible, vt, {'general':[start,end],'tools':[tstart,tend]}


def build(source_root=ROOT, artifact_root=ROOT):
    source_root,artifact_root=Path(source_root),Path(artifact_root); sys.path.insert(0,str(source_root))
    spec=importlib.util.spec_from_file_location('rouge._upgrade_builder_360',ROOT/'rouge/current_upgrade_tickets.py')
    model=importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
    snapshot=json.loads((source_root/'research/p3-expansion-313/current-topic.json').read_bytes())
    html={}; downloads={}
    for key,revision in (('general',440806),('tools',355079)):
        raw=(artifact_root/PACK/(key+'-w-page.html')).read_bytes()
        record=json.loads((artifact_root/PACK/(key+'-w-download.json')).read_bytes())
        text=raw.decode('utf8')
        if record['http_status']!=200 or record['bytes']!=len(raw) or record['sha256']!=sha256(raw).hexdigest() or record['revision']!=revision:
            raise ValueError('Actual successful download required')
        if re.findall(r'"wgRevisionId":(\d+)',text)!=[str(revision)] or record['resolved_url'].startswith('https://sisyphus.'):
            raise ValueError('Challenge responses are not source evidence')
        html[key]=text; downloads[key]=record
    section,tools,documented,documented_tools,spans=source_sections(html)
    from rouge import current_rest_travel as rest
    p=rest.packet(); target=rest.locate('choices',model.REST_CHOICE)
    choice=snapshot['details']['choices'][model.REST_CHOICE]
    if p is None or target is None or choice['displayData']['itemId']!='rogue_6_upgrade_ticket_all' or choice['description']!='获得高级物资配给券':
        raise ValueError('Exact named item and existing original reader required')
    data={'schema':'current_upgrade_tickets_360_v1','game_commit':model.version.NEW_COMMIT,
          'rows':model.source_rows(snapshot['details']),
          'rest_source':{'choice':choice,'target':target,'source_identity':json.loads(json.dumps(p['source_identity'])),
                         'original_quantity':None,'actual_obtained':None},
          'documented_recruitment':documented,'documented_tools':documented_tools,
          'community_revisions':{'general':440806,'tools':355079},
          'complete_acquisition_pool':False,'actual_owned':None,'actual_candidates':None,
          'actual_upgraded':None,'actual_cultivation':None,'run_updated':False,'calculation_applied':False}
    notes={'section':360,'preparation_only':True,'game_commit':model.version.NEW_COMMIT,
           'source_fields':['details.upgradeTickets','details.items','details.relics','details.choices'],
           'source_record_count':18,'explicit_relic_source_bindings':8,'exact_event_source_count':1,
           'documented_source_downloads':downloads,'complete_html_section_character_spans':spans,
           'existing_scope_reused':{'063':'Recipient-negative invalidation already models old7 assignment lifecycles; no new recipient or calculation claim.',
                                   '331':'Already shows advanced supply voucher usage. Reuse exact event reader; new entry provides complete18 ranges and reverse exact-source lookup.',
                                   '354':'47 explicit recruitment/stashed pairs cover94 recruitTickets only; no upgradeTickets. Link existing ordinary directory, do not recreate stashing.'},
           'binding_scope':'Eight sources are derived from immediate_reward exact id+count blackboard, not ID suffixes or matching names. Each full parent item/relic and ticket/item is retained.',
           'range_limit':'Named professionList/rarityList establish voucher coverage only. Do not decode numeric masks or establish actual upgradability from listed stars.',
           'count_limit':'Eight relic reward records explicitly say1. Safety-corner choice does not give a quantity; never borrow that1.',
           'terminology_scope':'General PRTS recruitment section440806 explains normal first-recruit cap, promotion and first-recruit upgraded states with temporary/assist/Amiya exceptions. Full section retained; this is documentation, not game execution.',
           'failed_attempts':'Initial fixed-index requests returned HTTP200 challenge pages with no revision. Retained separately as failed attempts; excluded from source manifest.',
           'unknown':['actual inventory','actual candidates and complete eligibility','actual recipient','actual upgrade/cultivation',
                      'complete acquisition pool','server menu eligibility','ordinary voucher concrete origins','whether upgrade vouchers can be stashed'],
           'not_performed':['game operation','capture','chat','private-state read/write','formal tests','native GUI validation'],
           'licensing':'Full PRTS public source and attribution retained; community prose follows source-site CC BY-NC-SA terms and game assets/text retain their rightsholders.'}
    output={model.DATA:encode(data),PACK+'/source-notes.json':encode(notes),
            PACK+'/documented-recruitment.html':section,PACK+'/documented-tools.html':tools}
    names={model.DATA,PACK+'/source-notes.json',PACK+'/general-w-page.html',PACK+'/general-w-download.json',
           PACK+'/tools-w-page.html',PACK+'/tools-w-download.json',PACK+'/documented-recruitment.html',
           PACK+'/documented-tools.html','research/p3-expansion-313/current-topic.json',
           'rouge/data/current-rest-travel.json','research/p3-current-rest-travel-331/runtime-manifest.json'}
    files={}
    for name in sorted(names):
        raw=output.get(name)
        if raw is None: raw=((artifact_root if name.startswith(PACK+'/') else source_root)/name).read_bytes()
        files[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    output[model.MANIFEST]=encode({'schema':'current_upgrade_tickets_360_manifest_v1','game_commit':model.version.NEW_COMMIT,'files':files})
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true')
    p.add_argument('--source-root',type=Path,default=ROOT); p.add_argument('--output-root',type=Path,default=ROOT)
    args=p.parse_args(); output=build(args.source_root,args.output_root)
    for name,raw in output.items():
        path=args.output_root/name
        if args.check:
            if path.read_bytes()!=raw: raise ValueError('Build differs:'+name)
        else: path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
    print(json.dumps({'prepared_only':True,'upgrade_records':18,'explicit_relic_sources':8,
                      'manifest_sha256':sha256(output[PACK+'/runtime-manifest.json']).hexdigest()}))
