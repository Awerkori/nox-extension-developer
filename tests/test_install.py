import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch


spec = importlib.util.spec_from_file_location('install', Path(__file__).resolve().parents[1] / 'scripts/install.py')
install = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install)


class Installer(unittest.TestCase):
    def setUp(self):
        base = Path(tempfile.gettempdir())
        self.tmp = tempfile.TemporaryDirectory(prefix='nox-install-test-', dir=base)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'nox-extension-developer'
        self.root.mkdir()
        (self.root / 'SKILL.md').write_text('fixture')
        self.destination = Path(self.tmp.name) / 'skills'
        self.destination.mkdir()

    def run_install(self):
        with patch.object(install, 'ROOT', self.root), patch.object(install, 'DESTINATIONS', {'opencode': self.destination}), patch.object(sys, 'argv', ['install.py', 'opencode']), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            install.main()

    def test_link_and_idempotence(self):
        self.run_install()
        link = self.destination / self.root.name
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), self.root)
        self.run_install()
        self.assertTrue(link.is_symlink())

    def test_renamed_source_uses_canonical_skill_name(self):
        renamed = self.root.with_name('downloaded-release')
        self.root.rename(renamed)
        self.root = renamed
        self.run_install()
        link = self.destination / 'nox-extension-developer'
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), renamed)

    def test_refuses_existing_directory_and_dangling_link(self):
        dest = self.destination / self.root.name
        dest.mkdir()
        (dest / 'keep').write_text('preserve')
        with self.assertRaises(SystemExit):
            self.run_install()
        self.assertEqual((dest / 'keep').read_text(), 'preserve')
        (dest / 'keep').unlink()
        dest.rmdir()
        dest.symlink_to(self.destination / 'missing')
        with self.assertRaises(SystemExit):
            self.run_install()
        self.assertTrue(os.path.lexists(dest))
        self.assertTrue(dest.is_symlink())


if __name__ == '__main__':
    unittest.main()
