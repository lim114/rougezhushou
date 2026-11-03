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

def verified_zero(crop,anchor_height,engine,*,recognizer_only=False):
    """The observed upright glyph needs both topology and independent OCR.

    A recognizer-only pass is safe only after finding a unique isolated zero.
    Other glyphs (including the 1 in 10) preclude this fast path. No old numeric
    result or screen coordinate serves as evidence for the current frame.
    """
    gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
    mask=cv2.threshold(gray,205,255,cv2.THRESH_BINARY)[1]
    count,labels,stats,_=cv2.connectedComponentsWithStats(mask)
    significant=[s for s in stats[1:] if .4*anchor_height<=s[3]<=1.5*anchor_height
                 and s[4]>=20]
    if len(significant)!=1:return False
    candidates=[]
    for i,(x,y,w,h,area) in enumerate(stats[1:],1):
        if not (.4*anchor_height<=h<=1.5*anchor_height and .55<=w/h<=1.05 and area>=20):continue
        if x<=0 or y<=0 or x+w>=crop.shape[1] or y+h>=crop.shape[0]:continue
        glyph=(labels[y:y+h,x:x+w]==i).astype(np.uint8)
        _,hierarchy=cv2.findContours(glyph,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None or sum(c[3]>=0 for c in hierarchy[0])!=1:continue
        ref=cv2.resize(zero_reference().astype(np.uint8),(w,h),interpolation=cv2.INTER_NEAREST)
        # One-pixel tolerance handles antialiasing after continuous resize;
        # topology, component dimensions and independent OCR still must agree.
        kernel=np.ones((3,3),np.uint8)
        score=(np.count_nonzero(glyph&cv2.dilate(ref,kernel))+
               np.count_nonzero(ref&cv2.dilate(glyph,kernel)))/(np.count_nonzero(glyph)+np.count_nonzero(ref))
        if score>=.99:candidates.append(glyph*255)
    if len(candidates)!=1:return False
    # Recognition is checked on the isolated glyph, with surrounding pattern removed.
    glyph=candidates[0]
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
    def valid(t):
        dx,dy=center(t)[0]-x,center(t)[1]-y
        return t['confidence']>=.9 and re.fullmatch(r'\d{1,3}',t['text']) and (
            abs(dx)<.035*ux and -.065*uy<dy<-.012*uy if side=='above' else .02*ux<dx<.09*ux and abs(dy)<.045*uy)
    values={int(t['text']) for t in texts if valid(t)}
    if len(values)==1:return next(iter(values))
    h,w=image.shape[:2]
    bounds=(x-.035*ux,y-.065*uy,x+.035*ux,y-.012*uy) if side=='above' else (x+.025*ux,y-.04*uy,x+.074*ux,y+.015*uy)
    x0,y0,x1,y1=bounds
    x0=max(0,int(x0*w));x1=min(w,int(x1*w));y0=max(0,int(y0*h));y1=min(h,int(y1*h))
    crop=image[y0:y1,x0:x1]
    if not crop.size:return None
    height=(max(p[1] for p in anchor['box'])-min(p[1] for p in anchor['box']))*h
    if not values and side=='above' and verified_zero(crop,height,engine,recognizer_only=True):return 0
    # Numeric controls are upright relative to their observed label. Applying
    # the generic orientation classifier can rotate a real 6 into a confident 9.
    raw,_=engine(cv2.resize(crop,None,fx=4,fy=4),use_cls=False)
    values={int(text) for _,text,score in raw or [] if score>=.9 and re.fullmatch(r'\d{1,3}',text)}
    if not values:
        gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
        normalized=cv2.normalize(gray,None,0,255,cv2.NORM_MINMAX)
        raw,_=engine(cv2.resize(normalized,None,fx=4,fy=4),use_cls=False)
        values={int(text) for _,text,score in raw or [] if score>=.9 and re.fullmatch(r'\d{1,3}',text)}
    if len(values)==1:return next(iter(values))
    if not values and side=='above':
        if verified_zero(crop,height,engine):return 0
    return None


def read_run(image,texts,engine,*,icon_cache=None,run_context=None):
    texts=recheck_run_names(image,texts,engine)
    texts=reconfirm_owned_popup_footer(image,texts,engine)
    anchors={t['text']:t for t in texts if t['confidence']>=.9}
    held=anchors.get('收藏品') or next(iter(sorted([t for t in texts if t['text']=='收起' and t['confidence']>=.9],key=lambda t:center(t)[0])),None)
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
    count=near_number(image,texts,held,engine) if held['text']=='收藏品' else None
    crew=anchors.get('干员')
    crew_count=near_number(image,texts,crew,engine,side='right') if crew else None
    if is_roster:
        crew=next((t for t in texts if t['text']=='收起' and t['confidence']>=.9 and center(t)[0]>center(held)[0]),None)
        if crew:crew_count=near_number(image,texts,crew,engine,side='right')
    ids=[];tool_ids=[]
    if held['text']=='收起' and is_map:
        for card in cards:
            if not card['confirmed']:continue
            (tool_ids if card['id'] in tactical_tools() else ids).append(card['id'])
    from .run_config import confirmed_config
    known=confirmed_config(run_context)
    fresh=read_config(image,texts,held,engine=engine,known_config=known) if is_map else {}
    config={**known,**fresh}
    icons=resolve_difficulty_icons(resolve_owned_icons(match_held_icons(image,held,count,cache=icon_cache),cards),config.get('difficulty'))
    if count==0 and icons:count=None
    ids=sorted(set(ids+[record['id'] for record in icons if record['confirmed'] and record['id'] in catalog()['relics']]))
    tool_ids=sorted(set(tool_ids+[record['id'] for record in icons if record['confirmed'] and record['id'] in tactical_tools()]))
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
    resources=read_resources(image,texts) if is_map else {}
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
    red=[c for c in counters if c['id']=='rogue_6_relic_cargo_2']
    parts=resources.get('parts_count')
    if red and parts:
        # Existing documented rule caps the applied part count at 99. A badge
        # alone is not proof of the uncapped resource quantity or its capacity.
        if red[0]['value']==min(99,parts['value']):
            parts['counter_crosscheck']={'relic_id':red[0]['id'],'value':red[0]['value'],
                'score':red[0]['score'],'source':red[0]['source']}
        else:
            resources.pop('parts_count')
            limitations.append('悲伤的红计数与零件箱数值冲突；本帧不更新零件数，保留最近确认记录。')
    return {'page':'run_roster' if is_roster else 'run_map','relics':{
        'ids':ids,'count':count,'icons':icons,'cards':cards,'counters':counters,
        'unbound_counters':unbound_counters,'source':'held_bar'},
        'tactical_tools':{'ids':sorted(set(tool_ids)),'source':'held_bar_or_cards'},
        'crew_count':crew_count,'operators':members,'selected_operator':selected['id'] if selected else None,
        'resources':resources,
        'config':config,
        'config_reuse':{'run_id':(run_context or {}).get('run_id'),
                        'fields':sorted(set(known)-set(fresh))},
        'counter_performance':counter_performance,
        'limitations':limitations}


def read_owned_cards(texts,held):
    """Keep the public identity contract while grouping cards in two dimensions."""
    return read_held_cards(texts,held)


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
    names=[t for t in texts if t['confidence']>=.9 and center(t)[0]>center(branch)[0]
           and len(identity_index().get(normalized_name(t['text']),set()))==1]
    skill_panel=next((t for t in texts if t['text']=='技能' and t['confidence']>=.9),None)
    if skill_panel is None:return members
    # Two observed controls establish the UI scale; glyph size can vary by name.
    panel_ux=(center(branch)[0]-center(skill_panel)[0])/(.1762-.0595)
    panel_uy=panel_ux*w/h*1127/2052
    for name in names:
        key=next(iter(identity_index()[normalized_name(name['text'])]))
        x,y=center(name);ux,uy=panel_ux,panel_uy
        levels=[t for t in texts if t['confidence']>=.9 and re.fullmatch(r'\d{1,2}',t['text'])
                and .055*ux<x-center(t)[0]<.20*ux and abs(center(t)[1]-y)<.025*uy]
        badge=min(levels,key=lambda t:x-center(t)[0]) if levels else None
        value=int(badge['text']) if badge else None
        bx,by=center(badge) if badge else (min(p[0] for p in name['box'])-.075*ux,y)
        if badge is None:
            x0=max(0,round((bx-.035*ux)*w));x1=min(w,round((bx+.035*ux)*w))
            y0=max(0,round((y-.025*uy)*h));y1=min(h,round((y+.025*uy)*h))
            roi=image[y0:y1,x0:x1]
            if roi.size:
                raw,_=engine(cv2.resize(roi,None,fx=4,fy=4),use_cls=False)
                values={int(v) for _,v,score in raw or [] if score>=.9 and re.fullmatch(r'\d{1,2}',v)}
                value=next(iter(values)) if len(values)==1 else None
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
    ux,uy=space
    """Accept three independently bright mastery dots; unclear/partial pips stay unknown."""
    h,w=image.shape[:2];gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY);ranks={}
    radius=max(1,round(h*.0015*uy))
    for i in range(count):
        cx=x+.083*ux+i*.0377*ux
        background=gray[max(0,round((y-.084*uy)*h)):round((y-.062*uy)*h),
                        max(0,round((cx-.009*ux)*w)):round((cx+.009*ux)*w)]
        if not background.size:continue
        dark=float(np.percentile(background,20))
        # Small OCR/grid rounding changes must not move a pip outside its core.
        search=max(1,round(h*uy*.0035))
        found=False
        for ox in range(-search,search+1):
            for oy in range(-search,search+1):
                cores=[]
                for dx,dy in ((0,-.077),(-.0023,-.069),(.0023,-.069)):
                    px=round((cx+dx*ux)*w)+ox;py=round((y+dy*uy)*h)+oy
                    roi=gray[max(0,py-radius):py+radius+1,max(0,px-radius):px+radius+1]
                    cores.append(float(np.median(roi)) if roi.size else 0)
                if all(value>=120 and value-dark>=70 for value in cores):found=True;break
            if found:break
        if found:ranks[i+1]=10
    return ranks


