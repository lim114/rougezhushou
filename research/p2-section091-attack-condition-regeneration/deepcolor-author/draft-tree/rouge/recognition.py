"""Visible observations only. OCR confidence is not a hidden-node probability."""
import time,json
from copy import deepcopy
import numpy as np
import cv2
from .catalog import catalog, stage_previews, operator_profiles
from .operator_recognition import read_operator, read_skill_crops, refine_training_texts,read_module_page
from .run_recognition import read_run
from .viewport import prepare_frame,map_evidence
from .map_recognition import read_map
from .recognition_cache import ExactImageCache,CachedOCR
from .node_events import read_node_content,annotate_map_content
from .dynamic_ocr import DynamicOCR,normalize_regions
from .anchors import units

def node_names():
    return {'未知的凶戾', '未知的诡秘'} | {
        value['name'] for value in catalog().get('node_types', {}).values()}

def refine_map_texts(image,texts,nodes,engine):
    """A sparse coarse pass triggers overlapping OCR tiles around actual labels."""
    h,w=image.shape[:2]
    font=float(np.median([(max(p[1] for p in n['box'])-min(p[1] for p in n['box']))*h for n in nodes]))
    xs=[p[0]*w for n in nodes if not n.get('detail_panel_label') for p in n['box']]
    ys=[p[1]*h for n in nodes if not n.get('detail_panel_label') for p in n['box']]
    if not xs:return texts
    x0=max(0,round(min(xs)-font*14));x1=min(w,round(max(xs)+font*14))
    y0=max(0,round(min(ys)-font*6));y1=min(h,round(max(ys)+font*4))
    extra=[]
    # Tiles cover the discovered area; their positions are not field coordinates.
    for left in range(x0,x1,1000):
        right=min(x1,left+1100);roi=image[y0:y1,left:right]
        if not roi.size:continue
        raw,_=engine(roi)
        for box,text,score in raw or []:
            record={'text':text.replace(' ',''),'confidence':float(score),
                    'box':[[(float(x)+left)/w,(float(y)+y0)/h] for x,y in box]}
            cx=sum(p[0] for p in record['box'])/4;cy=sum(p[1] for p in record['box'])/4
            if any(t['text']==record['text'] and abs(sum(p[0] for p in t['box'])/4-cx)<font/w
                   and abs(sum(p[1] for p in t['box'])/4-cy)<font/h for t in extra):continue
            extra.append(record)
    kept=[t for t in texts if not (x0/w<sum(p[0] for p in t['box'])/4<x1/w
                                   and y0/h<sum(p[1] for p in t['box'])/4<y1/h)]
    return kept+extra

