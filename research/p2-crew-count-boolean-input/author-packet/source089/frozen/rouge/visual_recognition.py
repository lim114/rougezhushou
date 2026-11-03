"""Experimental image-only landmarks. No text detector/recognizer is loaded.

ORB registration locates reference artwork anywhere in the current frame. A
reference never supplies its old numeric values; only current icon pixels count.
"""
import json,time
from copy import deepcopy
from pathlib import Path
import cv2
import numpy as np
from .viewport import prepare_frame,map_evidence
from .recognition_cache import ExactImageCache
from .operator_recognition import match_potential
from .relic_recognition import match_held_icons,resolve_difficulty_icons
from .catalog import operator_profiles,catalog,tactical_tools

class VisualReader:
    def __init__(self, *, cache_enabled=True):
        self.cache_enabled=cache_enabled
        self.orb=cv2.ORB_create(nfeatures=4000,edgeThreshold=7,patchSize=21,fastThreshold=10)
        self.matcher=cv2.BFMatcher(cv2.NORM_HAMMING)
        folder=Path(__file__).parent/'data/visual-anchors'
        self.references=[]
        self.icon_cache=ExactImageCache(max_bytes=2*1024*1024,max_entries=8) if cache_enabled else None
        self.feature_cache=ExactImageCache(max_bytes=4*1024*1024,max_entries=2) if cache_enabled else None
        self._last_frame=self._last_rect=self._last_context=self._last_result=None
        self._frame_cache_max_bytes=32*1024*1024
        for entry in json.loads((folder/'manifest.json').read_text(encoding='utf8'))['entries']:
            im=cv2.imdecode(np.fromfile(folder/entry['file'],np.uint8),0)
            kp,des=self.orb.detectAndCompute(im,None)
            self.references.append((entry,im.shape,kp,des))

    def read(self,image,*,client_rect=None,run_context=None):
        start=time.perf_counter()
        rect=tuple(client_rect) if client_rect is not None else None
        context_snapshot=deepcopy(run_context)
        from .run_config import confirmed_config
        # Bind the full echoed records, including provenance/capture time. A
        # new run or changed configuration must never reuse the old run result.
        try:
            context=json.dumps({'run_id':(context_snapshot or {}).get('run_id'),
                'config':confirmed_config(context_snapshot),'orb':self._orb_settings()},
                sort_keys=True,ensure_ascii=False,allow_nan=False)
        except (TypeError,ValueError,AttributeError):
            context=None
        previous=self._last_frame
        if (self.cache_enabled and context is not None and previous is not None
                and rect==self._last_rect and context==self._last_context
                and image.shape==previous.shape and image.dtype==previous.dtype
                # Cheap inequality rejection is not an equality test. Every
                # candidate still requires the full current source below.
                and np.array_equal(image[::32,::32],previous[::32,::32])
                and np.array_equal(image,previous)):
            result=deepcopy(self._last_result)
            result['observed_at']=time.time()
            result['performance']={'total_ms':(time.perf_counter()-start)*1000,'backend':'visual',
                'ocr_model_calls':0,'stages_ms':{},'reuse':'exact_frame',
                'feature_cache_hits':0,'icon_cache_hits':0,'current_frame_feature_calls':0}
            return result
        keep=self.cache_enabled and context is not None and image.nbytes<=self._frame_cache_max_bytes
        # One immutable source snapshot binds computation and the cache entry;
        # never copy a possibly modified caller buffer after computing facts.
        frame=image.copy() if keep else image
        feature_hits=self.feature_cache.hits if self.feature_cache else 0
        feature_misses=self.feature_cache.misses if self.feature_cache else 0
        icon_hits=self.icon_cache.hits if self.icon_cache else 0
        result=self._read(frame,client_rect=rect,run_context=context_snapshot)
        result['performance'].update(total_ms=(time.perf_counter()-start)*1000,reuse='none',
            feature_cache_hits=self.feature_cache.hits-feature_hits if self.cache_enabled and self.feature_cache else 0,
            icon_cache_hits=self.icon_cache.hits-icon_hits if self.cache_enabled and self.icon_cache else 0,
            current_frame_feature_calls=self.feature_cache.misses-feature_misses if self.cache_enabled and self.feature_cache else 1)
        if keep:
            self._last_frame=frame;self._last_rect=rect;self._last_context=context
            self._last_result=deepcopy(result)
        else:
            self._last_frame=self._last_rect=self._last_context=self._last_result=None
        return result

    def _orb_settings(self):
        # The detector's real parameters govern both cache levels, even when a
        # diagnostic caller changes an ORB setting on this reader instance.
        return (self.orb.getMaxFeatures(),self.orb.getScaleFactor(),self.orb.getNLevels(),
            self.orb.getEdgeThreshold(),self.orb.getFirstLevel(),self.orb.getWTA_K(),
            self.orb.getScoreType(),self.orb.getPatchSize(),self.orb.getFastThreshold())

    def _current_features(self,gray):
        def compute():
            points,descriptors=self.orb.detectAndCompute(gray,None)
            # cv2.KeyPoint cannot be deep-copied. Exact float32 coordinates and
            # descriptor bytes preserve the old target-point conversion/order.
            return np.asarray([point.pt for point in points],np.float32).reshape(-1,2),descriptors
        if self.cache_enabled and self.feature_cache:
            return self.feature_cache.call(gray,self._orb_settings(),compute)
        return compute()

    def _read(self,image,*,client_rect=None,run_context=None):
        start=time.perf_counter();im,viewport=prepare_frame(image,client_rect);h,w=im.shape[:2]
        icon_cache=self.icon_cache if self.cache_enabled else None
        # This is feature discovery over the complete frame, not a screen crop.
        scale=min(1,1600/w,1200/h)
        gray=cv2.resize(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),None,fx=scale,fy=scale)
        points,des=self._current_features(gray);matches=[]
        if des is not None:
            for entry,shape,rkp,rdes in self.references:
                if rdes is None:continue
                good=[a for pair in self.matcher.knnMatch(rdes,des,k=2) if len(pair)==2
                      for a,b in [pair] if a.distance<.7*b.distance]
                if len(good)<12:continue
                source=np.float32([rkp[m.queryIdx].pt for m in good])
                target=points[[m.trainIdx for m in good]]/scale
                transform,mask=cv2.estimateAffinePartial2D(source,target,method=cv2.RANSAC,ransacReprojThreshold=3)
                if transform is None:continue
                count=int(mask.sum());fraction=count/len(good)
                factor=float(np.linalg.norm(transform[0,:2]))
                if count<12 or fraction<.65 or not .25<factor<3:continue
                matches.append({'entry':entry,'matrix':transform,'inliers':count,'fraction':fraction,'scale':factor})
        training=next(iter(sorted([m for m in matches if m['entry']['kind']=='training'],key=lambda m:m['inliers'],reverse=True)),None)
        names=[m for m in matches if m['entry']['kind']=='identity' and training
               and .7<training['scale']/m['scale']<1.4]
        operator=None;page='unknown';run=None
        if len({m['entry']['id'] for m in names})==1:
            key=names[0]['entry']['id'];profile=operator_profiles()[key]
            anchor={'box':mapped(training,training['entry']['potential_box'],w,h),'text':'潜能'}
            potential=match_potential(im,anchor,cache=icon_cache);fields={};sources={}
            if potential:fields['potential']=potential['value'];sources['potential']=potential
            operator={'id':key,'name':profile['name'],'scope':'operator_profile','fields':fields,'sources':sources,
                'skill_ranks':{},'complete':False,'missing_fields':['level','elite','trust','module_id','module_level','selected_skill']+
                ['skill_rank_'+str(i+1) for i in range(len(profile['skills']))]+([] if potential else ['potential']),
                'limitations':['纯视觉实验只覆盖三个参考干员的身份和潜能；培养数字不由旧参考图补值。']}
            page='operator_detail'
        footer=next(iter(sorted([m for m in matches if m['entry']['kind']=='footer'],key=lambda m:m['inliers'],reverse=True)),None)
        if footer:
            anchor={'box':mapped(footer,footer['entry']['held_box'],w,h),'text':'收藏品'}
            from .run_config import confirmed_config
            config=confirmed_config(run_context)
            icons=resolve_difficulty_icons(match_held_icons(im,anchor,None,cache=icon_cache),config.get('difficulty'))
            run={'page':'run_map','operators':[],'crew_count':None,'config':config,'resources':{},
                'config_reuse':{'run_id':(run_context or {}).get('run_id'),'fields':sorted(config)},
                'relics':{'ids':sorted({r['id'] for r in icons if r['confirmed'] and r['id'] in catalog()['relics']}),
                         'icons':icons,'count':None,'source':'visual_held_bar'},
                'tactical_tools':{'ids':sorted({r['id'] for r in icons if r['confirmed'] and r['id'] in tactical_tools()}),'source':'visual_held_bar'},
                'limitations':['纯视觉实验不读取数量、难度和文字；图标多解保持未知，库存不宣称完整。']}
        result={'observed_at':time.time(),'page':page,'size':viewport['source_size'],'texts':[],'nodes':[],
                'map':None,'node_content':None,'stage':None,'drop_estimate':None,'operator':operator,'run':run,
                'limitations':['纯视觉实验：未覆盖自由文字、数字、完整地图；不替代已确认的本局历史。'],
                'visual_landmarks':[{'kind':m['entry']['kind'],'id':m['entry'].get('id'),'inliers':m['inliers'],
                                    'inlier_fraction':m['fraction']} for m in matches],
                'viewport':viewport,'performance':{'total_ms':(time.perf_counter()-start)*1000,'backend':'visual',
                                                  'ocr_model_calls':0,'stages_ms':{}}}
        map_evidence(result,viewport)
        return result

def mapped(match,box,w,h):
    points=np.float32(box).reshape(-1,1,2)
    return [[float(x)/w,float(y)/h] for x,y in cv2.transform(points,match['matrix']).reshape(-1,2)]
