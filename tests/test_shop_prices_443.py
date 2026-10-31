"""Current card prices survive leaving a shop without becoming purchases."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import json,time,unittest
import numpy as np
import cv2
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from rouge.player_shop_hover import shop_snapshot,ShopNameReader
from rouge.player_shop_memory import qualified,remember,compare_shops,comparison_text,recorded_shops,ShopMemoryPanel
from rouge.run_state import RunState
ROOT=Path(__file__).resolve().parents[1]

def public_frame(second):return json.loads((ROOT/f'research/shop-price-443/public-{second}-ocr.json').read_bytes())
def amounts(snapshot):return {r['name']:r.get('price')for r in snapshot['items']}

class ShopPrices443Tests(unittest.TestCase):
    def test_public_storefront_without_purchase_button_has_visible_prices_only(self):
        frame=public_frame(164);raw=frame['raw'];before=deepcopy(raw)
        self.assertFalse(any('购买'in r[1]for r in raw))
        snapshot=shop_snapshot(raw,frame['shape']);values=amounts(snapshot)
        self.assertEqual(values,{'浪花':6,'悲伤的红':12,'“老妈的鼓励”':12,'伪翅':None})
        self.assertFalse(snapshot['complete']);self.assertEqual(raw,before)
    def test_covered_price_stays_unknown_not_neighbour_or_balance(self):
        frame=public_frame(158);values=amounts(shop_snapshot(frame['raw'],frame['shape']))
        self.assertIsNone(values['浪花']);self.assertIsNone(values['伪翅'])
        self.assertEqual(values['悲伤的红'],12)
        self.assertNotIn(883,values.values())
    def test_map_and_missing_storefront_anchors_are_not_a_shop(self):
        frame=public_frame(148);self.assertIsNone(shop_snapshot(frame['raw'],frame['shape']))
        frame=public_frame(164)
        for missing in ('刷新','当前余额','前瞻性投资系统'):
            raw=[r for r in frame['raw']if r[1]!=missing]
            self.assertIsNone(shop_snapshot(raw,frame['shape']))
    def test_continuous_scale_and_translation_keep_price_binding(self):
        frame=public_frame(164)
        for scale in (.65,.83,1.37):
            raw=[[[[x*scale+31,y*scale+17]for x,y in box],text,score]for box,text,score in frame['raw']]
            self.assertEqual(amounts(shop_snapshot(raw,(int(frame['shape'][0]*scale+40),int(frame['shape'][1]*scale+70),3))),amounts(shop_snapshot(frame['raw'],frame['shape'])))
    def test_ambiguous_and_signed_numeric_reads_do_not_become_prices(self):
        frame=public_frame(164);raw=deepcopy(frame['raw'])
        number=next(r for r in raw if r[1]=='6');other=deepcopy(number);other[1]='9';raw.append(other)
        self.assertIsNone(amounts(shop_snapshot(raw,frame['shape']))['浪花'])
        raw=deepcopy(frame['raw']);next(r for r in raw if r[1]=='6')[1]='-6'
        self.assertIsNone(amounts(shop_snapshot(raw,frame['shape']))['浪花'])
    def test_name_only_same_pixels_cannot_certify_old_price_after_numeric_change(self):
        frame=public_frame(164);raw=deepcopy(frame['raw']);calls=[]
        reader=ShopNameReader(lambda *a,**kw:(calls.append(1)or raw,None))
        image=np.zeros(frame['shape'],np.uint8);reader.identify(image,(710,65))
        self.assertEqual(amounts(reader.snapshot(image))['浪花'],6)
        box=next(r[0]for r in raw if r[1]=='6');x,y=map(int,box[0]);image[y,x]=255
        self.assertIsNone(reader.snapshot(image));next(r for r in raw if r[1]=='6')[1]='0'
        reader.identify(image,(710,65));self.assertEqual(len(calls),2)
        self.assertEqual(amounts(reader.snapshot(image))['浪花'],0)
    def test_price_zero_qualifies_but_bad_price_does_not_erase_name(self):
        frame=public_frame(164);snapshot=shop_snapshot(frame['raw'],frame['shape'])
        for bad in (True,-1,'12',None,[],float('inf')):
            value=deepcopy(snapshot);value['items'][0]['price']=bad
            self.assertEqual(qualified(value)[0],{'id':'rogue_6_scrap_G_05','name':'浪花'})
        snapshot['items'][0]['price']=0;self.assertEqual(qualified(snapshot)[0]['price'],0)
    def test_missed_number_fallback_and_cache_both_use_the_actual_price_area(self):
        frame=public_frame(164);raw=[r for r in frame['raw']if r[1]!='6'];calls=[]
        image=np.zeros(frame['shape'],np.uint8);cv2.putText(image,'6',(920,333),cv2.FONT_HERSHEY_SIMPLEX,1.5,(255,255,255),3)
        def engine(*args,**kw):
            if kw.get('use_det')is False:return [['6',.99]],None
            calls.append(1);return raw,None
        reader=ShopNameReader(engine);reader.identify(image,(710,65))
        self.assertEqual(amounts(reader.snapshot(image))['浪花'],6)
        image[320,920]=255-image[320,920]
        self.assertIsNone(reader.snapshot(image));reader.identify(image,(710,65));self.assertEqual(len(calls),2)
    def test_fallback_does_not_turn_a_signed_read_into_an_unsigned_price(self):
        frame=public_frame(164);raw=deepcopy(frame['raw']);next(r for r in raw if r[1]=='6')[1]='-6'
        image=np.zeros(frame['shape'],np.uint8);cv2.putText(image,'6',(920,333),cv2.FONT_HERSHEY_SIMPLEX,1.5,(255,255,255),3)
        result=shop_snapshot(raw,frame['shape'],image=image,engine=lambda *a,**kw:([['6',.99]],None))
        self.assertIsNone(amounts(result)['浪花'])
    def test_normal_sampling_enters_run_state_and_restart_without_hover_or_held_claim(self):
        frame=public_frame(164);snapshot=shop_snapshot(frame['raw'],frame['shape'])
        with TemporaryDirectory()as folder:
            file=Path(folder)/'run.json';run=RunState(file);before=deepcopy(run.state['relics']);at=run.state['started_at']+1
            self.assertTrue(run.apply({'page':'shop','shop':snapshot},at))
            self.assertEqual(run.state['relics'],before)
            self.assertEqual(recorded_shops(run.state)[0][1]['items'],snapshot['items'])
            self.assertEqual(RunState(file).state['history'],run.state['history'])
    def test_price_only_change_is_recorded_separately_and_old_record_is_immutable(self):
        frame=public_frame(164);snapshot=shop_snapshot(frame['raw'],frame['shape'])
        with TemporaryDirectory()as folder:
            run=RunState(Path(folder)/'run.json');at=time.time()
            self.assertTrue(remember(run,snapshot,run.state['id'],at));first=deepcopy(run.state['history'])
            newer=deepcopy(snapshot);newer['items'][0]['price']=0
            self.assertTrue(remember(run,newer,run.state['id'],at));self.assertFalse(remember(run,newer,run.state['id'],at))
            self.assertEqual(run.state['history'][:len(first)],first)
            rows=recorded_shops(run.state);self.assertEqual(len(rows),2)
            text=comparison_text(compare_shops(rows,rows[-1][0]))
            self.assertIn('6→0源石锭',text);self.assertIn('变化不证明刷新',text)
    def test_old_unpriced_snapshot_is_not_filled_with_newer_price(self):
        frame=public_frame(164);snapshot=shop_snapshot(frame['raw'],frame['shape']);old=deepcopy(snapshot)
        for r in old['items']:r.pop('price',None)
        state={'history':[{'kind':'shop_items_read','at':1,**old},{'kind':'shop_items_read','at':2,**snapshot}]}
        rows=recorded_shops(state);self.assertTrue(all('price'not in r for r in rows[0][1]['items']))
        self.assertNotIn('price_changes',compare_shops(rows,1))

class ShopPriceWidgets443Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def test_reading_earlier_price_survives_refresh_with_newer_observation(self):
        frame=public_frame(164);snapshot=shop_snapshot(frame['raw'],frame['shape'])
        state={'id':'isolated-shop-prices','history':[{'kind':'shop_items_read','at':1,**snapshot}]}
        panel=ShopMemoryPanel(SimpleNamespace(state=state,save_issue=None));self.addCleanup(panel.close)
        panel.entries.setCurrentRow(0);self.assertIn('6源石锭',panel.detail.toPlainText())
        panel.search.setText('浪花');newer=deepcopy(snapshot);newer['items'][0]['price']=0
        state['history'].append({'kind':'shop_items_read','at':2,**newer});panel.refresh()
        self.assertEqual(panel.snapshots.currentData(),0);self.assertEqual(panel.search.text(),'浪花')
        self.assertIn('6源石锭',panel.detail.toPlainText());self.assertIn('标价以所选记录为准',panel.notice.text())
        panel.snapshots.setCurrentIndex(0);panel.entries.setCurrentRow(0)
        self.assertIn('0源石锭',panel.detail.toPlainText());self.assertIn('标价：0',panel.entries.item(0).text())
        self.assertIn('不证明持有、购买',panel.detail.toPlainText())
    def test_shop_and_part_catalog_reuse_the_existing_exact_part_images(self):
        from rouge.view_catalog import relic_icon,DATA
        from rouge.player_parts import part_rows
        rows=part_rows();self.assertEqual(len(rows),44)
        for row in rows:
            expected=QIcon(str(DATA/'part-icons'/(row['icon']+'.png'))).pixmap(72,72).toImage()
            self.assertFalse(expected.isNull(),row['id'])
            self.assertEqual(relic_icon(row['icon']).pixmap(72,72).toImage(),expected,row['id'])
    def test_current_and_historical_shop_share_one_collapsible_comparison(self):
        from rouge.player_shop_replay import ShopReplayPage
        page=ShopReplayPage();self.addCleanup(page.close)
        self.assertIs(page.comparison_toggle,page.panel.comparison_toggle)
        self.assertFalse(page.comparison_toggle.isChecked());self.assertTrue(page.panel.comparison.isHidden())
        page.comparison_toggle.click();self.assertFalse(page.panel.comparison.isHidden())
        page.refresh({'id':'different-isolated-run','history':[]})
        self.assertFalse(page.comparison_toggle.isChecked());self.assertTrue(page.panel.comparison.isHidden())

if __name__=='__main__':unittest.main()