def read_selected_member(image,texts,engine):
    panel=next((t for t in texts if t['text']=='技能' and t['confidence']>=.9),None)
    if panel is None:return None
    names=[t for t in texts if t['confidence']>=.9 and center(t)[1]<center(panel)[1]
           and center(t)[0]<center(panel)[0]+.5*(max(p[0] for p in panel['box'])-min(p[0] for p in panel['box']))
           and len(identity_index().get(normalized_name(t['text']),set()))==1]
    identities={next(iter(identity_index()[normalized_name(t['text'])])) for t in names}
    if len(identities)!=1:return None
    name=max(names,key=lambda t:max(p[1] for p in t['box'])-min(p[1] for p in t['box']));key=next(iter(identity_index()[normalized_name(name['text'])]));profile=operator_profiles()[key]
    h,w=image.shape[:2];nx,ny=center(name)
    uy=(center(panel)[1]-ny)/(.436121-.162684);ux=uy*h/w*2052/1127
    fields={};sources={};ranks={}
    values={int(m.group(1)) for t in texts if t['confidence']>=.9
            and -.04*ux<center(t)[0]-nx<.08*ux and .015*uy<center(t)[1]-ny<.12*uy
            and (m:=re.fullmatch(r'(\d{1,2})/?',t['text']))}
    caps={int(t['text'][1:]) for t in texts if t['confidence']>=.9
          and .07*ux<center(t)[0]-nx<.18*ux and .015*uy<center(t)[1]-ny<.12*uy
          and re.fullmatch(r'/\d{2}',t['text'])}
    if len(caps)==1:
        phases=[i for i,p in enumerate(profile['phases']) if p['max_level']==next(iter(caps))]
        if len(phases)==1:fields['elite']=phases[0];sources['elite']='本局当前面板精英上限与档案唯一匹配'
    if len(values)==1 and 'elite' in fields and 1<=next(iter(values))<=profile['phases'][fields['elite']]['max_level']:
        fields['level']=next(iter(values));sources['level']='本局左侧当前等级；排除右侧账号卡片等级'
    if not profile['modules'] or ('elite' in fields and all(fields['elite']<m['unlock_elite'] for m in profile['modules'])):
        fields.update(module_id=None,module_level=0);sources['module_id']='本局精英阶段未开放模组'
    required_titles={skill['levels'][-1]['name'] for skill in profile['skills']}
    if not required_titles<={t['text'] for t in texts if t['confidence']>=.9}:
        left=min(p[0] for p in name['box'])
        x0=max(0,round((left-.01*ux)*w));x1=min(w,round((left+.26*ux)*w))
        y0=max(0,round((center(panel)[1]+.025*uy)*h));y1=min(h,round((center(panel)[1]+.52*uy)*h))
        roi=image[y0:y1,x0:x1]
        if roi.size:
            raw,_=engine(cv2.resize(roi,None,fx=2,fy=2))
            texts=texts+[{'text':t.replace(' ',''),'confidence':float(score),'box':[[(px/2+x0)/w,(py/2+y0)/h] for px,py in box]} for box,t,score in raw or [] if score>=.85]
    for i,skill in enumerate(profile['skills'],1):
        anchor=next((t for t in texts if t['text']==skill['levels'][-1]['name'] and t['confidence']>=.9 and
                     center(t)[0]<center(panel)[0]+.025*ux and center(t)[1]>center(panel)[1]),None)
        if anchor is None:continue
        _,y=center(anchor)
        left=min(p[0] for p in name['box'])
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
