from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from rouge import current_event_directory as model


class EventSourcePathContractTests(TestCase):
    def test_non_text_rejected_before_path_constructor(self):
        for value in (None, 0, False, [], Path('source.json')):
            with self.subTest(value=value), patch.object(model, 'PurePosixPath') as parse:
                with self.assertRaises(ValueError):
                    model._file(value)
                parse.assert_not_called()

    def test_canonical_file_and_invalid_paths(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source.json').write_text('{}', encoding='utf-8')
            (root / 'folder').mkdir()
            with patch.object(model, 'ROOT', root):
                self.assertEqual(model._file('source.json'), root / 'source.json')
                for name in ('../source.json', '/source.json', 'C:/source.json', 'folder/../source.json', './source.json', 'folder//file', 'folder', 'absent.json', 'folder\\file'):
                    with self.subTest(name=name), self.assertRaises(ValueError):
                        model._file(name)

    def test_file_and_parent_link_rejection(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / 'folder'
            folder.mkdir()
            file = folder / 'source.json'
            file.write_text('{}', encoding='utf-8')
            for link in (file, folder):
                with self.subTest(link=link), patch.object(model, 'ROOT', root), patch.object(Path, 'is_symlink', lambda path: path == link):
                    with self.assertRaises(ValueError):
                        model._file('folder/source.json')
