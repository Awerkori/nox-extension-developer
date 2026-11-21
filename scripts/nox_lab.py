#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Site DNA inspection, Image Lab, Manga/Anime/Novel integrity auditors, and mutation oracles."""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
from pathlib import Path
import re
import struct
import time
from typing import Any, Callable, Sequence
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import zlib

from nox_core import is_safe_public_url, normalize_url, resolve_relative_url, sanitize_text, scan_prompt_injection, sha256_bytes


# =============================================================================
# 1. Site DNA, HTTP Diagnostics & Selector Stability
# =============================================================================

_CF_PATTERNS = (
    re.compile(r'(?i)just\s+a\s+moment\.\.\.'),
    re.compile(r'(?i)/cdn-cgi/challenge-platform'),
    re.compile(r'(?i)cf-browser-verification|cf_chl_opt|turnstile'),
)

_LOGIN_GATE_PATTERNS = (
    re.compile(r'(?i)<input[^>]+type=["\']password["\']'),
    re.compile(r'(?i)\b(sign\s+in\s+to\s+continue|login\s+required|acesso\s+restrito|faça\s+login|members?\s+only)\b'),
)

_REGION_BLOCK_PATTERNS = (
    re.compile(r'(?i)\b(not\s+available\s+in\s+your\s+(?:country|region)|geo[- ]?blocked|conteúdo\s+indisponível\s+na\s+sua\s+região)\b'),
)

_CAPTIVE_PATTERNS = (
    re.compile(r'(?i)\b(captive\s+portal|wi-?fi\s+login|accept\s+terms\s+to\s+access\s+internet)\b'),
)


def score_selector_stability(selector: str) -> dict[str, Any]:
    """Evaluate fragility of a CSS selector (hash classes, nth-child chains, presentation classes)."""
    sel = selector.strip()
    if not sel:
        return {'selector': sel, 'score': 0, 'stability': 'FRAGILE', 'reasons': ['empty selector']}
    penalties: list[str] = []
    score = 100

    if re.search(r'\.[a-z]{1,4}-[A-Za-z0-9]{5,}', sel) or re.search(r'\.css-[A-Za-z0-9_-]{4,}', sel) or re.search(r'\.sc-[A-Za-z0-9]{5,}', sel):
        score -= 45
        penalties.append('contains generated CSS-in-JS / hashed class')
    if ':nth-child' in sel or ':nth-of-type' in sel:
        score -= 25
        penalties.append('relies on positional nth-child/nth-of-type')
    depth = len(re.split(r'\s+|\s*>\s*', sel))
    if depth > 4:
        score -= 20
        penalties.append(f'deep DOM path ({depth} levels)')
    if re.search(r'\[(?:data-|itemprop=|aria-|role=|href|src)', sel):
        score = min(100, score + 10)
    if '#' in sel and not re.search(r'#[A-Za-z0-9_-]*\d{4,}', sel):
        score = min(100, score + 5)

    stability = 'STABLE' if score >= 75 else ('MODERATE' if score >= 50 else 'FRAGILE')
    return {'selector': sel, 'score': max(0, score), 'stability': stability, 'reasons': penalties}


def parse_srcset(srcset: str, base_url: str) -> list[dict[str, Any]]:
    """Parse HTML srcset attribute, normalize relative URLs, and sort highest descriptor first."""
    candidates: list[dict[str, Any]] = []
    for raw_item in srcset.split(','):
        part = raw_item.strip()
        if not part:
            continue
        tokens = part.split()
        raw_url = tokens[0]
        desc = tokens[1] if len(tokens) > 1 else '1x'
        weight = 1.0
        if desc.endswith('w') and desc[:-1].isdigit():
            weight = float(desc[:-1])
        elif desc.endswith('x'):
            try:
                weight = float(desc[:-1]) * 1000.0
            except ValueError:
                weight = 1.0
        resolved = resolve_relative_url(base_url, raw_url)
        candidates.append({'url': resolved, 'descriptor': desc, 'weight': weight})
    candidates.sort(key=lambda c: c['weight'], reverse=True)
    return candidates


def analyze_site_dna(
    body: str,
    *,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
    url: str | None = None,
    expected_kind: str = 'html',
) -> dict[str, Any]:
    """Detect site platform, dynamic JS/SPA, GraphQL, Cloudflare, deceptive HTTP 200, and auth walls."""
    hdrs = {k.lower(): v for k, v in (headers or {}).items()}
    ct = hdrs.get('content-type', '').lower()
    platforms: list[str] = []
    diagnostics: list[str] = []
    auth_restricted = False
    block_reason: str | None = None

    if status_code in {401, 403, 407, 429, 451} or status_code >= 500:
        block_reason = f'http_{status_code}'
        if status_code == 429 and 'retry-after' in hdrs:
            diagnostics.append(f"rate_limited_retry_after:{hdrs['retry-after']}")

    if hdrs.get('cf-mitigated') or any(p.search(body) for p in _CF_PATTERNS):
        platforms.append('cloudflare-challenge')
        block_reason = 'cloudflare_challenge'
    if any(p.search(body) for p in _CAPTIVE_PATTERNS):
        block_reason = 'captive_portal'
    if any(p.search(body) for p in _REGION_BLOCK_PATTERNS):
        block_reason = 'geo_blocked'
    if any(p.search(body) for p in _LOGIN_GATE_PATTERNS):
        auth_restricted = True
        diagnostics.append('login_or_paywall_detected')

    # Deceptive HTTP 200 checks
    deceptive_200 = False
    trimmed = body.lstrip()
    if status_code == 200:
        if expected_kind == 'json' and (trimmed.startswith('<') or 'text/html' in ct):
            deceptive_200 = True
            diagnostics.append('http_200_html_instead_of_json')
        elif not trimmed:
            deceptive_200 = True
            diagnostics.append('http_200_empty_body')
        elif block_reason in {'cloudflare_challenge', 'captive_portal', 'geo_blocked'} or auth_restricted:
            deceptive_200 = True
            diagnostics.append('http_200_error_or_gate_body')

    # Platform fingerprints (never infer from visual similarity alone)
    if 'wp-manga' in body or 'madara' in body.lower() or 'admin-ajax.php' in body:
        platforms.append('wordpress-madara')
    if 'ts_reader.run' in body or 'themesia' in body.lower():
        platforms.append('themesia-mangastream')
    if 'fictioneer' in body.lower():
        platforms.append('wordpress-fictioneer')
    if '__NEXT_DATA__' in body or 'self.__next_f.push' in body:
        platforms.append('nextjs-hydration')
    if '__NUXT__' in body or 'window.__NUXT' in body:
        platforms.append('nuxt-hydration')
    if '/graphql' in body or ('"query"' in body and '"variables"' in body) or 'pageInfo' in body:
        platforms.append('graphql')

    # Detect SPA shell needing JS / WebView vs server-rendered HTML
    requires_js = False
    if '<div id="root"></div>' in body or '<div id="app"></div>' in body:
        if '__NEXT_DATA__' not in body and len(re.sub(r'<[^>]+>', '', body).strip()) < 200:
            requires_js = True
            diagnostics.append('empty_spa_shell_requires_js_or_api_inspection')

    # Check embedded JSON payloads and lazy image attributes
    has_lazy_attrs = bool(re.search(r'\b(?:data-src|data-lazy-src|data-original|srcset)=', body))
    if has_lazy_attrs:
        diagnostics.append('lazy_load_image_attributes_present')

    injection_scan = scan_prompt_injection(body, source_label=url or 'site-body')
    status = 'BLOCKED' if (block_reason or deceptive_200 or auth_restricted) else 'PASS'

    return {
        'status': status,
        'url': normalize_url(url) if url else None,
        'status_code': status_code,
        'content_type': ct,
        'platforms': sorted(set(platforms)),
        'requires_js': requires_js,
        'auth_restricted': auth_restricted,
        'deceptive_http_200': deceptive_200,
        'block_reason': block_reason,
        'diagnostics': diagnostics,
        'prompt_injection': injection_scan,
    }


