"""Owned-popup scheduling: current controls, transformed layouts and fallback.

The four originals are existing development captures from one user. Only
Kal'tsit supplied template descriptors; other identities test those controls,
not independent overall OCR accuracy. Resizes and edits are derived cases.
"""
import hashlib
import json
from pathlib import Path
import unittest

import cv2
import numpy as np

from rouge.page_features import PageFeatureRouter

ROOT=Path(__file__).resolve().parents[1]
INVENTORY=ROOT/'.cache/research/page-routing-056/epoch-1791136902879484600/inventory.json'


def original(name,animated=False):
    record=next(r for r in json.loads(INVENTORY.read_text(encoding='utf-8'))['samples'] if r['id']==name)
    key='animation_image' if animated else 'image'
    path=ROOT/record[key]
    expected=record['animation_sha256'] if animated else record['sha256']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
    image=cv2.imdecode(np.fromfile(path,dtype=np.uint8),cv2.IMREAD_COLOR)
    if record['client_rect'] is None:return image
    left,top,right,bottom=record['client_rect']
    return image[top:bottom,left:right].copy()


class OwnedPopupFeatureTests(unittest.TestCase):
    def assert_popup(self,image,router=None):
        router=router or PageFeatureRouter()
        result=router.classify(image)
        self.assertTrue(result['specialized'],result)
        self.assertEqual([c['page'] for c in result['candidates']],['run_owned_popup'])
        self.assertFalse(result['facts_from_features'])
        candidate=result['candidates'][0]
        self.assertEqual(candidate['matched_controls'],4)
        self.assertEqual({e['side'] for e in candidate['evidence']},{'left','right'})
        self.assertFalse(candidate['facts_from_features'])
        for forbidden in ('fields','name','operator_id','level','ids','count','complete'):
            self.assertNotIn(forbidden,candidate)
        height,width=image.shape[:2]
        for left,top,right,bottom in candidate['regions']:
            self.assertTrue(0<=left<right<=width and 0<=top<bottom<=height)
        return result

    def test_four_original_identities_and_actual_second_myrtle_frame(self):
        for name in ('kaltsit_owned','chen_owned','leizi_owned','myrtle_owned'):
            with self.subTest(name=name):self.assert_popup(original(name))
        self.assert_popup(original('myrtle_owned',animated=True))

    def test_continuous_scales_use_current_geometry(self):
        for name in ('kaltsit_owned','myrtle_owned'):
            for factor in (.5,.65,.8,1.25):
                with self.subTest(name=name,factor=factor):
                    self.assert_popup(cv2.resize(original(name),None,fx=factor,fy=factor))

    def test_translation_maps_regions_and_control_transform(self):
        source=original('myrtle_owned');height,width=source.shape[:2]
        canvas=np.zeros((height+95,width+125,3),np.uint8)
        canvas[35:35+height,45:45+width]=source
        normal=self.assert_popup(source)['candidates'][0]['transform']
        moved=self.assert_popup(canvas)['candidates'][0]['transform']
        self.assertAlmostEqual(moved[0][2]-normal[0][2],45,delta=3)
        self.assertAlmostEqual(moved[1][2]-normal[1][2],35,delta=3)

    def test_varying_count_digits_do_not_supply_page_facts(self):
        image=original('kaltsit_owned')
        page=next(p for p in PageFeatureRouter().pages if p['page']=='run_owned_popup')
        left,top,_,_=page['source_client_rect']
        for x0,y0,x1,y1 in page['feature_only_count_redactions']:
            image[y0-top:y1-top,x0-left:x1-left]=0
            cv2.putText(image,'8',(x0-left,y1-top-2),cv2.FONT_HERSHEY_SIMPLEX,
                        .7,(255,255,255),1)
        self.assert_popup(image)

    def test_changed_body_preserves_scheduling_only(self):
        image=original('chen_owned')
        image[350:650,100:600]=0
        self.assert_popup(image)

    def test_each_missing_current_core_rejects_other_identity(self):
        image=original('leizi_owned')
        page=next(p for p in PageFeatureRouter().pages if p['page']=='run_owned_popup')
        rw,rh=page['reference_size'];height,width=image.shape[:2]
        for anchor in page['anchors']:
            with self.subTest(core=anchor['key']):
                altered=image.copy();x0,y0,x1,y1=anchor['box']
                cv2.rectangle(altered,(int(x0*width/rw)-10,int(y0*height/rh)-10),
                              (int(x1*width/rw)+10,int(y1*height/rh)+10),(0,0,0),-1)
                self.assertFalse(PageFeatureRouter().classify(altered)['specialized'])

    def test_dim_crop_and_too_small_keep_full_discovery(self):
        image=original('kaltsit_owned');height,width=image.shape[:2]
        for altered in (np.round(image*.5).astype(np.uint8),image[:int(height*.90)],
                        image[:,int(width*.35):],cv2.resize(image,None,fx=.35,fy=.35)):
            with self.subTest(shape=altered.shape):
                self.assertFalse(PageFeatureRouter().classify(altered)['specialized'])

    def test_existing_map_relic_and_node_pages_never_claim_popup(self):
        for name in ('exploration-map','run-relic-multicard','map-template-node-detail'):
            with self.subTest(name=name):
                self.assertNotIn('run_owned_popup',[c['page'] for c in
                    PageFeatureRouter().classify(original(name))['candidates']])

    def test_old_binary_assets_and_reference_scope_unchanged(self):
        before=json.loads((ROOT/'.cache/batch-059-before/manifest.json').read_text(encoding='utf-8'))
        assets={n:v for n,v in before['source_hashes'].items()
                if n.startswith('rouge/data/page-features/') and Path(n).suffix in ('.npz','.png')}
        self.assertEqual(len(assets),20)
        for name,value in assets.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),value)
        router=PageFeatureRouter();self.assertEqual(len(router.pages),5)
        page=next(p for p in router.pages if p['page']=='run_owned_popup')
        self.assertEqual(page['independent_training_sources'],1)
        self.assertFalse(page['facts_from_features'])
        self.assertEqual({a['key'] for a in page['anchors']},
                         {'owned_button','owned_header_prefix','collapse','squad'})


if __name__=='__main__':unittest.main()
