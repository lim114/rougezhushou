"""Match references only inside the held-item bar; refuse visually ambiguous tiers."""
import json
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np
from .catalog import catalog,tactical_tools
from .operator_recognition import center
from .anchors import units

@lru_cache(maxsize=1)
def artwork_families():
    """Only expand identical-art candidates from independently recorded tables."""
    source=Path(__file__).parent/'data/relic-reference-equivalence.json'
    if not source.exists():return {}
    data=json.loads(source.read_text(encoding='utf8'))
    return {rid:family['ids'] for family in data['families'].values() for rid in family['ids']}

@lru_cache(maxsize=1)
def difficulty_families():
    """Index the pinned groups once; grade changes never require icon matching."""
    from .run_config import config_data
    return {tier['relicId']:(key,tuple(group['relicData']))
            for key,group in config_data()['difficulty_upgrade_relic_groups'].items()
            for tier in group['relicData']}


def resolve_difficulty_icons(icons,difficulty):
    """Use the pinned grade mapping only for one unambiguous artwork family."""
    result=[dict(icon) for icon in icons]
    from .run_config import config_data,difficulty_value
    grade=difficulty_value(difficulty)
    if grade is None:return result
    groups=difficulty_families()
    for icon in result:
        candidates=set(icon.get('candidates',[]))
        families={groups[rid][0] for rid in candidates if rid in groups}
        if len(families)!=1 or any(rid not in groups for rid in candidates):continue
        key,tiers=groups[next(iter(candidates))]
        eligible=[v for v in tiers if v['equivalentGrade']<=grade]
        if not eligible:continue
        tier=max(eligible,key=lambda v:v['equivalentGrade']);chosen=tier['relicId']
        if chosen not in candidates:continue
        if icon.get('confirmed') and icon.get('source')!='held_icon_and_run_difficulty':
            # A complete owned description is direct evidence. Do not silently
            # replace it with a possibly misread grade.
            if icon.get('name_usage_confirmed'):
                icon.pop('difficulty_conflict',None)
                owned=next((v for v in tiers if v['relicId']==icon['id']),None)
                if owned:
                    icon.update(difficulty_group=key,difficulty_tier=owned['equivalentGrade'],
                        tier_label=config_data().get('difficulty_upgrade_relic_labels',{}).get(str(owned['equivalentGrade'])))
                if chosen!=icon['id']:
                    icon['difficulty_conflict']={'grade':grade,'expected_id':chosen,'owned_id':icon['id']}
            continue
        icon.pop('difficulty_conflict',None)
        icon.update(id=chosen,confirmed=True,source='held_icon_and_run_difficulty',
                    difficulty=grade,difficulty_group=key,difficulty_tier=tier['equivalentGrade'],
                    tier_label=config_data().get('difficulty_upgrade_relic_labels',{}).get(str(tier['equivalentGrade'])),
                    difficulty_source=(difficulty or {}).get('source'))
    return result


def resolve_owned_icons(icons,cards):
    """Corroborate artwork with exact owned names/usages only when assignment is unique."""
    result=[dict(icon) for icon in icons]
    known=set(catalog()['relics'])|set(tactical_tools())
    names={c['id'] for c in cards if c.get('confirmed') and c.get('source')=='held_name_and_usage'
           and c.get('id') in known and c.get('candidates')==[c['id']]}
    occupied={r['id'] for r in result if r.get('confirmed')}
    for icon in result:
        if icon.get('confirmed'):continue
        choices=(set(icon.get('candidates',[]))&names)-occupied
        if len(choices)!=1:continue
        choice=next(iter(choices))
        slots=[r for r in result if not r.get('confirmed') and choice in r.get('candidates',[])]
        if len(slots)!=1:continue
        for field in ('difficulty','difficulty_group','difficulty_tier','tier_label','difficulty_source','difficulty_conflict'):
            icon.pop(field,None)
        icon.update(id=choice,confirmed=True,source='held_icon_and_usage',name_usage_confirmed=True)
        occupied.add(choice)
    return result

@lru_cache(maxsize=3)
def templates(height):
    folder=Path(__file__).parent/'data'
    result=[]
    for entry in reference_entries():
        rgba=_artwork(entry['file'])
        if rgba is None or rgba.ndim!=3 or rgba.shape[2]!=4:continue
        for scale in (.056,.064,.072,.080):
            size=round(height*scale)
            # Packed textures are not necessarily square (e.g. VIP tickets).
            factor=size/max(rgba.shape[:2])
            resized=cv2.resize(rgba,(max(1,round(rgba.shape[1]*factor)),max(1,round(rgba.shape[0]*factor))),interpolation=cv2.INTER_AREA)
            mask=(resized[:,:,3]>=220).astype(np.uint8)*255
            if np.count_nonzero(mask)<20:continue
            result.append((entry['id'],resized[:,:,:3],mask))
    return result