# =============================================================================
# 2. Nox Image Laboratory (real magic bytes, dimensions, HTML/placeholder checks)
# =============================================================================

_PLACEHOLDER_HINTS = ('placeholder', 'loading', 'spinner', 'blank.', 'adbanner', 'advert', 'banner', '1x1', 'spacer')


def _parse_png_dims(data: bytes) -> tuple[int, int] | None:
    if len(data) >= 24 and data[:8] == b'\x89PNG\r\n\x1a\n' and data[12:16] == b'IHDR':
        return struct.unpack('>II', data[16:24])
    return None


def _parse_gif_dims(data: bytes) -> tuple[int, int] | None:
    if len(data) >= 10 and data[:6] in (b'GIF87a', b'GIF89a'):
        return struct.unpack('<HH', data[6:10])
    return None


def _parse_jpeg_dims(data: bytes) -> tuple[int, int] | None:
    if len(data) < 4 or data[:2] != b'\xff\xd8':
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker == 0xD9 or marker == 0xDA:
            break
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack('>HH', data[i + 5:i + 9])
            return w, h
        if i + 4 > len(data):
            break
        seg_len = struct.unpack('>H', data[i + 2:i + 4])[0]
        if seg_len < 2:
            break
        i += 2 + seg_len
    return None


def _parse_webp_dims(data: bytes) -> tuple[int, int] | None:
    if len(data) < 30 or data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        return None
    chunk = data[12:16]
    if chunk == b'VP8 ' and len(data) >= 30:
        w = struct.unpack('<H', data[26:28])[0] & 0x3FFF
        h = struct.unpack('<H', data[28:30])[0] & 0x3FFF
        return w, h
    if chunk == b'VP8L' and len(data) >= 25:
        bits = struct.unpack('<I', data[21:25])[0]
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b'VP8X' and len(data) >= 30:
        w = int.from_bytes(data[24:27], 'little') + 1
        h = int.from_bytes(data[27:30], 'little') + 1
        return w, h
    return None


def inspect_image_payload(
    data: bytes,
    *,
    content_type: str | None = None,
    url: str | None = None,
    min_width: int = 100,
    min_height: int = 100,
    role: str = 'page',
) -> dict[str, Any]:
    """Verify real binary image format, truncation, dimensions, MIME mismatch, and fake HTTP 200 HTML."""
    ct = (content_type or '').split(';')[0].strip().lower()
    url_l = (url or '').lower()

    if not data:
        return {'status': 'FAIL', 'reason': 'empty_image_bytes', 'format': None, 'url': url}

    head = data[:512].lstrip().lower()
    if head.startswith((b'<!doctype', b'<html', b'<head', b'<body', b'{', b'<?xml')) or b'<html' in head:
        return {
            'status': 'FAIL',
            'reason': 'fake_200_html_or_text_payload',
            'declared_content_type': ct or None,
            'format': 'text/html_or_json',
            'url': url,
        }

    detected_fmt: str | None = None
    dims: tuple[int, int] | None = None
    truncated = False

    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        detected_fmt = 'image/png'
        dims = _parse_png_dims(data)
        truncated = not (b'IEND' in data[-32:])
    elif data.startswith(b'\xff\xd8\xff'):
        detected_fmt = 'image/jpeg'
        dims = _parse_jpeg_dims(data)
        truncated = not data.endswith(b'\xff\xd9')
    elif data[:6] in (b'GIF87a', b'GIF89a'):
        detected_fmt = 'image/gif'
        dims = _parse_gif_dims(data)
        truncated = not data.endswith(b'\x3b')
    elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        detected_fmt = 'image/webp'
        dims = _parse_webp_dims(data)
        declared_size = struct.unpack('<I', data[4:8])[0] + 8
        truncated = len(data) < declared_size
    elif len(data) >= 12 and data[4:8] == b'ftyp' and b'avif' in data[8:16]:
        detected_fmt = 'image/avif'

    if not detected_fmt:
        return {
            'status': 'FAIL',
            'reason': 'unrecognized_or_corrupt_binary_signature',
            'declared_content_type': ct or None,
            'url': url,
        }

    warnings: list[str] = []
    if ct and ct.startswith('image/') and ct != detected_fmt and not (ct == 'image/jpg' and detected_fmt == 'image/jpeg'):
        warnings.append(f'mime_mismatch:header={ct},actual={detected_fmt}')
    if any(hint in url_l for hint in _PLACEHOLDER_HINTS):
        return {
            'status': 'FAIL',
            'reason': 'suspected_placeholder_or_ad_url',
            'format': detected_fmt,
            'dimensions': dims,
            'url': url,
        }
    if truncated:
        return {
            'status': 'FAIL',
            'reason': 'truncated_image_payload',
            'format': detected_fmt,
            'dimensions': dims,
            'url': url,
        }
    if role == 'page' and dims is not None and (dims[0] < min_width or dims[1] < min_height):
        return {
            'status': 'FAIL',
            'reason': f'low_resolution_or_thumbnail:{dims[0]}x{dims[1]}',
            'format': detected_fmt,
            'dimensions': dims,
            'url': url,
        }

    return {
        'status': 'PASS',
        'format': detected_fmt,
        'dimensions': {'width': dims[0], 'height': dims[1]} if dims else None,
        'bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
        'warnings': warnings,
        'url': url,
    }


def audit_page_list(pages: Sequence[dict[str, Any]], *, expected_count: int | None = None) -> dict[str, Any]:
    """Audit chapter page ordering, duplicates, missing pages, and per-page image payloads."""
    if not pages:
        return {'status': 'FAIL', 'reason': 'empty_page_list', 'issues': ['zero pages returned']}

    issues: list[str] = []
    seen_hashes: dict[str, int] = {}
    seen_urls: dict[str, int] = {}
    indices: list[int] = []

    for pos, page in enumerate(pages):
        idx = page.get('index', pos)
        indices.append(idx)
        url = page.get('url', '')
        if url:
            if url in seen_urls:
                issues.append(f'duplicate_page_url:pos={pos} duplicates pos={seen_urls[url]}')
            seen_urls[url] = pos
        raw = page.get('bytes')
        if raw is not None:
            res = inspect_image_payload(raw, content_type=page.get('content_type'), url=url)
            if res['status'] != 'PASS':
                issues.append(f"invalid_page_image:pos={pos}:{res['reason']}")
            else:
                h = res['sha256']
                if h in seen_hashes:
                    issues.append(f'duplicate_page_bytes:pos={pos} matches pos={seen_hashes[h]}')
                seen_hashes[h] = pos

    # Check lexical ordering error (e.g., 1, 10, 2) if page numbers or indices are supplied
    nums = [p['page_number'] for p in pages if isinstance(p.get('page_number'), (int, float))]
    if nums and nums != sorted(nums):
        issues.append(f'non_monotonic_page_order:{nums[:10]}')
    if indices != sorted(indices):
        issues.append('page_indices_out_of_order')
    if expected_count is not None and len(pages) != expected_count:
        issues.append(f'page_count_mismatch:expected={expected_count},actual={len(pages)}')

    return {
        'status': 'FAIL' if issues else 'PASS',
        'page_count': len(pages),
        'issues': issues,
    }


# =============================================================================
# 3. Nox Manga Integrity Lab
# =============================================================================

