from pathlib import Path
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'verification/sections/299-preparation/before/rouge/battle_view.py'
raw=SOURCE.read_bytes();assert raw==(ROOT/'rouge/battle_view.py').read_bytes()
nl='\r\n' if b'\r\n'in raw else '\n'
def replace(old,new):
 global raw
 a=old.replace('\n',nl).encode();b=new.replace('\n',nl).encode();assert raw.count(a)==1,old[:90];raw=raw.replace(a,b)
replace('from .battle_entry_reference_view import BattleEntryReferencePanel,entry_packet',
 'from .battle_entry_reference_view import BattleEntryReferencePanel,entry_packet\nfrom . import spawn_candidates\nfrom .spawn_candidates_view import SpawnCandidatesPanel')
replace("        self.branch_toggle=QCheckBox('展开特殊出怪条件与位置');layout.addWidget(self.branch_toggle)","""        candidates=QHBoxLayout()
        self.spawn_candidates_button=QPushButton('查看本关全部候选资料');candidates.addWidget(self.spawn_candidates_button)
        self.spawn_group_button=QPushButton('查看所选条目的同组候选');candidates.addWidget(self.spawn_group_button)
        layout.addLayout(candidates)
        self.spawn_candidates_window=None;self.candidate_preview_window=None
        self._spawn_candidates_current=False;self._candidate_preview_token=None
        self.spawn_candidates_button.clicked.connect(lambda:self.open_spawn_candidates())
        self.spawn_group_button.clicked.connect(self.open_current_spawn_candidates)
        self.branch_toggle=QCheckBox('展开特殊出怪条件与位置');layout.addWidget(self.branch_toggle)""")
