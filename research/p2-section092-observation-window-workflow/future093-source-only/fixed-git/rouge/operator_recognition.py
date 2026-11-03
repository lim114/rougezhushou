"""Read operator training; icon matches are gated by score and ambiguity."""
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np
from .catalog import operator_profiles
from .anchors import units,crop as anchor_crop

def center(record):
    return tuple(sum(point[axis] for point in record['box'])/4 for axis in (0,1))

def normalized_name(text):
    return ''.join(c for c in unicodedata.normalize('NFKC',text).casefold() if c.isalnum())

def training_units(image,texts,anchor,font):
    elite=[t for t in texts if t['text']=='精英化' and t['confidence']>=.9]
    potential=[t for t in texts if t['text']=='潜能' and t['confidence']>=.9]
    if len(elite)==len(potential)==1:
        h,w=image.shape[:2]
        ux=(center(potential[0])[0]-center(elite[0])[0])/(.9539-.8243)
        if ux>0:return ux,ux*w/h*1127/2052
    return units(image,anchor,font)

@lru_cache(maxsize=1)
def identity_index():
    result={}
    for key,profile in operator_profiles().items():
        for name in set([profile['name'],*profile.get('aliases',[])]):
            if name:result.setdefault(normalized_name(name),set()).add(key)
    return result

def match_identity(texts):
    matches=None
    for record in texts:
        x,y=center(record)
        if record['confidence']<.85:continue
        candidates=identity_index().get(normalized_name(record['text']),set())
        if candidates:matches=candidates if matches is None else matches&candidates
    if not matches:return None
    if len(matches)>1:
        # Amiya's forms share both names. The visible subclass must disambiguate them.
        matches={key for key in matches if any(t['text']==operator_profiles()[key].get('subprofession')
                 and t['confidence']>=.85 for t in texts)}
    if len(matches)!=1:return None
    key=next(iter(matches))
    return key,operator_profiles()[key]

def refine_training_texts(image,texts,engine):
    """Recover small labels from current semantic anchors, never a screen slot."""
    h,w=image.shape[:2]
    def reread(anchor,font,bounds,scale=2):
        x,y=center(anchor);ux,uy=units(image,anchor,font)
        a,b,c,d=bounds
        x0=max(0,round((x+a*ux)*w));y0=max(0,round((y+b*uy)*h))
        x1=min(w,round((x+c*ux)*w));y1=min(h,round((y+d*uy)*h))
        roi=image[y0:y1,x0:x1]
        if not roi.size:return []
        raw,_=engine(cv2.resize(roi,None,fx=scale,fy=scale))
        return [{'text':text.replace(' ',''),'confidence':float(score),
            'box':[[(px/scale+x0)/w,(py/scale+y0)/h] for px,py in box]}
            for box,text,score in raw or [] if score>=.8]
    if not any(t['text'].upper() in ('LV','EXP') for t in texts):
        elite=[t for t in texts if t['text']=='精英化' and t['confidence']>=.9]
        if len(elite)==1:texts=texts+reread(elite[0],36.3,(-.16,-.30,.14,-.07))
    exp=[t for t in texts if t['text']=='EXP' and t['confidence']>=.9]
    level=[t for t in texts if re.fullmatch(r'[IV]?LV',t['text'].upper()) and t['confidence']>=.65]
    if not level and len(exp)==1:
        texts+=reread(exp[0],18.6,(-.10,-.065,-.005,.025),3)
    level=[t for t in texts if re.fullmatch(r'[IV]?LV',t['text'].upper()) and t['confidence']>=.65]
    if len(level)==1:
        a=level[0];x,y=center(a);ux,uy=units(image,a,23.8)
        if not any(re.fullmatch(r'/\d{2}',t['text']) and t['confidence']>=.9
            and abs(center(t)[0]-x)<.10*ux and 0<center(t)[1]-y<.16*uy for t in texts):
            texts+=reread(a,23.8,(.005,.04,.10,.15),3)
    trust=[t for t in texts if t['text']=='信赖值' and t['confidence']>=.9]
    if len(trust)==1:
        a=trust[0];x,y=center(a);ux,uy=units(image,a,35.2)
        if not any(re.fullmatch(r'\d{1,3}%',t['text']) and t['confidence']>=.9
            and 0<center(t)[0]-x<.35*ux and abs(center(t)[1]-y)<.035*uy for t in texts):
            texts+=reread(a,35.2,(.08,-.04,.36,.04),2)
    return texts

