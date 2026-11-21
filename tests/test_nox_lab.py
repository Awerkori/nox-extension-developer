import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import nox_lab


def _make_png(width: int, height: int) -> bytes:
    ihdr = (width).to_bytes(4, 'big') + (height).to_bytes(4, 'big') + b'\x08\x02\x00\x00\x00'
    return b'\x89PNG\r\n\x1a\n' + b'\x00\x00\x00\rIHDR' + ihdr + b'\x00\x00\x00\x00IEND\xaeB`\x82'


class LabFunctionalTests(unittest.TestCase):
    def test_site_dna_cloudflare_deceptive_200_and_selector_stability(self):
        cf = nox_lab.analyze_site_dna('<html><title>Just a moment...</title><script src="/cdn-cgi/challenge-platform/x"></script></html>', status_code=403)
        self.assertEqual(cf['status'], 'BLOCKED')
        self.assertEqual(cf['block_reason'], 'cloudflare_challenge')

        deceptive = nox_lab.analyze_site_dna('<html><body>Please sign in to continue</body></html>', status_code=200, headers={'Content-Type': 'text/html'}, expected_kind='json')
        self.assertEqual(deceptive['status'], 'BLOCKED')
        self.assertTrue(deceptive['deceptive_http_200'])

        spa = nox_lab.analyze_site_dna('<!DOCTYPE html><html><body><div id="root"></div><script src="/app.js"></script></body></html>')
        self.assertTrue(spa['requires_js'])

        fragile = nox_lab.score_selector_stability('div > div > div > ul > li:nth-child(3) > a.css-1a2b3c4d')
        stable = nox_lab.score_selector_stability('article[data-chapter-id] a[href]')
        self.assertEqual(fragile['stability'], 'FRAGILE')
        self.assertEqual(stable['stability'], 'STABLE')

    def test_image_lab_valid_vs_html_fake_truncated_lowres_and_duplicates(self):
        valid_png = _make_png(800, 1200)
        ok = nox_lab.inspect_image_payload(valid_png, content_type='image/png', url='https://cdn.ex.org/p1.png')
        self.assertEqual(ok['status'], 'PASS')
        self.assertEqual(ok['dimensions'], {'width': 800, 'height': 1200})

        fake_html = nox_lab.inspect_image_payload(b'<html><body>Hotlink denied</body></html>', content_type='image/jpeg', url='https://cdn.ex.org/p1.jpg')
        self.assertEqual(fake_html['status'], 'FAIL')
        self.assertEqual(fake_html['reason'], 'fake_200_html_or_text_payload')

        truncated = nox_lab.inspect_image_payload(valid_png[:-10], content_type='image/png')
        self.assertEqual(truncated['status'], 'FAIL')
        self.assertEqual(truncated['reason'], 'truncated_image_payload')

        tiny = nox_lab.inspect_image_payload(_make_png(10, 10), content_type='image/png')
        self.assertEqual(tiny['status'], 'FAIL')
        self.assertIn('low_resolution', tiny['reason'])

        dup_pages = nox_lab.audit_page_list([
            {'index': 0, 'page_number': 1, 'url': 'https://cdn.ex.org/1.png', 'bytes': valid_png},
            {'index': 1, 'page_number': 2, 'url': 'https://cdn.ex.org/2.png', 'bytes': valid_png},
        ])
        self.assertEqual(dup_pages['status'], 'FAIL')
        self.assertTrue(any('duplicate_page_bytes' in i for i in dup_pages['issues']))

    def test_manga_fractional_chapters_ad_links_and_empty_allowed(self):
        good = nox_lab.audit_manga_content(
            {'title': 'Obra Teste', 'url': '/manga/1'},
            [
                {'name': 'Prólogo', 'url': '/c/0', 'chapter_number': 0.0},
                {'name': 'Capítulo 59,5', 'url': '/c/59-5', 'chapter_number': 59.5},
            ],
        )
        self.assertEqual(good['status'], 'PASS')

        rounded = nox_lab.audit_manga_content(
            {'title': 'Obra Teste', 'url': '/manga/1'},
            [{'name': 'Cap. 59.5', 'url': '/c/59-5', 'chapter_number': 60}],
        )
        self.assertEqual(rounded['status'], 'FAIL')
        self.assertTrue(any('precision_loss' in i for i in rounded['issues']))

        ad_infiltrated = nox_lab.audit_manga_content(
            {'title': 'Obra Teste', 'url': '/manga/1'},
            [{'name': 'Promo', 'url': 'https://doubleclick.net/ad'}],
        )
        self.assertEqual(ad_infiltrated['status'], 'FAIL')

    def test_anime_hoster_vs_videolist_and_hls_drm(self):
        # Mandatory counterexample: hoster exists, getVideoList empty -> FAIL
        no_vid = nox_lab.audit_anime_content(
            {'title': 'Anime A', 'url': '/a/1'},
            [{'name': 'Ep 1', 'url': '/e/1'}],
            [{'name': 'Server1'}],
            [],
        )
        self.assertEqual(no_vid['status'], 'FAIL')

        hls_ok = '#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=800000\n720p/index.m3u8\n'
        ok = nox_lab.audit_anime_content(
            {'title': 'Anime A', 'url': '/a/1'},
            [{'name': 'Ep 1', 'url': '/e/1'}],
            [{'name': 'Server1'}],
            [{'videoUrl': 'https://cdn.ex/master.m3u8', 'hls_manifest': hls_ok}],
        )
        self.assertEqual(ok['status'], 'PASS')

        hls_drm = '#EXTM3U\n#EXT-X-KEY:METHOD=SAMPLE-AES,URI="https://license.ex/k"\nseg0.ts\n'
        drm = nox_lab.audit_anime_content(
            {'title': 'Anime A', 'url': '/a/1'},
            [{'name': 'Ep 1', 'url': '/e/1'}],
            [{'name': 'Server1'}],
            [{'videoUrl': 'https://cdn.ex/drm.m3u8', 'hls_manifest': hls_drm}],
        )
        self.assertEqual(drm['status'], 'BLOCKED')

    def test_novel_readability_and_lnreader_inconclusive_preservation(self):
        nav_only = nox_lab.audit_novel_content(
            {'name': 'Novel X', 'path': '/n/x'},
            [{'name': 'Ch 1', 'path': '/c/1'}],
            '<div>Prev | Next | Back to top</div>',
        )
        self.assertEqual(nav_only['status'], 'FAIL')

        good = nox_lab.audit_novel_content(
            {'name': 'Novel X', 'path': '/n/x'},
            [{'name': 'Ch 1', 'path': '/c/1'}],
            '<p>Once upon a time in a quiet village surrounded by mist, a young traveler arrived carrying an old notebook full of maps and secrets.</p>',
        )
        self.assertEqual(good['status'], 'PASS')

        inc = nox_lab.interpret_lnreader_check_plugin(0, 'Result: INCONCLUSIVE (403 from remote site)')
        self.assertEqual(inc['status'], 'INCONCLUSIVE')

    def test_search_oracle_pagination_loop_and_mutation_self_test(self):
        zero = nox_lab.audit_search_and_pagination('Solo Leveling', [])
        self.assertEqual(zero['status'], 'FAIL')

        ignored = nox_lab.audit_search_and_pagination(
            'UniqueQuery',
            [{'title': 'Popular 1', 'url': '/1'}],
            expected_title_substr='UniqueQuery',
            popular_results=[{'title': 'Popular 1', 'url': '/1'}],
        )
        self.assertEqual(ignored['status'], 'FAIL')

        loop = nox_lab.audit_search_and_pagination(
            'Manga',
            [{'title': 'Manga 1', 'url': '/1'}],
            page1_results=[{'url': '/1'}],
            page2_results=[{'url': '/1'}],
            has_next_page=True,
        )
        self.assertEqual(loop['status'], 'FAIL')

        mut_ok = nox_lab.run_mutation_self_test(lambda h: 'data-title' in h, '<div data-title="ok">', '<div class="x">')
        self.assertEqual(mut_ok['status'], 'PASS')
        mut_bad = nox_lab.run_mutation_self_test(lambda _: True, 'a', 'b')
        self.assertEqual(mut_bad['status'], 'FAIL')

    def test_scrambled_visual_diff_metadata_mapping_network_har_dates_mirrors_schema_dash(self):
        import struct
        import zlib
        def _solid_png(w: int, h: int, rgb: bytes) -> bytes:
            raw = b''.join(b'\x00' + rgb * w for _ in range(h))
            ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
            def _chunk(ct: bytes, d: bytes) -> bytes:
                return struct.pack('>I', len(d)) + ct + d + struct.pack('>I', zlib.crc32(ct + d) & 0xFFFFFFFF)
            return b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr) + _chunk(b'IDAT', zlib.compress(raw)) + _chunk(b'IEND', b'')

        # 0011 scrambled image detection
        scram = nox_lab.detect_scrambled_or_protected_image(_make_png(800, 1200), html_context='<canvas id="p"></canvas><script>ctx.drawImage(img,0,0)</script>')
        self.assertTrue(scram['scrambled_or_canvas_protected'])
        self.assertEqual(scram['status'], 'INCONCLUSIVE')

        # 0024/0055/0186/0281/0291/0655 visual diff & blank screen detection
        p_ok = _solid_png(8, 8, b'\x10\x20\x30')
        # Blank uniform white vs patterned
        p_diff = _solid_png(8, 8, b'\xfe\xfe\xfe')
        vdiff = nox_lab.compare_visual_captures(p_ok, p_diff, redact_boxes=[(0, 0, 2, 2)], expected_label='manga')
        self.assertEqual(vdiff['status'], 'FAIL')
        self.assertTrue(vdiff['blank_screen_detected'])
        self.assertEqual(vdiff['privacy_redacted_boxes'], 1)
        self.assertEqual(nox_lab.compare_visual_captures(p_ok, p_ok)['status'], 'PASS')

        # 0037/0038/0040 map image servers & routes
        sample_page = '<html><a href="/search?q=x">S</a><a href="/manga/one">M</a><img referrerpolicy="no-referrer" data-src="https://cdn2.ex.org/1.webp"/></html>'
        mapped = nox_lab.map_image_servers_and_routes(sample_page, 'https://ex.org/')
        self.assertEqual(mapped['status'], 'PASS')
        self.assertTrue(mapped['referer_policy_detected'])
        self.assertEqual(mapped['image_hosts'][0]['host'], 'cdn2.ex.org')

        # 0041 smart metadata ignoring ads
        meta_html = '<html lang="pt-BR"><body><div class="ad-banner"><h1>Buy Coins!</h1></div><h1>Real Obra</h1><div itemprop="author">A. Autor</div><a rel="tag">Action</a></body></html>'
        meta = nox_lab.extract_smart_metadata(meta_html)
        self.assertEqual(meta['title'], 'Real Obra')
        self.assertEqual(meta['author'], 'A. Autor')
        self.assertIn('Action', meta['genres'])

        # 0042/0081/0275/0276 site vs extension diff
        cmp_ok = nox_lab.compare_site_vs_extension_output({'title': 'Obra', 'chapters': [{'url': '/c/2'}, {'url': '/c/1'}]}, {'title': 'Obra', 'chapters': [{'url': '/c/2'}, {'url': '/c/1'}]})
        self.assertEqual(cmp_ok['status'], 'PASS')
        cmp_bad = nox_lab.compare_site_vs_extension_output({'title': 'Obra', 'chapters': [{'url': '/c/2'}, {'url': '/c/1'}]}, {'title': 'Obra', 'chapters': [{'url': '/c/1'}, {'url': '/c/2'}]})
        self.assertEqual(cmp_bad['status'], 'FAIL')

        # 0043/0045/0277 old vs recent & combined filters
        ep = nox_lab.audit_old_vs_recent_chapters_and_filters([{'url': 'https://old-cdn.ex/c/1', 'page_count': 12}], [{'url': 'https://new-cdn.ex/c/99', 'page_count': 18}], [{'filter_name': 'genre', 'expected_attr': 'action', 'results': [{'genre': 'action'}]}])
        self.assertEqual(ep['status'], 'PASS')
        self.assertTrue(ep['multi_epoch_hosts_detected'])

        # 0047/0048/0050 network faults, HTML drift & HAR replay
        sim = nox_lab.simulate_network_faults_and_html_drift(lambda h: 'data-id' in h, '<div class="card" data-id="1">OK</div>')
        self.assertEqual(sim['status'], 'PASS')
        har = nox_lab.replay_recorded_har_fixture({'log': {'entries': [{'request': {'method': 'GET', 'url': 'https://ex.org/?token=Bearer%20xyz'}, 'response': {'status': 200, 'headers': [{'name': 'Cache-Control', 'value': 'max-age=60'}], 'content': {'text': '<p>ok</p>'}}}]}})
        self.assertEqual(har['status'], 'PASS')

        # 0066/0067/0068/0097/0496/0497 + DASH/subtitles
        dates = nox_lab.parse_and_validate_dates(['2026-11-20', 'há 2 horas'])
        self.assertEqual(dates['status'], 'PASS')
        mirrors = nox_lab.verify_official_mirrors_and_regional_responses('https://ex.org', ['https://m1.ex.org', 'https://evil.invalid'], ['https://m1.ex.org'])
        self.assertIn('https://m1.ex.org/', mirrors['accepted_mirrors'])
        self.assertEqual(len(mirrors['rejected_mirrors']), 1)
        sch = nox_lab.detect_schema_evolution_and_canary({'items': [{'id': 1, 'title': 'a'}]}, {'items': [{'id': '1'}]}, schedule_authorized=True)
        self.assertEqual(sch['status'], 'FAIL')
        self.assertIn('items[].title', sch['removed_fields'])

        mpd = '<MPD type="static"><Period><AdaptationSet><Representation id="720p"/></AdaptationSet></Period></MPD>'
        self.assertEqual(nox_lab.inspect_dash_and_subtitles(mpd, kind='mpd')['status'], 'PASS')
        self.assertEqual(nox_lab.inspect_dash_and_subtitles('<MPD><ContentProtection/></MPD>', kind='mpd')['status'], 'BLOCKED')
        self.assertEqual(nox_lab.inspect_dash_and_subtitles('WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nHi', kind='vtt')['status'], 'PASS')

    def test_0011_unscramble_slices_and_0096_0097_persisted_canary_budget(self):
        png_bytes = b'\x89PNG\r\n\x1a\n' + b'\x00\x00\x00\rIHDR' + (100).to_bytes(4, 'big') + (200).to_bytes(4, 'big') + b'\x08\x02\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00IEND\xaeB`\x82'
        unsc = nox_lab.detect_scrambled_or_protected_image(
            png_bytes,
            html_context='<canvas id="reader"></canvas><script>ctx.drawImage(img,0,0)</script>',
            slice_permutation=[3, 1, 2, 0],
            rows=2,
            cols=2,
            tile_data=[b'T0', b'T1', b'T2', b'T3'],
        )
        self.assertEqual(unsc['status'], 'PASS')
        self.assertEqual(unsc['unscramble_plan']['reassembled_size'], 8)
        self.assertEqual(len(unsc['unscramble_plan']['tile_mappings']), 4)

        bad_perm = nox_lab.detect_scrambled_or_protected_image(png_bytes, slice_permutation=[0, 0, 1, 2], rows=2, cols=2)
        self.assertEqual(bad_perm['status'], 'FAIL')

        drm_blk = nox_lab.detect_scrambled_or_protected_image(png_bytes, html_context='<script>navigator.requestMediaKeySystemAccess("com.widevine.alpha")</script>')
        self.assertEqual(drm_blk['status'], 'BLOCKED')

        import json
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'canary.json'
            blocked = nox_lab.run_authorized_canary_monitor('example.org', {'a': 1}, {'a': 1}, state_file=state, max_requests_per_day=2, schedule_authorized=False)
            self.assertEqual(blocked['status'], 'BLOCKED')

            r1 = nox_lab.run_authorized_canary_monitor('example.org', {'a': 1}, {'a': 2}, state_file=state, max_requests_per_day=2, schedule_authorized=True)
            self.assertEqual(r1['status'], 'PASS')
            self.assertEqual(r1['requests_today'], 1)
            self.assertEqual(r1['budget_remaining'], 1)

            r2 = nox_lab.run_authorized_canary_monitor('example.org', {'items': [1]}, {'items': ['x']}, state_file=state, max_requests_per_day=2, schedule_authorized=True)
            self.assertEqual(r2['status'], 'FAIL')
            self.assertEqual(r2['budget_remaining'], 0)

            r3 = nox_lab.run_authorized_canary_monitor('example.org', {'a': 1}, {'a': 1}, state_file=state, max_requests_per_day=2, schedule_authorized=True)
            self.assertEqual(r3['status'], 'BLOCKED')
            self.assertEqual(r3['reason'], 'daily_canary_budget_exhausted')
            saved = json.loads(state.read_text(encoding='utf-8'))
            self.assertEqual(len(saved['domains']['example.org']['history']), 2)


if __name__ == '__main__':
    unittest.main()
