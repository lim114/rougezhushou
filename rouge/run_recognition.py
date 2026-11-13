"""Evidence from held-item bars and recruited-operator pages, never reward offers."""
import re
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np
from .catalog import catalog,operator_profiles,tactical_tools
from .operator_recognition import center,identity_index,normalized_name
from .relic_recognition import match_held_icons,resolve_owned_icons,resolve_difficulty_icons
from .elite_recognition import card_elite
from .recruitment_recognition import recruitment_marker,promotion_marker
from .resource_recognition import read_resources
from .run_config import read_config
from .anchors import units
from .held_cards import read_held_cards,held_card_regions
from .counter_badges import read_counter_badges
from .local_counters import read_local_counter_badges
from .recipient_recognition import read_recipient_buffs,read_owned_popup_member,reconfirm_owned_popup_footer
from .relic_counter_semantics import counter_resources
from .operator_name_recheck import recheck_run_names

@lru_cache(maxsize=1)
def zero_reference():
    return cv2.imdecode(np.fromfile(Path(__file__).with_name('data')/'ui-icons/collection-counter-zero.png',dtype=np.uint8),0)>0

def _isolated_zero(crop,anchor_height):
    """Return the unique matching glyph from these pixels, including the check for a leading 1 in 10."""
    gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
    mask=cv2.threshold(gray,205,255,cv2.THRESH_BINARY)[1]
    _,labels,stats,_=cv2.connectedComponentsWithStats(mask)
    significant=[(i,s) for i,s in enumerate(stats[1:],1) if .4*anchor_height<=s[3]<=1.5*anchor_height
                 and s[4]>=20]
    if len(significant)!=1:return None
    i,(x,y,w,h,_)=significant[0]
    if not .55<=w/h<=1.05 or x<=0 or y<=0 or x+w>=crop.shape[1] or y+h>=crop.shape[0]:return None
    glyph=(labels[y:y+h,x:x+w]==i).astype(np.uint8)
    _,hierarchy=cv2.findContours(glyph,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None or sum(c[3]>=0 for c in hierarchy[0])!=1:return None
    ref=cv2.resize(zero_reference().astype(np.uint8),(w,h),interpolation=cv2.INTER_NEAREST)
    # One-pixel tolerance handles antialiasing after continuous resize.
    kernel=np.ones((3,3),np.uint8)
    score=(np.count_nonzero(glyph&cv2.dilate(ref,kernel))+
           np.count_nonzero(ref&cv2.dilate(glyph,kernel)))/(np.count_nonzero(glyph)+np.count_nonzero(ref))
    return glyph*255 if score>=.99 else None


def _read_zero(glyph,engine,*,recognizer_only):
    if glyph is None:return False
    # Detection used to locate this isolated shape again. A tight line image
    # with a small blank margin is what the recognizer expects; a large square
    # border can change its output from 0 to a letter even at high confidence.
    margin=max(2,round(glyph.shape[0]*.2)) if recognizer_only else max(4,round(glyph.shape[0]*.8))
    padded=cv2.copyMakeBorder(glyph,margin,margin,margin,margin,cv2.BORDER_CONSTANT,value=0)
    if recognizer_only:
        raw,_=engine(padded,use_det=False,use_cls=False)
        return len(raw or [])==1 and raw[0][0]=='0' and raw[0][1]>=.5
    raw,_=engine(cv2.resize(padded,None,fx=4,fy=4),use_cls=False)
    return len(raw or [])==1 and raw[0][1]=='0' and raw[0][2]>=.5


def near_number(image,texts,anchor,engine,*,side='above'):
    x,y=center(anchor);ux,uy=units(image,anchor,38.3 if anchor['text']=='收藏品' else 35.2)
    text_values=set()
    for record in texts:
        if record['confidence']>=.9 and re.fullmatch(r'\d{1,3}',record['text']):
            tx,ty=center(record)
            dx,dy=tx-x,ty-y
            nearby=(abs(dx)<.035*ux and -.065*uy<dy<-.012*uy if side=='above'
                    else .02*ux<dx<.09*ux and abs(dy)<.045*uy)
            if nearby:text_values.add(int(record['text']))
    if len(text_values)==1:return next(iter(text_values))
    h,w=image.shape[:2]
    bounds=(x-.035*ux,y-.065*uy,x+.035*ux,y-.012*uy) if side=='above' else (x+.025*ux,y-.04*uy,x+.074*ux,y+.015*uy)
    x0,y0,x1,y1=bounds
    x0=max(0,int(x0*w));x1=min(w,int(x1*w));y0=max(0,int(y0*h));y1=min(h,int(y1*h))
    crop=image[y0:y1,x0:x1]
    if not crop.size:return None
    if side=='above':
        height=(max(p[1] for p in anchor['box'])-min(p[1] for p in anchor['box']))*h
        if not text_values:
            glyph=_isolated_zero(crop,height)
            if _read_zero(glyph,engine,recognizer_only=True):return 0
    # Numeric controls are upright relative to their observed label. Applying
    # the generic orientation classifier can rotate a real 6 into a confident 9.
    for normalize in (False,True):
        digits=crop
        if normalize:
            gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
            digits=cv2.normalize(gray,None,0,255,cv2.NORM_MINMAX)
        raw,_=engine(cv2.resize(digits,None,fx=4,fy=4),use_cls=False)
        readings={int(text) for _,text,score in raw or [] if score>=.9 and re.fullmatch(r'\d{1,3}',text)}
        if readings:return next(iter(readings)) if len(readings)==1 else None
    if side=='above':
        # Conflicting initial text skips the fast zero pass. Check its pixels here instead.
        if text_values:glyph=_isolated_zero(crop,height)
        if _read_zero(glyph,engine,recognizer_only=False):return 0
    return None


def read_run(image,texts,engine,*,icon_cache=None,run_context=None,on_hud=None,on_map_gold=None,native_content=None,on_map_config=None):
    texts=recheck_run_names(image,texts,engine)
    texts=reconfirm_owned_popup_footer(image,texts,engine)
    anchors={t['text']:t for t in texts if t['confidence']>=.9}
    held=anchors.get('收藏品') or min((t for t in texts if t['text']=='收起' and t['confidence']>=.9),key=lambda t:center(t)[0],default=None)
    if not held:return None
    cards=read_owned_cards(texts,held) if held['text']=='收起' else []
    if cards and '零件箱' not in anchors:
        from .held_footer import reconfirm_held_footer
        verified,_=reconfirm_held_footer(image,texts,held,cards,engine)
        if verified:
            texts=[verified if t['text']=='零件箱' else t for t in texts]
            anchors['零件箱']=verified
    is_map=(all(name in anchors for name in ('目标生命值','指挥等级','零件箱'))
            or expanded_held_page(anchors,held,cards))
    normal_roster='技能' in anchors and '分支+' in anchors and '收起' in anchors
    # Multiple owned-buff rows can cover both cultivation tabs. The popup
    # context independently proves only its current owner; it cannot supply
    # cultivation values from the obscured panel or from a previous frame.
    popup_member=read_owned_popup_member(image,texts) if not normal_roster else None
    is_roster=normal_roster or popup_member is not None
    if not (is_map or is_roster):return None
    if not is_map:cards=[]
    from .run_config import confirmed_config
    known=confirmed_config(run_context)
    fresh=None
    if on_map_config is not None and is_map and not is_roster:
        fresh=read_config(image,texts,held,engine=engine,known_config=known)
        on_map_config({**known,**fresh})
    resources = None
    if is_map and on_hud is not None:
        def publish_gold(gold):
            on_hud({'gold': gold})
            if on_map_gold is not None and not is_roster:
                on_map_gold(gold)
        resources = read_resources(image, texts, engine, on_gold=publish_gold, native_content=native_content)
        # Parts and held-card counters still require the inventory cross-check below.
        from .relic_counter_semantics import HUD_RESOURCE_LABELS
        hud = {key: value for key, value in resources.items() if key in HUD_RESOURCE_LABELS or key == 'gold'}
        if any(key in HUD_RESOURCE_LABELS for key in hud):
            on_hud(hud)
    count=near_number(image,texts,held,engine) if held['text']=='收藏品' else None
    crew = anchors.get('干员')
    if is_roster:
        held_x = center(held)[0]
        crew = next((t for t in texts if t['text']=='收起' and t['confidence']>=.9
                     and center(t)[0]>held_x), crew)
    crew_count=near_number(image,texts,crew,engine,side='right') if crew else None
    ids, tool_ids = set(), set()
    for card in cards:
        if card['confirmed']:
            (tool_ids if card['id'] in tactical_tools() else ids).add(card['id'])
    if fresh is None:fresh=read_config(image,texts,held,engine=engine,known_config=known) if is_map else {}
    config={**known,**fresh}
    icons=resolve_difficulty_icons(resolve_owned_icons(match_held_icons(image,held,count,cache=icon_cache),cards),config.get('difficulty'))
    if count==0 and icons:count=None
    icon_ids = {icon['id'] for icon in icons if icon['confirmed']}
    if icon_ids:
        relics = catalog()['relics']
        tools = tactical_tools()
        ids.update(rid for rid in icon_ids if rid in relics)
        tool_ids.update(rid for rid in icon_ids if rid in tools)
    members=read_roster(image,texts,engine) if normal_roster else []
    selected=read_selected_member(image,texts,engine) if normal_roster else popup_member
    recipient_buffs=read_recipient_buffs(image,texts,selected,engine=engine) if selected else None
    if recipient_buffs:
        selected={**selected,'char_buff_ids':recipient_buffs['ids'],
            'char_buffs_complete':recipient_buffs['complete'],
            'recipient_buffs':recipient_buffs,
            'sources':{**selected.get('sources',{}),
                'char_buff_ids':{'source':recipient_buffs['source'],
                    'complete':recipient_buffs['complete'],'issues':recipient_buffs['issues']}}}
    if selected:
        previous=next((m for m in members if m['id']==selected['id']),{})
        members=[m for m in members if m['id']!=selected['id']]+[{**previous,**selected,
            'skill_ranks':{**previous.get('skill_ranks',{}),**selected.get('skill_ranks',{})},
            'sources':{**previous.get('sources',{}),**selected.get('sources',{})}}]
    for member in members:
        if member['fields'].get('elite')==2 and member.get('card_position'):
            ranks=read_card_masteries(image,*member['card_position'],len(operator_profiles()[member['id']]['skills']),space=member.get('card_scale',(1,1)))
            member['skill_ranks']={**member['skill_ranks'],**ranks}
            if ranks:member['sources']['skill_ranks']='本局卡片各技能三个亮起专精标记分别确认'
    if resources is None:
        resources=read_resources(image,texts,engine,native_content=native_content) if is_map else {}
    counters=[];unbound_counters=[];counter_performance={}
    if held['text']=='收起' and is_map:
        badges,regions,counter_performance,_=read_local_counter_badges(image,texts,held,engine)
        counters=read_held_counters(image,texts,held,badges=badges,regions=regions)
        used={tuple(tuple(p) for p in c['marker']['box']) for c in counters}
        unbound_counters=[{'value':b['value'],'box':b['box'],'marker':{'box':b['marker_box']},
            'score':b['score'],'confidence':b['confidence'],'source':b['source'],
            'identity_confirmed':False} for b in badges
            if tuple(tuple(p) for p in b['marker_box']) not in used]
    limitations=['只确认持有栏与本局队伍；不可见藏品、数量和培养字段保持未知。']
    resources.update(counter_resources(counters))
    red=next((c for c in counters if c['id']=='rogue_6_relic_cargo_2'),None)
    parts=resources.get('parts_count')
    if red and parts:
        # Existing documented rule caps the applied part count at 99. A badge
        # alone is not proof of the uncapped resource quantity or its capacity.
        if red['value']==min(99,parts['value']):
            parts['counter_crosscheck']={'relic_id':red['id'],'value':red['value'],
                'score':red['score'],'source':red['source']}
        else:
            resources.pop('parts_count')
            limitations.append('悲伤的红计数与零件箱数值冲突；本帧不更新零件数，保留最近确认记录。')
    return {'page':'run_roster' if is_roster else 'run_map','relics':{
        'ids':sorted(ids),'count':count,'icons':icons,'cards':cards,'counters':counters,
        'unbound_counters':unbound_counters,'source':'held_bar'},
        'tactical_tools':{'ids':sorted(tool_ids),'source':'held_bar_or_cards'},
        'crew_count':crew_count,'operators':members,'selected_operator':selected['id'] if selected else None,
        'resources':resources,
        'config':config,
        'config_reuse':{'run_id':(run_context or {}).get('run_id'),
                        'fields':sorted(set(known)-set(fresh))},
        'counter_performance':counter_performance,
        'limitations':limitations}


read_owned_cards = read_held_cards


def expanded_held_page(anchors,held,cards):
    """An expanded held panel can hide the top HUD; verify its own footer.

    Font-relative alignment and ordered controls are observed on this frame.
    A reward description or a shop price never establishes held ownership.
    The signature does not establish complete inventory or its total count.
    """
    if held['text']!='收起' or not any(c['confirmed'] for c in cards):return False
    controls=[anchors.get(n) for n in ('零件箱','干员','编队')]
    if not all(controls):return False
    hx,hy=center(held)
    font=max(p[1] for p in held['box'])-min(p[1] for p in held['box'])
    centers=[center(c) for c in controls]
    return (font>0 and hx<centers[0][0]<centers[1][0]<centers[2][0]
            and all(.5*font<=max(p[1] for p in c['box'])-min(p[1] for p in c['box'])<=2*font
                    and abs(y-hy)<=3*font for c,(_,y) in zip(controls,centers)))


def read_held_counters(image,texts,held,*,badges=None,regions=None):
    """Bind a verified marker only to a unique, complete held-card identity.

    The value is visual evidence, not a generic mechanism input. Clipped titles,
    overlapping regions and multiple badges for one card remain unbound. Neither
    the badge nor a missing badge proves recipient, used state or completeness.
    """
    regions=[r for r in (held_card_regions(texts,held) if regions is None else regions) if r['confirmed']]
    if not regions:return []
    def contains(bounds,points):
        x0,y0,x1,y1=bounds
        return all(x0<=x<=x1 and y0<=y<=y1 for x,y in points)
    candidates={}
    for badge in (read_counter_badges(image,texts) if badges is None else badges):
        matches=[r for r in regions if contains(r['icon_bounds'],badge['box'])
                 and contains(r['icon_bounds'],badge['marker_box'])]
        if len(matches)!=1:continue
        region=matches[0];rid=region['candidates'][0]
        candidates.setdefault(rid,[]).append({'id':rid,'title':region['title'],
            'value':badge['value'],'box':badge['box'],'marker':{'box':badge['marker_box']},
            'score':badge['score'],'confidence':badge['confidence'],
            'source':'held_full_name_usage_and_'+badge['source']})
    return [records[0] for records in candidates.values() if len(records)==1]


def read_roster(image,texts,engine):
    members=[];h,w=image.shape[:2]
    branch=next((t for t in texts if t['text']=='分支+' and t['confidence']>=.9),None)
    if branch is None:return members
    skill_panel=next((t for t in texts if t['text']=='技能' and t['confidence']>=.9),None)
    if skill_panel is None:return members
    branch_x = center(branch)[0]
    # Two observed controls establish the UI scale; glyph size can vary by name.
    ux = (branch_x-center(skill_panel)[0])/(.1762-.0595)
    uy = ux*w/h*1127/2052
    identities = identity_index()
    names, levels = [], []
    for text in texts:
        if not (text['confidence'] >= .9):
            continue
        x,y = center(text)
        if re.fullmatch(r'\d{1,2}', text['text']):
            levels.append((int(text['text']),x,y))
        if x > branch_x:
            matches = identities.get(normalized_name(text['text']), ())
            if len(matches) == 1:
                names.append((text,next(iter(matches)),x,y))
    for name,key,x,y in names:
        nearby = (level for level in levels if .055*ux < x-level[1] < .20*ux and abs(level[2]-y) < .025*uy)
        badge = min(nearby, key=lambda level:x-level[1], default=None)
        if badge is None:
            value = None
            bx,by = min(p[0] for p in name['box'])-.075*ux,y
            x0=max(0,round((bx-.035*ux)*w));x1=min(w,round((bx+.035*ux)*w))
            y0=max(0,round((y-.025*uy)*h));y1=min(h,round((y+.025*uy)*h))
            roi=image[y0:y1,x0:x1]
            if roi.size:
                raw,_=engine(cv2.resize(roi,None,fx=4,fy=4),use_cls=False)
                values={int(v) for _,v,score in raw or [] if score>=.9 and re.fullmatch(r'\d{1,2}',v)}
                value=next(iter(values)) if len(values)==1 else None
        else:
            value,bx,by = badge
        member=roster_member(image,key,bx,by,value,space=(ux,uy))
        member['card_scale']=[ux,uy]
        members.append(member)
    return members


def roster_member(image,key,x,y,value,space=(1,1)):
    profile=operator_profiles()[key]
    if value is not None and not 1<=value<=max(p['max_level'] for p in profile['phases']):value=None
    emblem=card_elite(image,x,y,space)
    promotion=promotion_marker(image,x,y,space)
    fields={};sources={'reference_level':'卡片等级为账号参考，不等同于本局当前培养'}
    if emblem and emblem['value']<len(profile['phases']):
        elite=emblem['value']
        if promotion and not promotion['advanced'] and len(profile['phases'])==3:elite=min(elite,1)
        fields['elite']=elite
        if value is not None:fields['level']=min(value,profile['phases'][elite]['max_level'])
        sources.update(elite={'emblem':emblem,'promotion':promotion},level='账号卡片等级与本局已确认精英阶段上限取较低值')
        if not profile['modules'] or all(elite<m['unlock_elite'] for m in profile['modules']):
            fields.update(module_id=None,module_level=0)
            sources['module_id']='本局精英阶段未开放模组'
    required=['level','elite','potential','trust','module_id','module_level','selected_skill']
    result={'id':key,'name':profile['name'],'scope':'run','fields':fields,'reference_level':value,'skill_ranks':{},'card_position':[x,y],
            'sources':sources,'missing_fields':[f for f in required if f not in fields]}
    marker=recruitment_marker(image,x,y,space)
    if marker:
        result['recruitment_kind']=marker['kind'];sources['recruitment_kind']=marker
    if promotion:
        result['advanced']=promotion['advanced'];sources['advanced']=promotion
    return result


def read_card_masteries(image,x,y,count,space=(1,1)):
    """Accept three independently bright mastery dots; unclear/partial pips stay unknown."""
    ux,uy=space
    h,w=image.shape[:2];gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY);ranks={}
    radius=max(1,round(h*.0015*uy))
    search=max(1,round(h*uy*.0035))
    for i in range(count):
        cx=x+.083*ux+i*.0377*ux
        background=gray[max(0,round((y-.084*uy)*h)):round((y-.062*uy)*h),
                        max(0,round((cx-.009*ux)*w)):round((cx+.009*ux)*w)]
        if not background.size:continue
        dark=float(np.percentile(background,20))
        # Small OCR/grid rounding changes must not move a pip outside its core.
        centers=[(round((cx+dx*ux)*w),round((y+dy*uy)*h))
                 for dx,dy in ((0,-.077),(-.0023,-.069),(.0023,-.069))]
        found=False
        for ox in range(-search,search+1):
            for oy in range(-search,search+1):
                for dot_x,dot_y in centers:
                    px=dot_x+ox;py=dot_y+oy
                    roi=gray[max(0,py-radius):py+radius+1,max(0,px-radius):px+radius+1]
                    value=float(np.median(roi)) if roi.size else 0
                    if not (value>=120 and value-dark>=70):break
                else:
                    found=True
                    break
            if found:break
        if found:ranks[i+1]=10
    return ranks