def read_skill_markers(image,anchor,count,space=None):
    """Read the three white/dark mastery pips and the blue selection corner.

    Layout is anchored to RANK, never to an operator portrait/name length.
    Unclear contrast yields unknown rather than mastery zero.
    """
    ux,uy=space or units(image,anchor,24.9)
    h,w=image.shape[:2];x,y=center(anchor)
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    masteries={};blue_scores=[]
    for i in range(count):
        base=x-.207*ux+i*.058*ux
        roi=gray[max(0,int((y-.045*uy)*h)):min(h,int((y-.022*uy)*h)),
                 max(0,int(base*w)):min(w,int((base+.014*ux)*w))]
        if roi.size:
            background=float(np.percentile(roi,15))
            dots=[]
            for dx,dy in ((.008,-.0353),(.0053,-.027),(.0106,-.027)):
                cx=round((base+dx*ux)*w);cy=round((y+dy*uy)*h);radius=max(1,round(h*.0023*uy))
                core=gray[max(0,cy-radius):cy+radius+1,max(0,cx-radius):cx+radius+1]
                value=float(np.median(core)) if core.size else 0
                if value>=205 and background<100:dots.append(1)
                elif 35<=value<=105 and value-background>=10:dots.append(0)
                else:dots.append(None)
            if None not in dots:masteries[i+1]=sum(dots)
        corner=image[max(0,int((y-.045*uy)*h)):min(h,int((y-.015*uy)*h)),
                     max(0,int((x-.167*ux+i*.058*ux)*w)):min(w,int((x-.146*ux+i*.058*ux)*w))]
        if corner.size:
            hsv=cv2.cvtColor(corner,cv2.COLOR_BGR2HSV)
            mask=cv2.inRange(hsv,np.array([90,150,150]),np.array([115,255,255]))
            blue_scores.append(float(np.count_nonzero(mask))/mask.size)
        else:blue_scores.append(0)
    ranked=sorted([(score,i+1) for i,score in enumerate(blue_scores)],reverse=True)
    selected=ranked[0][1] if ranked and ranked[0][0]>.08 and (len(ranked)==1 or ranked[0][0]-ranked[1][0]>.06) else None
    return masteries,selected

def selected_module_row(image,anchor):
    """The selected module card has a white arrow at its right edge."""
    x,y=center(anchor);h,w=image.shape[:2]
    ux,uy=units(image,anchor,36.3)
    right=max(p[0] for p in anchor['box'])
    roi=anchor_crop(image,(right,y-.01*uy,1,y+.18*uy))
    if not roi.size:return False
    reference=cv2.imdecode(np.fromfile(Path(__file__).parent/'data/ui-icons/module-selected-arrow.png',dtype=np.uint8),0)
    gray=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
    best=0
    for factor in np.arange(.65,1.41,.05):
        scale=h*uy/1127*factor
        ref=cv2.resize(reference,None,fx=scale,fy=scale)
        if ref.shape[0]>=gray.shape[0] or ref.shape[1]>=gray.shape[1]:continue
        scores=cv2.matchTemplate(gray,ref,cv2.TM_CCOEFF_NORMED)
        best=max(best,float(scores.max()))
    return best>=.85


