import datetime as dt
import hashlib
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import nox_enhancements as ne


def _png_bytes(w: int = 800, h: int = 1200, text_chunk: bytes | None = None) -> bytes:
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', 0)
    extra = chunk(b'tEXt', text_chunk) if text_chunk else b''
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + extra + chunk(b'IEND', b'')


class Enhancements1026To1150Tests(unittest.TestCase):
    def test_registry_has_125_unique_enhancements_1026_to_1150(self):
        ids = [e[0] for e in ne.ENHANCEMENTS_1026_1150]
        fns = [e[3].__name__ for e in ne.ENHANCEMENTS_1026_1150]
        titles = [e[2] for e in ne.ENHANCEMENTS_1026_1150]
        self.assertEqual(ids, [str(i) for i in range(1026, 1151)])
        self.assertEqual(len(set(fns)), 125)
        self.assertEqual(len(set(titles)), 125)

    def test_family1_1026_to_1040_url_and_http_guards(self):
        # 1026..1030
        self.assertEqual(ne.detect_idn_homograph('https://pаypal.com')['status'], 'FAIL')  # cyrillic a
        self.assertEqual(ne.detect_idn_homograph('https://example.org')['status'], 'PASS')
        self.assertTrue(ne.check_ipv4_mapped_ipv6_ssrf('http://[::ffff:127.0.0.1]/')['blocked'])
        self.assertFalse(ne.check_ipv4_mapped_ipv6_ssrf('https://8.8.8.8/')['blocked'])
        self.assertTrue(ne.check_numeric_ip_ssrf('http://0x7f000001/')['blocked'])
        self.assertTrue(ne.check_numeric_ip_ssrf('http://2130706433/')['blocked'])
        self.assertTrue(ne.check_numeric_ip_ssrf('http://0177.0.0.1/')['blocked'])
        self.assertFalse(ne.check_numeric_ip_ssrf('https://example.org/')['blocked'])
        self.assertEqual(ne.extract_http_refresh_redirect('0; url=/v2/home', 'https://ex.org')['target_url'], 'https://ex.org/v2/home')
        self.assertEqual(ne.extract_http_refresh_redirect('invalid', 'https://ex.org')['status'], 'FAIL')
        self.assertTrue(ne.extract_meta_refresh_redirect('<meta http-equiv="refresh" content="0;url=https://ex.org/ok">', 'https://ex.org')['found'])
        self.assertFalse(ne.extract_meta_refresh_redirect('<html></html>', 'https://ex.org')['found'])

        # 1031..1035
        self.assertEqual(ne.normalize_protocol_relative_url('//cdn.ex.org/a.png')['normalized'], 'https://cdn.ex.org/a.png')
        self.assertTrue(ne.fix_double_percent_encoding('https://ex.org/a%2520b')['had_double_encoding'])
        self.assertEqual(ne.fix_double_percent_encoding('https://ex.org/a%20b')['fixed_url'], 'https://ex.org/a%20b')
        self.assertEqual(ne.normalize_url_preserving_spa_hash('https://ex.org/#/manga/1')['normalized'], 'https://ex.org/#/manga/1')
        self.assertNotIn('#top', ne.normalize_url_preserving_spa_hash('https://ex.org/manga/1#top')['normalized'])
        self.assertTrue(ne.canonicalize_signed_query_params('https://cdn.ex/p.png?b=1&a=2&sig=xyz')['signed_query_preserved'])
        self.assertEqual(ne.canonicalize_signed_query_params('https://ex.org/?b=1&a=2')['url'], 'https://ex.org/?a=2&b=1')
        now = dt.datetime(2026, 11, 21, tzinfo=dt.timezone.utc)
        self.assertEqual(ne.check_signed_url_expiration('https://cdn.ex/p.png?expires=1000', now=now)['status'], 'FAIL')
        self.assertEqual(ne.check_signed_url_expiration(f'https://cdn.ex/p.png?expires={int(now.timestamp()) + 3600}', now=now)['status'], 'PASS')

        # 1036..1040
        self.assertEqual(ne.parse_retry_after_header('120', max_wait_s=60)['capped_wait_seconds'], 60.0)
        self.assertEqual(ne.parse_retry_after_header('abc')['status'], 'FAIL')
        self.assertEqual(ne.sanitize_content_disposition_filename('attachment; filename="../../etc/passwd"')['status'], 'FAIL')
        self.assertEqual(ne.sanitize_content_disposition_filename('attachment; filename="page1.png"')['safe_filename'], 'page1.png')
        import base64
        b64_png = base64.b64encode(_png_bytes(10, 10)).decode()
        self.assertEqual(ne.validate_inline_data_uri_image(f'data:image/png;base64,{b64_png}')['status'], 'PASS')
        self.assertEqual(ne.validate_inline_data_uri_image('data:text/html;base64,PGI+')['status'], 'FAIL')
        self.assertEqual(ne.detect_vary_user_agent_divergence({'Vary': 'User-Agent'}, '<a>d</a>', '<b>m</b>')['status'], 'INCONCLUSIVE')
        self.assertEqual(ne.audit_cookie_attributes(['cf=1; SameSite=None'])['status'], 'FAIL')
        self.assertEqual(ne.audit_cookie_attributes(['cf=1; SameSite=Lax; Secure'])['status'], 'PASS')

    def test_family2_1041_to_1055_dom_and_hydration(self):
        self.assertEqual(ne.extract_nextjs_rsc_payload('<script>self.__next_f.push([1,"chapter_list"])</script>')['chunks_count'], 1)
        self.assertEqual(ne.resolve_nuxt_flat_data('[{"title":1},"Obra"]')['status'], 'PASS')
        self.assertEqual(ne.resolve_nuxt_flat_data('{bad')['status'], 'FAIL')
        self.assertEqual(len(ne.extract_json_ld_metadata('<script type="application/ld+json">{"@type":"Book","name":"X"}</script>')['items']), 1)
        self.assertEqual(ne.extract_opengraph_fallback('<meta property="og:title" content="Manga X">')['opengraph']['og:title'], 'Manga X')
        self.assertEqual(ne.decode_cf_email('1a7b791a7f62')['status'], 'PASS')
        self.assertEqual(ne.decode_cf_email('bad')['status'], 'FAIL')
        self.assertEqual(ne.unescape_double_html_entities('Obra &amp;quot;1&amp;quot;')['text'], 'Obra "1"')
        self.assertEqual(ne.strip_zero_width_chars('Cap\u200b 1\ufeff')['text'], 'Cap 1')
        self.assertEqual(ne.detect_utf8_latin1_mojibake('CapÃ­tulo 1')['mojibake_detected'], True)
        self.assertEqual(ne.extract_noscript_images('<noscript><img src="https://cdn.ex/1.jpg"/></noscript>')['urls'], ['https://cdn.ex/1.jpg'])
        self.assertEqual(ne.extract_css_background_image_urls('style="background-image: url(https://ex/c.jpg)"')['urls'], ['https://ex/c.jpg'])
        self.assertEqual(ne.detect_inline_svg_placeholder('data:image/svg+xml;base64,PHN2Zz4=')['status'], 'FAIL')
        self.assertEqual(ne.inspect_graphql_partial_error({'data': None, 'errors': [{'message': 'Denied'}]})['status'], 'FAIL')
        self.assertEqual(ne.detect_graphql_persisted_query_failure({'errors': [{'message': 'PERSISTED_QUERY_NOT_FOUND'}]})['status'], 'FAIL')
        self.assertTrue(ne.detect_disabled_next_page_control('<button class="next" disabled>Next</button>')['disabled'])
        self.assertEqual(ne.extract_js_hidden_chapter_links('<div data-href="/ch/9" onclick="location.href=\'/ch/10\'"></div>')['urls'], ['/ch/9', '/ch/10'])

    def test_family3_1056_to_1070_manga_and_images(self):
        self.assertEqual(ne.parse_roman_numeral_chapter('Chapter XIV')['chapter_number'], 14.0)
        self.assertEqual(ne.parse_cjk_fullwidth_chapter('第１２.５話')['chapter_number'], 12.5)
        sv = ne.parse_season_volume_prefixed_chapter('Vol. 3 Ch. 24.5')
        self.assertEqual((sv['volume_or_season'], sv['chapter_number']), (3, 24.5))
        self.assertTrue(ne.detect_ranged_chapter_bundle('Capítulos 10 ao 12')['is_range'])
        self.assertEqual(ne.classify_special_extra_chapter('Omake Special')['kind'], 'extra')
        self.assertEqual(ne.extract_scanlator_group('[NoxScans] Cap. 1')['scanlator'], 'NoxScans')
        anim_webp = b'RIFF\x20\x00\x00\x00WEBPVP8X\x0a\x00\x00\x00ANIM\x00\x00'
        self.assertTrue(ne.detect_animated_webp(anim_webp)['is_animated'])
        self.assertEqual(ne.inspect_jpeg_exif_orientation(b'\xff\xd8\xff\xe1\x00\x10Exif\x00\x00')['status'], 'PASS')
        self.assertEqual(ne.inspect_png_text_warnings(_png_bytes(800, 1200, b'Comment\x00Hotlink error'))['status'], 'FAIL')
        self.assertEqual(ne.inspect_png_text_warnings(_png_bytes(800, 1200))['status'], 'PASS')
        avif_box = b'\x00\x00\x00\x1cftypavif\x00\x00\x00\x00avif\x00\x00\x00\x14ispe\x00\x00\x00\x00' + struct.pack('>II', 720, 1280)
        av = ne.parse_avif_ispe_dimensions(avif_box)
        self.assertEqual((av['width'], av['height']), (720, 1280))
        self.assertEqual(ne.detect_legacy_incompatible_image_format(b'BM\x00\x00')['status'], 'FAIL')
        self.assertEqual(ne.validate_partial_content_range(206, 'bytes 0-99/500', 100)['status'], 'PASS')
        self.assertEqual(ne.validate_partial_content_range(206, 'bytes 0-99/500', 50)['status'], 'FAIL')
        self.assertIn('image/webp', ne.build_image_accept_header()['Accept'])
        self.assertEqual(ne.detect_cover_infiltrated_as_page0(b'cover', [b'cover', b'p1'])['status'], 'FAIL')
        self.assertEqual(ne.classify_webtoon_aspect_ratio(720, 4000)['format_class'], 'webtoon_strip')

    def test_family4_1071_to_1085_anime_and_media(self):
        self.assertEqual(ne.validate_hls_byterange('#EXT-X-BYTERANGE:1024@0\nseg.ts')['byterange_segments'], 1)
        self.assertEqual(ne.resolve_hls_init_map('#EXT-X-MAP:URI="init.mp4"', 'https://cdn.ex/v/pl.m3u8')['init_segments'], ['https://cdn.ex/v/init.mp4'])
        self.assertTrue(ne.detect_hls_ad_discontinuity('#EXTM3U\n#EXT-X-DISCONTINUITY\nad.ts')['possible_ad_stitching'])
        self.assertEqual(ne.classify_hls_vod_vs_live('#EXTM3U\n#EXT-X-ENDLIST')['stream_mode'], 'VOD')
        self.assertEqual(ne.detect_dash_drm_content_protection('<MPD><ContentProtection/></MPD>')['status'], 'BLOCKED')
        self.assertEqual(ne.expand_dash_segment_template('seg-$RepresentationID$-$Number$.m4s', rep_id='720p', number=4)['url'], 'seg-720p-4.m4s')
        self.assertEqual(ne.validate_webvtt_subtitles('WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nOk')['status'], 'PASS')
        self.assertEqual(ne.validate_srt_subtitles('1\n00:00:01,000 --> 00:00:02,000\nHi\n')['status'], 'PASS')
        self.assertEqual(ne.validate_ass_subtitles('[Script Info]\n[Events]\nDialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,Hi')['status'], 'PASS')
        self.assertEqual(ne.parse_hls_alternative_audio('#EXT-X-MEDIA:TYPE=AUDIO,LANGUAGE="pt-BR"')['audio_languages'], ['pt-BR'])
        self.assertEqual(ne.sort_video_qualities([{'quality': '480p'}, {'quality': '1080p'}])['ordered_qualities'], ['1080p', '480p'])
        self.assertEqual(ne.detect_hoster_dmca_or_deleted('<div>File was deleted due to DMCA</div>')['status'], 'FAIL')
        packed = "}('0 1=\"2://3/4.5\"',6,6,'var|url|https|cdn|v|mp4'.split('|'),0,{})"
        self.assertIn('https://cdn/v.mp4', ne.unpack_dean_edwards_packer(packed)['unpacked'])
        self.assertTrue(ne.normalize_hoster_embed_url('https://h.ex/e/abc123?utm_source=x')['is_embed'])
        self.assertEqual(ne.detect_audio_only_hls_variant('BANDWIDTH=128000,CODECS="mp4a.40.2"')['status'], 'FAIL')

    def test_family5_1086_to_1100_lnreader(self):
        self.assertEqual(ne.verify_novel_unicode_preservation('Capítulo 1 — 魔法')['status'], 'PASS')
        self.assertEqual(ne.verify_novel_unicode_preservation('bad \ufffd')['status'], 'FAIL')
        self.assertEqual(ne.deduplicate_leading_chapter_title('Chapter 5', ['Chapter 5', 'Real text'])['paragraphs'], ['Real text'])
        self.assertEqual(ne.classify_translator_author_notes('<div class="tl-note">Note</div>')['notes_count'], 1)
        self.assertEqual(ne.strip_invisible_anti_scrape_watermarks('<p>Hi<span style="display:none">junk</span></p>')['cleaned_html'], '<p>Hi</p>')
        self.assertTrue(ne.detect_multipage_novel_chapter('<a href="/ch/1?page=2">Next</a>')['is_multipage'])
        self.assertEqual(ne.verify_litrpg_tables_preserved('<table><tr><td>HP</td></tr></table>', '<p>HP</p>')['status'], 'FAIL')
        self.assertEqual(ne.classify_novel_site_platform('<div class="fictioneer-chapter"></div>')['platform'], 'fictioneer')
        self.assertEqual(ne.check_lnreader_plugin_contract_fields("id='x';name='X';site='https://x';version='1.0.0';icon='src/i.png'")['status'], 'PASS')
        self.assertEqual(ne.check_lnreader_plugin_contract_fields("id='x'")['status'], 'FAIL')
        self.assertEqual(ne.check_lnreader_semver_bump('1.0.0', '1.0.1')['status'], 'PASS')
        self.assertEqual(ne.validate_lnreader_icon_spec('src/en/x/icon.png', _png_bytes(128, 128))['status'], 'PASS')
        self.assertEqual(ne.detect_forbidden_lnreader_http_clients("import axios from 'axios';")['status'], 'FAIL')
        self.assertEqual(ne.detect_lnreader_paragraph_loss("parseChapter() { return $('div').text(); }")['status'], 'FAIL')
        self.assertEqual(ne.check_unbalanced_chapter_html('<p>Open only')['status'], 'FAIL')
        self.assertEqual(ne.check_lnreader_filter_wiring("filters = { sort: {} }; popularNovels(pageNo, { filters }) { return []; }")['status'], 'PASS')
        self.assertEqual(ne.normalize_novel_status('Em Andamento')['normalized_status'], 'Ongoing')

    def test_family6_1101_to_1115_kotlin_and_ksp(self):
        self.assertEqual(ne.detect_unclosed_okhttp_response('val x = resp.body.string()')['status'], 'FAIL')
        self.assertEqual(ne.detect_headers_builder_overwrite('val h = Headers.Builder().build()')['status'], 'FAIL')
        self.assertEqual(ne.detect_simpledateformat_without_locale('SimpleDateFormat("yyyy-MM-dd")')['status'], 'FAIL')
        self.assertEqual(ne.detect_runblocking_in_suspend('suspend fun get() { runBlocking { } }')['status'], 'FAIL')
        self.assertEqual(ne.detect_sync_execute_in_suspend('suspend fun get() { client.newCall(req).execute() }')['status'], 'FAIL')
        self.assertEqual(ne.detect_date_upload_seconds_bug(1700000000)['status'], 'FAIL')
        self.assertEqual(ne.detect_baseurl_concat_without_slash('val u = "$baseUrl${manga.url}"')['status'], 'INCONCLUSIVE')
        self.assertEqual(ne.detect_duplicate_source_annotations('@Source\nclass A\n@Source\nclass B')['status'], 'FAIL')
        self.assertEqual(ne.verify_version_code_bumped('versionCode = 1', 'versionCode = 2')['status'], 'PASS')
        self.assertEqual(ne.check_content_warning_migration('isNsfw = true')['status'], 'INCONCLUSIVE')
        self.assertEqual(ne.detect_cross_ecosystem_or_wildcard_imports('import eu.kanade.tachiyomi.animesource.S', 'keiyoushi')['status'], 'FAIL')
        self.assertEqual(ne.detect_fragile_filter_index_cast('val g = filters[0] as Genre')['status'], 'FAIL')
        self.assertEqual(ne.verify_episode_and_page_indexing([{'index': 0}, {'index': 2}], kind='page')['status'], 'FAIL')
        self.assertEqual(ne.detect_blocking_thread_sleep('Thread.sleep(500)')['status'], 'FAIL')
        self.assertEqual(ne.detect_debug_print_statements('println("debug")')['status'], 'INCONCLUSIVE')

    def test_family7_1116_to_1130_android_gradle_and_logcat(self):
        rules = ne.parse_deeplink_tuples('deeplink { scheme = "https"\n host = "ex.org"\n pathPattern = "/manga/.*" }')['tuples']
        self.assertEqual(ne.match_url_against_deeplink_tuple('https://ex.org/manga/1', rules[0])['status'], 'PASS')
        self.assertEqual(ne.build_safe_adb_am_start_command('https://ex.org/manga/1', 'eu.x')['status'], 'PASS')
        dex_hdr = b'dex\n035\x00' + b'\x00' * 24 + struct.pack('<I', 112) + b'\x00' * 4 + struct.pack('<I', 0x12345678) + b'\x00' * 12 + struct.pack('<I', 10) + b'\x00' * 52
        self.assertEqual(ne.inspect_dex_binary_header(dex_hdr)['status'], 'PASS')
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / 'a.apk'
            with zipfile.ZipFile(apk, 'w') as zf:
                zf.writestr('AndroidManifest.xml', b'm')
                zf.writestr('resources.arsc', b'r')
            self.assertEqual(ne.verify_apk_resources_and_icons(apk)['status'], 'PASS')
        self.assertEqual(ne.check_gradle_legacy_vs_modern_version_drift('extVersionCode = 1\nversionCode = 2')['status'], 'FAIL')
        self.assertEqual(ne.diagnose_gradle_oom_error('java.lang.OutOfMemoryError: Java heap space')['kind'], 'heap_space')
        self.assertEqual(ne.parse_kotlin_compiler_errors('e: file:///src/A.kt:12:5 Unresolved reference: x')['errors_count'], 1)
        self.assertTrue(ne.validate_local_properties_sdk_dir('sdk.dir=/mnt/c/Android/Sdk')['is_wsl_mnt'])
        self.assertEqual(ne.validate_adb_wireless_endpoint('192.168.1.5:5555')['status'], 'PASS')
        self.assertEqual(ne.validate_adb_wireless_endpoint('8.8.8.8:5555')['status'], 'FAIL')
        self.assertEqual(ne.detect_logcat_anr('ANR in app.mihon', target_package='app.mihon')['status'], 'FAIL')
        self.assertEqual(ne.classify_logcat_tls_failure('javax.net.ssl.SSLHandshakeException')['status'], 'FAIL')
        self.assertEqual(ne.extract_kotlinx_missing_field_error("Field 'pages' is required for type")['missing_dto_fields'], ['pages'])
        self.assertEqual(len(ne.extract_extension_stack_frame('at eu.kanade.tachiyomi.extension.pt.x.X.parse(X.kt:42)')['extension_frames']), 1)
        self.assertEqual(ne.check_apk_abi_coverage(['lib/armeabi-v7a/libx.so'])['status'], 'FAIL')

    def test_family8_1131_to_1140_security_hardening(self):
        with tempfile.TemporaryDirectory() as tmp:
            zb = Path(tmp) / 'bomb.zip'
            with zipfile.ZipFile(zb, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('big.txt', b'A' * 500_000)
            self.assertEqual(ne.detect_zip_bomb(zb, max_ratio=10.0)['status'], 'FAIL')
        self.assertEqual(ne.audit_gitmodules_safety('[submodule "x"]\n url = ssh://evil.invalid/x')['status'], 'FAIL')
        self.assertEqual(ne.audit_gradle_properties_rce('org.gradle.jvmargs=-javaagent:/tmp/pwn.jar')['status'], 'FAIL')
        self.assertEqual(ne.audit_github_workflow_script_injection('on: workflow_run:\nrun: echo ${{ github.event.issue.title }}')['status'], 'FAIL')
        self.assertEqual(ne.detect_kotlin_reflection_obfuscation('Class.forName("java.lang.Runtime")')['status'], 'FAIL')
        self.assertEqual(ne.detect_js_dynamic_code_execution('const fn = new Function("return 1")')['status'], 'FAIL')
        self.assertEqual(ne.audit_npmrc_safety('registry=https://evil-npm.invalid/')['status'], 'FAIL')
        self.assertEqual(ne.check_cross_platform_path_safety('C:\\dir\\CON.kt')['status'], 'FAIL')
        sarif = ne.export_security_findings_sarif([{'kind': 'gradle_rce', 'severity': 'FAIL', 'file': 'build.gradle.kts'}])
        self.assertEqual(sarif['version'], '2.1.0')
        bw = ne.build_bwrap_sandbox_command(Path('.'), ['echo', 'hi'])
        self.assertIn('--unshare-net', bw['sandbox_command'])

    def test_family9_1141_to_1150_issue_diff_ux_and_audit(self):
        diff = '- document.select("div.old")\n+ document.select("div.new") // https://cdn.ex/api'
        ex = ne.extract_selectors_and_endpoints_from_diff(diff)
        self.assertEqual(ex['added_selectors'], ['div.new'])
        self.assertEqual(ex['removed_selectors'], ['div.old'])
        self.assertEqual(ne.detect_transitive_revert_chain([{'title': 'Revert "Fix" (#55)', 'merged_at': '2026-11-01'}])['reverted_pr_numbers'], [55])
        self.assertEqual(ne.cluster_duplicate_issues([{'id': 1, 'extension': 'Komiwa', 'symptom': 'ad'}, {'id': 2, 'extension': 'Komiwa', 'symptom': 'ad'}])['clusters_count'], 1)
        self.assertEqual(ne.check_patch_memory_staleness('2020-01-01T00:00:00+00:00', lib_old='1.4', lib_new='1.6')['status'], 'FAIL')
        sh = ne.shrink_failing_html_fixture(['<div>header</div>', '<div class="broken">', '<div>footer</div>'], lambda h: 'broken' in h)
        self.assertEqual(sh['minimized_lines'], 1)
        self.assertEqual(ne.check_search_metamorphic_consistency(['Manga A'], ['Manga A'])['status'], 'PASS')
        self.assertEqual(ne.compute_first_pass_readiness({'G0': 'PASS', 'G8': 'BLOCKED'})['blockers'], ['G8'])
        self.assertIn('Cloudflare', ne.explain_diagnostic_code('NOX-ERR-001', lang='pt-BR')['message'])
        cp = ne.build_continuation_summary_payload(1000, 150, {'G0': 'PASS'})
        self.assertEqual(cp['remaining_new_to_2000'], 850)
        self.assertFalse(ne.validate_three_counters(1000, 150, 1150)['target_2000_reached'])


class Enhancements1151To1200Tests(unittest.TestCase):
    def test_registry_count_175_and_distinctness(self):
        self.assertEqual(len(ne.ENHANCEMENT_REGISTRY), 175)
        self.assertEqual(ne.measure_enhancement_signal_to_noise_ratio(ne.ENHANCEMENT_REGISTRY)['status'], 'PASS')

    def test_family10_1151_to_1165_upstream_patterns(self):
        self.assertEqual(ne.check_lnreader_deprecated_default_cover('import { defaultCover } from "@libs/defaultCover"')['status'], 'FAIL')
        self.assertEqual(ne.check_lnreader_deprecated_default_cover('export default new NovelPlugin()')['status'], 'PASS')
        self.assertEqual(ne.check_lnreader_rate_limit_classification([200, 429])['status'], 'INCONCLUSIVE')
        self.assertEqual(ne.check_lnreader_rate_limit_classification([200])['status'], 'PASS')
        self.assertEqual(ne.check_lnreader_plugin_error_usage('throw new Error("boom")')['status'], 'FAIL')
        self.assertEqual(ne.check_lnreader_plugin_error_usage('import { PluginError } from "@libs/pluginError"; throw new PluginError("ok")')['status'], 'PASS')
        self.assertEqual(ne.check_lnreader_ts_typecheck_compliance('const x: any = 1')['status'], 'FAIL')
        self.assertEqual(ne.check_lnreader_ts_typecheck_compliance('const x: string = "ok"')['status'], 'PASS')
        self.assertEqual(ne.check_yuzono_premium_or_capacity_limit('Video available for premium-only members')['status'], 'BLOCKED')
        self.assertEqual(ne.check_yuzono_premium_or_capacity_limit('<video src="ok.mp4"/>')['status'], 'PASS')
        self.assertEqual(ne.verify_yuzono_download_vs_seek_tracks([{'quality': 'seek-preview', 'url': 'thumb.vtt'}])['status'], 'FAIL')
        self.assertEqual(ne.verify_yuzono_download_vs_seek_tracks([{'quality': '1080p', 'url': 'ep.mp4'}])['status'], 'PASS')
        self.assertEqual(ne.check_yuzono_theme_to_source_migration('class OldTheme {}')['status'], 'FAIL')
        self.assertEqual(ne.check_yuzono_theme_to_source_migration('class Good : AniSource() { override val name = "X" }')['status'], 'PASS')
        self.assertEqual(ne.validate_yuzono_video_headers_preservation([{'url': 'https://cdn.ex/v.m3u8', 'headers': {}}])['status'], 'FAIL')
        self.assertEqual(ne.validate_yuzono_video_headers_preservation([{'url': 'https://cdn.ex/v.m3u8', 'headers': {'Referer': 'https://ex.org/'}}])['status'], 'PASS')
        self.assertEqual(ne.check_keiyoushi_mirror_retry_coverage('val u = "https://rus.com-x.life/a.jpg"')['status'], 'FAIL')
        self.assertEqual(ne.check_keiyoushi_mirror_retry_coverage('val u = "https://rus.com-x.life/a.jpg"; fun mirrorRetry() {}')['status'], 'PASS')
        self.assertEqual(ne.audit_keiyoushi_solomanga_multisrc_adoption('class X : SoloManga() { override val client: OkHttpClient = OkHttpClient() }')['status'], 'FAIL')
        self.assertEqual(ne.audit_keiyoushi_solomanga_multisrc_adoption('class X : SoloManga()')['status'], 'PASS')
        self.assertEqual(ne.verify_keiyoushi_reader_encrypted_dto_handling('val x = dto.encryptedPages!!.length')['status'], 'FAIL')
        self.assertEqual(ne.verify_keiyoushi_reader_encrypted_dto_handling('val x = dto.__r?.let { decode(it) }')['status'], 'PASS')
        self.assertEqual(ne.audit_google_drive_sec_fetch_rewrite('https://drive.google.com/uc?id=12345')['canonical_url'], 'https://lh3.googleusercontent.com/d/12345')
        self.assertEqual(ne.audit_google_drive_sec_fetch_rewrite('https://cdn.ex/1.jpg')['status'], 'PASS')
        self.assertEqual(ne.check_kotlin_override_super_call_leak('override fun fetchPageList() { TODO() }')['status'], 'FAIL')
        self.assertEqual(ne.check_kotlin_override_super_call_leak('override fun fetchPageList() { return listOf() }')['status'], 'PASS')
        self.assertEqual(ne.detect_hardcoded_cookie_or_session_token('val h = "cf_clearance=secret123"')['status'], 'FAIL')
        self.assertEqual(ne.detect_hardcoded_cookie_or_session_token('val h = "Accept: application/json"')['status'], 'PASS')
        self.assertEqual(ne.verify_lnreader_chapter_path_relativity([{'path': 'https://old.com/ch1'}])['status'], 'FAIL')
        self.assertEqual(ne.verify_lnreader_chapter_path_relativity([{'path': 'ch1'}])['status'], 'PASS')

    def test_family11_1166_to_1185_deepening_and_security(self):
        self.assertEqual(ne.validate_slice_permutation_bijection([2, 0, 3, 1], 2, 2)['status'], 'PASS')
        self.assertEqual(ne.validate_slice_permutation_bijection([0, 0, 1, 2], 2, 2)['status'], 'FAIL')
        self.assertEqual(ne.compute_tile_unscramble_map(100, 200, [1, 0], 1, 2)['status'], 'PASS')
        self.assertEqual(ne.compute_tile_unscramble_map(10, 10, [0], 2, 2)['status'], 'FAIL')
        self.assertEqual(ne.detect_canvas_drm_boundary('<script>requestMediaKeySystemAccess()</script>')['status'], 'BLOCKED')
        self.assertEqual(ne.detect_canvas_drm_boundary('<canvas/>')['status'], 'PASS')
        ok_xml = '<hierarchy><node text="Search" clickable="true" bounds="[0,0][100,100]"/></hierarchy>'
        bad_xml = '<hierarchy><node text="HTTP error 403" bounds="[0,0][100,100]"/></hierarchy>'
        self.assertEqual(ne.parse_uiautomator_bounds_coordinates(ok_xml)['status'], 'PASS')
        self.assertEqual(ne.parse_uiautomator_bounds_coordinates('<bad')['status'], 'FAIL')
        self.assertEqual(ne.detect_uiautomator_error_banners(bad_xml)['status'], 'FAIL')
        self.assertEqual(ne.detect_uiautomator_error_banners(ok_xml)['status'], 'PASS')
        self.assertEqual(ne.build_uiautomator_navigation_commands(ok_xml, ('search',))['status'], 'PASS')
        self.assertEqual(ne.build_uiautomator_navigation_commands(ok_xml, ('nonexistent',))['status'], 'FAIL')
        with tempfile.TemporaryDirectory() as tmp:
            sf = Path(tmp) / 'c.json'
            self.assertEqual(ne.enforce_canary_daily_request_budget(sf, 'ex.org', 1, False)['status'], 'BLOCKED')
            self.assertEqual(ne.enforce_canary_daily_request_budget(sf, 'ex.org', 1, True)['status'], 'PASS')
            self.assertEqual(ne.enforce_canary_daily_request_budget(sf, 'ex.org', 1, True)['status'], 'BLOCKED')
        fp = ne.compute_dom_structural_fingerprint('<div id="main"><ul id="chapters"><li>1</li></ul></div>')
        self.assertEqual(fp['status'], 'PASS')
        self.assertEqual(ne.compute_dom_structural_fingerprint('plain text')['status'], 'FAIL')
        self.assertEqual(ne.diff_dom_structural_fingerprints('<div id="a"><p>1</p></div>', '<span id="z"><b>2</b></span>')['status'], 'FAIL')
        self.assertEqual(ne.diff_dom_structural_fingerprints('<div id="a"><p>1</p></div>', '<div id="a"><p>2</p></div>')['status'], 'PASS')
        self.assertEqual(ne.detect_cloudflare_turnstile_or_captcha('<div class="cf-turnstile"></div>')['status'], 'BLOCKED')
        self.assertEqual(ne.detect_cloudflare_turnstile_or_captcha('<div class="manga"></div>')['status'], 'PASS')
        self.assertEqual(ne.validate_mp4_moov_and_ftyp_header(b'\x00\x00\x00\x18ftypisom\x00\x00moov')['status'], 'PASS')
        self.assertEqual(ne.validate_mp4_moov_and_ftyp_header(b'<html>not mp4</html>')['status'], 'FAIL')
        self.assertEqual(ne.detect_http_meta_refresh_loop('<meta http-equiv="refresh" content="0;url=http://127.0.0.1/">')['status'], 'FAIL')
        self.assertEqual(ne.detect_http_meta_refresh_loop('<title>ok</title>')['status'], 'PASS')
        self.assertEqual(ne.detect_zip_slip_path_traversal(['../../etc/passwd'])['status'], 'FAIL')
        self.assertEqual(ne.detect_zip_slip_path_traversal(['classes.dex'])['status'], 'PASS')
        self.assertEqual(ne.detect_gradlew_tampering_or_non_official_url('distributionUrl=https\\://evil.com/g.zip')['status'], 'FAIL')
        self.assertEqual(ne.detect_gradlew_tampering_or_non_official_url('distributionUrl=https\\://services.gradle.org/distributions/gradle-8.5-bin.zip\ndistributionSha256Sum=' + 'a' * 64)['status'], 'PASS')
        self.assertEqual(ne.detect_unsafe_webview_bridge_exposure('webView.addJavascriptInterface(x, "n")')['status'], 'FAIL')
        self.assertEqual(ne.detect_unsafe_webview_bridge_exposure('webView.settings.javaScriptEnabled = true')['status'], 'PASS')
        self.assertEqual(ne.check_kotlinx_serialization_json_config('val j = Json { isLenient = true }')['status'], 'FAIL')
        self.assertEqual(ne.check_kotlinx_serialization_json_config('val j = Json { ignoreUnknownKeys = true }')['status'], 'PASS')
        self.assertEqual(ne.detect_infinite_pagination_loop_risk('return MangasPage(list, true)')['status'], 'FAIL')
        self.assertEqual(ne.detect_infinite_pagination_loop_risk('return MangasPage(list, doc.selectFirst(nextSelector) != null)')['status'], 'PASS')
        self.assertEqual(ne.verify_cover_url_fallback_and_non_placeholder(['https://ex.org/no-cover.png'])['status'], 'FAIL')
        self.assertEqual(ne.verify_cover_url_fallback_and_non_placeholder(['https://cdn.ex/cover123.jpg'])['status'], 'PASS')
        self.assertEqual(ne.check_android_manifest_cleartext_traffic('<application android:usesCleartextTraffic="true"/>')['status'], 'FAIL')
        self.assertEqual(ne.check_android_manifest_cleartext_traffic('<application android:usesCleartextTraffic="false"/>')['status'], 'PASS')
        red = ne.redact_headers_and_tokens_in_evidence('Authorization: Bearer secret123\nCookie: sid=abc')
        self.assertTrue(red['redacted_secrets'])
        self.assertNotIn('secret123', red['sanitized_text'])

    def test_family12_1186_to_1200_issue_consolidation_and_saturation(self):
        self.assertEqual(ne.distinguish_closed_unmerged_pr({'id': 2918, 'is_pr': True, 'state': 'closed', 'merged_at': None})['classification'], 'CLOSED_UNMERGED')
        self.assertEqual(ne.cross_check_issue_pr_closure_links({'number': 10}, {'id': 20, 'is_pr': True, 'state': 'closed', 'merged': True, 'merged_at': '2026-11-20T00:00:00Z', 'merge_commit_sha': 'a'*40, 'post_merge_verified': True, 'body': 'Closes #10'})['status'], 'PASS')
        self.assertEqual(ne.cross_check_issue_pr_closure_links({'number': 10}, {'id': 21, 'is_pr': True, 'state': 'open', 'body': 'Closes #10'})['status'], 'FAIL')
        ranked = ne.rank_historical_fixes_by_symptom_similarity('google drive 403', [
            {'pr_number': 21153, 'ecosystem': 'keiyoushi', 'classification': 'VERIFIED_FIX', 'title': 'Google Drive 403'},
            {'pr_number': 2918, 'ecosystem': 'lnreader', 'classification': 'CLOSED_UNMERGED', 'title': '429'},
        ])
        self.assertEqual(ranked['ranked'][0]['pr_number'], 21153)
        self.assertEqual(ranked['excluded_unmerged_count'], 1)
        self.assertEqual(ne.verify_multi_ecosystem_issue_coverage({'ecosystems_verified': ['keiyoushi', 'yuzono', 'lnreader']})['status'], 'PASS')
        self.assertEqual(ne.verify_multi_ecosystem_issue_coverage({'ecosystems_verified': ['keiyoushi']})['status'], 'FAIL')
        self.assertEqual(ne.audit_review_council_real_execution({'substantive_checks_executed': True, 'reviews': [1, 2, 3, 4]})['status'], 'PASS')
        self.assertEqual(ne.audit_review_council_real_execution({'reviews': []})['status'], 'FAIL')
        self.assertEqual(ne.verify_pr_state_consistency_across_reports({'records': [{'pr_number': 21282, 'upstream_merged_at': '2026-11-21'}]}, ['PRs abertos #21282'])['status'], 'FAIL')
        self.assertEqual(ne.verify_pr_state_consistency_across_reports({'records': [{'pr_number': 21282, 'upstream_merged_at': '2026-11-21'}]}, ['#21282 merged em 2026-11-21'])['status'], 'PASS')
        self.assertEqual(ne.verify_no_false_c05_image_routing([{'id': '0775', 'title': 'Captura indiscriminada de exceções', 'capability_group': 'C05: Img'}])['status'], 'FAIL')
        self.assertEqual(ne.verify_no_false_c05_image_routing([{'id': '0024', 'title': 'Comparação visual de screenshots', 'capability_group': 'C05: Img'}])['status'], 'PASS')
        self.assertEqual(ne.verify_no_section_level_routing_mismatch([{'id': '0325', 'capability_group': 'C02: Env'}])['status'], 'FAIL')
        self.assertEqual(ne.verify_no_section_level_routing_mismatch([{'id': '0325', 'capability_group': 'C11: Sec'}])['status'], 'PASS')
        self.assertEqual(ne.check_catalog_item_binding_coherence({'id': '0001', 'capability_group': 'C01', 'functions': 'f', 'trigger_point': 't', 'acceptance_criteria': 'a'})['status'], 'PASS')
        self.assertEqual(ne.check_catalog_item_binding_coherence({'id': '0001'})['status'], 'FAIL')
        with tempfile.TemporaryDirectory() as tmp:
            rp = Path(tmp) / 'OUT.md'
            rp.write_text('# OK\n', encoding='utf-8')
            self.assertEqual(ne.verify_all_markdown_deliverables_sha256(tmp, ['OUT.md'])['status'], 'PASS')
            self.assertEqual(ne.verify_all_markdown_deliverables_sha256(tmp, ['MISSING.md'])['status'], 'FAIL')
        self.assertEqual(ne.audit_no_external_global_install_mutation({'drifted_copies': []})['status'], 'PASS')
        self.assertEqual(ne.audit_no_external_global_install_mutation({'modified_external_paths': ['/x']})['status'], 'FAIL')
        self.assertEqual(ne.verify_autofix_suggestion_safety({'recommended_actions': ['Rewrite drive url'], 'ranked_verified_precedents': [{'classification': 'VERIFIED_FIX'}]})['status'], 'PASS')
        self.assertEqual(ne.verify_autofix_suggestion_safety({'recommended_actions': ['Set HostnameVerifier -> true'], 'ranked_verified_precedents': []})['status'], 'FAIL')
        self.assertEqual(ne.measure_enhancement_signal_to_noise_ratio({'1': {'function': 'a', 'title': 'A'}})['status'], 'PASS')
        self.assertEqual(ne.check_beginner_plain_language_ux_safety('Status: PASS\nNext step: Done')['status'], 'PASS')
        self.assertEqual(ne.check_beginner_plain_language_ux_safety('Traceback (most recent call last):')['status'], 'FAIL')
        self.assertEqual(ne.evaluate_qualitative_expansion_saturation(1000, 200, 175, True)['saturation_decision'], 'CONCLUDE_AT_1200_HIGH_VALUE')
        self.assertEqual(ne.evaluate_qualitative_expansion_saturation(1000, 150, 125, True)['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
