"""Stdlib Source-text assembly only; never import or execute candidate/project."""
from pathlib import Path
import difflib
import hashlib
import json

PACKET = Path('/workspace/.continuation/section099-run-persistence-v2')
BASE = Path('/workspace/.continuation/resume098-run-cache-v2/candidate/rouge/run_state.py')
raw = BASE.read_bytes()
source = raw.decode('utf-8')
newline = '\r\n' if '\r\n' in source else '\n'


def change(old, new):
    global source
    old = old.replace('\n', newline)
    new = new.replace('\n', newline)
    assert source.count(old) == 1, old
    source = source.replace(old, new, 1)


change("        self.preserve_unreadable=False\n        self.reset(save=False)\n        try:",
       "        self.preserve_unreadable=False\n        self.save_issue=None\n        self.reset(save=False)\n        repair_needs_save=False\n        try:")
change("        except FileNotFoundError:pass\n        except (OSError,ValueError):",
       "        except FileNotFoundError:\n            # A dangling link or unknown lstat is not a confirmed absent entry.\n            confirmed_absent=False\n            try:self.file.lstat()\n            except FileNotFoundError:confirmed_absent=True\n            except OSError:pass\n            if not confirmed_absent:\n                self.preserve_unreadable=True\n                self.state['notice']='原本局记录无法读取；手动重置前不会覆盖原路径。'\n        except (OSError,ValueError):")
change("            if self.restore_origin_discovery_buffs():self.save()",
       "            repair_needs_save=self.restore_origin_discovery_buffs()")
change("            self.state['notice']='原本局记录无法读取，已保留原文件；手动重置前不会覆盖它。'\n\n    def restore_passed_node_types",
       "            self.state['notice']='原本局记录无法读取，已保留原文件；手动重置前不会覆盖它。'\n        # Saving accepted repairs is separate from reading/qualifying the file.\n        if repair_needs_save:self.save()\n\n    def restore_passed_node_types")
change("    def save(self):\n        if self.preserve_unreadable:return\n        self.file.parent.mkdir(exist_ok=True)\n        temporary=self.file.with_suffix('.tmp')\n        temporary.write_text(json.dumps(self.state,ensure_ascii=False,indent=2),encoding='utf-8')\n        temporary.replace(self.file)\n",
       """    def save(self):
        # A failed session must not retry, including after a manual new run.
        # The explicit reset still clears memory; it cannot make failed IO safe.
        if self.preserve_unreadable or self.save_issue:return False
        text=json.dumps(self.state,ensure_ascii=False,indent=2)
        # Decoding an escaped native high/low pair would fold two Python points.
        # Refuse that lossy write before any directory or temporary-file IO.
        if any(0xd800<=ord(a)<=0xdbff and 0xdc00<=ord(b)<=0xdfff
               for a,b in zip(text,text[1:])):
            self.save_issue='本局记录含暂时无法无损保存的文字，保存未完成'
            return False
        # Escape lone code units after JSON quoting, retaining ordinary Unicode
        # and write_text's original platform newline policy.
        text=text.encode('utf-8',errors='backslashreplace').decode('utf-8')
        try:
            self.file.parent.mkdir(exist_ok=True)
            temporary=self.file.with_suffix('.tmp')
            temporary.write_text(text,encoding='utf-8')
            temporary.replace(self.file)
        except OSError:
            self.save_issue='本局记录保存未完成'
            return False
        return True

    def persistence_notice(self):
        if not self.save_issue:return ''
        return (self.save_issue+'；新的读取及“开始新局”的结果仅在当前运行有效。'
            '重新启动可能恢复磁盘中较早的记录；当前运行不会再次写入或覆盖本局记录。')
""")
change("    def summary(self):\n        status=self.inventory_status();state=self.state\n",
       "    def summary(self):\n        status=self.inventory_status();state=self.state\n        notice=state['notice']\n        if self.save_issue:\n            notice=notice.replace('持续累积并保存','持续累积')+'\\n'+self.persistence_notice()\n")