def read_module_page(image,texts):
    labels={t['text'] for t in texts if t['confidence']>=.85}
    if '基础数值' not in labels or 'ORIGINAL' not in labels:return None
    matches=[]
    for key,profile in operator_profiles().items():
        for module in profile['modules']:
            for t in texts:
                if t['text']==module['name'] and t['confidence']>=.9:
                    matches.append((key,module,t))
    owners={key for key,_,_ in matches}
    if len(owners)!=1:return None
    key=owners.pop();profile=operator_profiles()[key]
    fields={};sources={};viewed=[]
    attribute_labels={'atk':('攻击',),'def':('防御',),'max_hp':('生命上限',),'magic_resistance':('法术抗性',)}
    changes={}
    for attr,names in attribute_labels.items():
        anchors=[t for t in texts if t['confidence']>=.8 and
                 any(name in t['text'] for name in names) and '速度' not in t['text']]
        for anchor in anchors:
            _,y=center(anchor)
            for t in texts:
                m=re.fullmatch(r'\d+(?:\.\d+)?\(\+(\d+(?:\.\d+)?)\)',t['text'])
                if m and t['confidence']>=.9 and center(t)[0]>center(anchor)[0] and abs(center(t)[1]-y)<.65*(max(p[1] for p in anchor['box'])-min(p[1] for p in anchor['box'])):
                    changes[attr]=float(m.group(1))
    for owner,module,anchor in matches:
        equipped=selected_module_row(image,anchor)
        stages=[phase['level'] for phase in module['levels'] if changes and
                all(phase['attributes'].get(attr)==value for attr,value in changes.items())]
        stage=stages[0] if len(stages)==1 else None
        viewed.append({'id':module['id'],'name':module['name'],'level':stage,'equipped':equipped})
        if equipped and stage:
            fields.update(module_id=module['id'],module_level=stage)
            sources['module_id']='模组面板名称与当前选中卡右侧白色箭头'
            sources['module_level']='模组属性增量与档案阶段唯一对应'
    for name in profile.get('initial_modules',[]):
        anchor=next((t for t in texts if t['text']==name and t['confidence']>=.9),None)
        if anchor and selected_module_row(image,anchor):
            fields.update(module_id=None,module_level=0);sources['module_id']='当前选中基础证章'
    missing=[field for field in ('level','elite','potential','trust','module_id','module_level') if field not in fields]
    missing+=['skill_rank_'+str(i+1) for i in range(len(profile['skills']))]
    if profile['skills']:missing.append('selected_skill')
    return {'id':key,'name':profile['name'],'scope':'operator_profile','fields':fields,'sources':sources,
            'skill_ranks':{},'viewed_modules':viewed,'missing_fields':missing,'complete':False,
            'limitations':['模组页面只更新有证据的装备字段；培养及技能信息由同一干员详情页补齐。']}

@lru_cache(maxsize=1)
def potential_icons():
    folder=Path(__file__).parent/'data/ui-icons'
    return {rank:cv2.imdecode(np.fromfile(folder/f'potential-{rank}.png',dtype=np.uint8),cv2.IMREAD_UNCHANGED)
            for rank in range(1,7)}

def match_potential(image,anchor,*,cache=None):
    ux,uy=units(image,anchor,38.3)
    h,w=image.shape[:2]
    box=anchor['box']
    left=min(p[0] for p in box);right=max(p[0] for p in box)
    top=min(p[1] for p in box);bottom=max(p[1] for p in box)
    label_height=(bottom-top)*h
    x0=max(0,int((left-.13*ux)*w));x1=min(w,int((right-.01*ux)*w))
    y0=max(0,int((top-.09*uy)*h));y1=min(h,int((bottom+.10*uy)*h))
    roi=image[y0:y1,x0:x1]
    if not roi.size or label_height<6:return None
    if cache is not None:
        return cache.call(roi,('potential',label_height),lambda: _match_potential_roi(roi,label_height))
    return _match_potential_roi(roi,label_height)


def _match_potential_roi(roi,label_height):
    scores=[]
    for rank,original in potential_icons().items():
        best=0
        for ratio in np.arange(2.3,4.6,.1):
            size=round(label_height*ratio)
            if size<12 or size>=min(roi.shape[:2]):continue
            template=cv2.resize(original,(size,size),interpolation=cv2.INTER_AREA)
            mask=(template[:,:,3]>200).astype(np.uint8)*255
            differences=cv2.matchTemplate(roi,template[:,:,:3],cv2.TM_SQDIFF_NORMED,mask=mask)
            differences=np.nan_to_num(differences,nan=100,posinf=100,neginf=100)
            best=max(best,1-float(differences.min()))
        scores.append((best,rank))
    scores.sort(reverse=True)
    best,rank=scores[0];margin=best-scores[1][0]
    if best<.90 or margin<.025:return None
    return {'value':rank,'score':best,'margin':margin,'source':'game potential icon templates 1–6'}

