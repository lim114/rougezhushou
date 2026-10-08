"""Read explicit owned operator-buff popups; never infer recipients from offers.

All boxes follow the supplied frame's normalized coordinates. No screen-size
or operator-specific field position is stored. Missing evidence cannot clear
the caller's run memory.
"""
import re
import unicodedata
import math
import time
from copy import deepcopy
from functools import lru_cache

import cv2
import numpy as np

from .catalog import operator_profiles
from .relics import mechanics
from .relic_recognition import _reference_image


def _canonical(value):
    value=unicodedata.normalize('NFKC',value).replace('−','-')
    # Formatting brackets and prose punctuation may differ after line OCR;
    # effect signs, decimals, percentages and units must remain exact.
    return ''.join(c for c in value if not c.isspace()
                   and (c in '+-.%/' or not unicodedata.category(c).startswith('P')))


def _bounds(record,width,height):
    points=record['box']
    return (min(p[0] for p in points)*width,min(p[1] for p in points)*height,
            max(p[0] for p in points)*width,max(p[1] for p in points)*height)


def _inside(record,region,width,height):
    x0,y0,x1,y1=_bounds(record,width,height)
    a,b,c,d=region
    return a<=x0 and b<=y0 and x1<=c and y1<=d


@lru_cache(maxsize=1)
def _catalog():
    result={}
    for bid,entry in mechanics()['char_buffs'].items():
        raw=entry.get('raw',{})
        if raw.get('buffType')!='FROM_RELIC' or raw.get('id')!=bid:continue
        name=raw.get('outerName');desc=raw.get('desc');icon=raw.get('iconId')
        if not name or not desc or not icon:continue
        if raw.get('innerName')!=name or raw.get('functionDesc')!=desc:continue
        result[bid]={'id':bid,'name':name,'description':desc,'icon_id':icon,
                     'profession':entry.get('required_profession'),'source':entry.get('source')}
    return result


def _popup_region(image,header):
    """Locate a bounded dark UI container around the observed owned-count line."""
    height,width=image.shape[:2]
    hx0,hy0,hx1,hy1=_bounds(header,width,height);font=max(1,hy1-hy0)
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    _,_,stats,_=cv2.connectedComponentsWithStats((gray<65).astype(np.uint8))
    candidates=[]
    for x,y,w,h,area in stats[1:]:
        if x<=0 or y<=0 or x+w>=width or y+h>=height:continue
        if not (x<=hx0 and y<=hy0 and hx1<=x+w and hy1<=y+h):continue
        if w<(hx1-hx0)+font or h<font*3 or area/(w*h)<.65:continue
        # The header belongs near the top of its own container, rather than
        # somewhere inside a large dark background region.
        if hy0-y>font*2 or y+h-hy1<font*2:continue
        candidates.append((x,y,x+w,y+h))
    return min(candidates,key=lambda r:(r[2]-r[0])*(r[3]-r[1])) if candidates else None


