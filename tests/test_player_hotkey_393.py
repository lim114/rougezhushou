import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.player_hotkey import GlobalHotkey,DEFAULT,WM_HOTKEY,parse_shortcut,load_preferences,save_preferences

class Api:
    def __init__(self):self.keys={};self.fail=False;self.release_fail=False
    def register(self,i,m,v):
        if self.fail:return False
        self.keys[i]=(m,v);return True
    def unregister(self,i):
        if self.release_fail:return False
        return self.keys.pop(i,None)is not None

class Hotkey(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def test_canonical_supported_keys(self):
        self.assertEqual(parse_shortcut('alt+ctrl+space'),(DEFAULT,3,32))
        self.assertEqual(parse_shortcut('Ctrl+Shift+F11'),('Ctrl+Shift+F11',6,122))
        self.assertEqual(parse_shortcut('Tab',True),('Tab',0,9))
    def test_invalid_or_reserved_combinations(self):
        for text in ('Tab','A','F1','Ctrl+Ctrl+A','Win+A','Ctrl+F12','Ctrl+','Ctrl+Enter','Ctrl+A,B'):
            with self.subTest(text=text),self.assertRaises(ValueError):parse_shortcut(text)
    def test_missing_preferences_never_written(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'new.json';data,warning=load_preferences(p)
            self.assertEqual(data,{'enabled':True,'shortcut':DEFAULT,'allow_single':False});self.assertEqual(warning,'');self.assertFalse(p.exists())
    def test_bad_preferences_remain_untouched(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'prefs.json'
            for raw in ('broken','[]',json.dumps({'enabled':'false','shortcut':'Tab','allow_single':True}),json.dumps({'enabled':True,'shortcut':'Tab','allow_single':False})):
                p.write_text(raw);data,warning=load_preferences(p);self.assertEqual(data['shortcut'],DEFAULT);self.assertTrue(warning);self.assertEqual(p.read_text(),raw)
    def test_preferences_atomic_round_trip(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'child/prefs.json';data={'enabled':False,'shortcut':'Tab','allow_single':True}
            save_preferences(p,data);self.assertEqual(load_preferences(p),(data,''));self.assertEqual(list(p.parent.iterdir()),[p])
    def test_conflict_preserves_previous_registration(self):
        api=Api();key=GlobalHotkey(api=api)
        try:
            self.assertTrue(key.configure(True,DEFAULT)[0]);original=key.binding;api.fail=True
            ok,message=key.configure(True,'Ctrl+Shift+F10');self.assertFalse(ok);self.assertIn('占用',message);self.assertEqual(key.binding,original);self.assertEqual(len(api.keys),1)
        finally:key.close()
    def test_change_unregisters_old_and_close_is_idempotent(self):
        api=Api();key=GlobalHotkey(api=api)
        key.configure(True,DEFAULT);old=key.binding[0];key.configure(True,DEFAULT);self.assertEqual(key.binding[0],old)
        key.configure(True,'Ctrl+Shift+F10');self.assertNotIn(old,api.keys);self.assertEqual(len(api.keys),1);key.close();key.close();self.assertFalse(api.keys)
    def test_only_exact_owned_message_triggers(self):
        api=Api();key=GlobalHotkey(api=api);seen=[];key.triggered.connect(lambda:seen.append(True))
        try:
            key.configure(True,DEFAULT);i,m,v=key.binding
            for msg,identity,packed in ((0,i,m|(v<<16)),(WM_HOTKEY,i+1,m|(v<<16)),(WM_HOTKEY,i,4|(v<<16)),(WM_HOTKEY,i,m|(65<<16))):self.assertFalse(key.dispatch(msg,identity,packed))
            self.assertTrue(key.dispatch(WM_HOTKEY,i,m|(v<<16)));self.assertEqual(seen,[True])
            key.configure(False,DEFAULT);self.assertFalse(key.dispatch(WM_HOTKEY,i,m|(v<<16)))
        finally:key.close()
    def test_release_failure_preserves_binding(self):
        api=Api();key=GlobalHotkey(api=api);key.configure(True,DEFAULT);old=key.binding;api.release_fail=True
        self.assertFalse(key.configure(False,DEFAULT)[0]);self.assertEqual(key.binding,old)
        api.release_fail=False;key.close()
    def test_write_failure_is_explicit(self):
        with tempfile.TemporaryDirectory()as d:
            with self.assertRaises(OSError):save_preferences(Path(d),{})
    def test_receiver_never_shown_and_not_a_toolbar_handle(self):
        api=Api();key=GlobalHotkey(api=api)
        try:self.assertFalse(key.receiver.isVisible());self.assertIsNone(key.receiver.parentWidget())
        finally:key.close()
