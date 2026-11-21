from contextlib import redirect_stdout
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import nox
import nox_matrix


class CliAndMatrixTests(unittest.TestCase):
    def test_matrix_0001_to_1200_completeness_semantic_bindings_and_three_counters(self):
        summary = nox_matrix.validate_matrix()
        self.assertEqual(summary['status'], 'PASS')
        self.assertEqual(summary['missing_0001_1000'], [])
        self.assertEqual(summary['duplicates'], 0)
        self.assertEqual(summary['inconsistent_items'], [])
        self.assertEqual(summary['ORIGINAL_IMPLEMENTADO'], 1000)
        self.assertEqual(summary['NOVO_IMPLEMENTADO'], 200)
        self.assertEqual(summary['TOTAL_VALIDO'], 1200)
        self.assertEqual(summary['autonomous_1001_plus'], 200)
        self.assertEqual(summary['total_items'], 1200)
        self.assertTrue(summary['target_original_1000_reached'])
        self.assertFalse(summary['target_2000_reached'])
        self.assertEqual(summary['target_2000_aspirational_status'], 'CONCLUDED_AT_1200_QUALITATIVE_SATURATION')

    def test_no_false_c05_or_section_routing_mismatches_in_matrix(self):
        import nox_enhancements
        items = nox_matrix.load_matrix()['items']
        by_id = {it['id']: it for it in items}
        self.assertEqual(nox_enhancements.verify_no_false_c05_image_routing(items)['false_c05_items'], [])
        self.assertEqual(nox_enhancements.verify_no_section_level_routing_mismatch(items)['section_mismatches'], [])
        for bad_id in ('0376', '0409', '0771', '0775', '0813', '0842', '0845', '0995'):
            self.assertFalse(by_id[bad_id]['capability_group'].startswith('C05'), f'{bad_id} must not route to C05')
        self.assertTrue(by_id['0325']['capability_group'].startswith('C11'))
        self.assertTrue(by_id['0454']['capability_group'].startswith('C12'))
        self.assertTrue(by_id['0511']['capability_group'].startswith('C02'))

    def test_benchmark_executes_baseline_and_level2_scenarios(self):
        bench = nox_matrix.run_benchmark()
        self.assertEqual(bench['status'], 'PASS')
        l1 = bench['level1_synthetic_unit_comparison']
        self.assertGreater(l1['baseline_v1_0_3']['passed'], 0)
        self.assertGreater(l1['new_v1_2_0']['passed'], l1['baseline_v1_0_3']['passed'])
        self.assertEqual(l1['new_v1_2_0']['dev_passed'], '8/8')
        self.assertEqual(l1['new_v1_2_0']['blind_passed'], '8/8')
        self.assertEqual(bench['level2_http_functional_scenarios']['status'], 'PASS')

    def test_cli_subcommands_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            tp = Path(tmp)
            report_file = tp / 'report.json'
            report_file.write_text(json.dumps({
                'overall_status': 'PASS',
                'receipts': [{'check_id': 'c1', 'status': 'NOT_RUN', 'oracle': 'device', 'timestamp': '2026-11-21T00:00:00+00:00'}],
                'claims': [{'check_id': 'c1', 'statement': 'App works'}],
            }))
            # Unsupported claim report must exit 1
            proc_rep = subprocess.run([sys.executable, str(ROOT / 'scripts/nox.py'), 'report', str(report_file)], capture_output=True, text=True)
            self.assertEqual(proc_rep.returncode, 1)
            self.assertEqual(json.loads(proc_rep.stdout)['status'], 'FAIL')

            # matrix --id 0031 query must exit 0
            proc_mat = subprocess.run([sys.executable, str(ROOT / 'scripts/nox.py'), 'matrix', '--id', '0031'], capture_output=True, text=True)
            self.assertEqual(proc_mat.returncode, 0)
            self.assertEqual(json.loads(proc_mat.stdout)['item']['id'], '0031')

            # security-audit on repo root itself must exit 0
            proc_sec = subprocess.run([sys.executable, str(ROOT / 'scripts/nox.py'), 'security-audit', str(ROOT)], capture_output=True, text=True)
            self.assertEqual(proc_sec.returncode, 0)
            self.assertEqual(json.loads(proc_sec.stdout)['status'], 'PASS')

            # dry-run references sync must return NOT_RUN (exit 2)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(nox.main(['--dry-run', 'references', 'sync', 'keiyoushi']), 2)

    def test_verify_report_catches_missing_paths_and_accepts_valid_report(self):
        import nox_core
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'scripts').mkdir()
            (root / 'scripts/ok.py').write_text('pass\n')
            bad_rep = root / 'BAD.md'
            bad_rep.write_text('See `scripts/missing.py`.\n')
            self.assertEqual(nox_core.verify_report_claims(bad_rep, root)['status'], 'FAIL')

            good_rep = root / 'GOOD.md'
            good_rep.write_text('See `scripts/ok.py`.\n')
            self.assertEqual(nox_core.verify_report_claims(good_rep, root)['status'], 'PASS')

    def test_new_cli_commands_search_enhance_issues_deeplink_and_ui_plan(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(nox.main(['enhance', '--list']), 0)
            self.assertEqual(nox.main(['issues', 'verify-historical']), 0)
            # No device connected -> BLOCKED (exit code 2) cleanly without failing software contract
            self.assertIn(nox.main(['adb', 'ui-plan', '--package', 'app.mihon', '--source', 'Ex', '--query', 'Test']), {0, 2})

        with tempfile.TemporaryDirectory() as tmp:
            tp = Path(tmp)
            kt = tp / 'Ex.kt'
            kt.write_text('import keiyoushi.source.KeiSource\nclass Ex : KeiSource() { fun id(): Long = 1L }\n', encoding='utf-8')
            buf_diag = io.StringIO()
            with redirect_stdout(buf_diag):
                rc_diag = nox.main(['autofix-diagnose', str(tp), '--symptom', 'Google Drive 403 cover error'])
            self.assertEqual(rc_diag, 0)
            self.assertEqual(json.loads(buf_diag.getvalue())['ecosystem'], 'keiyoushi')

            buf_rc = io.StringIO()
            with redirect_stdout(buf_rc):
                rc_council = nox.main(['review-council', str(kt), '--enabled', '--ecosystem', 'keiyoushi'])
            self.assertEqual(rc_council, 0)
            self.assertEqual(json.loads(buf_rc.getvalue())['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
