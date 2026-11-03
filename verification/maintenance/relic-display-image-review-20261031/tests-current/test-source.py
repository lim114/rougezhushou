"""Original image provenance, labelled group references, and old rendering parity."""
from pathlib import Path
from types import ModuleType,SimpleNamespace
from tempfile import TemporaryDirectory
from hashlib import sha1,sha256
from unittest.mock import patch
import json,unittest
from PySide6.QtWidgets import QApplication
from rouge import view_catalog as pictures,player_inventory as inventory

ROOT=Path(__file__).resolve().parents[1]
COMPARISON={}


class RelicDisplayImagesReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance()or QApplication([])
        cls.old=ModuleType('rouge._before_relic_display_images');cls.old.__package__='rouge';cls.old.__file__=str(ROOT/'rouge/view_catalog.py')
        exec(compile((ROOT/'research/relic-display-image-review-20261031/before-view_catalog.py').read_bytes(),'<own-prior-view-catalog>','exec'),cls.old.__dict__)
        cls.manifest=json.loads((pictures.DATA/'relic-display-icons.json').read_bytes())

    def test_all_named_original_assets_keep_pinned_git_blobs_and_decode_in_qt(self):
        exact=[r for r in self.manifest['icons'].values()if r['display_scope']=='exact_named_asset']
        self.assertEqual(len(exact),21);self.assertEqual(len({r['file']for r in exact}),16)
        for r in exact:
            raw=(pictures.DATA/r['file']).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(),r['sha256'])
            self.assertEqual(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),r['git_blob_sha1'])
            self.assertIn(self.manifest['commit'],r['url'])
            self.assertFalse(pictures.relic_icon(r['id']).pixmap(72,72).isNull(),r['id'])

    def test_complete_catalog_keeps_every_prior_icon_and_changes_only_the_25_declared_rows(self):
        rows=inventory.inventory_rows({},held_only=False);changed=[];unchanged=0;missing=[]
        for r in rows:
            identity=r['icon']or''
            for edge in (28,46,72):
                before=self.old.relic_icon(identity).pixmap(edge,edge).toImage();after=pictures.relic_icon(identity).pixmap(edge,edge).toImage()
                if identity in self.manifest['icons']:
                    self.assertTrue(before.isNull(),identity);self.assertFalse(after.isNull(),identity)
                else:self.assertEqual(after,before,identity)
            if identity in self.manifest['icons']:changed.append(r['id'])
            else:unchanged+=1
            if pictures.relic_icon(identity).pixmap(46,46).isNull():missing.append(r['id'])
        self.assertEqual(len(changed),25);self.assertEqual(missing,['rogue_6_legacy_10'])
        COMPARISON.update(total_rows=len(rows),changed=changed,unchanged=unchanged,remaining_missing=missing,edges=[28,46,72],all_original_icons_equal=True)

    def test_four_group_pictures_are_labelled_references_with_distinct_item_identity(self):
        p=inventory.InventoryPanel(SimpleNamespace(state={'relics':{}}));self.addCleanup(p.close)
        p.held.setChecked(False)
        refs={k:r for k,r in self.manifest['icons'].items()if r['display_scope']=='group_reference'}
        self.assertEqual(len(refs),4)
        for identity,r in refs.items():
            row=p.rows[identity];self.assertEqual(row['id'],identity)
            self.assertIn('独立图样尚未核验',pictures.relic_icon_note(identity))
            item=next(p.entries.item(i)for i in range(p.entries.count())if p.entries.item(i).data(256)==identity)
            self.assertIn('分组',item.toolTip());p.entries.setCurrentItem(item)
            self.assertIn('图片说明',p.detail.toPlainText());self.assertIn('不据此判断实际持有或效果',p.detail.toPlainText())
            p.hover_card.install(row,p.version.currentData(),p.source_index,p.source_signature)
            self.assertEqual(p.hover_card.identity,identity);self.assertIn('分组',p.hover_card.notice.text())
            self.assertFalse(p.hover_card.picture.pixmap().isNull())

    def test_view_fallback_no_longer_calls_the_recognition_model(self):
        from rouge import relic_recognition
        with patch.object(relic_recognition,'artwork_families',side_effect=AssertionError('recognition module called')):
            pictures.relic_display_records.cache_clear()
            self.assertFalse(pictures.relic_icon('rogue_6_relic_legacy_22_a').pixmap(46,46).isNull())
            self.assertFalse(pictures.relic_icon('rogue_6_legacy_01_1').pixmap(46,46).isNull())
        with patch.object(relic_recognition,'artwork_families',side_effect=ValueError('old dependency')):
            with self.assertRaisesRegex(ValueError,'old dependency'):self.old.relic_icon('rogue_6_relic_legacy_22_a')

    def test_missing_and_corrupt_picture_do_not_borrow_another_item_or_decode_as_success(self):
        self.assertTrue(pictures.relic_icon('rogue_6_legacy_10').pixmap(46,46).isNull())
        self.assertTrue(pictures.relic_icon('not-an-existing-item').isNull())
        with TemporaryDirectory()as folder,patch.object(pictures,'DATA',Path(folder)):
            root=Path(folder);pictures.relic_display_records.cache_clear()
            self.assertTrue(pictures.relic_icon('missing').isNull())
            (root/'bad.png').write_bytes(b'not a PNG')
            (root/'relic-display-icons.json').write_text(json.dumps({'icons':{'bad':{'file':'bad.png'}}}),'utf8')
            pictures.relic_display_records.cache_clear();self.assertTrue(pictures.relic_icon('bad').pixmap(46,46).isNull())
        pictures.relic_display_records.cache_clear()

    def test_shop_uses_the_same_original_image_and_keeps_observation_scope(self):
        from rouge.player_shop_memory import ShopMemoryPanel,recorded_shops
        from rouge.expansion_reference import packet
        from copy import deepcopy
        identity='rogue_6_relic_cargo_15';item=packet()['current']['details']['items'][identity]
        state={'id':'isolated-image-review','history':[{'kind':'shop_items_read','at':1,
            'source':'fresh_shop_exact_names','complete':False,'items':[{'id':identity,'name':item['name']}]}]}
        original=deepcopy(state);rows=recorded_shops(state)
        p=ShopMemoryPanel(SimpleNamespace(state=state,save_issue=None));self.addCleanup(p.close)
        self.assertEqual(p.entries.count(),1);entry=p.entries.item(0);p.entries.setCurrentItem(entry)
        self.assertEqual(entry.data(256),identity);self.assertEqual(entry.text(),item['name'])
        self.assertFalse(entry.icon().pixmap(46,46).isNull())
        self.assertIn('不证明持有、购买',p.detail.toPlainText());p.refresh()
        self.assertEqual(p.entries.currentItem().data(256),identity)
        self.assertEqual(recorded_shops(state),rows);self.assertEqual(state,original)

    def test_public_pool_rendering_preserves_every_count_and_probability_cell(self):
        from rouge.public_archive_view import ArchiveDialog
        from rouge import public_archive as model
        with TemporaryDirectory()as folder:
            p=ArchiveDialog(Path(folder)/'no-personal-cache.json');self.addCleanup(p.close)
            p.pools.setCurrentRow(0)
            self.assertIsNotNone(p.pools.currentItem())
            # Synthetic member records test presentation; these are not a live pool or measured frequency.
            rows=[{'name':'装饰性佯谬','rate':0.125,'count':1,'total':8,'effect':'测试展示，不是实际统计','icon':'rogue_6_relic_cargo_15'},
                  {'name':'襁褓中的猫','rate':None,'count':None,'total':None,'effect':'测试分组参考','icon':'rogue_6_legacy_01_1'}]
            with patch.object(model,'members',return_value=rows):p.render_members()
            self.assertEqual(p.members.rowCount(),2)
            self.assertEqual([p.members.item(0,i).text()for i in range(4)],['装饰性佯谬','12.50%','1／8','测试展示，不是实际统计'])
            self.assertEqual([p.members.item(1,i).text()for i in(1,2)],['未知','未核对'])
            for i in range(2):self.assertFalse(p.members.item(i,0).icon().pixmap(46,46).isNull())
            self.assertIn('独立图样尚未核验',p.members.item(1,0).toolTip())

    def test_history_current_reference_name_and_image_clear_on_source_loss_without_state_mutation(self):
        from rouge.player_evidence_history import EvidenceHistoryPage,evidence_rows,evidence_icon
        from copy import deepcopy
        state={'id':'isolated-history-image-review','history':[
            {'kind':'relic_confirmed','id':'rogue_6_relic_cargo_15','at':1},
            {'kind':'relic_confirmed','id':'rogue_6_legacy_01_1','at':2}]};original=deepcopy(state)
        self.assertEqual(evidence_rows(state)[0]['name'],'固定资料名称未核对')
        p=EvidenceHistoryPage();self.addCleanup(p.close);p.refresh(state);entries=p.lists['relic']
        entries.setCurrentRow(0);self.assertIn('装饰性佯谬',entries.item(0).text())
        self.assertFalse(entries.item(0).icon().pixmap(46,46).isNull())
        self.assertIn('不表示当时版本或领取来源已核验',p.detail.toPlainText())
        entries.setCurrentRow(1);self.assertIn('分组',p.detail.toPlainText())
        with patch('rouge.expansion_reference.packet',return_value=None):
            p.refresh(state);self.assertEqual(entries.currentRow(),1)
            self.assertTrue(entries.item(0).icon().pixmap(46,46).isNull())
            self.assertIn('固定资料名称未核对',entries.item(0).text())
            self.assertNotIn('分组',p.detail.toPlainText())
        p.refresh(state);self.assertEqual(entries.currentRow(),1)
        self.assertFalse(entries.item(0).icon().pixmap(46,46).isNull())
        self.assertEqual(state,original)
        self.assertTrue(evidence_icon({'kind':'relic','id':'bad'}, {'bad':{'iconId':'../rogue_6_relic_cargo_15'}}).isNull())
