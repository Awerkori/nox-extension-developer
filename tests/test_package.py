import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location('package', Path(__file__).resolve().parents[1] / 'scripts/package.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def test_distribution_contains_bilingual_documentation(self):
        required = {'README.en.md', 'docs/pt-BR/guia.md', 'docs/en/guide.md',
                    'prompts/install-pt-BR.txt', 'prompts/install-en.txt',
                    'assets/banner.svg', 'assets/logo.svg', 'SECURITY.md',
                    'CONTRIBUTING.md', 'CONTRIBUTING.en.md', 'CODE_OF_CONDUCT.md'}
        self.assertTrue(required.issubset(package.FILES))

    def test_deterministic_allowlist_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='nox-package-') as tmp:
            root = Path(tmp) / 'source'
            root.mkdir()
            for name in package.FILES:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(name)
            (root / 'secret.txt').write_text('do not package')
            a, b = Path(tmp) / 'a.zip', Path(tmp) / 'b.zip'
            package.build(root, a)
            package.build(root, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            with zipfile.ZipFile(a) as archive:
                self.assertEqual(set(archive.namelist()), {'nox-extension-developer/' + n for n in package.FILES})
            with self.assertRaises(FileExistsError):
                package.build(root, a)

    def test_refuses_symlink_source(self):
        with tempfile.TemporaryDirectory(prefix='nox-package-') as tmp:
            root = Path(tmp) / 'source'
            root.mkdir()
            for name in package.FILES:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(name)
            (root / 'SKILL.md').unlink()
            (root / 'SKILL.md').symlink_to(root / 'README.md')
            with self.assertRaises(ValueError):
                package.build(root, Path(tmp) / 'a.zip')

    def test_failed_write_leaves_no_published_archive(self):
        with tempfile.TemporaryDirectory(prefix='nox-package-') as tmp:
            root = Path(tmp) / 'source'
            root.mkdir()
            for name in package.FILES:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(name)
            output = Path(tmp) / 'candidate.zip'
            with patch.object(zipfile.ZipFile, 'writestr', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    package.build(root, output)
            self.assertFalse(output.exists())

    def test_refuses_symlink_parent_directory(self):
        with tempfile.TemporaryDirectory(prefix='nox-package-') as tmp:
            root = Path(tmp) / 'source'
            root.mkdir()
            for name in package.FILES:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(name)
            scripts = root / 'scripts'
            moved = root / 'scripts-real'
            scripts.rename(moved)
            scripts.symlink_to(moved, target_is_directory=True)
            with self.assertRaises(ValueError):
                package.build(root, Path(tmp) / 'candidate.zip')