replace('    def open_highland_top(self):', '''    def _clear_candidate_preview(self):
        if self.candidate_preview_window is not None:
            self.candidate_preview_window.set_stage(None)
            self.candidate_preview_window.close()
            self.candidate_preview_window.deleteLater()
            self.candidate_preview_window=None
        self._candidate_preview_token=None

    def _current_main_spawn_id(self):
        item=self.spawn_list.currentItem()
        row=item.data(Qt.ItemDataRole.UserRole) if item else None
        return row['id'] if row and not row.get('branch') and self._rows_stage==self.current_stage else None

    def _refresh_spawn_candidates(self):
        packet=spawn_candidates.stage_reference(self.current_stage)
        known=bool(packet and packet.get('source_valid'))
        self.spawn_candidates_button.setVisible(packet is not None)
        self.spawn_candidates_button.setEnabled(known)
        identity=self._current_main_spawn_id()
        linked=known and identity is not None and any(m['action_id']==identity
            for r in packet['groups']+packet['packages'] for m in r['members'])
        self.spawn_group_button.setVisible(packet is not None)
        self.spawn_group_button.setEnabled(bool(linked))
        self.spawn_group_button.setToolTip('只查看固定主出怪计划；条件分支不借用同名候选组。')
        if self.spawn_candidates_window is not None:
            origin=self._current_main_spawn_id() if self._spawn_candidates_current else None
            if self._spawn_candidates_current and origin is None:
                self.spawn_candidates_window.set_reference(None)
            else:
                self.spawn_candidates_window.set_reference(self.current_stage,origin,
                    scope_key=(self.current_stage,'current' if self._spawn_candidates_current else 'all',origin))
        if self._candidate_preview_token is not None and not spawn_candidates.resolve_reference(self._candidate_preview_token):
            self._clear_candidate_preview()

    def open_spawn_candidates(self,origin_action_id=None):
        packet=(spawn_candidates.stage_reference(self.current_stage) if origin_action_id is None else
                spawn_candidates.action_reference(self.current_stage,origin_action_id))
        if not packet or not packet.get('source_valid') or not (packet['groups'] or packet['packages']):
            if self.spawn_candidates_window is not None:self.spawn_candidates_window.set_reference(None)
            return False
        self._spawn_candidates_current=origin_action_id is not None
        if self.spawn_candidates_window is None:
            self.spawn_candidates_window=SpawnCandidatesPanel(self)
            self.spawn_candidates_window.spawnReferenceSelected.connect(self._request_spawn_candidate)
            self.spawn_candidates_window.sourceInvalidated.connect(self._clear_candidate_preview)
        self.spawn_candidates_window.set_reference(self.current_stage,origin_action_id,
            scope_key=(self.current_stage,'current' if self._spawn_candidates_current else 'all',origin_action_id))
        self.spawn_candidates_window.show();self.spawn_candidates_window.raise_();self.spawn_candidates_window.activateWindow()
        return True

    def open_current_spawn_candidates(self):
        identity=self._current_main_spawn_id()
        return False if identity is None else self.open_spawn_candidates(identity)

    def _request_spawn_candidate(self,token):
        panel=self.spawn_candidates_window
        if panel is None or not isinstance(token,dict) or not panel.packet or not panel.packet.get('source_valid'):
            return False
        if token.get('stage_id')!=self.current_stage or token.get('origin_action_id')!=panel.origin_action_id or (
                token.get('scope_key')!=panel.packet.get('scope_key')):return False
        if self._spawn_candidates_current and self._current_main_spawn_id()!=token.get('origin_action_id'):return False
        resolved=spawn_candidates.resolve_reference(token)
        reference=resolved['member'].get('spawn_reference') if resolved else None
        if not reference or reference['stage_id']!=self.current_stage:return False
        rows=spawn_rows(self.current_stage,include_branches=False)
        matching=[row for row in rows if row['id']==reference['action_id'] and
            row['action']==resolved['member']['raw_action'] and row['action']['key']==reference['enemy_id']]
        if len(matching)!=1:return False
        self._clear_candidate_preview()
        # A separate fixed preview keeps the reader's original filters, cell,
        # enemy, ordinal and text untouched. It never controls a game instance.
        preview=BattlePreviewPanel(self);preview.setWindowFlag(Qt.WindowType.Window,True)
        preview.setWindowTitle('出怪候选资料 · '+panel.packet['stage_name']+' · '+resolved['member']['display_name'])
        preview.resize(1050,720);preview.set_context(copy.deepcopy(self.context));preview.set_stage(self.current_stage)
        index=next((i for i,row in enumerate(preview.rows) if row['id']==reference['action_id']),None)
        if index is None:
            preview.close();preview.deleteLater();return False
        preview.spawn_list.setCurrentRow(index);preview._spawn_selected(preview.spawn_list.currentItem())
        preview._render_enemy(reference['enemy_id'],reference['level'])
        self.candidate_preview_window=preview;self._candidate_preview_token=copy.deepcopy(token)
        preview.show();preview.raise_();preview.activateWindow();return True

    def open_highland_top(self):''')
replace('    def _load_stage(self,sid):\n        self._rows_stage=None;', '''    def _load_stage(self,sid):
        self._clear_candidate_preview()
        if self.spawn_candidates_window is not None:self.spawn_candidates_window.set_reference(None)
        self._rows_stage=None;''')
replace('        self._refresh_branch_positions()\n\n    def _refresh_branch_positions(self,*_):',
 '        self._refresh_branch_positions()\n        self._refresh_spawn_candidates()\n\n    def _refresh_branch_positions(self,*_):')
replace("        self._render_enemy(row['action']['key'],selected[1] if selected else None,preserve=preserve)\n\n    def _occurrence_changed", "        self._render_enemy(row['action']['key'],selected[1] if selected else None,preserve=preserve)\n        self._refresh_spawn_candidates()\n\n    def _occurrence_changed")
destination=ROOT/'.cache/p3-299-root-integration/candidate/rouge/battle_view.py';destination.parent.mkdir(parents=True,exist_ok=True)
assert not destination.exists();destination.write_bytes(raw)
print('299 exact parent source draft, SHA '+sha256(raw).hexdigest()+', not promoted or tested')
