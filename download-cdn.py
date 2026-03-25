#!/usr/bin/env python3
"""
download-cdn.py
Downloads all cdn.myportfolio.com assets from the live austinroberthermann.com site.
Fetches each live page to get fresh signed ?h= URLs, deduplicates by UUID keeping
highest-resolution version, and saves to organized local folders.

Usage: python3 download-cdn.py
"""

import re
import os
import time
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs

BASE_URL = "https://austinroberthermann.com"
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Map page slug → local save folder
# Photo gallery pages go into Images-* for use by build-galleries.py
# Other pages go into assets/{slug}/
PAGE_FOLDER_MAP = {
    # Photography pages
    "nature":                 "assets/photography/nature",
    "article-one":            "assets/photography/article-one",
    "2021-2025":              "assets/photography/2021-2025",
    "2016-2020":              "assets/photography/2016-2020",
    "2011-2015":              "assets/photography/2011-2015",
    "2000-2010":              "assets/photography/2000-2010",
    # Building/Other pages
    "deardorff":              "assets/building/deardorff",
    "chromogenic-process":    "assets/building/chromogenic-process",
    "durst-printo":           "assets/building/durst-printo",
    "sunvisor":               "assets/building/sunvisor",
    # Motion pages
    "sanjam":                 "assets/motion/sanjam",
    "all-kinds-of-planes":    "assets/motion/all-kinds-of-planes",
    "all-kinds-of-cars":      "assets/motion/all-kinds-of-cars",
    "magic-tricks":           "assets/motion/magic-tricks",
    "figure-03-volcanos":     "assets/motion/figure-03-volcanos",
    "figure-02-earths-layers":"assets/motion/figure-02-earths-layers",
    "figure-01-limestone-cave":"assets/motion/figure-01-limestone-cave",
    "working-in-teams":       "assets/motion/working-in-teams",
    "google-dots":            "assets/motion/google-dots",
    "fp-blend":               "assets/motion/fp-blend",
    "demyulederby":           "assets/motion/demyulederby",
    "poo-power":              "assets/motion/poo-power",
    "fashion":                "assets/motion/fashion",
}

CDN_PATTERN = re.compile(
    r'(https://cdn\.myportfolio\.com/[a-f0-9]+/[a-f0-9-]+(?:_rw_\d+|_carw_[\dx]+)?\.(?:jpg|jpeg|gif|png)(?:\?h=[a-f0-9]+)?)',
    re.IGNORECASE
)

# UUID extraction: match the UUID portion of the filename
UUID_PATTERN = re.compile(r'/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', re.IGNORECASE)

def get_resolution_score(url):
    """Returns a sort key for resolution — higher is better."""
    # JPG variants: _rw_600, _rw_1200, _rw_1920, _rw_3840
    m = re.search(r'_rw_(\d+)', url)
    if m:
        return int(m.group(1))
    # GIF variants: _carw_5x4x32, _carw_5x4x64, ..., _carw_5x4x2560
    m = re.search(r'_carw_\w+x(\d+)', url)
    if m:
        return int(m.group(1))
    # No size suffix → treat as moderate
    return 500

def fetch_page(slug):
    """Fetches the live page and returns HTML content."""
    url = f"{BASE_URL}/{slug}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} fetching /{slug}")
        return ""
    except Exception as e:
        print(f"  Error fetching /{slug}: {e}")
        return ""

def extract_cdn_urls(html):
    """Extract all CDN URLs from HTML, dedup by UUID keeping highest-res."""
    raw_urls = CDN_PATTERN.findall(html)

    # Also catch URLs that might be in JS strings without quotes issues
    # Try a broader pattern for any cdn URL
    broader = re.findall(r'https://cdn\.myportfolio\.com/[^\s"\'<>]+', html)
    for u in broader:
        if u not in raw_urls and 'cdn.myportfolio.com' in u:
            raw_urls.append(u)

    # Dedup by UUID, keep highest resolution
    by_uuid = {}
    for url in raw_urls:
        m = UUID_PATTERN.search(url)
        if not m:
            continue
        uuid = m.group(1).lower()
        score = get_resolution_score(url)
        if uuid not in by_uuid or score > by_uuid[uuid][1]:
            by_uuid[uuid] = (url, score)

    return [v[0] for v in by_uuid.values()]

def get_local_filename(url):
    """Derive a clean local filename from a CDN URL."""
    path = urlparse(url).path
    filename = os.path.basename(path)
    # Remove query string if present (shouldn't be in path, but just in case)
    filename = filename.split('?')[0]
    return filename

def download_file(url, dest_path):
    """Download a single file. Returns True on success."""
    if os.path.exists(dest_path):
        return None  # Already exists, skip

    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(dest_path, 'wb') as f:
            f.write(data)
        return True
    except urllib.error.HTTPError as e:
        print(f"    HTTP {e.code}: {url}")
        return False
    except Exception as e:
        print(f"    Error: {e} — {url}")
        return False

def main():
    total_downloaded = 0
    total_skipped = 0
    total_failed = 0

    for slug, folder_rel in PAGE_FOLDER_MAP.items():
        folder_abs = os.path.join(REPO_ROOT, folder_rel)
        os.makedirs(folder_abs, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"/{slug}  →  {folder_rel}/")
        print(f"  Fetching live page...")

        html = fetch_page(slug)
        if not html:
            print(f"  ⚠️  Could not fetch page, skipping.")
            continue

        urls = extract_cdn_urls(html)
        print(f"  Found {len(urls)} unique CDN assets")

        if not urls:
            print(f"  (no CDN assets found on this page)")
            continue

        page_downloaded = 0
        page_skipped = 0
        page_failed = 0

        for url in urls:
            filename = get_local_filename(url)
            dest = os.path.join(folder_abs, filename)
            result = download_file(url, dest)

            if result is True:
                page_downloaded += 1
                total_downloaded += 1
                print(f"    ✓ {filename}")
            elif result is None:
                page_skipped += 1
                total_skipped += 1
            else:
                page_failed += 1
                total_failed += 1

            # Small delay to be polite to the CDN
            if result is True:
                time.sleep(0.1)

        print(f"  → Downloaded: {page_downloaded}, Skipped (exists): {page_skipped}, Failed: {page_failed}")

    print(f"\n{'='*60}")
    print(f"DONE")
    print(f"Total downloaded: {total_downloaded}")
    print(f"Total skipped (already existed): {total_skipped}")
    print(f"Total failed: {total_failed}")

if __name__ == "__main__":
    main()