def _icon_match(image,title,region,icon_id):
    reference=_reference_image(icon_id)
    if reference is None or reference.ndim!=3 or reference.shape[2]!=4:return None
    height,width=image.shape[:2]
    x0,y0,x1,y1=_bounds(title,width,height);font=max(1,y1-y0)
    left,top,right,bottom=region
    # The artwork column lies to the left of this row's name. Its scale is
    # searched continuously relative to the observed text height.
    roi_x0=max(left,round(x0-font*7));roi_x1=min(right,round(x0))
    roi_y0=max(top,round(y0-font*1.5));roi_y1=min(bottom,round(y1+font*4))
    roi=image[roi_y0:roi_y1,roi_x0:roi_x1]
    if not roi.size:return None
    best=None
    for size in range(max(8,round(font*2)),max(9,round(font*6))+1,max(1,round(font*.1))):
        factor=size/max(reference.shape[:2])
        template=cv2.resize(reference,(max(1,round(reference.shape[1]*factor)),
                                      max(1,round(reference.shape[0]*factor))),interpolation=cv2.INTER_AREA)
        if template.shape[0]>roi.shape[0] or template.shape[1]>roi.shape[1]:continue
        mask=(template[:,:,3]>=220).astype(np.uint8)*255
        if np.count_nonzero(mask)<20:continue
        distances=cv2.matchTemplate(roi,template[:,:,:3],cv2.TM_SQDIFF_NORMED,mask=mask)
        distances=np.nan_to_num(distances,nan=1,posinf=1,neginf=1)
        distance,_,position,_=cv2.minMaxLoc(distances);score=1-distance
        if best is None or score>best['score']:
            px=position[0]+roi_x0;py=position[1]+roi_y0
            best={'id':icon_id,'score':float(score),'box':[[px/width,py/height],
                [(px+template.shape[1])/width,py/height],
                [(px+template.shape[1])/width,(py+template.shape[0])/height],
                [px/width,(py+template.shape[0])/height]]}
    return best if best and best['score']>=.94 else None


def _reconfirm_description(image,description,region,engine):
    """Read already observed lines inside the owned popup, keeping exact prose.

    Transparent popups can let dark underlying numbers join full-frame OCR.
    Local Otsu separates the actual light foreground within each current OCR
    line; it never edits a recognized number or substitutes catalog text.
    """
    if engine is None or not description:return None
    height,width=image.shape[:2];verified=[];started=time.perf_counter()
    for text in description:
        x0,y0,x1,y1=_bounds(text,width,height)
        font=y1-y0
        if not font>0 or not _inside(text,region,width,height):return None
        margin=font*.1
        left=max(0,int(region[0]),math.floor(x0-margin))
        top=max(0,int(region[1]),math.floor(y0-margin))
        right=min(width,int(region[2]),math.ceil(x1+margin))
        bottom=min(height,int(region[3]),math.ceil(y1+margin))
        crop=image[top:bottom,left:right]
        if not crop.size:return None
        gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
        threshold,binary=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        raw,_=engine(cv2.resize(binary,None,fx=4,fy=4,interpolation=cv2.INTER_LINEAR),
                     use_det=False,use_cls=False)
        if not raw or len(raw)!=1 or len(raw[0])!=2:return None
        line,confidence=raw[0]
        if not isinstance(line,str) or not line or not math.isfinite(confidence) or confidence<.9:return None
        record=deepcopy(text);record['text']=line;record['confidence']=float(confidence)
        record['source']='owned_popup_local_otsu_reconfirm'
        verified.append(record)
    return {'texts':verified,'source':'owned_popup_local_otsu_reconfirm',
            'local_ocr_calls':len(verified),'elapsed_ms':(time.perf_counter()-started)*1000}


def _retain_stronger_current_lines(original,reconfirmed):
    """One fallback candidate from whole, aligned current OCR lines only.

    The caller uses this only after the complete local candidate failed its
    exact prose check. It must check that whole candidate again. No character
    is changed, supplied from the catalog, or taken from a previous frame.
    """
    if not reconfirmed or len(original)!=len(reconfirmed.get('texts',[])):return None
    lines=[];choices=[];retained=False
    for index,(current,local) in enumerate(zip(original,reconfirmed['texts'])):
        if (not current.get('box') or current['box']!=local.get('box')
                or local.get('source')!='owned_popup_local_otsu_reconfirm'):return None
        score=current.get('confidence',0)
        keep=(not isinstance(score,bool) and isinstance(score,(int,float,np.floating))
              and math.isfinite(score) and .95<=score<=1 and score>local['confidence'])
        chosen=deepcopy(current if keep else local)
        if keep:chosen['source']='owned_popup_current_original_line_retained';retained=True
        lines.append(chosen)
        choices.append({'index':index,'source':'current_full_ocr' if keep else 'current_local_otsu_rec',
                        'original_confidence':current.get('confidence',0),
                        'reconfirm_confidence':local['confidence'],'selected_confidence':chosen['confidence']})
    if not retained:return None
    result=deepcopy(reconfirmed);result.update(texts=lines,
        source='owned_popup_current_and_local_otsu_reconfirm',line_choices=choices)
    return result