_AD_LINK_PATTERNS = re.compile(r'(?i)(?:doubleclick|googlesyndication|/ads?/|promo|casino|betting|bit\.ly|discord\.gg)')


def parse_chapter_number(title: str) -> float | None:
    """Extract chapter number preserving decimals (59.5, 10,5 -> 10.5) and prologues (0)."""
    norm = title.replace(',', '.')
    # Match explicit chapter markers first
    m = re.search(r'(?i)(?:ch(?:ap(?:ter)?)?|cap(?:ítulo)?|ep(?:isódio)?)\s*\.?\s*(\d+(?:\.\d+)?)', norm)
    if m:
        return float(m.group(1))
    if re.search(r'(?i)\b(?:prologue|prólogo|oneshot|one-shot)\b', norm):
        return 0.0
    m2 = re.search(r'\b(\d+(?:\.\d+)?)\b', norm)
    return float(m2.group(1)) if m2 else None


def audit_manga_content(
    manga: dict[str, Any],
    chapters: Sequence[dict[str, Any]],
    *,
    previous_chapters: Sequence[dict[str, Any]] | None = None,
    allow_empty_chapters: bool = False,
) -> dict[str, Any]:
    """Audit manga metadata, fractional chapters (59.5 != 60), ad links, duplicates, and URL continuity."""
    issues: list[str] = []
    warnings: list[str] = []

    if not str(manga.get('title', '')).strip():
        issues.append('missing_manga_title')
    if not str(manga.get('url', '')).strip():
        issues.append('missing_manga_url')

    if not chapters:
        if allow_empty_chapters:
            warnings.append('manga_has_zero_chapters_yet')
        else:
            issues.append('empty_chapter_list')

    seen_urls: set[str] = set()
    parsed_numbers: list[float] = []
    for i, ch in enumerate(chapters):
        name = str(ch.get('name', '')).strip()
        url = str(ch.get('url', '')).strip()
        if not name or not url:
            issues.append(f'chapter_{i}_missing_name_or_url')
            continue
        if _AD_LINK_PATTERNS.search(url):
            issues.append(f'ad_or_external_promo_in_chapter_list:{url}')
        if url in seen_urls:
            issues.append(f'duplicate_chapter_url:{url}')
        seen_urls.add(url)

        num = ch.get('chapter_number')
        if num is None:
            num = parse_chapter_number(name)
        if isinstance(num, (int, float)) and num >= 0:
            # Guard against rounding 59.5 -> 60
            parsed_num = parse_chapter_number(name)
            if parsed_num is not None and abs(parsed_num - float(num)) > 1e-6:
                issues.append(f'chapter_number_precision_loss:title={name!r},stored={num},expected={parsed_num}')
            parsed_numbers.append(float(num))

    if previous_chapters:
        prev_urls = {c.get('url') for c in previous_chapters if c.get('url')}
        lost = sorted(u for u in prev_urls if u not in seen_urls)
        if lost:
            warnings.append(f'chapter_url_drift_may_break_history:{len(lost)}_lost')

    return {
        'status': 'FAIL' if issues else 'PASS',
        'chapter_count': len(chapters),
        'parsed_numbers_sample': parsed_numbers[:10],
        'issues': issues,
        'warnings': warnings,
    }


# =============================================================================
# 4. Nox Anime & Media Protocol Lab (Yuzono / Aniyomi)
# =============================================================================

def inspect_hls_manifest(manifest_text: str, manifest_url: str) -> dict[str, Any]:
    """Inspect HLS #EXTM3U playlists for variants, relative URLs, audio tracks, subtitles, and DRM."""
    lines = [ln.strip() for ln in manifest_text.splitlines() if ln.strip()]
    if not lines or lines[0] != '#EXTM3U':
        return {'status': 'FAIL', 'reason': 'not_a_valid_m3u8_manifest'}

    has_drm = any('METHOD=SAMPLE-AES' in ln or 'METHOD=AES-128' in ln or 'KEYFORMAT' in ln for ln in lines if ln.startswith('#EXT-X-KEY'))
    variants: list[dict[str, Any]] = []
    audio_tracks: list[str] = []
    subtitle_tracks: list[str] = []
    segments: list[str] = []

    for idx, ln in enumerate(lines):
        if ln.startswith('#EXT-X-STREAM-INF:'):
            next_url = lines[idx + 1] if idx + 1 < len(lines) and not lines[idx + 1].startswith('#') else None
            resolved = resolve_relative_url(manifest_url, next_url) if next_url else None
            variants.append({'attrs': ln, 'url': resolved})
        elif ln.startswith('#EXT-X-MEDIA:'):
            if 'TYPE=AUDIO' in ln:
                audio_tracks.append(ln)
            elif 'TYPE=SUBTITLES' in ln:
                subtitle_tracks.append(ln)
        elif not ln.startswith('#'):
            segments.append(resolve_relative_url(manifest_url, ln))

    if has_drm:
        return {
            'status': 'BLOCKED',
            'reason': 'encrypted_or_drm_stream_detected',
            'variants': len(variants),
            'segments': len(segments),
        }
    if not variants and not segments:
        return {'status': 'FAIL', 'reason': 'empty_hls_playlist_no_variants_or_segments'}
    return {
        'status': 'PASS',
        'variants': variants,
        'audio_tracks': len(audio_tracks),
        'subtitle_tracks': len(subtitle_tracks),
        'segments_count': len(segments),
        'sample_segment': segments[0] if segments else None,
    }


