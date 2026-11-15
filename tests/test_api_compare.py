import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('api_compare', Path(__file__).resolve().parents[1] / 'scripts/api_compare.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class APIComparison(unittest.TestCase):
    def test_unknown_versions_are_indeterminate(self):
        for version in ('unknown', '???', 'latest', '   '):
            with self.subTest(version=version):
                old = self.contract('keiyoushi')
                old['versions']['api'] = version
                new = self.contract('keiyoushi')
                new['versions']['api'] = version
                self.assertEqual(api.compare(old, new)['classification'], 'INDETERMINADO')

    def contract(self, ecosystem):
        symbols = {
            'keiyoushi': {'KeiSource.chapterList': '(SManga): List<SChapter>'},
            'yuzono': {'AnimeHttpSource.getVideoList': '(Hoster): List<Video>'},
            'lnreader': {'PluginBase.parseChapter': '(path: string): Promise<string>'},
        }
        return {'ecosystem': ecosystem, 'scope': 'fixture-contract', 'complete': True,
                'symbols': symbols[ecosystem].copy(), 'versions': {'api': '1.2.0'}}

    def test_three_ecosystems_additive_and_breaking(self):
        for ecosystem in ('keiyoushi', 'yuzono', 'lnreader'):
            with self.subTest(ecosystem=ecosystem):
                old = self.contract(ecosystem)
                new = self.contract(ecosystem)
                symbol = next(iter(old['symbols']))
                self.assertEqual(api.compare(old, new)['classification'], 'COMPATIVEL_NO_ESCOPO_DECLARADO')
                new['symbols']['source.extra'] = '(): Result'
                self.assertEqual(api.compare(old, new)['classification'], 'INDETERMINADO')
                new['symbols'][symbol] = '(incompatible-argument): IncompatibleResult'
                self.assertEqual(api.compare(old, new)['classification'], 'POTENCIALMENTE_INCOMPATIVEL')
                new['symbols'].pop(symbol)
                self.assertEqual(api.compare(old, new)['classification'], 'POTENCIALMENTE_INCOMPATIVEL')

    def test_uncertainty_and_isolation(self):
        old = self.contract('lnreader')
        new = self.contract('lnreader')
        new['complete'] = False
        self.assertEqual(api.compare(old, new)['classification'], 'INDETERMINADO')
        new['versions']['api'] = '1.3.0'
        self.assertEqual(api.compare(old, new)['classification'], 'INDETERMINADO')
        new['versions']['api'] = '2.0.0'
        self.assertEqual(api.compare(old, new)['classification'], 'POTENCIALMENTE_INCOMPATIVEL')
        new['ecosystem'] = 'yuzono'
        with self.assertRaises(ValueError):
            api.compare(old, new)

    def test_extract_source_detects_signature_changes_conservatively(self):
        cases = {
            'keiyoushi': ('interface MangaApi {\n fun chapters(id: String): List<Chapter>\n}', 'fun chapters(id: String): List<Chapter>', 'fun chapters(id: Int): List<Chapter>'),
            'yuzono': ('interface AnimeApi {\n fun videos(id: String): List<Video>\n}', 'fun videos(id: String): List<Video>', 'fun videos(id: Int): List<Video>'),
            'lnreader': ('interface PluginBase {\n parseChapter(path: string): Promise<string>;\n}', 'parseChapter(path: string): Promise<string>;', 'parseChapter(path: number): Promise<string>;'),
        }
        for ecosystem, (source, before, after) in cases.items():
            with self.subTest(ecosystem=ecosystem):
                old = api.extract(source, ecosystem, 'fixture.ts' if ecosystem == 'lnreader' else 'fixture.kt')
                new = api.extract(source.replace(before, after), ecosystem, old['scope'])
                self.assertFalse(old['complete'])
                self.assertEqual(api.compare(old, new)['classification'], 'POTENCIALMENTE_INCOMPATIVEL')
