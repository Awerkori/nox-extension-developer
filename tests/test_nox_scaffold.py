import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import nox_scaffold


class ScaffoldAndFunctionalScenariosTests(unittest.TestCase):
    def test_scaffold_produces_official_non_mixed_ecosystems(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            k = nox_scaffold.scaffold_extension('keiyoushi', 'ScanManga', 'https://scan.example', lang='pt-BR', output_dir=root / 'k')
            y = nox_scaffold.scaffold_extension('yuzono', 'AnimeBox', 'https://anime.example', lang='pt-BR', output_dir=root / 'y')
            l = nox_scaffold.scaffold_extension('lnreader', 'NovelHub', 'https://novel.example', lang='en', output_dir=root / 'l')

            self.assertEqual(k['inspection']['ecosystem'], 'keiyoushi')
            self.assertEqual(k['inspection']['architecture'], 'modern-ksp')
            self.assertIn('KeiSource', Path(k['created_files'][1]).read_text())

            self.assertEqual(y['inspection']['ecosystem'], 'yuzono')
            self.assertEqual(y['inspection']['architecture'], 'modern-ksp')
            self.assertIn('AnimeHttpSource', Path(y['created_files'][1]).read_text())

            self.assertEqual(l['inspection']['ecosystem'], 'lnreader')
            self.assertEqual(l['inspection']['architecture'], 'lnreader-standalone')
            self.assertIn('@libs/fetch', Path(l['created_files'][0]).read_text())

    def test_end_to_end_http_scenarios_creation_repair_update(self):
        res = nox_scaffold.run_functional_scenarios()
        self.assertEqual(res['status'], 'PASS')
        self.assertEqual(res['scenario_a_creation']['status'], 'PASS')
        self.assertEqual(res['scenario_b_repair']['before_statuses'], ['FAIL', 'FAIL', 'FAIL'])
        self.assertEqual(res['scenario_b_repair']['after_statuses'], ['PASS', 'PASS', 'PASS'])
        self.assertEqual(res['scenario_c_update']['status'], 'PASS')
        self.assertTrue(res['scenario_c_update']['rename_blocked'])


if __name__ == '__main__':
    unittest.main()