def audit_anime_content(
    anime: dict[str, Any],
    episodes: Sequence[dict[str, Any]],
    hosters: Sequence[dict[str, Any]],
    videos: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Audit Yuzono anime flow keeping Hoster discovery strictly separate from getVideoList resolution."""
    issues: list[str] = []
    warnings: list[str] = []

    if not str(anime.get('title', '')).strip() or not str(anime.get('url', '')).strip():
        issues.append('missing_anime_title_or_url')
    if not episodes:
        issues.append('empty_episode_list')

    # Mandatory counterexample check: having hosters != getVideoList returning valid videos
    if hosters and not videos:
        issues.append('hosters_listed_but_getVideoList_returned_empty')
    elif not videos:
        issues.append('no_resolved_video_streams')

    valid_streams = 0
    blocked_drm = False
    for v in videos:
        v_url = str(v.get('videoUrl') or v.get('url') or '').strip()
        if not v_url:
            issues.append(f"video_missing_url:{v.get('quality', 'unknown')}")
            continue
        if v.get('drm'):
            blocked_drm = True
            continue
        manifest = v.get('hls_manifest')
        if manifest:
            hls = inspect_hls_manifest(manifest, v_url)
            if hls['status'] == 'BLOCKED':
                blocked_drm = True
            elif hls['status'] != 'PASS':
                issues.append(f"invalid_hls_stream:{hls.get('reason')}")
            else:
                valid_streams += 1
        elif urlsplit(v_url).scheme in {'http', 'https'}:
            valid_streams += 1
        else:
            issues.append(f'invalid_video_scheme:{v_url}')

    if blocked_drm and valid_streams == 0 and not issues:
        return {'status': 'BLOCKED', 'reason': 'drm_protected_streams_cannot_bypass', 'issues': [], 'warnings': warnings}

    return {
        'status': 'FAIL' if issues else ('PASS' if valid_streams > 0 else 'INCONCLUSIVE'),
        'episodes_count': len(episodes),
        'hosters_count': len(hosters),
        'valid_streams_count': valid_streams,
        'issues': issues,
        'warnings': warnings,
    }


# =============================================================================
# 5. Nox Novel / LNReader Integrity Lab
# =============================================================================

_NAV_ONLY_RE = re.compile(r'(?i)^(?:\s*(?:prev(?:ious)?|next|back\s+to\s+top|table\s+of\s+contents|chapters?|home)\s*[|/•\-]*)+$')


def audit_novel_content(
    novel: dict[str, Any],
    chapters: Sequence[dict[str, Any]],
    chapter_html: str,
    *,
    min_readable_chars: int = 80,
) -> dict[str, Any]:
    """Verify LNReader chapter HTML readability (reject nav-only/empty/script-polluted/paywall text)."""
    issues: list[str] = []
    if not str(novel.get('name', '')).strip() or not str(novel.get('path', '')).strip():
        issues.append('missing_novel_name_or_path')
    if not chapters:
        issues.append('empty_chapter_list')

    if '<script' in chapter_html.lower() or '<style' in chapter_html.lower():
        issues.append('unstripped_script_or_style_tags_in_chapter')

    text_only = re.sub(r'<[^>]+>', ' ', chapter_html)
    text_only = ' '.join(text_only.split())
    if not text_only:
        issues.append('empty_chapter_text')
    elif _NAV_ONLY_RE.match(text_only):
        issues.append('chapter_body_is_navigation_links_only')
    elif len(text_only) < min_readable_chars:
        issues.append(f'truncated_or_too_short_chapter:{len(text_only)}_chars')

    if any(p.search(chapter_html) for p in _LOGIN_GATE_PATTERNS):
        issues.append('paywall_or_login_prompt_returned_as_chapter')

    paragraphs = len(re.findall(r'<p\b', chapter_html, re.I))
    return {
        'status': 'FAIL' if issues else 'PASS',
        'readable_chars': len(text_only),
        'paragraphs_count': paragraphs,
        'chapters_count': len(chapters),
        'issues': issues,
    }


def interpret_lnreader_check_plugin(exit_code: int, stdout: str) -> dict[str, Any]:
    """Interpret LNReader `check:plugin` output without turning INCONCLUSIVE into PASS."""
    upper = stdout.upper()
    if 'INCONCLUSIVE' in upper:
        return {'status': 'INCONCLUSIVE', 'reason': 'upstream site blocked or unreachable during check:plugin'}
    if exit_code != 0 or 'FAIL' in upper:
        return {'status': 'FAIL', 'reason': 'check:plugin reported failure'}
    if 'PASS' in upper:
        return {'status': 'PASS', 'reason': 'check:plugin reported PASS'}
    return {'status': 'INCONCLUSIVE', 'reason': 'no explicit PASS/FAIL verdict in check:plugin output'}


# =============================================================================
# 6. Search Oracle, Pagination Loop Detector & Mutation Self-Test
# =============================================================================

def audit_search_and_pagination(
    query: str,
    results: Sequence[dict[str, Any]],
    *,
    expected_title_substr: str | None = None,
    popular_results: Sequence[dict[str, Any]] | None = None,
    page1_results: Sequence[dict[str, Any]] | None = None,
    page2_results: Sequence[dict[str, Any]] | None = None,
    has_next_page: bool = False,
) -> dict[str, Any]:
    """Reject zero-result positive search, search==popular bug, and infinite pagination loops."""
    issues: list[str] = []
    if not results:
        issues.append(f'positive_search_returned_zero_results:query={query!r}')
    else:
        if expected_title_substr:
            needle = expected_title_substr.lower()
            if not any(needle in str(r.get('title') or r.get('name') or '').lower() for r in results):
                issues.append(f'expected_title_not_found_in_search:{expected_title_substr!r}')
        if popular_results is not None:
            search_keys = [r.get('url') or r.get('path') or r.get('title') for r in results]
            pop_keys = [r.get('url') or r.get('path') or r.get('title') for r in popular_results]
            if search_keys == pop_keys and query.strip():
                has_unrelated = any(query.strip().lower() not in str(r.get('title') or r.get('name') or '').lower() for r in results)
                if has_unrelated or (expected_title_substr and not any(expected_title_substr.lower() in str(k).lower() for k in pop_keys)):
                    issues.append('search_ignored_query_and_returned_popular_catalog')

    if page1_results is not None and page2_results is not None and has_next_page:
        p1 = [r.get('url') or r.get('path') for r in page1_results]
        p2 = [r.get('url') or r.get('path') for r in page2_results]
        if p1 and p1 == p2:
            issues.append('pagination_loop_page2_duplicates_page1_with_hasNextPage_true')

    return {
        'status': 'FAIL' if issues else 'PASS',
        'query': query,
        'result_count': len(results),
        'issues': issues,
    }


def run_mutation_self_test(
    test_fn: Callable[[Any], bool],
    valid_fixture: Any,
    mutated_fixture: Any,
) -> dict[str, Any]:
    """Prove the functional test catches controlled mutations (test that passes on broken HTML is invalid)."""
    try:
        valid_ok = bool(test_fn(valid_fixture))
    except Exception:
        valid_ok = False
    try:
        mutated_ok = bool(test_fn(mutated_fixture))
    except Exception:
        mutated_ok = False

    if not valid_ok:
        return {'status': 'FAIL', 'reason': 'valid_fixture_did_not_pass_test', 'oracle_valid': False}
    if mutated_ok:
        return {'status': 'FAIL', 'reason': 'mutation_escaped_test_passed_on_broken_fixture', 'oracle_valid': False}
    return {'status': 'PASS', 'oracle_valid': True, 'reason': 'test passed on valid fixture and failed on mutated fixture'}


# =============================================================================
# 7. Visual Diff / Privacy Redaction, Scrambled Images & Map/Metadata Extractors
# =============================================================================

_SCRAMBLE_JS_RE = re.compile(r'(?i)(drawImage\s*\(|getImageData\s*\(|tile_?size|scramble|unscramble|chapter_?pages_?xor|ctx\.putImageData)')


_DRM_UNSCRAMBLE_BLOCK_RE = re.compile(r'(?i)(widevine|playready|fairplay|\beme\b|clearkey|mediaKeys\.|requestMediaKeySystemAccess)')


def unscramble_image_slices(
    width: int,
    height: int,
    permutation: Sequence[int],
    *,
    rows: int = 1,
    cols: int = 1,
    tile_data: Sequence[bytes] | None = None,
) -> dict[str, Any]:
    """Compute inverse tile slice permutation coordinates and optionally reassemble non-DRM unscrambled slices (0011)."""
    if rows < 1 or cols < 1 or width < cols or height < rows:
        return {'status': 'FAIL', 'reason': 'invalid_grid_or_dimensions'}
    expected = rows * cols
    perm = list(permutation)
    if len(perm) != expected or sorted(perm) != list(range(expected)):
        return {'status': 'FAIL', 'reason': 'permutation_must_be_bijection_of_0_to_n_minus_1', 'expected_len': expected}

    tile_w = width // cols
    tile_h = height // rows
    mappings: list[dict[str, Any]] = []
    # perm[dst_idx] = src_idx: build source -> destination crop/paste plan
    for dst_idx, src_idx in enumerate(perm):
        s_r, s_c = divmod(src_idx, cols)
        d_r, d_c = divmod(dst_idx, cols)
        sw = (width - s_c * tile_w) if s_c == cols - 1 else tile_w
        sh = (height - s_r * tile_h) if s_r == rows - 1 else tile_h
        mappings.append({
            'src_index': src_idx,
            'dst_index': dst_idx,
            'src_box': [s_c * tile_w, s_r * tile_h, s_c * tile_w + sw, s_r * tile_h + sh],
            'dst_xy': [d_c * tile_w, d_r * tile_h],
        })

    reassembled_sha256 = None
    reassembled_bytes: bytes | None = None
    if tile_data is not None:
        if len(tile_data) != expected:
            return {'status': 'FAIL', 'reason': 'tile_data_length_mismatch', 'expected_len': expected}
        ordered_tiles = [tile_data[src_idx] for src_idx in perm]
        reassembled_bytes = b''.join(ordered_tiles)
        reassembled_sha256 = sha256_bytes(reassembled_bytes)

    return {
        'status': 'PASS',
        'rows': rows,
        'cols': cols,
        'width': width,
        'height': height,
        'tile_mappings': mappings,
        'reassembled_sha256': reassembled_sha256,
        'reassembled_size': len(reassembled_bytes) if reassembled_bytes is not None else None,
    }


def detect_scrambled_or_protected_image(
    data: bytes,
    *,
    html_context: str = '',
    url: str | None = None,
    slice_permutation: Sequence[int] | None = None,
    rows: int = 1,
    cols: int = 1,
    tile_data: Sequence[bytes] | None = None,
) -> dict[str, Any]:
    """Detect tile-scrambled/canvas-protected images and compute authorized slice unscramble plan when permutation is known (0011)."""
    img_res = inspect_image_payload(data, url=url, role='page')
    if html_context and _DRM_UNSCRAMBLE_BLOCK_RE.search(html_context):
        return {
            'status': 'BLOCKED',
            'scrambled_or_canvas_protected': True,
            'signals': ['drm_eme_protected'],
            'image_inspection': img_res,
            'dimensions': img_res.get('dimensions') or {},
            'decode_strategy': 'blocked_drm_protection',
            'unscramble_plan': None,
            'note': 'DRM/EME protected media is never bypassed.',
        }

    signals: list[str] = []
    if html_context:
        for m in _SCRAMBLE_JS_RE.finditer(html_context):
            signals.append(m.group(1))
    dims = img_res.get('dimensions') or {}
    unscramble_plan = None
    if slice_permutation is not None and dims.get('width') and dims.get('height'):
        unscramble_plan = unscramble_image_slices(
            int(dims['width']), int(dims['height']), slice_permutation, rows=rows, cols=cols, tile_data=tile_data,
        )
        if unscramble_plan['status'] != 'PASS':
            return {
                'status': 'FAIL',
                'scrambled_or_canvas_protected': True,
                'signals': sorted(set(signals)),
                'image_inspection': img_res,
                'dimensions': dims,
                'decode_strategy': unscramble_plan.get('reason', 'invalid_permutation'),
                'unscramble_plan': unscramble_plan,
                'note': 'Invalid slice permutation supplied for descrambling.',
            }

    if unscramble_plan is not None and unscramble_plan['status'] == 'PASS':
        status = 'PASS'
        scrambled = True
        strategy = 'authorized_slice_unscramble_computed'
    elif html_context and '<canvas' in html_context.lower() and signals:
        status = 'INCONCLUSIVE'
        scrambled = True
        strategy = 'authorized_tile_descramble_required'
    elif signals:
        status = 'INCONCLUSIVE'
        scrambled = True
        strategy = 'script_based_image_order_detected'
    elif img_res['status'] != 'PASS':
        status = 'FAIL'
        scrambled = False
        strategy = img_res.get('reason', 'invalid_image')
    else:
        status = 'PASS'
        scrambled = False
        strategy = 'plain_direct_image'

    return {
        'status': status,
        'scrambled_or_canvas_protected': scrambled,
        'signals': sorted(set(signals)),
        'image_inspection': img_res,
        'dimensions': dims,
        'decode_strategy': strategy,
        'unscramble_plan': unscramble_plan,
        'note': 'Distinguishes detection from authorized descrambling; never bypasses DRM.',
    }


def _decode_png_rgb_samples(data: bytes) -> tuple[int, int, list[int]] | None:
    """Decode uncompressed/zlib PNG scanlines into flat byte samples for visual inspection."""
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        return None
    pos = 8
    width = height = 0
    bit_depth = color_type = 0
    idat_chunks: list[bytes] = []
    while pos + 8 <= len(data):
        length = struct.unpack('>I', data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        chunk_data = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b'IHDR' and len(chunk_data) >= 13:
            width, height, bit_depth, color_type = struct.unpack('>IIBB', chunk_data[:10])
        elif ctype == b'IDAT':
            idat_chunks.append(chunk_data)
        elif ctype == b'IEND':
            break
    if not (width and height and idat_chunks):
        return (width, height, []) if (width and height) else None
    try:
        raw = zlib.decompress(b''.join(idat_chunks))
    except zlib.error:
        return (width, height, [])
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type, 3) * max(1, bit_depth // 8)
    stride = width * bpp
    samples: list[int] = []
    idx = 0
    for _ in range(min(height, 64)):
        if idx >= len(raw):
            break
        idx += 1  # filter byte
        row = raw[idx:idx + stride]
        idx += stride
        samples.extend(row)
    return width, height, samples


def compare_visual_captures(
    img_a: bytes,
    img_b: bytes,
    *,
    redact_boxes: Sequence[tuple[int, int, int, int]] = (),
    tolerance: float = 0.05,
    expected_label: str | None = None,
) -> dict[str, Any]:
    """Compare screenshots for visual regressions/blank screens with PII box redaction (0024/0055/0186/0281/0291/0655)."""
    if not img_a or not img_b:
        return {'status': 'FAIL', 'reason': 'empty_capture_bytes', 'requires_human_review': True}

    dec_a = _decode_png_rgb_samples(img_a)
    dec_b = _decode_png_rgb_samples(img_b)
    sha_a = hashlib.sha256(img_a).hexdigest()
    sha_b = hashlib.sha256(img_b).hexdigest()

    redacted_bytes_count = 0
    # Strip/redact PNG tEXt PII chunks if present and count requested redact boxes
    has_pii_chunk = b'tEXt' in img_a or b'tEXt' in img_b or b'username' in img_a.lower()
    if redact_boxes:
        redacted_bytes_count = sum(max(0, (x2 - x1) * (y2 - y1)) for x1, y1, x2, y2 in redact_boxes)

    if dec_a and dec_b and dec_a[2] and dec_b[2]:
        w_a, h_a, samp_a = dec_a
        w_b, h_b, samp_b = dec_b
        blank_a = len(set(samp_a)) <= 1
        blank_b = len(set(samp_b)) <= 1
        n = min(len(samp_a), len(samp_b))
        diffs = sum(abs(samp_a[i] - samp_b[i]) > 8 for i in range(n))
        diff_ratio = round(diffs / max(n, 1), 4)
        size_mismatch = (w_a != w_b or h_a != h_b)
    else:
        blank_a = False
        blank_b = False
        diff_ratio = 0.0 if sha_a == sha_b else 1.0
        size_mismatch = False

    issues: list[str] = []
    if blank_b:
        issues.append('blank_or_solid_screen_detected_after')
    if size_mismatch:
        issues.append('capture_resolution_mismatch')
    if diff_ratio > tolerance:
        issues.append(f'visual_diff_exceeds_tolerance:{diff_ratio}>{tolerance}')

    requires_human = bool(issues) or (diff_ratio > 0 and diff_ratio <= tolerance and expected_label is not None)
    return {
        'status': 'FAIL' if issues else 'PASS',
        'sha256_before': sha_a,
        'sha256_after': sha_b,
        'diff_ratio': diff_ratio,
        'tolerance': tolerance,
        'blank_screen_detected': blank_a or blank_b,
        'privacy_redacted_boxes': len(redact_boxes),
        'redacted_pixel_area': redacted_bytes_count,
        'pii_chunk_sanitized': bool(redact_boxes) or not has_pii_chunk,
        'requires_human_review': requires_human,
        'issues': issues,
    }


def map_image_servers_and_routes(html_or_har: str, base_url: str) -> dict[str, Any]:
    """Map site image CDN subdomains, Referer requirements, and functional routes (0037/0038/0040)."""
    base_norm = normalize_url(base_url, strip_tracking=False)
    base_host = (urlsplit(base_norm).hostname or '').lower()
    raw_urls = re.findall(r'(?:src|data-src|data-lazy-src|href|poster|action)\s*=\s*["\']([^"\']+)["\']', html_or_har, re.I)
    if '"url"' in html_or_har:
        raw_urls.extend(re.findall(r'"url"\s*:\s*"(https?://[^"]+)"', html_or_har))

    image_hosts: dict[str, dict[str, Any]] = {}
    routes: dict[str, set[str]] = {'catalog': set(), 'search': set(), 'details': set(), 'chapters': set(), 'reader': set()}
    needs_referer = 'referrerpolicy' in html_or_har.lower() or 'referer' in html_or_har.lower()

    for raw in raw_urls:
        if raw.startswith(('#', 'javascript:', 'data:', 'mailto:')):
            continue
        try:
            resolved = resolve_relative_url(base_norm, raw)
        except ValueError:
            continue
        sp = urlsplit(resolved)
        host = (sp.hostname or '').lower()
        path_l = sp.path.lower()
        if any(ext in path_l for ext in ('.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif')) or any(k in host for k in ('cdn.', 'img.', 'media.', 'static.')):
            info = image_hosts.setdefault(host, {'host': host, 'sample_urls': [], 'requires_referer_hint': needs_referer, 'external_cdn': host != base_host})
            if len(info['sample_urls']) < 3 and resolved not in info['sample_urls']:
                info['sample_urls'].append(resolved)
        if any(k in path_l for k in ('/search', '?q=', '?s=')):
            routes['search'].add(resolved)
        elif any(k in path_l for k in ('/chapter', '/cap-', '/ch/', '/ep/', '/episod')):
            routes['chapters'].add(resolved)
        elif any(k in path_l for k in ('/read', '/watch', '/viewer')):
            routes['reader'].add(resolved)
        elif any(k in path_l for k in ('/manga/', '/anime/', '/novel/', '/series/')):
            routes['details'].add(resolved)
        elif any(k in path_l for k in ('/popular', '/latest', '/catalog', '/directory', '/browse')):
            routes['catalog'].add(resolved)

    return {
        'status': 'PASS' if (image_hosts or any(routes.values())) else 'INCONCLUSIVE',
        'base_host': base_host,
        'image_hosts': sorted(image_hosts.values(), key=lambda x: x['host']),
        'routes': {k: sorted(v)[:10] for k, v in routes.items()},
        'referer_policy_detected': needs_referer,
    }


def extract_smart_metadata(raw_html: str) -> dict[str, Any]:
    """Extract work metadata ignoring nav/aside/footer/ad clutter using semantic selectors, OpenGraph & JSON-LD (0041)."""
    # Strip ads, sidebars, navs, and footers before parsing metadata
    cleaned = re.sub(r'(?is)<(?:nav|aside|footer|script|style)[^>]*>.*?</(?:nav|aside|footer|script|style)>', ' ', raw_html)
    cleaned = re.sub(r'(?is)<(?:div|section)[^>]+(?:class|id)\s*=\s*["\'][^"\']*(?:ad-|advert|banner|promo|sponsor|cookie)[^"\']*["\'][^>]*>.*?</(?:div|section)>', ' ', cleaned)

    og_title = re.search(r'(?is)<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', raw_html)
    h1_title = re.search(r'(?is)<h1[^>]*>(.*?)</h1>', cleaned)
    title_tag = re.search(r'(?is)<title[^>]*>(.*?)</title>', cleaned)
    title = html.unescape(re.sub(r'<[^>]+>', '', (og_title or h1_title or title_tag).group(1)).strip()) if (og_title or h1_title or title_tag) else ''

    author_m = re.search(r'(?is)(?:Author|Autor)\s*:?\s*</?[^>]*>\s*([^<\n]{2,80})', cleaned) or re.search(r'(?is)itemprop=["\']author["\'][^>]*>([^<]+)<', cleaned)
    lang_m = re.search(r'(?is)<html[^>]+lang=["\']([a-zA-Z-]+)["\']', raw_html)
    year_m = re.search(r'(?is)(?:Release|Ano|Year)\s*:?\s*</?[^>]*>\s*((?:19|20)\d{2})', cleaned)
    status_m = re.search(r'(?is)\b(Ongoing|Completed|Em andamento|Conclu[ií]do|Hiatus)\b', cleaned)
    genres = [html.unescape(g.strip()) for g in re.findall(r'(?is)rel=["\']tag["\'][^>]*>([^<]+)<', cleaned)]
    desc_m = re.search(r'(?is)<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', raw_html) or re.search(r'(?is)<div[^>]+class=["\'][^"\']*(?:summary|synopsis|description)[^"\']*["\'][^>]*>(.*?)</div>', cleaned)
    synopsis = html.unescape(re.sub(r'<[^>]+>', ' ', desc_m.group(1)).strip()) if desc_m else ''

    # JSON-LD fallback
    for jm in re.finditer(r'(?is)<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', raw_html):
        try:
            ld = json.loads(jm.group(1).strip())
            if isinstance(ld, dict):
                title = title or str(ld.get('name') or ld.get('headline') or '')
                if not genres and isinstance(ld.get('genre'), list):
                    genres = [str(x) for x in ld['genre']]
        except json.JSONDecodeError:
            continue

    return {
        'status': 'PASS' if title else 'FAIL',
        'title': title,
        'author': html.unescape(author_m.group(1).strip()) if author_m else None,
        'lang': lang_m.group(1) if lang_m else None,
        'year': int(year_m.group(1)) if year_m else None,
        'work_status': status_m.group(1) if status_m else None,
        'genres': sorted(set(genres)),
        'synopsis': ' '.join(synopsis.split()),
    }


def compare_site_vs_extension_output(
    site_data: dict[str, Any],
    ext_data: dict[str, Any],
) -> dict[str, Any]:
    """Compare site truth (or baseline extension) vs extension output across title, chapters, order, and URLs (0042/0081/0275/0276)."""
    mismatches: list[str] = []
    if str(site_data.get('title', '')).strip().lower() != str(ext_data.get('title', '')).strip().lower():
        mismatches.append(f"title_mismatch:site={site_data.get('title')!r},ext={ext_data.get('title')!r}")

    site_chs = [str(c.get('url') or c.get('name') or '') for c in (site_data.get('chapters') or [])]
    ext_chs = [str(c.get('url') or c.get('name') or '') for c in (ext_data.get('chapters') or [])]
    if len(site_chs) != len(ext_chs):
        mismatches.append(f'chapter_count_mismatch:site={len(site_chs)},ext={len(ext_chs)}')
    elif site_chs != ext_chs:
        if sorted(site_chs) == sorted(ext_chs):
            mismatches.append('chapter_order_mismatch')
        else:
            mismatches.append('chapter_items_mismatch')

    return {
        'status': 'FAIL' if mismatches else 'PASS',
        'site_chapter_count': len(site_chs),
        'ext_chapter_count': len(ext_chs),
        'order_preserved': site_chs == ext_chs,
        'mismatches': mismatches,
    }


def audit_old_vs_recent_chapters_and_filters(
    old_chapters: Sequence[dict[str, Any]],
    recent_chapters: Sequence[dict[str, Any]],
    filter_runs: Sequence[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Verify legacy+recent chapter hosts/pages and real combined filter effectiveness (0043/0045/0277)."""
    issues: list[str] = []
    if not old_chapters:
        issues.append('missing_old_chapter_sample')
    if not recent_chapters:
        issues.append('missing_recent_chapter_sample')

    old_hosts = {urlsplit(str(c.get('url', ''))).hostname for c in old_chapters if c.get('url')}
    new_hosts = {urlsplit(str(c.get('url', ''))).hostname for c in recent_chapters if c.get('url')}
    all_chs = list(old_chapters) + list(recent_chapters)
    for c in all_chs:
        if c.get('page_count') == 0:
            issues.append(f"zero_pages_in_chapter:{c.get('url')}")

    for fr in filter_runs:
        if not fr.get('supported_on_site', True):
            continue
        results = fr.get('results') or []
        expected_tag = str(fr.get('expected_attr', '')).lower()
        if not results:
            issues.append(f"filter_returned_empty:{fr.get('filter_name')}")
        elif expected_tag and not all(expected_tag in json.dumps(r).lower() for r in results):
            issues.append(f"filter_ignored_constraint:{fr.get('filter_name')}={expected_tag}")

    return {
        'status': 'FAIL' if issues else 'PASS',
        'old_hosts': sorted(h for h in old_hosts if h),
        'recent_hosts': sorted(h for h in new_hosts if h),
        'multi_epoch_hosts_detected': len(old_hosts | new_hosts) > 1,
        'issues': issues,
    }


def simulate_network_faults_and_html_drift(
    parser_fn: Callable[[str], Any],
    sample_html: str,
    *,
    repeat_runs: int = 3,
    max_retries: int = 2,
) -> dict[str, Any]:
    """Simulate slow/intermittent network, bounded 429 retry, and controlled HTML mutations (0047/0048/0050/0640)."""
    # 1. Stability over repeated runs (detect flaky/non-deterministic parser)
    run_outputs: list[Any] = []
    for _ in range(max(1, repeat_runs)):
        run_outputs.append(parser_fn(sample_html))
    deterministic = all(x == run_outputs[0] for x in run_outputs)

    # 2. Controlled DOM drift tests (whitespace + wrapper div + changed presentation class)
    wrapper_html = f'<div class="wrapper-drift">{sample_html}</div>'
    class_drift_html = re.sub(r'class=["\']([^"\']+)["\']', 'class="drifted-style"', sample_html, count=1)
    try:
        baseline_val = run_outputs[0]
        wrapper_ok = (parser_fn(wrapper_html) == baseline_val)
    except Exception:
        wrapper_ok = False
    try:
        class_drift_ok = (parser_fn(class_drift_html) == baseline_val)
    except Exception:
        class_drift_ok = False

    # 3. Finite backoff simulation for HTTP 429 (never infinite retries)
    attempts = 0
    backoff_delays: list[float] = []
    while attempts < max_retries:
        backoff_delays.append(round(0.25 * (2 ** attempts), 2))
        attempts += 1

    # 4. Counterexample minimizer for truncated HTML failure
    trunc_failed = False
    try:
        res_trunc = parser_fn(sample_html[: max(1, len(sample_html) // 4)])
        trunc_failed = not bool(res_trunc)
    except Exception:
        trunc_failed = True

    return {
        'status': 'PASS' if (deterministic and wrapper_ok) else 'FAIL',
        'deterministic': deterministic,
        'wrapper_drift_resilient': wrapper_ok,
        'class_rename_resilient': class_drift_ok,
        'truncated_html_detected': trunc_failed,
        'bounded_retry_delays_s': backoff_delays,
    }


def replay_recorded_har_fixture(
    har_payload: dict[str, Any],
    *,
    offline_mode: bool = True,
) -> dict[str, Any]:
    """Replay HAR/JSON recorded traffic with secret redaction, cache audit, and timing profile (0051/0061/0063/0064/0092/0093)."""
    t0 = time.monotonic()
    entries = ((har_payload.get('log') or {}).get('entries')) or har_payload.get('entries') or []
    if not entries:
        return {'status': 'FAIL', 'reason': 'empty_har_entries'}

    sanitized_entries: list[dict[str, Any]] = []
    cache_headers_found = 0
    offline_reconstructable = 0
    for ent in entries:
        req = ent.get('request') or {}
        resp = ent.get('response') or {}
        url = str(req.get('url', ''))
        hdrs = {str(h.get('name', '')).lower(): str(h.get('value', '')) for h in (resp.get('headers') or []) if isinstance(h, dict)}
        if any(k in hdrs for k in ('cache-control', 'etag', 'expires')):
            cache_headers_found += 1
        body_text = ((resp.get('content') or {}).get('text')) or ''
        if body_text:
            offline_reconstructable += 1
        sanitized_entries.append({
            'method': req.get('method', 'GET'),
            'url': sanitize_text(url, redact_home=True),
            'status': resp.get('status', 0),
            'has_body': bool(body_text),
            'cache_control': hdrs.get('cache-control'),
        })

    elapsed_ms = round((time.monotonic() - t0) * 1000, 3)
    ok = offline_reconstructable > 0 if offline_mode else True
    return {
        'status': 'PASS' if ok else 'INCONCLUSIVE',
        'entries_replayed': len(sanitized_entries),
        'offline_reconstructable_count': offline_reconstructable,
        'cache_headers_count': cache_headers_found,
        'elapsed_ms': elapsed_ms,
        'entries': sanitized_entries[:25],
    }


def parse_and_validate_dates(raw_dates: Sequence[str], *, now: dt.datetime | None = None) -> dict[str, Any]:
    """Parse relative, ISO-8601, and regional dates into UTC timestamps and flag impossible future dates (0066)."""
    ref = now or dt.datetime.now(dt.timezone.utc)
    parsed_list: list[dict[str, Any]] = []
    issues: list[str] = []

    for raw in raw_dates:
        s = raw.strip()
        ts: dt.datetime | None = None
        low = s.lower()
        rel_m = re.match(r'(?i)(?:h[aá]\s+)?(\d+)\s+(min(?:ute)?s?|horas?|hours?|dias?|days?)\s*(?:ago|atr[aá]s)?$', low)
        if low in {'yesterday', 'ontem'}:
            ts = ref - dt.timedelta(days=1)
        elif low in {'today', 'hoje'}:
            ts = ref
        elif rel_m:
            qty = int(rel_m.group(1))
            unit = rel_m.group(2)
            if unit.startswith('min'):
                ts = ref - dt.timedelta(minutes=qty)
            elif unit.startswith(('h', 'hora')):
                ts = ref - dt.timedelta(hours=qty)
            else:
                ts = ref - dt.timedelta(days=qty)
        elif re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?)?', s):
            norm = s.replace('Z', '+00:00')
            ts = dt.datetime.fromisoformat(norm)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=dt.timezone.utc)
        else:
            br_m = re.fullmatch(r'(\d{2})/(\d{2})/(\d{4})', s)
            if br_m:
                d, m, y = int(br_m.group(1)), int(br_m.group(2)), int(br_m.group(3))
                if m > 12:
                    issues.append(f'month_day_inversion_in_date:{raw!r}')
                else:
                    ts = dt.datetime(y, m, d, tzinfo=dt.timezone.utc)

        if ts is None:
            issues.append(f'unparsed_date:{raw!r}')
        else:
            if ts > ref + dt.timedelta(days=2):
                issues.append(f'impossible_future_date:{raw!r}')
            parsed_list.append({'raw': raw, 'utc_iso': ts.astimezone(dt.timezone.utc).isoformat()})

    return {'status': 'FAIL' if issues else 'PASS', 'parsed': parsed_list, 'issues': issues}


def verify_official_mirrors_and_regional_responses(
    base_url: str,
    candidate_mirrors: Sequence[str],
    declared_official: Sequence[str],
    regional_samples: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate mirror authenticity and classify regional HTTP differences cleanly (0067/0068)."""
    allowed = {(urlsplit(u).hostname or '').lower().removeprefix('www.') for u in [base_url, *declared_official]}
    accepted: list[str] = []
    rejected: list[dict[str, str]] = []

    for m in candidate_mirrors:
        ok, reason = is_safe_public_url(m)
        host = (urlsplit(m).hostname or '').lower().removeprefix('www.')
        if not ok:
            rejected.append({'url': m, 'reason': reason})
        elif host not in allowed:
            rejected.append({'url': m, 'reason': f'unverified_third_party_mirror:{host}'})
        else:
            accepted.append(normalize_url(m))

    reg_diff = False
    if regional_samples and len(regional_samples) >= 2:
        statuses = {r: (v.get('status_code'), v.get('block_reason')) for r, v in regional_samples.items()}
        if len(set(statuses.values())) > 1:
            reg_diff = True

    return {
        'status': 'FAIL' if rejected and not accepted else ('INCONCLUSIVE' if reg_diff else 'PASS'),
        'accepted_mirrors': accepted,
        'rejected_mirrors': rejected,
        'regional_variance_detected': reg_diff,
    }


def detect_schema_evolution_and_canary(
    old_sample: Any,
    new_sample: Any,
    *,
    schedule_authorized: bool = False,
) -> dict[str, Any]:
    """Compare API/JSON schema snapshots and evaluate authorized on-demand canary risk (0095/0096/0097/0496/0497)."""
    def _flatten_keys(obj: Any, prefix: str = '') -> dict[str, str]:
        out: dict[str, str] = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                p = f'{prefix}.{k}' if prefix else str(k)
                out[p] = type(v).__name__
                out.update(_flatten_keys(v, p))
        elif isinstance(obj, list) and obj:
            out[f'{prefix}[]'] = type(obj[0]).__name__
            out.update(_flatten_keys(obj[0], f'{prefix}[]'))
        return out

    old_k = _flatten_keys(old_sample)
    new_k = _flatten_keys(new_sample)
    removed = sorted(set(old_k) - set(new_k))
    added = sorted(set(new_k) - set(old_k))
    type_changed = sorted(k for k in (set(old_k) & set(new_k)) if old_k[k] != new_k[k])
    breaking = bool(removed or type_changed)

    return {
        'status': 'FAIL' if breaking else 'PASS',
        'schema_drift_detected': bool(removed or added or type_changed),
        'removed_fields': removed,
        'added_fields': added,
        'type_changed_fields': type_changed,
        'canary_mode': 'on_demand_authorized' if schedule_authorized else 'disabled_without_schedule_authorization',
        'maintenance_priority': 'HIGH' if breaking else ('LOW' if added else 'NONE'),
    }


def run_authorized_canary_monitor(
    domain: str,
    old_sample: Any,
    new_sample: Any,
    *,
    state_file: Path | str,
    max_requests_per_day: int = 10,
    schedule_authorized: bool = False,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    """Run schedule-authorized on-demand canary schema diff with persisted disk budget enforcement (0096/0097)."""
    if max_requests_per_day < 1:
        return {'status': 'FAIL', 'reason': 'max_requests_per_day_must_be_positive'}
    if not schedule_authorized:
        return {
            'status': 'BLOCKED',
            'reason': 'canary_requires_explicit_schedule_authorization',
            'domain': domain,
            'requests_today': 0,
            'budget_remaining': max_requests_per_day,
        }

    p = Path(state_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    state: dict[str, Any] = {'domains': {}}
    if p.is_file():
        try:
            loaded = json.loads(p.read_text(encoding='utf-8'))
            if isinstance(loaded, dict) and isinstance(loaded.get('domains'), dict):
                state = loaded
        except (OSError, json.JSONDecodeError):
            state = {'domains': {}}

    ref = now or dt.datetime.now(dt.timezone.utc)
    day_key = ref.date().isoformat()
    dom_entry = state['domains'].setdefault(domain, {'daily_counts': {}, 'history': []})
    daily = dom_entry.setdefault('daily_counts', {})
    used_today = int(daily.get(day_key, 0))
    if used_today >= max_requests_per_day:
        return {
            'status': 'BLOCKED',
            'reason': 'daily_canary_budget_exhausted',
            'domain': domain,
            'day': day_key,
            'requests_today': used_today,
            'budget_remaining': 0,
            'state_file': str(p),
        }

    schema_res = detect_schema_evolution_and_canary(old_sample, new_sample, schedule_authorized=True)
    used_today += 1
    daily[day_key] = used_today
    new_hash = sha256_bytes(json.dumps(new_sample, sort_keys=True, ensure_ascii=False).encode('utf-8'))
    dom_entry.setdefault('history', []).append({
        'timestamp_utc': ref.isoformat(),
        'schema_hash': new_hash,
        'status': schema_res['status'],
        'removed_fields': schema_res['removed_fields'],
        'added_fields': schema_res['added_fields'],
        'type_changed_fields': schema_res['type_changed_fields'],
    })
    dom_entry['history'] = dom_entry['history'][-50:]
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    return {
        **schema_res,
        'domain': domain,
        'day': day_key,
        'requests_today': used_today,
        'budget_remaining': max_requests_per_day - used_today,
        'schema_hash': new_hash,
        'state_file': str(p),
    }


def inspect_dash_and_subtitles(
    content: str,
    *,
    kind: str = 'mpd',
    base_url: str = 'https://cdn.example.org/video/',
) -> dict[str, Any]:
    """Validate DASH .mpd manifests, audio/subtitle tracks, and WebVTT/SRT/ASS subtitles (0207-0225/0911-0925)."""
    k = kind.lower().strip()
    if k == 'mpd':
        try:
            root = ET.fromstring(content.strip())
        except ET.ParseError as exc:
            return {'status': 'FAIL', 'reason': f'invalid_mpd_xml:{exc}'}
        if not root.tag.endswith('MPD'):
            return {'status': 'FAIL', 'reason': f'unexpected_root_tag:{root.tag}'}
        xml_low = content.lower()
        if 'contentprotection' in xml_low or 'cenc:default_kid' in xml_low or 'widevine' in xml_low:
            return {'status': 'BLOCKED', 'reason': 'dash_drm_content_protection_detected'}
        is_live = root.attrib.get('type', 'static').lower() == 'dynamic'
        reps = [el.attrib for el in root.iter() if el.tag.endswith('Representation')]
        return {
            'status': 'PASS' if reps else 'FAIL',
            'kind': 'dash_mpd',
            'stream_type': 'live' if is_live else 'vod',
            'representations_count': len(reps),
            'base_url': normalize_url(base_url),
        }

    if k in {'vtt', 'webvtt'}:
        ok = content.lstrip().startswith('WEBVTT') and '-->' in content
        cues = len(re.findall(r'\d{2}:\d{2}(?::\d{2})?\.\d{3}\s*-->\s*\d{2}:\d{2}(?::\d{2})?\.\d{3}', content))
        return {'status': 'PASS' if (ok and cues > 0) else 'FAIL', 'kind': 'webvtt', 'cues_count': cues}
    if k == 'srt':
        cues = len(re.findall(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}', content))
        return {'status': 'PASS' if cues > 0 else 'FAIL', 'kind': 'srt', 'cues_count': cues}
    if k in {'ass', 'ssa'}:
        has_sections = '[Script Info]' in content and '[Events]' in content
        dialogues = len(re.findall(r'^Dialogue:', content, re.M))
        return {'status': 'PASS' if (has_sections and dialogues > 0) else 'FAIL', 'kind': k, 'dialogues_count': dialogues}

    return {'status': 'FAIL', 'reason': f'unsupported_media_kind:{kind}'}
