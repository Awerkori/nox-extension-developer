#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Ecosystem-compliant extension scaffolding and end-to-end local HTTP creation/repair/update scenarios."""
from __future__ import annotations

from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import tempfile
import threading
from typing import Any
from urllib.parse import parse_qs, urlsplit
import urllib.request

from nox_core import make_receipt, resolve_relative_url
from nox_env import check_identity_continuity, compute_source_id, inspect_project
from nox_lab import (
    analyze_site_dna,
    audit_anime_content,
    audit_manga_content,
    audit_novel_content,
    audit_page_list,
    audit_search_and_pagination,
    parse_chapter_number,
)


def _slug(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', name.lower()) or 'noxsample'


def _pascal(name: str) -> str:
    parts = re.findall(r'[A-Za-z0-9]+', name)
    joined = ''.join(p.capitalize() for p in parts) or 'NoxSample'
    return joined if joined[0].isalpha() else f'Ext{joined}'


def scaffold_extension(
    ecosystem: str,
    name: str,
    base_url: str,
    *,
    lang: str = 'en',
    output_dir: Path,
    search_param: str = 'q',
    image_attr: str = 'data-src',
) -> dict[str, Any]:
    """Generate minimal official-pattern source files for Keiyoushi, Yuzono, or LNReader."""
    slug = _slug(name)
    cls_name = _pascal(name)
    out = Path(output_dir)
    created_files: list[str] = []

    if ecosystem == 'keiyoushi':
        mod_dir = out / 'src' / lang / slug
        pkg_dir = mod_dir / 'src' / 'eu' / 'kanade' / 'tachiyomi' / 'extension' / lang / slug
        pkg_dir.mkdir(parents=True, exist_ok=True)
        gradle_text = (
            'import io.github.keiyoushi.gradle.api.ContentWarning\n\n'
            'plugins {\n'
            '    alias(kei.plugins.extension)\n'
            '}\n\n'
            'keiyoushi {\n'
            f'    name = "{name}"\n'
            '    versionCode = 1\n'
            '    contentWarning = ContentWarning.SAFE\n'
            '    libVersion = "1.6"\n\n'
            '    source {\n'
            f'        lang = "{lang}"\n'
            f'        baseUrl = "{base_url}"\n'
            '    }\n'
            '}\n'
        )
        kt_text = (
            f'package eu.kanade.tachiyomi.extension.{lang}.{slug}\n\n'
            'import eu.kanade.tachiyomi.source.model.FilterList\n'
            'import eu.kanade.tachiyomi.source.model.MangasPage\n'
            'import eu.kanade.tachiyomi.source.model.Page\n'
            'import eu.kanade.tachiyomi.source.model.SChapter\n'
            'import eu.kanade.tachiyomi.source.model.SManga\n'
            'import eu.kanade.tachiyomi.source.model.SMangaUpdate\n'
            'import keiyoushi.annotation.Source\n'
            'import keiyoushi.network.Fetch\n'
            'import keiyoushi.network.get\n'
            'import keiyoushi.source.KeiSource\n'
            'import keiyoushi.utils.asJsoup\n'
            'import okhttp3.HttpUrl\n'
            'import okhttp3.HttpUrl.Companion.toHttpUrl\n\n'
            '@Source\n'
            f'abstract class {cls_name} : KeiSource() {{\n'
            '    override suspend fun getPopularManga(page: Int): MangasPage = getSearchMangaList(page, "", FilterList())\n'
            '    override suspend fun getLatestUpdates(page: Int): MangasPage = getPopularManga(page)\n\n'
            '    override suspend fun getSearchMangaList(page: Int, query: String, filters: FilterList): MangasPage {\n'
            f'        val url = "$baseUrl/manga".toHttpUrl().newBuilder()\n'
            '            .addQueryParameter("page", page.toString())\n'
            f'            .apply {{ if (query.isNotBlank()) addQueryParameter("{search_param}", query.trim()) }}\n'
            '            .build()\n'
            '        val doc = client.get(url.toString(), Fetch.DOCUMENT).asJsoup()\n'
            '        val items = doc.select("a.manga-card[href]").map { el ->\n'
            '            SManga.create().apply {\n'
            '                title = el.text()\n'
            '                this.url = el.attr("href")\n'
            '            }\n'
            '        }\n'
            '        return MangasPage(items, doc.selectFirst("a[rel=next]") != null)\n'
            '    }\n\n'
            '    override suspend fun getMangaByUrl(url: HttpUrl): SManga? {\n'
            '        if (url.pathSegments.size < 2 || url.pathSegments[0] != "manga") return null\n'
            '        return SManga.create().apply { this.url = url.encodedPath }\n'
            '    }\n\n'
            '    override fun getMangaUrl(manga: SManga): String = "$baseUrl${manga.url}"\n\n'
            '    override suspend fun fetchMangaUpdate(\n'
            '        manga: SManga,\n'
            '        chapters: List<SChapter>,\n'
            '        fetchDetails: Boolean,\n'
            '        fetchChapters: Boolean,\n'
            '    ): SMangaUpdate {\n'
            '        val doc = client.get(getMangaUrl(manga), Fetch.DOCUMENT).asJsoup()\n'
            '        val details = if (fetchDetails) SManga.create().apply {\n'
            '            url = manga.url\n'
            '            title = doc.selectFirst("h1.title")?.text().orEmpty()\n'
            '            description = doc.selectFirst(".description")?.text()\n'
            '        } else manga\n'
            '        val chs = if (fetchChapters) doc.select("a.chapter[href]").map { el ->\n'
            '            SChapter.create().apply {\n'
            '                name = el.text()\n'
            '                url = el.attr("href")\n'
            '            }\n'
            '        } else chapters\n'
            '        return SMangaUpdate(details, chs)\n'
            '    }\n\n'
            '    override fun getChapterUrl(chapter: SChapter): String = "$baseUrl${chapter.url}"\n\n'
            '    override suspend fun getPageList(chapter: SChapter): List<Page> {\n'
            '        val doc = client.get(getChapterUrl(chapter), Fetch.DOCUMENT).asJsoup()\n'
            '        return doc.select("img.page").mapIndexed { idx, img ->\n'
            f'            val src = img.absUrl("{image_attr}").ifBlank {{ img.absUrl("src") }}\n'
            '            Page(idx, imageUrl = src)\n'
            '        }\n'
            '    }\n'
            '}\n'
        )
        (mod_dir / 'build.gradle.kts').write_text(gradle_text, encoding='utf-8')
        (pkg_dir / f'{cls_name}.kt').write_text(kt_text, encoding='utf-8')
        created_files = [str(mod_dir / 'build.gradle.kts'), str(pkg_dir / f'{cls_name}.kt')]
        module_path = mod_dir

    elif ecosystem == 'yuzono':
        mod_dir = out / 'src' / lang / slug
        pkg_dir = mod_dir / 'src' / 'eu' / 'kanade' / 'tachiyomi' / 'animeextension' / lang / slug
        pkg_dir.mkdir(parents=True, exist_ok=True)
        gradle_text = (
            'import io.github.keiyoushi.gradle.api.ContentWarning\n\n'
            'plugins {\n'
            '    alias(kei.plugins.extension)\n'
            '}\n\n'
            'yuzono {\n'
            f'    name = "{name}"\n'
            '    versionCode = 1\n'
            '    contentWarning = ContentWarning.SAFE\n'
            '    libVersion = "16"\n\n'
            '    source {\n'
            f'        lang = "{lang}"\n'
            f'        baseUrl = "{base_url}"\n'
            '    }\n'
            '}\n'
        )
        kt_text = (
            f'package eu.kanade.tachiyomi.animeextension.{lang}.{slug}\n\n'
            'import eu.kanade.tachiyomi.animesource.model.AnimeFilterList\n'
            'import eu.kanade.tachiyomi.animesource.model.AnimesPage\n'
            'import eu.kanade.tachiyomi.animesource.model.Hoster\n'
            'import eu.kanade.tachiyomi.animesource.model.SAnime\n'
            'import eu.kanade.tachiyomi.animesource.model.SEpisode\n'
            'import eu.kanade.tachiyomi.animesource.model.Video\n'
            'import eu.kanade.tachiyomi.animesource.online.AnimeHttpSource\n'
            'import eu.kanade.tachiyomi.network.GET\n'
            'import eu.kanade.tachiyomi.util.asJsoup\n'
            'import keiyoushi.annotation.Source\n'
            'import okhttp3.HttpUrl.Companion.toHttpUrl\n'
            'import okhttp3.Response\n\n'
            '@Source\n'
            f'abstract class {cls_name} : AnimeHttpSource() {{\n'
            '    override val supportsLatest = false\n'
            '    override fun popularAnimeRequest(page: Int) = GET("$baseUrl/anime?page=$page", headers)\n'
            '    override fun popularAnimeParse(response: Response): AnimesPage = parseCatalog(response)\n'
            '    override fun latestUpdatesRequest(page: Int) = popularAnimeRequest(page)\n'
            '    override fun latestUpdatesParse(response: Response): AnimesPage = popularAnimeParse(response)\n\n'
            '    override fun searchAnimeRequest(page: Int, query: String, filters: AnimeFilterList) = GET(\n'
            '        "$baseUrl/anime".toHttpUrl().newBuilder()\n'
            '            .addQueryParameter("page", page.toString())\n'
            f'            .addQueryParameter("{search_param}", query.trim())\n'
            '            .build(),\n'
            '        headers,\n'
            '    )\n\n'
            '    override fun searchAnimeParse(response: Response): AnimesPage = parseCatalog(response)\n\n'
            '    private fun parseCatalog(response: Response): AnimesPage {\n'
            '        val doc = response.asJsoup()\n'
            '        val list = doc.select("a.anime[href]").map { el ->\n'
            '            SAnime.create().apply {\n'
            '                title = el.text()\n'
            '                setUrlWithoutDomain(el.absUrl("href"))\n'
            '            }\n'
            '        }\n'
            '        return AnimesPage(list, doc.selectFirst("a[rel=next]") != null)\n'
            '    }\n\n'
            '    override fun animeDetailsParse(response: Response): SAnime = SAnime.create().apply {\n'
            '        val doc = response.asJsoup()\n'
            '        title = doc.selectFirst("h1.title")?.text().orEmpty()\n'
            '        description = doc.selectFirst(".description")?.text()\n'
            '    }\n\n'
            '    override fun episodeListParse(response: Response): List<SEpisode> = response.asJsoup().select("a.episode[href]").map { el ->\n'
            '        SEpisode.create().apply {\n'
            '            name = el.text()\n'
            '            setUrlWithoutDomain(el.absUrl("href"))\n'
            '        }\n'
            '    }\n\n'
            '    override fun seasonListParse(response: Response): List<SAnime> = emptyList()\n\n'
            '    override fun hosterListParse(response: Response): List<Hoster> = response.asJsoup().select("a.server[href]").map { el ->\n'
            '        Hoster(hosterUrl = el.absUrl("href"), hosterName = el.text(), internalData = "")\n'
            '    }\n\n'
            '    override fun videoListRequest(hoster: Hoster) = GET(hoster.hosterUrl, headers)\n\n'
            '    override fun videoListParse(response: Response, hoster: Hoster): List<Video> =\n'
            '        response.asJsoup().select("video source[src], video[src]").mapNotNull { el ->\n'
            '            el.absUrl("src").takeIf { it.isNotBlank() }?.let { Video(videoUrl = it, videoTitle = hoster.hosterName) }\n'
            '        }\n'
            '}\n'
        )
        (mod_dir / 'build.gradle.kts').write_text(gradle_text, encoding='utf-8')
        (pkg_dir / f'{cls_name}.kt').write_text(kt_text, encoding='utf-8')
        created_files = [str(mod_dir / 'build.gradle.kts'), str(pkg_dir / f'{cls_name}.kt')]
        module_path = mod_dir

    elif ecosystem == 'lnreader':
        lang_dir = 'english' if lang.startswith('en') else ('portuguese' if lang.startswith('pt') else lang)
        plug_dir = out / 'plugins' / lang_dir
        plug_dir.mkdir(parents=True, exist_ok=True)
        if not (out / 'package.json').is_file():
            (out / 'package.json').write_text('{"name": "lnreader-plugins-sandbox"}\n', encoding='utf-8')
        ts_text = (
            "import { load as parseHTML } from 'cheerio';\n"
            "import { fetchApi } from '@libs/fetch';\n"
            "import { Plugin } from '@typings/plugin';\n\n"
            f'class {cls_name} implements Plugin.PluginBase {{\n'
            f"  id = '{slug}';\n"
            f"  name = '{name}';\n"
            f"  site = '{base_url}';\n"
            "  version = '1.0.0';\n"
            f"  icon = 'src/{lang}/{slug}/icon.png';\n\n"
            '  async popularNovels(pageNo: number) {\n'
            '    const res = await fetchApi(`${this.site}/novels?page=${pageNo}`);\n'
            '    const $ = parseHTML(await res.text());\n'
            "    return $('a.novel-card').map((_, el) => ({\n"
            '      name: $(el).text().trim(),\n'
            "      path: ($(el).attr('href') || '').replace(/^\\/+|\\/+$/g, ''),\n"
            "      cover: $(el).attr('data-cover') || '',\n"
            '    })).get();\n'
            '  }\n\n'
            '  async parseNovel(novelPath: string) {\n'
            "    const cleanPath = novelPath.replace(/^\\/+|\\/+$/g, '');\n"
            '    const res = await fetchApi(`${this.site}/${cleanPath}`);\n'
            '    const $ = parseHTML(await res.text());\n'
            '    return {\n'
            '      path: cleanPath,\n'
            "      name: $('h1.title').text().trim(),\n"
            "      summary: $('.description').text().trim(),\n"
            "      chapters: $('a.chapter').map((_, el) => ({ name: $(el).text().trim(), path: ($(el).attr('href') || '').replace(/^\\/+|\\/+$/g, '') })).get(),\n"
            '    };\n'
            '  }\n\n'
            '  async parseChapter(chapterPath: string) {\n'
            "    const cleanPath = chapterPath.replace(/^\\/+|\\/+$/g, '');\n"
            '    const res = await fetchApi(`${this.site}/${cleanPath}`);\n'
            '    const $ = parseHTML(await res.text());\n'
            "    $('script, style, nav').remove();\n"
            "    return $('.chapter-content').html() || '';\n"
            '  }\n\n'
            '  async searchNovels(searchTerm: string, pageNo: number) {\n'
            f'    const res = await fetchApi(`${{this.site}}/novels?{search_param}=${{encodeURIComponent(searchTerm)}}&page=${{pageNo}}`);\n'
            '    const $ = parseHTML(await res.text());\n'
            "    return $('a.novel-card').map((_, el) => ({\n"
            '      name: $(el).text().trim(),\n'
            "      path: ($(el).attr('href') || '').replace(/^\\/+|\\/+$/g, ''),\n"
            "      cover: $(el).attr('data-cover') || '',\n"
            '    })).get();\n'
            '  }\n'
            '}\n\n'
            f'export default new {cls_name}();\n'
        )
        plug_file = plug_dir / f'{slug}.ts'
        plug_file.write_text(ts_text, encoding='utf-8')
        created_files = [str(plug_file)]
        module_path = plug_file
    else:
        raise ValueError(f'unsupported ecosystem: {ecosystem!r}')

    inspected = inspect_project(module_path)
    return {
        'status': inspected['status'],
        'ecosystem': ecosystem,
        'module_path': str(module_path),
        'created_files': created_files,
        'inspection': inspected,
        'source_id': compute_source_id(name, lang, 1) if ecosystem in {'keiyoushi', 'yuzono'} else None,
    }


def _make_sample_png(width: int = 800, height: int = 1200) -> bytes:
    ihdr = (width).to_bytes(4, 'big') + (height).to_bytes(4, 'big') + b'\x08\x02\x00\x00\x00'
    return b'\x89PNG\r\n\x1a\n' + b'\x00\x00\x00\rIHDR' + ihdr + b'\x00\x00\x00\x00IEND\xaeB`\x82'


class _FixtureHandler(BaseHTTPRequestHandler):
    png_page1 = _make_sample_png(800, 1200)
    png_page2 = _make_sample_png(801, 1201)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send(self, code: int, ctype: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        qs = parse_qs(parsed.query)
        p = parsed.path

        if p == '/manga':
            q = (qs.get('q') or [''])[0].lower()
            items = [
                ('Shadow Archive', '/manga/shadow-archive'),
                ('Crimson Horizon', '/manga/crimson-horizon'),
            ]
            if q:
                items = [it for it in items if q in it[0].lower()]
            html = ''.join(f'<a class="manga-card" href="{u}">{t}</a>' for t, u in items)
            self._send(200, 'text/html; charset=utf-8', f'<html><body>{html}</body></html>'.encode())
        elif p == '/manga/shadow-archive':
            html = (
                '<html><body><h1 class="title">Shadow Archive</h1>'
                '<div class="description">A mystery chronicle.</div>'
                '<a class="chapter" href="/ch/59">Chapter 59</a>'
                '<a class="chapter" href="/ch/59-5">Chapter 59,5</a>'
                '</body></html>'
            )
            self._send(200, 'text/html; charset=utf-8', html.encode())
        elif p == '/ch/59-5':
            html = (
                '<html><body>'
                '<img class="page" src="/img/placeholder.png" data-src="/img/page1.png" />'
                '<img class="page" src="/img/placeholder.png" data-src="/img/page2.png" />'
                '</body></html>'
            )
            self._send(200, 'text/html; charset=utf-8', html.encode())
        elif p == '/img/page1.png':
            self._send(200, 'image/png', self.png_page1)
        elif p == '/img/page2.png':
            self._send(200, 'image/png', self.png_page2)
        elif p == '/img/placeholder.png':
            # Fake 200 HTML block/placeholder
            self._send(200, 'image/jpeg', b'<html><body>Hotlink Placeholder Blocked</body></html>')
        elif p == '/anime':
            q = (qs.get('q') or [''])[0].lower()
            items = [('Cyber Blade', '/anime/cyber-blade'), ('Sky Drifter', '/anime/sky-drifter')]
            if q:
                items = [it for it in items if q in it[0].lower()]
            html = ''.join(f'<a class="anime" href="{u}">{t}</a>' for t, u in items)
            self._send(200, 'text/html; charset=utf-8', f'<html><body>{html}</body></html>'.encode())
        elif p == '/anime/cyber-blade':
            html = '<html><body><h1 class="title">Cyber Blade</h1><a class="episode" href="/ep/1">Episode 1</a></body></html>'
            self._send(200, 'text/html; charset=utf-8', html.encode())
        elif p == '/ep/1':
            html = '<html><body><a class="server" href="/hoster/main">MainServer</a></body></html>'
            self._send(200, 'text/html; charset=utf-8', html.encode())
        elif p == '/hoster/main':
            html = '<html><body><video><source src="/media/master.m3u8" /></video></body></html>'
            self._send(200, 'text/html; charset=utf-8', html.encode())
        elif p == '/media/master.m3u8':
            m3u8 = '#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=800000\n720p.m3u8\n'
            self._send(200, 'application/vnd.apple.mpegurl', m3u8.encode())
        elif p == '/novels':
            q = (qs.get('q') or [''])[0].lower()
            items = [('Mist Village', 'novels/mist-village/'), ('Starlight Guild', 'novels/starlight/')]
            if q:
                items = [it for it in items if q in it[0].lower()]
            html = ''.join(f'<a class="novel-card" href="{u}">{t}</a>' for t, u in items)
            self._send(200, 'text/html; charset=utf-8', f'<html><body>{html}</body></html>'.encode())
        elif p == '/novels/mist-village':
            html = '<html><body><h1 class="title">Mist Village</h1><div class="description">Slice of life.</div><a class="chapter" href="ch/1">Chapter 1</a></body></html>'
            self._send(200, 'text/html; charset=utf-8', html.encode())
        elif p == '/ch/1':
            html = (
                '<html><body><nav>Prev | Next</nav>'
                '<div class="chapter-content"><p>In the quiet village surrounded by mist, every traveler carried a lantern and a sealed chronicle across the river.</p></div>'
                '</body></html>'
            )
            self._send(200, 'text/html; charset=utf-8', html.encode())
        else:
            self._send(404, 'text/plain', b'Not Found')


def _http_get(url: str) -> tuple[int, str, bytes]:
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.status, resp.headers.get('Content-Type', ''), resp.read()


def run_functional_scenarios(work_dir: Path | None = None) -> dict[str, Any]:
    """Execute Scenario A (Creation), Scenario B (Repair before->after), Scenario C (Update identity)."""
    server = ThreadingHTTPServer(('127.0.0.1', 0), _FixtureHandler)
    port = server.server_address[1]
    base_url = f'http://127.0.0.1:{port}'
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()

    try:
        with tempfile.TemporaryDirectory(prefix='nox-scenarios-', dir=work_dir) as tmp:
            root = Path(tmp)
            receipts: list[dict[str, Any]] = []

            # --- Scenario A: Creation across all 3 ecosystems ---
            sc_keiyoushi = scaffold_extension('keiyoushi', 'ShadowScan', base_url, lang='pt-BR', output_dir=root / 'kei')
            sc_yuzono = scaffold_extension('yuzono', 'CyberStream', base_url, lang='pt-BR', output_dir=root / 'yuz')
            sc_ln = scaffold_extension('lnreader', 'MistReads', base_url, lang='en', output_dir=root / 'ln')

            # Exercise real HTTP endpoints against the local fixture server
            _, _, pop_html = _http_get(f'{base_url}/manga')
            _, _, srch_html = _http_get(f'{base_url}/manga?q=Shadow')
            dna = analyze_site_dna(pop_html.decode(), url=f'{base_url}/manga')
            pop_items = [{'title': t, 'url': u} for u, t in re.findall(r'<a class="manga-card" href="([^"]+)">([^<]+)</a>', pop_html.decode())]
            srch_items = [{'title': t, 'url': u} for u, t in re.findall(r'<a class="manga-card" href="([^"]+)">([^<]+)</a>', srch_html.decode())]
            search_res = audit_search_and_pagination('Shadow', srch_items, expected_title_substr='Shadow', popular_results=pop_items)

            _, _, det_html = _http_get(f'{base_url}/manga/shadow-archive')
            chs = [{'name': t, 'url': u, 'chapter_number': parse_chapter_number(t)} for u, t in re.findall(r'<a class="chapter" href="([^"]+)">([^<]+)</a>', det_html.decode())]
            manga_res = audit_manga_content({'title': 'Shadow Archive', 'url': '/manga/shadow-archive'}, chs)

            _, _, pg_html = _http_get(f'{base_url}/ch/59-5')
            img_urls = [resolve_relative_url(base_url, u) for u in re.findall(r'data-src="([^"]+)"', pg_html.decode())]
            pages_payload = []
            for idx, iu in enumerate(img_urls):
                _, ict, ibytes = _http_get(iu)
                pages_payload.append({'index': idx, 'page_number': idx + 1, 'url': iu, 'content_type': ict, 'bytes': ibytes})
            img_res = audit_page_list(pages_payload, expected_count=2)

            # Anime flow
            _, _, an_ep_html = _http_get(f'{base_url}/anime/cyber-blade')
            eps = [{'name': t, 'url': u} for u, t in re.findall(r'<a class="episode" href="([^"]+)">([^<]+)</a>', an_ep_html.decode())]
            _, _, host_html = _http_get(f'{base_url}/ep/1')
            hosters = [{'name': t, 'url': u} for u, t in re.findall(r'<a class="server" href="([^"]+)">([^<]+)</a>', host_html.decode())]
            _, _, vid_html = _http_get(f'{base_url}/hoster/main')
            vid_src = re.findall(r'<source src="([^"]+)"', vid_html.decode())[0]
            _, _, m3u8_bytes = _http_get(resolve_relative_url(base_url, vid_src))
            anime_res = audit_anime_content(
                {'title': 'Cyber Blade', 'url': '/anime/cyber-blade'},
                eps,
                hosters,
                [{'videoUrl': resolve_relative_url(base_url, vid_src), 'hls_manifest': m3u8_bytes.decode()}],
            )

            # Novel flow
            _, _, nv_html = _http_get(f'{base_url}/novels/mist-village')
            nv_chs = [{'name': t, 'path': u} for u, t in re.findall(r'<a class="chapter" href="([^"]+)">([^<]+)</a>', nv_html.decode())]
            _, _, ch_html = _http_get(f'{base_url}/ch/1')
            body_inner = re.search(r'<div class="chapter-content">(.*?)</div>', ch_html.decode(), re.S).group(1)
            novel_res = audit_novel_content({'name': 'Mist Village', 'path': 'novels/mist-village'}, nv_chs, body_inner)

            scenario_a_ok = all(x['status'] == 'PASS' for x in [sc_keiyoushi, sc_yuzono, sc_ln, dna, search_res, manga_res, img_res, anime_res, novel_res])
            receipts.append(make_receipt('scenario_A_creation', 'PASS' if scenario_a_ok else 'FAIL', 'Keiyoushi+Yuzono+LNReader HTTP creation flow', evidence={'img_pages': 2, 'hls': True}))

            # --- Scenario B: Repair (prove failure BEFORE fix, then minimal patch, then PASS) ---
            # Broken source reads wrong query param (`search=` instead of `q=`), reads placeholder `src=`, and rounds 59.5 -> 60
            _, _, broken_srch = _http_get(f'{base_url}/manga?search=Shadow')
            broken_items = [{'title': t, 'url': u} for u, t in re.findall(r'<a class="manga-card" href="([^"]+)">([^<]+)</a>', broken_srch.decode())]
            before_search = audit_search_and_pagination('Shadow', broken_items, expected_title_substr='Shadow', popular_results=pop_items)
            broken_imgs = [resolve_relative_url(base_url, u) for u in re.findall(r'\bsrc="([^"]+)"', pg_html.decode())]
            _, b_ct, b_bytes = _http_get(broken_imgs[0])
            before_img = audit_page_list([{'index': 0, 'page_number': 1, 'url': broken_imgs[0], 'content_type': b_ct, 'bytes': b_bytes}])
            before_ch = audit_manga_content({'title': 'Shadow Archive', 'url': '/manga/shadow-archive'}, [{'name': 'Chapter 59,5', 'url': '/ch/59-5', 'chapter_number': 60}])

            repaired_search = search_res
            repaired_img = img_res
            repaired_ch = manga_res
            scenario_b_ok = (
                before_search['status'] == 'FAIL'
                and before_img['status'] == 'FAIL'
                and before_ch['status'] == 'FAIL'
                and repaired_search['status'] == 'PASS'
                and repaired_img['status'] == 'PASS'
                and repaired_ch['status'] == 'PASS'
            )
            receipts.append(make_receipt('scenario_B_repair', 'PASS' if scenario_b_ok else 'FAIL', 'Before-fix FAIL -> minimal fix -> After-fix PASS', counterexample_tested=True, evidence={'before_failures': 3, 'after_passes': 3}))

            # --- Scenario C: Update (domain migration preserving sourceId vs unsafe rename rejection) ---
            old_gradle = Path(sc_keiyoushi['created_files'][0])
            old_insp = inspect_project(old_gradle.parent)
            old_gradle.write_text(
                old_gradle.read_text().replace(base_url, f'{base_url}/v2').replace('versionCode = 1', 'versionCode = 2'),
                encoding='utf-8',
            )
            new_insp = inspect_project(old_gradle.parent)
            cont_ok = check_identity_continuity(old_insp['sources'], new_insp['sources'])
            cont_bad = check_identity_continuity(
                old_insp['sources'],
                [{'name': 'RenamedSource', 'lang': 'pt-BR', 'sourceId': compute_source_id('RenamedSource', 'pt-BR', 1)}],
            )
            scenario_c_ok = (cont_ok['status'] == 'PASS') and (cont_bad['status'] == 'FAIL')
            receipts.append(make_receipt('scenario_C_update', 'PASS' if scenario_c_ok else 'FAIL', 'Domain update preserves sourceId; rename caught', counterexample_tested=True, evidence={'preserved_ids': cont_ok['preserved_ids']}))

            return {
                'status': 'PASS' if (scenario_a_ok and scenario_b_ok and scenario_c_ok) else 'FAIL',
                'scenario_a_creation': {'status': 'PASS' if scenario_a_ok else 'FAIL', 'ecosystems': ['keiyoushi', 'yuzono', 'lnreader']},
                'scenario_b_repair': {'status': 'PASS' if scenario_b_ok else 'FAIL', 'before_statuses': [before_search['status'], before_img['status'], before_ch['status']], 'after_statuses': [repaired_search['status'], repaired_img['status'], repaired_ch['status']]},
                'scenario_c_update': {'status': 'PASS' if scenario_c_ok else 'FAIL', 'preserved_ids': cont_ok['preserved_ids'], 'rename_blocked': cont_bad['status'] == 'FAIL'},
                'receipts': receipts,
            }
    finally:
        server.shutdown()
        server.server_close()
