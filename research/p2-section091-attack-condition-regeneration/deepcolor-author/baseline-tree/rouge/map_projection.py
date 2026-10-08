"""Fixed-bitmap ground-plane references, gated by image and grid identity."""
import hashlib,json,math
from dataclasses import dataclass
from functools import lru_cache
from numbers import Real
from pathlib import Path

DATA=Path(__file__).parent/'data'


def grid_digest(stage):
    grid=[[{k:stage['tiles'][i].get(k) for k in ('tileKey','heightType','buildableType','passableMask')}
        for i in row] for row in stage['map']]
    return hashlib.sha256(json.dumps(grid,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@lru_cache(maxsize=1)
def projection_data():
    return json.loads((DATA/'battle-map-projections.json').read_text(encoding='utf-8'))


def _finite(value):
    return isinstance(value,Real) and not isinstance(value,bool) and math.isfinite(value)


def _transform(matrix,x,y):
    if not _finite(x) or not _finite(y):return None
    divisor=matrix[6]*x+matrix[7]*y+matrix[8]
    if not math.isfinite(divisor) or abs(divisor)<1e-12:return None
    point=((matrix[0]*x+matrix[1]*y+matrix[2])/divisor,
        (matrix[3]*x+matrix[4]*y+matrix[5])/divisor)
    return point if all(math.isfinite(v) for v in point) else None


@dataclass(frozen=True)
class FixedMapProjection:
    matrix:tuple
    inverse:tuple
    rows:int
    cols:int
    width:int
    height:int
    tolerance_px:float

    def project(self,cell):
        """Return source pixels; invalid/out-of-grid positions stay unmapped."""
        if not isinstance(cell,dict):return None
        r,c=cell.get('row'),cell.get('col')
        if not _finite(r) or not _finite(c):return None
        if not (-.5<=r<=self.rows-.5 and -.5<=c<=self.cols-.5):return None
        return _transform(self.matrix,c,r)

    def cell_at(self,x,y):
        """Invert the ground reference. The right/bottom border is exclusive."""
        if not _finite(x) or not _finite(y) or not (0<=x<self.width and 0<=y<self.height):return None
        position=_transform(self.inverse,x,y)
        if position is None:return None
        c,r=position
        if not (-.5<=r<self.rows-.5 and -.5<=c<self.cols-.5):return None
        return {'row':math.floor(r+.5),'col':math.floor(c+.5)}


def projection_for(stage,image_sha256,image_size):
    """A stale image, alias, level, or geometry must never inherit a transform."""
    if not stage:return None
    data=projection_data();binding=data['stages'].get(stage['id'])
    if not binding:return None
    calibration=data['calibrations'][binding['calibration']];image=stage['image']
    if binding['level_sha256']!=stage['level_source']['sha256']:return None
    if binding['image_file']!=image['file']:return None
    if image_sha256!=image['sha256'] or image_sha256!=calibration['bitmap_sha256']:return None
    if tuple(image_size)!=(calibration['width'],calibration['height']):return None
    if (image['width'],image['height'])!=tuple(image_size):return None
    if (len(stage['map']),len(stage['map'][0]))!=(calibration['rows'],calibration['cols']):return None
    if grid_digest(stage)!=calibration['grid_sha256']:return None
    return FixedMapProjection(tuple(calibration['matrix']),tuple(calibration['inverse']),
        calibration['rows'],calibration['cols'],calibration['width'],calibration['height'],calibration['tolerance_px'])