@lru_cache(maxsize=3)
def prepared_templates(height):
    """Cache the algebraic screening terms at the observed UI scale."""
    result=[]
    for rid,template,mask in templates(height):
        binary=(mask!=0).astype(np.float32)
        pixels=template.astype(np.float32)*binary[:,:,None]
        energy=float(np.sum(pixels*pixels,dtype=np.float64))
        # Only reference terms persist across frames. Current-image terms
        # remain local to ProjectionScreen and are never reused approximately.
        projected=np.sum(pixels,axis=2)/np.sqrt(np.float32(3))
        projected_energy=float(np.sum(projected.astype(np.float64)**2))
        projected.setflags(write=False)
        result.append((rid,template,mask,pixels,binary,energy,(projected,projected_energy)))
    return result


@lru_cache(maxsize=1)
def reference_entries():
    folder=Path(__file__).parent/'data'
    return tuple(entry for name in ('relic-icon-receipt.json','tactical-icon-receipt.json')
        for entry in json.loads((folder/name).read_text(encoding='utf-8'))['icons'])


@lru_cache(maxsize=256)
def _artwork(file):
    """Immutable packaged artwork, shared across different observed UI scales."""
    folder=Path(__file__).parent/'data'
    image=cv2.imdecode(np.fromfile(folder/file,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
    if image is not None:image.setflags(write=False)
    return image


@lru_cache(maxsize=32)
def _reference_image(rid):
    entry=next((item for item in reference_entries() if item['id']==rid),None)
    return _artwork(entry['file']) if entry else None


@lru_cache(maxsize=256)
def _refined_template(rid,size):
    rgba=_reference_image(rid)
    if rgba is None:return None
    factor=size/max(rgba.shape[:2])
    resized=cv2.resize(rgba,(max(1,round(rgba.shape[1]*factor)),max(1,round(rgba.shape[0]*factor))),interpolation=cv2.INTER_AREA)
    mask=(resized[:,:,3]>=220).astype(np.uint8)*255
    return (resized[:,:,:3],mask) if np.count_nonzero(mask)>=20 else None


def _can_match(pixels,energy_image,template,mask,energy):
    """Screen distant references; final scores always use the original matcher.

    Binary-mask normalized SSD is (I² + T² - 2 I.T) / sqrt(I² T²).
    Reusing the scalar I² image avoids repeating three-channel mask work.
    A wide 0.02 guard below the accepted 0.90 score leaves borderline
    references, including the 0.025 ambiguity margin, for full verification.
    Invalid arithmetic also falls back to that verifier.
    """
    if energy<=0:return True
    local_energy=cv2.matchTemplate(energy_image,mask,cv2.TM_CCORR)
    cross=cv2.matchTemplate(pixels,template,cv2.TM_CCORR)
    denominator=np.sqrt(np.maximum(local_energy*energy,0))
    differences=np.divide(local_energy+energy-2*cross,denominator,
        out=np.full_like(local_energy,np.inf),where=denominator>0)
    minimum=float(np.min(differences))
    return not np.isfinite(minimum) or minimum<=.12

class EnergyScreen:
    """Reject references whose norm cannot fit anywhere in this bar.

    Cauchy-Schwarz gives normalized SSD >= r + 1/r - 2, where
    r = sqrt(image_energy / template_energy). Masked image energy cannot
    exceed its rectangular window's energy. Integral sums bound all
    translations, sharing each dimension pair across references.
    The .14 guard is wider than the existing .12 coarse verification limit.
    This bound never confirms an icon and is independent of screen position.
    """
    minimum_ratio = ((2.14 - np.sqrt(2.14 ** 2 - 4)) / 2) ** 2

    def __init__(self, pixels):
        self.integral = cv2.integral(np.sum(pixels.astype(np.float64) ** 2, axis=2))
        self.ceilings = {}

    def possible(self, shape, template_energy):
        if not np.isfinite(template_energy) or template_energy <= 0:
            return True
        if shape not in self.ceilings:
            h, w = shape
            a = self.integral
            windows = a[h:, w:] - a[:-h, w:] - a[h:, :-w] + a[:-h, :-w]
            self.ceilings[shape] = float(np.max(windows)) if windows.size else float('inf')
        ceiling = self.ceilings[shape]
        return not np.isfinite(ceiling) or ceiling + 1 >= template_energy * self.minimum_ratio


class ProjectionScreen:
    """A one-channel SSD lower bound, followed by the original RGB verifier.

    For each masked pixel, (sum_c(I_c - T_c) / sqrt(3))**2 is no
    greater than its RGB squared error. The rectangular window energy
    bounds masked image energy from above, so the projected numerator
    divided by sqrt(rectangular energy * RGB template energy) is a
    necessary lower bound on the original normalized SSD at every position.

    The .14 guard keeps .88 coarse seeds and the .90 confirmation margin
    for the original matcher. Nonfinite arithmetic falls back to that
    matcher. This object belongs to one current bar; no pixel values or
    correlations are reused across changed frames. Window sums are bounded.
    """
    limit = .14
    max_cache_bytes = 8 * 1024 * 1024
    max_cache_entries = 32

    def __init__(self, pixels, energy_screen):
        self.scalar = np.sum(pixels, axis=2) / np.sqrt(np.float32(3))
        self.square = self.scalar * self.scalar
        self.integral = energy_screen.integral
        self.windows = OrderedDict()
        self.cache_bytes = 0

    def window_energy(self, shape):
        if shape in self.windows:
            self.windows.move_to_end(shape)
            return self.windows[shape]
        h, w = shape
        a = self.integral
        value = a[h:, w:] - a[:-h, w:] - a[h:, :-w] + a[:-h, :-w]
        if value.nbytes <= self.max_cache_bytes:
            while self.windows and (len(self.windows) >= self.max_cache_entries or
                                    self.cache_bytes + value.nbytes > self.max_cache_bytes):
                _, old = self.windows.popitem(last=False)
                self.cache_bytes -= old.nbytes
            self.windows[shape] = value
            self.cache_bytes += value.nbytes
        return value

    def possible(self, template, mask, energy, projection=None):
        if not np.isfinite(energy) or energy <= 0:
            return True
        if projection is None:
            projected = np.sum(template, axis=2) / np.sqrt(np.float32(3))
            template_energy = float(np.sum(projected.astype(np.float64) ** 2))
        else:
            projected,template_energy=projection
        local = cv2.matchTemplate(self.square, mask, cv2.TM_CCORR)
        cross = cv2.matchTemplate(self.scalar, projected, cv2.TM_CCORR)
        lower = local + template_energy - 2 * cross
        if not np.all(np.isfinite(lower)):
            return True
        ceiling = self.limit * np.sqrt(np.maximum(self.window_energy(mask.shape) * energy, 0))
        # Correlations use float32 internally. Keep a generous cancellation
        # guard as well as the .02 score guard; neither can confirm an icon.
        error = 1e-4 * (np.abs(local) + template_energy + 2 * np.abs(cross)) + 4
        return not np.all(np.isfinite(ceiling)) or bool(np.any(lower <= ceiling + error))


def match_held_icons(image,anchor,count,*,cache=None):
    h,w=image.shape[:2];x,y=center(anchor)
    ux,uy=units(image,anchor,38.3 if anchor['text']=='收藏品' else 34.2)
    if count==0:count=None
    x0=max(0,round((x+.028*ux)*w));x1=min(w,round((x+(.028+min(.343,.064*count) if count is not None else .371)*ux)*w))
    y0=max(0,round((y-.071*uy)*h));y1=min(h,round((y+.017*uy)*h))
    roi=image[y0:y1,x0:x1]
    if not roi.size:return []
    # Match one local bar at a bounded canonical font size, not a whole frame.
    virtual_h=h*uy;ratio=min(1,900/virtual_h)
    roi=cv2.resize(roi,None,fx=ratio,fy=ratio)
    vh=round(virtual_h*ratio);vw=round(w*ux*ratio)
    compute=lambda:_match_bar(roi,vh,vw,0,0)
    found=cache.call(roi,('held_bar',vh,vw),compute) if cache else compute()
    for record in found:
        record['center']=[(x0+record['center'][0]*vw/ratio)/w,(y0+record['center'][1]*vh/ratio)/h]
    return found


def _refined_matches(roi, ordered):
    """Run the original verifier with bounded, frame-local concurrency.

    Results are consumed in the original sorted order, including ties. Only
    two independent OpenCV calls run at once. At most four pending result
    arrays fit in the 8 MiB queue budget (native scratch and the consumer's
    current array are separate). No executor survives this invocation.
    """
    def match(item):
        rid,size=item
        refined=_refined_template(rid,size)
        if refined is None:return None
        template,mask=refined;th,tw=template.shape[:2]
        if th>=roi.shape[0] or tw>=roi.shape[1]:return None
        differences=cv2.matchTemplate(roi,template,cv2.TM_SQDIFF_NORMED,mask=mask)
        return rid,tw,th,np.nan_to_num(differences,nan=10,posinf=10,neginf=10)

    matrix_bytes=max(1,roi.shape[0]*roi.shape[1]*np.dtype(np.float32).itemsize)
    batch_size=min(4,(8*1024*1024)//matrix_bytes)
    if len(ordered)<8 or batch_size<2:
        yield from map(match,ordered)
        return
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2,thread_name_prefix='rouge-relic-refine') as pool:
        for start in range(0,len(ordered),batch_size):
            yield from pool.map(match,ordered[start:start+batch_size])


def _match_bar(roi,h,w,x0,y0):
    if not np.any(roi):return []
    pixels=roi.astype(np.float32)
    energy_image=np.sum(pixels*pixels,axis=2)
    energy_screen=EnergyScreen(pixels)
    projection_screen=ProjectionScreen(pixels,energy_screen)
    found=[];near_misses=[];coarse_hits=[]
    def collect(differences,rid,tw,th,refine=False):
        # Match physical slots, including repeated artwork in separate slots.
        for _ in range(64):
            minimum,_,position,_=cv2.minMaxLoc(differences)
            score=1-float(minimum)
            if score<(.88 if refine else .90):break
            px,py=position
            record={'id':rid,'score':score,'center':[(x0+px+tw/2)/w,(y0+py+th/2)/h]}
            if score>=.90:
                found.append(record)
                if refine:coarse_hits.append((record,max(tw,th)))
            else:near_misses.append((record,max(tw,th)))
            rx=max(1,round(.025*w));ry=max(1,round(.04*h))
            differences[max(0,py-ry):py+ry+1,max(0,px-rx):px+rx+1]=10
    for rid,template,mask,screen_template,screen_mask,energy,*projection in prepared_templates(h):
        th,tw=template.shape[:2]
        if th>=roi.shape[0] or tw>=roi.shape[1]:continue
        if not energy_screen.possible((th,tw),energy):continue
        if not projection_screen.possible(screen_template,screen_mask,energy,*projection):continue
        if not _can_match(pixels,energy_image,screen_template,screen_mask,energy):continue
        # Keep original OpenCV scores/locations for every plausible reference.
        # Screening can never supply a confirmed identity or an ambiguity score.
        differences=cv2.matchTemplate(roi,template,cv2.TM_SQDIFF_NORMED,mask=mask)
        differences=np.nan_to_num(differences,nan=10,posinf=10,neginf=10)
        collect(differences,rid,tw,th,refine=True)
    # The four coarse sizes are seeds, not supported display resolutions.
    # A near miss may sit between them after resizing/antialiasing; test each
    # neighboring integer size using the original full-color masked matcher.
    # No near-miss score enters the returned candidates or confirms an item.
    refine_sizes=set();radius=max(1,round(h*.008))
    coarse_sizes={round(h*scale) for scale in (.056,.064,.072,.080)}
    for record,size in near_misses:
        if any(r['id']==record['id'] and abs(r['center'][0]-record['center'][0])<.025 for r in found):continue
        refine_sizes.update((record['id'],s) for s in range(max(1,size-radius),size+radius+1) if s not in coarse_sizes)
        # Compare competing identities at equally refined scales. Otherwise
        # refining only the challenger can manufacture an artwork ambiguity.
        for hit,hit_size in coarse_hits:
            if abs(hit['center'][0]-record['center'][0])<.025:
                refine_sizes.update((hit['id'],s) for s in range(max(1,hit_size-radius),hit_size+radius+1) if s not in coarse_sizes)
    for value in _refined_matches(roi,sorted(refine_sizes)):
        if value is None:continue
        rid,tw,th,differences=value
        collect(differences,rid,tw,th)
    pending=sorted(found,key=lambda r:r['score'],reverse=True);matches=[]
    while pending:
        best=pending.pop(0)
        neighbors=[r for r in pending if abs(r['center'][0]-best['center'][0])<.025]
        pending=[r for r in pending if r not in neighbors]
        candidates=[best['id']]
        if neighbors and best['score']-neighbors[0]['score']<.025:
            candidates+=[r['id'] for r in neighbors if best['score']-r['score']<.025]
        # Expand every visually eligible identity, including the runner-up.
        # Shared artwork cannot prove a tier, and a competing family's variant
        # must remain available for subsequent exact held-text confirmation.
        candidates+=[rid for candidate in tuple(candidates)
                     for rid in artwork_families().get(candidate,[])]
        best['candidates']=sorted(set(candidates))
        best['confirmed']=len(best['candidates'])==1
        matches.append(best)
    return matches