class ScreenReader:
    def __init__(self, *, cache_enabled=True,page_routing_enabled=True,page_ocr_enabled=True):
        self._engine = None
        self._frame_ocr = None
        self.cache_enabled = cache_enabled
        self.page_routing_enabled=page_routing_enabled
        self.page_ocr_enabled=page_ocr_enabled
        self._page_ocr=None
        self._page_router=None;self._page_route_age=0;self._page_route_retry_after=0
        self._page_verified_identity=None
        self._last_frame = self._last_rect = self._last_result = None
        self._last_context = None
        self._icon_cache = ExactImageCache(max_bytes=2*1024*1024,max_entries=8) if cache_enabled else None

    def read(self, image, *, client_rect=None,run_context=None):
        started = time.perf_counter()
        if image is None or image.size == 0:
            raise ValueError('没有有效画面。')
        rect = tuple(client_rect) if client_rect is not None else None
        if run_context is None:context=None
        else:
            from .run_config import confirmed_config
            fields={'value','modeDifficulty','id','name','level','usage','effect_verified','source'}
            context=json.dumps({'run_id':run_context.get('run_id'),
                'config':{key:{k:v for k,v in record.items() if k in fields}
                          for key,record in confirmed_config(run_context).items()}},sort_keys=True,ensure_ascii=False)
        previous = self._last_frame
        if (self.cache_enabled and previous is not None and rect == self._last_rect and context==self._last_context
                and image.shape == previous.shape and image.dtype == previous.dtype
                and np.array_equal(image, previous)):
            result = deepcopy(self._last_result)
            result['observed_at'] = time.time()
            result['performance'] = {'reuse': 'exact_frame', 'total_ms': (time.perf_counter()-started)*1000,
                'icon_cache_hits': 0, 'ocr_cache_hits': 0, 'stages_ms': {}}
            return result
        icon_hits = self._icon_cache.hits if self._icon_cache else 0
        ocr_hits = self._engine.cache.hits if isinstance(self._engine,CachedOCR) else 0
        result = self._read(image, client_rect=client_rect,run_context=run_context)
        result['performance'].update(reuse='none',total_ms=(time.perf_counter()-started)*1000,
            icon_cache_hits=self._icon_cache.hits-icon_hits if self._icon_cache else 0,
            ocr_cache_hits=self._engine.cache.hits-ocr_hits if isinstance(self._engine,CachedOCR) else 0)
        if self.cache_enabled and image.nbytes <= 32*1024*1024:
            # One frame only; the source client rectangle is part of identity.
            # No approximate hashes or timestamps stand in for pixel equality.
            self._last_frame = image.copy()
            self._last_rect = rect
            self._last_context = context
            self._last_result = deepcopy(result)
        else:
            self._last_frame = self._last_rect = self._last_result = None
            self._last_context = None
        return result

    def _read(self, image, *, client_rect=None,run_context=None):
        timings = {}
        mark = time.perf_counter()
        def elapsed(name):
            nonlocal mark
            now = time.perf_counter()
            timings[name] = timings.get(name,0.0)+(now-mark)*1000
            mark = now
        if self._engine is None:
            from rapidocr_onnxruntime import RapidOCR
            self._engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)
            if self.cache_enabled: self._engine = CachedOCR(self._engine)
            self._frame_ocr=DynamicOCR(self._engine) if self.cache_enabled else self._engine
        elapsed('initialization')
        if image is None or image.size == 0:
            raise ValueError('没有有效画面。')
        image,viewport=prepare_frame(image,client_rect)
        elapsed('viewport')
        routing={'strategy':'full_discovery','candidates':[],'visual_ms':0.,
                 'fallback_reason':'disabled' if not self.page_routing_enabled else None}
        regions=None;page_identity=None;force_discovery=False;page_batches=False
        if self.page_routing_enabled:
            from .page_features import PageFeatureRouter
            try:
                if self._page_router is None:self._page_router=PageFeatureRouter()
                plan=self._page_router.classify(image)
                routing.update(candidates=[c['page'] for c in plan['candidates']],
                    visual_ms=plan['elapsed_ms'],fallback_reason=plan['fallback_reason'])
                routing['feature_reuse']=plan.get('feature_reuse','none')
                if plan['specialized'] and len(plan['candidates'])==1:
                    candidate=plan['candidates'][0]
                    # Quantize outward from current visual anchors, rather than
                    # stored screenshot coordinates. Minor affine jitter does
                    # not repeatedly discard an otherwise identical domain.
                    domain=normalize_regions([[np.floor(x0/16)*16,np.floor(y0/16)*16,
                        np.ceil(x1/16)*16,np.ceil(y1/16)*16]
                        for x0,y0,x1,y1 in candidate['regions']],image.shape[:2])
                    page_identity=(candidate['page'],image.shape,image.dtype.str,domain)
                    if self.page_ocr_enabled and domain is not None:
                        from .page_ocr import PageOCR
                        if self._page_ocr is None or getattr(self._page_ocr,'engine',self._engine) is not self._engine:
                            self._page_ocr=PageOCR(self._engine,cache_enabled=self.cache_enabled)
                        page_batches=self._page_ocr._supported()
                    if page_batches:
                        # The visual candidate chooses current region priority.
                        # Full current DET boxes and exterior text still return,
                        # so first entry need not OCR the frame twice for trust.
                        regions=domain
                        routing.update(strategy='visual_region_ocr',fallback_reason=None)
                    elif not self.cache_enabled:
                        routing['fallback_reason']='cache_disabled'
                        force_discovery=True
                    elif self._page_verified_identity!=page_identity or domain is None:
                        routing['fallback_reason']='page_initial_discovery'
                        force_discovery=True
                    elif self._page_route_retry_after:
                        routing['fallback_reason']='semantic_retry_backoff'
                    elif self._page_route_age>=8:
                        routing['fallback_reason']='periodic_full_discovery';force_discovery=True
                    else:
                        regions=domain
                        routing.update(strategy='page_regions',fallback_reason=None)
            except (cv2.error,ValueError,OSError) as error:
                routing['fallback_reason']='visual_unavailable:'+type(error).__name__
        if self._page_route_retry_after:self._page_route_retry_after-=1
        elapsed('page_features')
        if page_batches:
            raw,_=self._page_ocr.read(image,regions=regions)
            if isinstance(self._frame_ocr,DynamicOCR):
                # Never seed the legacy dirty-domain reader with another
                # strategy's retained text. A later unknown page starts fresh.
                self._frame_ocr.image=None;self._frame_ocr.raw=[]
                self._frame_ocr.regions=None;self._frame_ocr.age=0
                self._frame_ocr.metrics=dict(self._page_ocr.metrics)
        elif isinstance(self._frame_ocr,DynamicOCR):
            raw,_=self._frame_ocr(image,regions=regions,seed_from_full=True,
                force_discovery=force_discovery,guard_outside=regions is not None)
        else:raw,_=self._frame_ocr(image)
        if not page_batches and regions is not None and isinstance(self._frame_ocr,DynamicOCR) and self._frame_ocr.regions is None:
            regions=None
            reason=('page_outside_regions_changed' if
                self._frame_ocr.metrics.get('outside_page_regions_changed') else 'page_changed_area_full')
            routing.update(strategy='full_discovery',fallback_reason=reason)
        elapsed('full_ocr')
        result=self._interpret(image,viewport,raw,elapsed,timings,run_context=run_context)
        if page_batches:
            result['performance']['ocr']=dict(self._page_ocr.metrics)
            coverage_verified=self._page_ocr.metrics.get('complete_current_texts') is True
            routing['semantic_verified']=coverage_verified and specialized_observation_valid(result,routing['candidates'][0])
            # Every current detector box has already been read. Rejecting an
            # incomplete/conflicting page hint must not repeat that same OCR.
            if not coverage_verified:
                routing.update(strategy='full_discovery',fallback_reason=
                    self._page_ocr.metrics.get('fallback_reason','region_coverage_unverified'))
            elif not routing['semantic_verified']:
                routing.update(strategy='full_discovery',
                    fallback_reason='semantic_validation_failed_complete_text')
                self._page_route_retry_after=2
            regions=None
        if regions is not None and not specialized_observation_valid(result,routing['candidates'][0]):
            # Never accept a guessed page or an incomplete specialized read.
            # Start fresh over the whole current frame, not prior-page values.
            routing.update(strategy='full_discovery',fallback_reason='semantic_validation_failed')
            self._page_route_retry_after=2
            if isinstance(self._frame_ocr,DynamicOCR):raw,_=self._frame_ocr(image,regions=None,force_discovery=True)
            else:raw,_=self._frame_ocr(image)
            elapsed('fallback_full_ocr')
            result=self._interpret(image,viewport,raw,elapsed,timings,run_context=run_context)
        self._page_route_age=self._page_route_age+1 if routing['strategy']=='page_regions' else 0
        self._page_verified_identity=(page_identity if page_identity is not None and
            specialized_observation_valid(result,page_identity[0]) else None)
        result['performance']['routing']=routing
        return result

    def _interpret(self,image,viewport,raw,elapsed,timings,*,run_context=None):
        h, w = image.shape[:2]
        texts = [{'text': text.replace(' ', ''), 'confidence': float(score),
                  'box': [[float(x)/w, float(y)/h] for x,y in box]} for box,text,score in (raw or [])]
        nodes = []
        for record in texts:
            # This font repeatedly reads 戾 as 房 on captured maps. Preserve
            # raw OCR and only normalize the exact known placeholder spelling.
            label_text = {'未知的凶房': '未知的凶戾', '未知的诡利': '未知的诡秘'}.get(record['text'], record['text'])
            for name in node_names():
                if label_text == name and record['confidence'] >= .7:
                    nodes.append({'type': name, 'box': record['box'], 'confidence': record['confidence'],
                                  'hidden': name.startswith('未知'), 'prediction': None})
                    break
        stage = None
        for record in texts:
            if record['confidence'] < .8:
                continue
            matches = [(sid, s) for sid,s in catalog()['stages'].items() if s['name'] == record['text']]
            if matches:
                sid, s = matches[0]
                stage = {'id': sid if len(matches) == 1 else None, **s, 'confidence': record['confidence'],
                         'variants': [{'id': k, **v, 'preview': stage_previews().get(k)} for k,v in matches]}
                break
        all_text = '\n'.join(t['text'] for t in texts)
        detail = '敌方情报' in all_text and '地图' in all_text
        if detail and stage:
            title=next(t for t in texts if t['text']==stage['name'])
            ux,uy=units(image,title,35.2)
            tx=sum(p[0] for p in title['box'])/4;ty=sum(p[1] for p in title['box'])/4
            labels=[t for t in texts if t['confidence']>=.95 and t['text'] in ('作战','紧急作战')
                and abs(sum(p[0] for p in t['box'])/4-tx)<.20*ux
                and 0<ty-sum(p[1] for p in t['box'])/4<.10*uy]
            for node in nodes:
                if any(node['box']==t['box'] for t in labels):node['detail_panel_label']=True
            if len(labels)==1:
                difficulty='FOUR_STAR' if labels[0]['text']=='紧急作战' else 'NORMAL'
                variants=[v for v in stage['variants'] if v['difficulty']==difficulty]
                if len(variants)==1:
                    stage['visible_variant_id']=variants[0]['id']
                    stage['variant_source']='节点详情标题的'+labels[0]['text']+'标签'
        page = 'node_detail' if detail and stage else 'exploration' if nodes else 'unknown'
        elapsed('visible_labels')
        if sum(any(t['text']==name for t in texts) for name in ('信赖值','潜能','精英化'))>=2:
            texts=refine_training_texts(image,texts,self._engine)
        operator=read_operator(image,texts,icon_cache=self._icon_cache)
        if operator and len(operator['skill_ranks'])<len(operator_profiles()[operator['id']]['skills']):
            local_sp=read_skill_crops(image,texts,self._engine,len(operator_profiles()[operator['id']]['skills']))
            if local_sp:operator=read_operator(image,texts,local_sp,icon_cache=self._icon_cache)
        if operator:page='operator_detail'
        else:
            operator=read_module_page(image,texts)
            if operator:page='operator_module'
        elapsed('operator')
        run=read_run(image,texts,self._engine,icon_cache=self._icon_cache,run_context=run_context)
        elapsed('run')
        if run and run['page']=='run_roster':page='run_roster'
        elif run and any(t['text']=='收起' and t['confidence']>=.9 for t in texts):page='run_relics'
        content=read_node_content(image,texts,page,stage,nodes)
        if content and content['kind']=='event' and page=='unknown':page='node_event'
        if content and run is None:
            run={'page':'node_event','operators':[],
                 'relics':{'ids':[],'icons':[],'count':None,'source':'unread'}}
        elapsed('node_content')
        result={'observed_at': time.time(), 'page': page, 'size': viewport['source_size'], 'texts': texts,
                'nodes': nodes, 'stage': stage, 'drop_estimate': None,'operator':operator,'run':run,'node_content':content,
                'limitations': ['隐藏节点尚未预测；掉落概率尚未计算。', '战斗地图视觉识别待开发；敌人列表是本地关卡候选，属性未套用本局修正。']}
        result['map'] = read_map(image, texts, nodes, run) if page in ('exploration','node_detail') else None
        if result['map'] and result['map']['status']=='insufficient' and len(nodes)>=3:
            refined=refine_map_texts(image,texts,nodes,self._engine)
            found=[]
            for t in refined:
                name={'未知的凶房':'未知的凶戾','未知的诡利':'未知的诡秘'}.get(t['text'],t['text'])
                if name in node_names() and t['confidence']>=.7:
                    n={'type':name,'box':t['box'],'confidence':t['confidence'],
                       'hidden':name.startswith('未知'),'prediction':None}
                    if stage and detail:
                        title=next((v for v in refined if v['text']==stage['name']),None)
                        if title:
                            tx=sum(p[0] for p in title['box'])/4;ty=sum(p[1] for p in title['box'])/4
                            ux,uy=units(image,title,35.2)
                            if abs(sum(p[0] for p in t['box'])/4-tx)<.20*ux and 0<ty-sum(p[1] for p in t['box'])/4<.10*uy:
                                n['detail_panel_label']=True
                    found.append(n)
            refined_map=read_map(image,refined,found,run)
            if refined_map['status']=='matched':
                result.update(map=refined_map,texts=refined,nodes=found)
                if isinstance(self._frame_ocr,DynamicOCR):
                    self._frame_ocr.raw=[[[[p[0]*w,p[1]*h] for p in t['box']],t['text'],t['confidence']] for t in refined]
        annotate_map_content(result['map'],content)
        elapsed('map')
        if result['map'] and result['map']['status']=='matched':
            result['limitations'][0] = '隐藏节点提供社区约束候选，不是实际揭示或概率；掉落概率尚未计算。'
        map_evidence(result,viewport)
        if run and result['map']: run['map'] = result['map']
        # Attach shared objects after remapping, so coordinates are transformed once.
        if run and content: run['node_content'] = result['node_content']
        result['viewport']=viewport
        elapsed('evidence')
        result['performance'] = {'stages_ms':timings,
            'ocr':dict(self._frame_ocr.metrics) if isinstance(self._frame_ocr,DynamicOCR)
                  else {'mode':'full_discovery','pixels':h*w,'regions':1}}
        return result


