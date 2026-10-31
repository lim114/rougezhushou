from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from rouge import player_acceptance
from player_ui_verification import run
out=R/'verification/maintenance/relic-display-image-review-20261031/native-current';out.mkdir(exist_ok=False);images=[];rendered=[]

def check(section,w,gui,require):
    w.show_compact();bar=w.compact_window;bar.open_inventory();gui.processEvents();popup=bar.inventory_popup;p=popup.panel;p.held.setChecked(False)
    data=json.loads((R/'rouge/data/relic-display-icons.json').read_bytes())
    def image(widget,name):
        gui.processEvents();file=out/(name+'.png');assert widget.grab().save(str(file));images.append({'path':file.relative_to(R).as_posix(),'sha256':sha256(file.read_bytes()).hexdigest()})
    def select(identity):
        row=data['icons'][identity];p.search.setText(row['name']);gui.processEvents()
        item=next(p.entries.item(i)for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==identity)
        p.entries.scrollToItem(item);QTest.mouseClick(p.entries.viewport(),Qt.MouseButton.LeftButton,pos=p.entries.visualItemRect(item).center());gui.processEvents()
        require(p.entries.currentItem().data(Qt.ItemDataRole.UserRole)==identity,'actual_selection_'+identity)
        require(not item.icon().pixmap(72,72).isNull(),'actual_decoded_icon_'+identity)
        require(p.reader.isVisible()and row['name']in p.detail.toPlainText(),'actual_reading_'+identity)
        rendered.append({'id':identity,'scope':row['display_scope'],'decoded_and_readable':True})
        return p.rows[identity]
    for identity in data['icons']:select(identity)
    require(len(rendered)==25,'all21_exact_and4_reference_entries_rendered_separately')
    select('rogue_6_relic_cargo_15');image(popup,'dlc1-collectible')
    select('rogue_6_legacy_04');image(popup,'legacy-original')
    row=select('rogue_6_legacy_01_1');require('独立图样尚未核验'in p.detail.toPlainText(),'group_reference_note_visible_in_reader')
    image(popup,'group-reference-reader')
    p.hover_card.install(row,p.version.currentData(),p.source_index,p.source_signature);p.hover_card.show();gui.processEvents()
    require(p.hover_card.identity=='rogue_6_legacy_01_1'and '分组的参考图'in p.hover_card.notice.text(),'group_hover_keeps_exact_identity_and_picture_scope')
    image(p.hover_card,'group-reference-card');p.hover_card.dismiss()
    current=p.entries.currentItem().data(Qt.ItemDataRole.UserRole);text=p.detail.toPlainText();p.refresh();gui.processEvents()
    require(p.entries.currentItem().data(Qt.ItemDataRole.UserRole)==current and p.detail.toPlainText()==text,'same_source_refresh_keeps_reading_and_scope')
    p.search.setText('开局助力');gui.processEvents();item=p.entries.item(0)
    require(item is not None and item.data(Qt.ItemDataRole.UserRole)=='rogue_6_legacy_10','unavailable_entry_remains_distinct')
    require(item.icon().pixmap(72,72).isNull(),'unavailable_asset_not_filled_with_another_item');image(popup,'remaining-unavailable')
    popup.hide()
    from types import SimpleNamespace
    from rouge.player_shop_memory import ShopMemoryPanel
    from rouge.expansion_reference import packet
    identity='rogue_6_relic_cargo_15';name=packet()['current']['details']['items'][identity]['name']
    state={'id':'isolated-ui-image-review','history':[{'kind':'shop_items_read','at':1,'source':'fresh_shop_exact_names','complete':False,'items':[{'id':identity,'name':name}]}]}
    original=deepcopy(state);shop=ShopMemoryPanel(SimpleNamespace(state=state,save_issue=None));shop.resize(650,640);shop.show();gui.processEvents()
    entry=shop.entries.item(0);QTest.mouseClick(shop.entries.viewport(),Qt.MouseButton.LeftButton,pos=shop.entries.visualItemRect(entry).center());gui.processEvents()
    require(shop.entries.currentItem().data(Qt.ItemDataRole.UserRole)==identity,'shop_exact_item_selected')
    require(not entry.icon().pixmap(72,72).isNull(),'shop_new_original_decodes')
    require('不证明持有、购买'in shop.detail.toPlainText(),'shop_observation_scope_retained')
    image(shop,'shop-original-image');shop.close();require(state==original,'shop_fixture_not_mutated')
    from rouge.public_archive_view import ArchiveDialog
    from rouge.public_archive import members
    archive=ArchiveDialog(out/'absent-isolated-cache.json');archive.show();gui.processEvents()
    require(archive.select_exact_pool('dlc1','rogue_6:诡意行商'),'public_exact_dlc1_pool_selected')
    index=next(i for i in range(archive.members.rowCount())if archive.members.item(i,0).text()==name)
    archive.members.selectRow(index);archive.members.scrollToItem(archive.members.item(index,0));gui.processEvents()
    require(not archive.members.item(index,0).icon().pixmap(72,72).isNull(),'public_new_original_decodes')
    require(archive.members.item(index,1).text()=='未知','public_absent_probability_remains_unknown')
    image(archive,'public-pool-original-image');archive.close()
    from rouge.player_evidence_history import EvidenceHistoryPage
    history={'id':'isolated-ui-history','history':[{'kind':'relic_confirmed','id':identity,'at':1},{'kind':'relic_confirmed','id':'rogue_6_legacy_01_1','at':2}]}
    original=deepcopy(history);page=EvidenceHistoryPage();page.resize(650,570);page.refresh(history);page.show();gui.processEvents()
    entries=page.lists['relic'];QTest.mouseClick(entries.viewport(),Qt.MouseButton.LeftButton,pos=entries.visualItemRect(entries.item(0)).center());gui.processEvents()
    require(name in page.detail.toPlainText(),'history_current_name_readable')
    require('当时版本或领取来源已核验'in page.detail.toPlainText(),'history_current_reference_qualification_visible')
    require(not entries.item(0).icon().pixmap(72,72).isNull(),'history_original_decodes');image(page,'history-original-image')
    QTest.mouseClick(entries.viewport(),Qt.MouseButton.LeftButton,pos=entries.visualItemRect(entries.item(1)).center());gui.processEvents()
    require('独立图样尚未核验'in page.detail.toPlainText(),'history_group_reference_visible');image(page,'history-group-reference')
    with patch('rouge.expansion_reference.packet',return_value=None):
        page.refresh(history);gui.processEvents()
        require(entries.currentRow()==1 and entries.item(0).icon().pixmap(72,72).isNull() and '固定资料名称未核对'in entries.item(0).text(),'history_source_loss_clears_reference_and_preserves_selection')
    page.refresh(history);gui.processEvents();require(entries.currentRow()==1 and not entries.item(0).icon().pixmap(72,72).isNull(),'history_source_recovery_restores_exact_reference')
    require(history==original,'history_fixture_not_mutated');page.close()
    popup.show();w.player_validation_target=popup

with patch.object(player_acceptance,'check',check):code=run(999,out/'receipt.json')
(out/'images.json').write_text(json.dumps({'images':images,'rendered':rendered,'not_game_samples':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)
