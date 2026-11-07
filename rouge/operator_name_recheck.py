"""Current-pixel rechecks; similarity locates work but never supplies a name."""
from copy import deepcopy
import cv2
from .operator_recognition import identity_index,normalized_name,center


def recheck_run_names(image,texts,engine):
    anchors={t['text']:t for t in texts if t['confidence']>=.9}
    if not all(k in anchors for k in ('技能','分支+','收藏品增益')):
        return texts
    index=identity_index();names={n for n,ids in index.items() if len(ids)==1}
    by_length={}
    for name in names:
        by_length.setdefault(len(name),[]).append(name)
    footer_y=center(anchors['收起'])[1] if '收起' in anchors else None
    h,w=image.shape[:2];out=deepcopy(texts);cross_checks=[]
    for position,record in enumerate(texts):
        name=normalized_name(record['text'])
        if name in names and record['confidence']>=.9:continue
        if record['confidence']<.7 or len(name)<3:continue
        # One substituted character locates a line for OCR; only an exact reread can name it.
        if not any(sum(a!=b for a,b in zip(other,name))<=1 for other in by_length.get(len(name),())):continue
        # Work is bounded to observed rows on this roster. No previous run,
        # selected UI value, fixed screenshot coordinates or fuzzy identity.
        if footer_y is not None and center(record)[1]>=footer_y:continue
        xs=[p[0]*w for p in record['box']];ys=[p[1]*h for p in record['box']]
        height=max(ys)-min(ys)
        if height<=0:continue
        margin=max(2,round(height*.12))
        x0=max(0,int(min(xs))-margin);x1=min(w,int(max(xs))+margin+1)
        y0=max(0,int(min(ys))-margin);y1=min(h,int(max(ys))+margin+1)
        crop=image[y0:y1,x0:x1]
        if not crop.size:continue
        gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
        binary=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        # Normalize polarity using the border, keeping every observed stroke.
        if (float(binary[0].mean())+float(binary[-1].mean()))/2<127:
            binary=255-binary
        raw,_=engine(cv2.resize(binary,None,fx=4,fy=4),use_det=False,use_cls=False)
        if len(raw or [])!=1:continue
        exact=normalized_name(raw[0][0]);score=float(raw[0][1])
        if exact not in names or score<.9:continue
        revised={'text':exact,'confidence':score,'box':deepcopy(record['box']),
            'name_recheck':{'source':'current_observed_name_line_otsu_recognizer',
                'original_text':record['text'],'original_confidence':record['confidence'],
                'exact_identity_verified':True}}
        if score>=.95:out[position]=revised
        else:cross_checks.append((position,revised))
    for position,revised in cross_checks:
        # Keep the ordinary owner threshold (.9), but require a second exact
        # current-frame location at .95. A repeated crop of the same line does
        # not constitute corroboration, nor does a previous roster record.
        cx,cy=center(revised)
        height=max(p[1] for p in revised['box'])-min(p[1] for p in revised['box'])
        peer=next((t for i,t in enumerate(out) if i!=position and t['confidence']>=.95 and
            normalized_name(t['text'])==revised['text'] and
            abs((pos:=center(t))[0]-cx)+abs(pos[1]-cy)>height*2),None)
        if peer is None:continue
        revised['name_recheck']['corroborating_evidence']={
            'box':deepcopy(peer['box']),'confidence':peer['confidence'],
            'source':'second_exact_current_frame_name_location'}
        out[position]=revised
    return out