def specialized_observation_valid(result,page):
    """Visual anchors schedule work; only current semantic readers accept it."""
    if page=='run_owned_popup':
        # The popup remains a run-roster observation. Its static controls do
        # not establish the selected owner, count, or completeness of buffs.
        if not specialized_observation_valid(result,'run_roster'):return False
        run=result['run'];selected=run.get('selected_operator')
        members=[member for member in run['operators']
                 if isinstance(member,dict) and member.get('id')==selected]
        if not selected or len(members)!=1:return False
        member=members[0];buffs=member.get('recipient_buffs')
        if not isinstance(buffs,dict):return False
        if (member.get('scope')!='run' or buffs.get('operator_id')!=selected
                or not member.get('name') or buffs.get('operator_name')!=member['name']
                or buffs.get('source')!='owned_operator_buff_popup'
                or type(buffs.get('count')) is not int or buffs['count']<=0):return False
        for key in ('header_evidence','popup_evidence'):
            evidence=buffs.get(key)
            if not isinstance(evidence,dict) or not evidence.get('box'):return False
        # A partial body is still attributable; retain its unknown entries.
        return True
    if page=='run_roster':
        run=result.get('run')
        return (result.get('page')=='run_roster' and isinstance(run,dict)
                and run.get('page')=='run_roster' and isinstance(run.get('operators'),list)
                and bool(run['operators']) and result.get('operator') is None
                and result.get('node_content') is None)
    operator=result.get('operator')
    if (result.get('page')!=page or not operator or operator.get('scope')!='operator_profile'
            or result.get('run') is not None or result.get('node_content') is not None):return False
    if page=='operator_detail':return operator.get('complete') is True
    if page=='operator_module':
        return all(key in operator.get('fields',{}) for key in ('module_id','module_level'))
    return False