def read_skill_crops(image,texts,engine,count=3):
    """Split the three skill cards on the verified desktop detail layout.

    Each result still needs a unique SP pair in the versioned skill table.
    """
    anchors=[t for t in texts if t['confidence']>=.90 and re.fullmatch(r'RANK[1-7]',t['text'].upper())]
    if len(anchors)!=1:return None
    ux,uy=training_units(image,texts,anchors[0],24.9)
    x,y=center(anchors[0]);h,w=image.shape[:2]
    records=[]
    for index in range(count):
        x0=max(0,int((x-.204*ux+index*.058*ux)*w));x1=min(w,int((x-.146*ux+index*.058*ux)*w))
        y0=max(0,int((y+.021*uy)*h));y1=min(h,int((y+.079*uy)*h))
        roi=image[y0:y1,x0:x1]
        if roi.size==0:records.append(None);continue
        raw,_=engine(cv2.resize(roi,None,fx=3,fy=3,interpolation=cv2.INTER_LINEAR))
        candidates=sorted(raw or [],key=lambda r:sum(p[0] for p in r[0])/4)
        if not candidates or any(score<.85 for _,_,score in candidates):records.append(None);continue
        digits=''.join(text.replace(' ','') for _,text,_ in candidates)
        if not re.fullmatch(r'\d{2,6}',digits):records.append(None);continue
        records.append({'text':digits,'confidence':min(r[2] for r in candidates)})
    return records