change("if conflicts else []),state['notice']])", "if conflicts else []),notice])")

candidate = source.encode('utf-8')
baseline = PACKET / 'baseline/rouge/run_state.py'
output = PACKET / 'candidate/rouge/run_state.py'
for path, data in ((baseline, raw), (output, candidate)):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(data)
patch = ''.join(difflib.unified_diff(raw.decode('utf-8').splitlines(True),
                                   source.splitlines(True),
                                   fromfile='a/rouge/run_state.py',
                                   tofile='b/rouge/run_state.py'))
with (PACKET / 'run-persistence.patch').open('x', encoding='utf-8', newline='') as handle:
    handle.write(patch)


def row(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


manifest = {
    'status': 'SOURCE_ONLY_NOT_APPLIED_NOT_EXECUTED',
    'section': 99,
    'completed_increment': 0,
    'runtime_pass': False,
    'scope': 'Run save IO continuity, qualified Unicode transport, separate load/save state, dangling-entry read protection and explicit manual-new-run boundary',
    'expected_after098': row(BASE),
    'baseline': row(baseline),
    'candidate': row(output),
    'tests': row(PACKET / 'candidate/tests/test_run_persistence_099.py'),
    'preliminary_v1_source_packet': str(Path('/workspace/.continuation/section099-run-persistence-v1/source-manifest.json')),
    'root_original_defect_reproduction_refs': [row(Path('/workspace/.continuation/resume099-100-original-reproduction-v1'+suffix)) for suffix in ('.json', '.log', '.exit-code')],
    'patch': row(PACKET / 'run-persistence.patch'),
    'assembly_source': row(Path(__file__)),
    'app_transport': 'No app replacement. Existing run_summary.setText(run.summary()) displays session persistence_notice after apply and reset, retaining actual 096/098 app increments.',
    'registry_transport': 'Root adds tests.test_run_persistence_099 to actually completed 098 scripts/verify_cloud.py registry, preserving all existing names/order.',
    'manual_reset_policy': 'Retain explicit new id/empty memory and clear load guard, but do not clear save_issue; no failed-session automatic retry or old-run rollback.',
    'save_failure_policy': 'OSError or native adjacent high/low refusal returns False, leaves accepted memory usable, never deletes/replays temporary evidence; other program/serialization errors propagate.',
    'source_references': [row(Path('/workspace/rougezhushou/rouge/run_state.py')),
                          row(Path('/workspace/rougezhushou/rouge/app.py')),
                          row(Path('/workspace/.continuation/section099-io-semantics-static-review-v1.md')),
                          row(Path('/workspace/.continuation/p2-after096-account-metadata-source-survey-v1/public-documents/python-json-3.12.html')),
                          row(Path('/workspace/.continuation/p2-after096-account-metadata-source-survey-v1/public-documents/rfc8259.html'))],
    'calls': {'project_imports': 0, 'project_calls': 0, 'tests': 0, 'fixture_codecs': 0,
              'Wine': 0, 'Qt': 0, 'Git': 0, 'private_reads': 0, 'tracked_writes': 0},
    'limitations': ['No native Windows/game/chat verification.',
                    'No fsync/atomic durability or multiple-writer claim.',
                    'Fixed distinct normal run-state.json/run-state.tmp paths; aliases/.tmp target/path encoding remain outside this section; only dangling-entry read guard qualified.',
                    'No universal arbitrary Python graph/value or non-CPython Unicode round-trip claim.',
                    'Existing serializer key/NaN/opaque input policy not expanded or normalized.',
                    'Source-only packet is not actual completed098 source, reproduction, full095 PASS, commit or publication.']
}
with (PACKET / 'source-manifest.json').open('x', encoding='utf-8') as handle:
    json.dump(manifest, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps({'status': manifest['status'], 'baseline': row(baseline),
                  'candidate': row(output), 'tests': manifest['tests']}, ensure_ascii=False))
