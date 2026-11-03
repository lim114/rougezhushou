"""Reuse the native440 harness for the reviewed map disclosure; no game inputs."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from player_ui_verification import run
from rouge import player_acceptance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    original=player_acceptance.check
    extra=[]
    def check(section,window,gui,require):
        original(section,window,gui,require)
        panel=window.compact_window.map_popup.panel
        require(not panel.finder.isVisible() and panel.view.isVisible(),'map_first_default_without_search_rows')
        default=args.receipt.with_name('map-default.png')
        require(window.compact_window.map_popup.grab().save(str(default)),'actual_default_map_snapshot_saved')
        extra.append({'file':default.as_posix(),'sha256':sha256(default.read_bytes()).hexdigest()})
        panel.finder_toggle.click();gui.processEvents()
        require(panel.node_query.isVisible() and panel.coverage_notice.isVisible(),'optional_search_and_coverage_expand_together')
        panel.finder_toggle.click();gui.processEvents()
        require(not panel.node_query.isVisible(),'optional_map_controls_collapse_without_reset')
        window.player_validation_target=window.compact_window.map_popup
    player_acceptance.check=check
    code=run(440,args.receipt)
    if code==0:
        view=args.receipt.with_name('review-extra-images.json')
        view.write_text(json.dumps({'kind':'maintenance_uses_native440_harness_not_new_section','images':extra},ensure_ascii=False,indent=2)+'\n','utf-8')
    raise SystemExit(code)