def read_operator(image,texts,skill_sp_texts=None,*,icon_cache=None):
    identity=match_identity(texts)
    if not identity:return None
    key,profile=identity
    markers={t['text']:t for t in texts if t['confidence']>=.80}
    if sum(name in markers for name in ('LV','信赖值','潜能','精英化'))<2:return None
    fields={};sources={};skill_ranks={}
    level_anchors=[t for t in texts if t['confidence']>=.65 and re.fullmatch(r'[IV]?LV',t['text'].upper())
                  ]
    if len(level_anchors)==1:
        x,y=center(level_anchors[0]);ux,uy=units(image,level_anchors[0],23.8)
        levels=[t for t in texts if re.fullmatch(r'\d{1,2}',t['text']) and t['confidence']>=.90
                and abs(center(t)[0]-x)<.06*ux and 0<center(t)[1]-y<.10*uy]
        if len(levels)==1:
            fields['level']=int(levels[0]['text']);sources['level']='LV 数字'
        caps=[int(t['text'][1:]) for t in texts if re.fullmatch(r'/\d{2}',t['text']) and t['confidence']>=.90
              and abs(center(t)[0]-x)<.10*ux and 0<center(t)[1]-y<.16*uy]
        if len(caps)==1:
            phases=[index for index,phase in enumerate(profile['phases']) if phase['max_level']==caps[0]]
            if len(phases)==1:fields['elite']=phases[0];sources['elite']='等级上限与本干员档案唯一匹配'
    if 'elite' not in fields or 'level' not in fields:
        exp=[t for t in texts if t['text']=='EXP' and t['confidence']>=.9]
        if len(exp)==1:
            x,y=center(exp[0]);ux,uy=units(image,exp[0],18.6)
            levels=[t for t in texts if t['confidence']>=.9 and re.fullmatch(r'\d{1,2}',t['text'])
                    and .015*ux<x-center(t)[0]<.10*ux and abs(center(t)[1]-y)<.04*uy]
            caps=[t for t in texts if t['confidence']>=.9 and re.fullmatch(r'/\d{2}',t['text'])
                  and abs(center(t)[0]-x)<.05*ux and .02*uy<center(t)[1]-y<.10*uy]
            if len(levels)==len(caps)==1:
                level,cap=int(levels[0]['text']),int(caps[0]['text'][1:])
                phases=[i for i,phase in enumerate(profile['phases']) if phase['max_level']==cap]
                if len(phases)==1 and 1<=level<=cap:
                    fields.update(level=level,elite=phases[0]);sources.update(level='EXP 左侧等级与相邻 /等级上限交叉确认',elite='相邻等级上限与本干员档案唯一匹配')
    if '信赖值' in markers:
        x,y=center(markers['信赖值']);ux,uy=units(image,markers['信赖值'],35.2)
        candidates=[t for t in texts if re.fullmatch(r'\d{1,3}%',t['text']) and t['confidence']>=.90
                    and 0<center(t)[0]-x<.35*ux and abs(center(t)[1]-y)<.035*uy]
        if len(candidates)==1:
            value=int(candidates[0]['text'][:-1])
            if 0<=value<=200:
                fields.update(trust=min(value,100),trust_display=value);sources['trust']='信赖值百分比；100% 起属性加成封顶'
    potential=match_potential(image,markers['潜能'],cache=icon_cache) if '潜能' in markers else None
    if potential:fields['potential']=potential['value'];sources['potential']=potential
    if not profile['modules']:
        fields.update(module_id=None,module_level=0);sources['module_id']='固定数据版本中本干员无可装备模组'
    else:
        # On the operator overview STAGE is shown only for the equipped module.
        stages=[int(m.group(1)) for t in texts if t['confidence']>=.90 and (m:=re.fullmatch(r'STAGE[.：:]?([123])',t['text'].upper()))]
        if len(stages)==1 and len(profile['modules'])==1:
            fields.update(module_id=profile['modules'][0]['id'],module_level=stages[0])
            sources['module_id']='详情页装备区 STAGE 与本干员唯一模组匹配'
        elif len(stages)==1:
            matches=[m for m in profile['modules'] if any(normalized_name(t['text'])==normalized_name(m['type'])
                     and t['confidence']>=.85 for t in texts)]
            if len(matches)==1:
                fields.update(module_id=matches[0]['id'],module_level=stages[0])
                sources['module_id']='详情页装备区模组型号与 STAGE'
        if 'elite' in fields and 'level' in fields and all(fields['elite']<m['unlock_elite'] or
                (fields['elite']==m['unlock_elite'] and fields['level']<m['unlock_level']) for m in profile['modules']):
            fields.update(module_id=None,module_level=0)
            sources['module_id']='实际精英/等级低于所有可装备模组门槛'
        for module in profile['modules']:
            if module['name'] in markers:
                stage=next((int(m.group(1)) for t in texts
                            if (m:=re.fullmatch(r'(?:STAGE|等级|阶段)[.：:]?([123])',t['text'].upper()))),None)
                if stage and any(t['text'] in ('已装备','卸下模组') and t['confidence']>=.9 for t in texts):
                    fields.update(module_id=module['id'],module_level=stage);sources['module_id']='模组名称与阶段文字'
    rank_records=[(t,int(m.group(1))) for t in texts
                  if t['confidence']>=.90 and (m:=re.fullmatch(r'RANK([1-7])',t['text'].upper()))]
    if len(rank_records)==1:
        anchor,common_rank=rank_records[0];x,y=center(anchor);ux,uy=training_units(image,texts,anchor,24.9)
        mastery,selected=read_skill_markers(image,anchor,len(profile['skills']),(ux,uy))
        if selected:fields['selected_skill']=selected;sources['selected_skill']='技能卡蓝色选中角标'
        if common_rank<7:
            skill_ranks={i:common_rank for i in range(1,len(profile['skills'])+1)}
        else:
            sp_records=[t for t in texts if t['confidence']>=.90 and re.fullmatch(r'\d{3,6}',t['text'])
                        and x-.25*ux<center(t)[0]<x-.04*ux and .015*uy<center(t)[1]-y<.09*uy]
            sp_records.sort(key=lambda t:center(t)[0])
            if skill_sp_texts is not None:sp_records=skill_sp_texts
            if len(sp_records)==len(profile['skills']):
                for i,record in enumerate(sp_records):
                    if record is None:continue
                    digits=record['text'];matches=[]
                    for rank,level in enumerate(profile['skills'][i]['levels'],1):
                        initial=str(level['initial_sp']);cost=str(level['sp_cost'])
                        if rank>=common_rank and digits.startswith(initial) and digits.endswith(cost) and 0<=len(digits)-len(initial)-len(cost)<=1:
                            matches.append(rank)
                    if len(matches)==1:skill_ranks[i+1]=matches[0]
            for skill,stage in mastery.items():
                rank=7+stage
                if skill in skill_ranks and skill_ranks[skill]!=rank:
                    skill_ranks.pop(skill)
                    sources.setdefault('conflicts',[]).append(f'S{skill} 图标与技力等级冲突')
                else:skill_ranks[skill]=rank
            sources['mastery_markers']=mastery
    required=['level','elite','potential','trust','module_id','module_level']
    missing=[field for field in required if field not in fields]
    missing+=['skill_rank_'+str(i+1) for i in range(len(profile['skills'])) if i+1 not in skill_ranks]
    if profile['skills'] and 'selected_skill' not in fields:missing.append('selected_skill')
    return {'id':key,'name':profile['name'],'scope':'operator_profile','fields':fields,'sources':sources,'skill_ranks':skill_ranks,
            'missing_fields':missing,'complete':not missing,
            'limitations':['只合并已确认字段；图标模糊或匹配多解时拒绝判断。',
                            '读取档案覆盖本数据版本可获得干员；不同页面布局仍需实机验证，缺失字段逐项列出。']}