def reconfirm_owned_popup_footer(image,texts,engine):
    """Re-read one currently observed weak footer, without lowering its gate.

    Strong owned-header, button, two title and aligned footer observations
    only locate work. An exact current REC result at .95 is still required;
    the ordinary owner/card/class checks run afterwards without changes.
    """
    if image is None or not image.size or engine is None:return texts
    # A weak, currently observed footer is necessary. Avoid full-image
    # container discovery when this pass has nothing to reconfirm.
    if not any(t.get('box') and t.get('text') in ('收藏品','收起','编队')
               and .9<=t.get('confidence',0)<.95 for t in texts):return texts
    strong=[t for t in texts if t.get('confidence',0)>=.95 and t.get('box')]
    if any(t['text'] in ('技能','分支+') for t in texts if t.get('confidence',0)>=.9):return texts
    headers=[t for t in strong if re.fullmatch(
        r'[*＊]?此干员已拥有以下(?:[2-9]|[1-9]\d)个收藏品增益',t['text'].replace(' ',''))]
    if len(headers)!=1:return texts
    height,width=image.shape[:2];header=headers[0]
    _,hy0,_,hy1=_bounds(header,width,height);font=max(1,hy1-hy0)
    buttons=[t for t in strong if t['text']=='收藏品增益'
             and 0<hy0-_bounds(t,width,height)[3]<font*5]
    if len(buttons)!=1:return texts
    region=_popup_region(image,header)
    if region is None:return texts
    titles={_canonical(entry['name']) for entry in _catalog().values()}
    visible_titles={_canonical(t['text']) for t in strong if _inside(t,region,width,height)
                    and _bounds(t,width,height)[1]>=hy1 and _canonical(t['text']) in titles}
    if len(visible_titles)<2:return texts
    footer={}
    for label in ('收藏品','收起','编队'):
        found=[(i,t) for i,t in enumerate(texts) if t.get('confidence',0)>=.9
               and t.get('box') and t['text']==label and _bounds(t,width,height)[1]>region[3]]
        if len(found)!=1:return texts
        footer[label]=found[0]
    weak=[(i,t) for i,t in footer.values() if t['confidence']<.95]
    if len(weak)!=1:return texts
    _,collapse=footer['收起'];fx0,fy0,fx1,fy1=_bounds(collapse,width,height)
    footer_font=fy1-fy0
    if footer_font<=0:return texts
    for _,record in footer.values():
        x0,y0,x1,y1=_bounds(record,width,height)
        if not .5*footer_font<=y1-y0<=2*footer_font:return texts
        if abs((y0+y1-fy0-fy1)/2)>3*footer_font:return texts
    if not (_bounds(footer['收藏品'][1],width,height)[2]<fx0
            and fx1<_bounds(footer['编队'][1],width,height)[0]):return texts
    position,record=weak[0];x0,y0,x1,y1=_bounds(record,width,height)
    if not (all(math.isfinite(v) for v in (x0,y0,x1,y1))
            and 0<=x0<x1<=width and 0<=y0<y1<=height):return texts
    left=max(0,math.floor(x0)-2);top=max(0,math.floor(y0)-2)
    right=min(width,math.ceil(x1)+2);bottom=min(height,math.ceil(y1)+2)
    crop=image[top:bottom,left:right]
    if not crop.size:return texts
    try:
        raw,_=engine(crop,use_det=False,use_cls=False)
    except Exception:
        return texts
    if not isinstance(raw,(list,tuple)) or len(raw)!=1:return texts
    if not isinstance(raw[0],(list,tuple)) or len(raw[0])!=2:return texts
    exact,score=raw[0]
    if (exact!=record['text'] or isinstance(score,bool)
            or not isinstance(score,(int,float,np.floating))
            or not math.isfinite(score) or not .95<=score<=1):return texts
    revised=deepcopy(texts)
    revised[position]['confidence']=float(score)
    revised[position]['footer_recheck']={
        'source':'current_owned_popup_footer_rect_recognizer',
        'original_confidence':record['confidence'],'confidence':float(score),
        'box':[[left/width,top/height],[right/width,top/height],
               [right/width,bottom/height],[left/width,bottom/height]],'padding_pixels':2,
        'use_det':False,'use_cls':False}
    return revised