def read_selected_member(image,texts,engine):
    panel=next((t for t in texts if t['text']=='技能' and t['confidence']>=.9),None)
    if panel is None:return None
    panel_x,panel_y=center(panel)
    name_right=panel_x+.5*(max(p[0] for p in panel['box'])-min(p[0] for p in panel['box']))
    positions=[(t,*center(t)) for t in texts if t['confidence']>=.9]
    index=identity_index()
    names={}
    for record,x,y in positions:
        if y<panel_y and x<name_right:
            matches=index.get(normalized_name(record['text']),())
            if len(matches)==1:
                names.setdefault(next(iter(matches)),[]).append((record,x,y))
    if len(names)!=1:return None
    key,rows=next(iter(names.items()))
    name,nx,ny=max(rows,key=lambda row:max(p[1] for p in row[0]['box'])-min(p[1] for p in row[0]['box']))
    left=min(p[0] for p in name['box'])
    profile=operator_profiles()[key]
    h,w=image.shape[:2]
    uy=(panel_y-ny)/(.436121-.162684);ux=uy*h/w*2052/1127
    fields={};sources={};ranks={}
    values={int(m.group(1)) for t,x,y in positions
            if -.04*ux<x-nx<.08*ux and .015*uy<y-ny<.12*uy
            and (m:=re.fullmatch(r'(\d{1,2})/?',t['text']))}
    caps={int(t['text'][1:]) for t,x,y in positions
          if .07*ux<x-nx<.18*ux and .015*uy<y-ny<.12*uy
          and re.fullmatch(r'/\d{2}',t['text'])}
    if len(caps)==1:
        cap=next(iter(caps))
        phases=[i for i,p in enumerate(profile['phases']) if p['max_level']==cap]
        if len(phases)==1:fields['elite']=phases[0];sources['elite']='本局当前面板精英上限与档案唯一匹配'
    if len(values)==1 and 'elite' in fields:
        level=next(iter(values))
        if 1<=level<=profile['phases'][fields['elite']]['max_level']:
            fields['level']=level;sources['level']='本局左侧当前等级；排除右侧账号卡片等级'
    if not profile['modules'] or ('elite' in fields and all(fields['elite']<m['unlock_elite'] for m in profile['modules'])):
        fields.update(module_id=None,module_level=0);sources['module_id']='本局精英阶段未开放模组'
    required_titles={skill['levels'][-1]['name'] for skill in profile['skills']}
    if not required_titles<={t['text'] for t,_,_ in positions}:
        x0=max(0,round((left-.01*ux)*w));x1=min(w,round((left+.26*ux)*w))
        y0=max(0,round((panel_y+.025*uy)*h));y1=min(h,round((panel_y+.52*uy)*h))
        roi=image[y0:y1,x0:x1]
        if roi.size:
            raw,_=engine(cv2.resize(roi,None,fx=2,fy=2))
            for box,t,score in raw or []:
                if float(score)>=.9:
                    record={'text':t.replace(' ',''),'box':[[(px/2+x0)/w,(py/2+y0)/h] for px,py in box]}
                    positions.append((record,*center(record)))
    for i,skill in enumerate(profile['skills'],1):
        y=next((ty for t,tx,ty in positions if t['text']==skill['levels'][-1]['name']
                and tx<panel_x+.025*ux and ty>panel_y),None)
        if y is None:continue
        crop=image[max(0,int((y-.12*uy)*h)):min(h,int((y-.083*uy)*h)),max(0,int((left-.007*ux)*w)):min(w,int((left+.012*ux)*w))]
        if not crop.size:continue
        raw,_=engine(cv2.resize(crop,None,fx=4,fy=4),use_cls=False)
        badges={int(text) for _,text,score in raw or [] if score>=.9 and re.fullmatch('[1-7]',text)}
        if len(badges)==1:
            rank=next(iter(badges))
            # A seven badge at elite 2 needs separate mastery evidence; do not assume mastery zero.
            if rank<7 or fields.get('elite',2)<2:ranks[i]=rank
    required=['level','elite','potential','trust','module_id','module_level','selected_skill']
    return {'id':key,'name':profile['name'],'scope':'run','fields':fields,'skill_ranks':ranks,'sources':sources,
            'missing_fields':[f for f in required if f not in fields]}