def read_owned_popup_member(image,texts):
    """Attribute a multi-buff run popup whose body covers both skill tabs.

    This additional context needs current exact names in two independent
    positions, a complete explicit owned-count header, its adjacent button,
    dynamically located dark container, two full buff titles and aligned run
    footer. It never creates hidden tab labels or operator training fields.
    A missing single tab or an unverified zero/one-entry layout stays unknown.
    """
    if image is None or not image.size:return None
    visible=[t for t in texts if t.get('confidence',0)>=.95 and t.get('box')]
    labels={t['text'] for t in texts if t.get('confidence',0)>=.9}
    if labels&{'技能','分支+'}:return None
    headers=[]
    for t in visible:
        match=re.fullmatch(r'[*＊]?此干员已拥有以下(\d{1,2})个收藏品增益',t['text'].replace(' ',''))
        if match and int(match.group(1))>=2:headers.append(t)
    if len(headers)!=1:return None
    height,width=image.shape[:2];header=headers[0]
    hx0,hy0,hx1,hy1=_bounds(header,width,height);font=max(1,hy1-hy0)
    buttons=[t for t in visible if t['text']=='收藏品增益'
             and _bounds(t,width,height)[3]<=hy0
             and 0<hy0-_bounds(t,width,height)[3]<font*5]
    if len(buttons)!=1:return None
    button=buttons[0];bx0,by0,bx1,by1=_bounds(button,width,height)
    region=_popup_region(image,header)
    if region is None:return None
    full_titles={_canonical(entry['name']) for entry in _catalog().values()}
    found_titles={_canonical(t['text']) for t in visible
                  if _inside(t,region,width,height) and _bounds(t,width,height)[1]>=hy1
                  and _canonical(t['text']) in full_titles}
    if len(found_titles)<2:return None
    footer={}
    for label in ('收藏品','收起','编队'):
        records=[t for t in visible if t['text']==label and _bounds(t,width,height)[1]>region[3]]
        if len(records)!=1:return None
        footer[label]=records[0]
    fx0,fy0,fx1,fy1=_bounds(footer['收起'],width,height);footer_font=fy1-fy0
    if footer_font<=0:return None
    for record in footer.values():
        x0,y0,x1,y1=_bounds(record,width,height)
        if not .5*footer_font<=y1-y0<=2*footer_font:return None
        if abs((y0+y1-fy0-fy1)/2)>3*footer_font:return None
    if not (_bounds(footer['收藏品'],width,height)[2]<fx0
            and fx1<_bounds(footer['编队'],width,height)[0]):return None
    profiles=operator_profiles();known_names={p['name'] for p in profiles.values()}
    owners=[t for t in visible if t['text'] in known_names
            and _bounds(t,width,height)[3]<=hy0
            and hy0-_bounds(t,width,height)[3]<font*5
            and _bounds(t,width,height)[2]<=bx0
            and abs(sum(_bounds(t,width,height)[axis] for axis in (1,3))/2-(by0+by1)/2)<font*3]
    if len(owners)!=1:return None
    owner=owners[0];identities=[oid for oid,p in profiles.items() if p['name']==owner['text']]
    if len(identities)!=1:return None
    # A class-limited named buff cannot establish a conflicting owner, even
    # when that other operator also happens to have a card on this roster.
    # These are the same pinned class constraints used by the buff reader.
    profession=profiles[identities[0]]['profession']
    for title in found_titles:
        candidates=[entry for entry in _catalog().values() if _canonical(entry['name'])==title]
        if all(entry['profession'] and profession not in entry['profession'].split('|') for entry in candidates):
            return None
    # This second exact name is outside the popup, to its right, and above
    # the currently observed footer. Duplicate or overlapping copies do not
    # independently establish an operator card.
    cards=[t for t in visible if t['text']==owner['text'] and t is not owner
           and _bounds(t,width,height)[0]>=region[2]+font
           and _bounds(t,width,height)[1]>by1+font
           and _bounds(t,width,height)[3]<min(_bounds(f,width,height)[1] for f in footer.values())]
    if len(cards)!=1:return None
    def evidence(record):
        value={'box':deepcopy(record['box'])}
        if record.get('footer_recheck'):value['footer_recheck']=deepcopy(record['footer_recheck'])
        return value
    context={'source':'current_multi_owned_popup_and_independent_run_card',
             'header':evidence(header),'button':evidence(button),'owner':evidence(owner),
             'card':evidence(cards[0]),
             'popup':{'box':[[float(region[0])/width,float(region[1])/height],
                            [float(region[2])/width,float(region[1])/height],
                            [float(region[2])/width,float(region[3])/height],
                            [float(region[0])/width,float(region[3])/height]]},
             'footer':{label:evidence(record) for label,record in footer.items()}}
    return {'id':identities[0],'name':owner['text'],'scope':'run','fields':{},'skill_ranks':{},
            'sources':{'owned_popup_context':context},
            'missing_fields':['level','elite','potential','trust','module_id','module_level','selected_skill']}


def read_recipient_buffs(image,texts,selected_member,*,engine=None):
    """Return confirmed visible buffs of one explicit selected run member.

    None means there is no safely attributable owned popup. A partial result
    retains only fully proven visible entries and must be merged with old
    run memory. Only ``complete=True`` permits replacing that member's list.
    An optional engine can independently reconfirm observed description lines
    inside this same popup. Names, owned-count context, icons and full canonical
    description still need their original checks. It never writes state or
    interacts with the game.
    """
    if image is None or not image.size or not isinstance(selected_member,dict):return None
    profiles=operator_profiles();oid=selected_member.get('id')
    if selected_member.get('scope')!='run' or oid not in profiles:return None
    profile=profiles[oid]
    if selected_member.get('name')!=profile['name']:return None
    if sum(p['name']==profile['name'] for p in profiles.values())!=1:return None
    visible=[t for t in texts if t.get('confidence',0)>=.9 and t.get('box')]
    anchors={t['text'] for t in visible}
    if not {'技能','分支+','收起','收藏品增益'}<=anchors:
        # Normal pages retain their original tab/context gate. Only the
        # separately verified multi-row owned layout may replace both tabs.
        popup_member=read_owned_popup_member(image,texts)
        if popup_member is None or popup_member['id']!=oid:return None
    headers=[]
    for t in visible:
        match=re.fullmatch(r'[*＊]?此干员已拥有以下(\d{1,2})个收藏品增益',t['text'].replace(' ',''))
        if match:headers.append((t,int(match.group(1))))
    if len(headers)!=1:return None
    header,total=headers[0];height,width=image.shape[:2]
    hx0,hy0,hx1,hy1=_bounds(header,width,height);font=max(1,hy1-hy0)
    buttons=[t for t in visible if t['text']=='收藏品增益'
             and _bounds(t,width,height)[3]<=hy0
             and 0<hy0-_bounds(t,width,height)[3]<font*5]
    if len(buttons)!=1:return None
    bx0,by0,bx1,by1=_bounds(buttons[0],width,height)
    names=[];known_names={p['name'] for p in profiles.values()}
    for t in visible:
        x0,y0,x1,y1=_bounds(t,width,height)
        if t['text'] not in known_names:continue
        if y1<=hy0 and hy0-y1<font*5 and x1<=bx0 and abs((y0+y1-by0-by1)/2)<font*3:
            names.append(t)
    if len(names)!=1 or names[0]['text']!=profile['name']:return None
    region=_popup_region(image,header)
    if region is None:return None
    body=[t for t in visible if t is not header and _inside(t,region,width,height)
          and _bounds(t,width,height)[1]>=hy1]
    entries=[];used=set();issues=[]
    # The public sample proves a populated popup only. Until a genuine zero
    # layout is observed, do not turn an empty OCR body into a memory clear.
    if total==0:issues.append('zero_layout_unverified')
    for bid,entry in _catalog().items():
        titles=[t for t in body if _canonical(t['text'])==_canonical(entry['name'])]
        if not titles:continue
        if len(titles)!=1:
            issues.append('duplicate_buff_title');continue
        title=titles[0];tx0,ty0,tx1,ty1=_bounds(title,width,height);line_height=max(1,ty1-ty0)
        following_titles=[_bounds(t,width,height)[1] for t in body if t is not title
            and any(_canonical(t['text'])==_canonical(e['name']) for e in _catalog().values())
            and _bounds(t,width,height)[1]>ty0]
        end=min(following_titles,default=region[3])
        description=sorted([t for t in body if t is not title
            and _bounds(t,width,height)[1]>=ty1-line_height*.2
            and _bounds(t,width,height)[3]<=end
            and abs(_bounds(t,width,height)[0]-tx0)<=line_height],
            key=lambda t:(_bounds(t,width,height)[1],_bounds(t,width,height)[0]))
        original_description=description
        reconfirmed=None
        if _canonical(''.join(t['text'] for t in description))!=_canonical(entry['description']):
            reconfirmed=_reconfirm_description(image,description,region,engine)
            if (reconfirmed and _canonical(''.join(t['text'] for t in reconfirmed['texts']))
                    !=_canonical(entry['description'])):
                candidate=_retain_stronger_current_lines(description,reconfirmed)
                if candidate and _canonical(''.join(t['text'] for t in candidate['texts']))==_canonical(entry['description']):
                    reconfirmed=candidate
            if (not reconfirmed or _canonical(''.join(t['text'] for t in reconfirmed['texts']))
                    !=_canonical(entry['description'])):
                issues.append('description_incomplete_or_conflicting');continue
            description=reconfirmed['texts']
        if entry['profession'] and profile['profession']!=entry['profession']:
            issues.append('profession_conflict');continue
        icon=_icon_match(image,title,region,entry['icon_id'])
        if icon is None:
            issues.append('icon_unconfirmed');continue
        entries.append({'id':bid,'name':entry['name'],'description':entry['description'],
                        'icon':icon,'name_evidence':{'box':[list(p) for p in title['box']]},
                        'description_evidence':[{'box':[list(p) for p in t['box']]} for t in description],
                        'source':'owned_operator_buff_popup','mechanism_source':entry['source']})
        if reconfirmed:
            entries[-1]['description_verification']={k:v for k,v in reconfirmed.items() if k!='texts'}
        used.update(id(t) for t in [title,*original_description])
    if any(id(t) not in used for t in body):issues.append('unrecognized_popup_text')
    if len(entries)!=total:issues.append('visible_count_incomplete')
    complete=not issues and len(entries)==total
    return {'operator_id':oid,'operator_name':profile['name'],'ids':[e['id'] for e in entries],
            'entries':entries,'count':total,'complete':complete,'status':'complete' if complete else 'partial',
            'issues':sorted(set(issues)),'source':'owned_operator_buff_popup',
            'header_evidence':{'box':[list(p) for p in header['box']]},
            'popup_evidence':{'box':[[region[0]/width,region[1]/height],
            [region[2]/width,region[1]/height],[region[2]/width,region[3]/height],[region[0]/width,region[3]/height]]}}
