#!/usr/bin/env python3
"""
fix-batch2.py
Batch 2 sitewide nav fixes:
  1. Remove deardorff/darkroom <li> from all pages
  2. Rename "plants" → "fauna" in photography nav
  3. Move "article one" above "2021-2025" in photography nav
  4. Add portraits / huron / dream cruise nav items after fauna
"""

import os, re, glob

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
HTML_FILES = sorted(glob.glob(os.path.join(REPO_ROOT, '*.html')))

# ---------------------------------------------------------------------------
# Helper: standard non-active nav <li>
# ---------------------------------------------------------------------------
def nav_li(href, label):
    return (
        '\n                  <li style="margin: 0; padding: 0">'
        '\n                    <a'
        f'\n                      href="{href}"'
        '\n                      style="'
        '\n                        font-size: 15px;'
        '\n                        color: #00008b;'
        '\n                        text-decoration: underline;'
        '\n                        display: block;'
        '\n                        padding: 0 0 1px 6px;'
        '\n                        line-height: 1.6;'
        '\n                      "'
        f'\n                      >{label}</a'
        '\n                    >'
        '\n                  </li>'
    )

NEW_PHOTO_ITEMS = (
    nav_li('portraits.html', 'portraits') +
    nav_li('huron.html', 'huron') +
    nav_li('dream-cruise.html', 'dream cruise')
)

# ---------------------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------------------
DEARDORFF_RE = re.compile(
    r'\s*<li style="margin: 0; padding: 0">\s*<a\s+href="deardorff\.html"[\s\S]*?</li>',
    re.DOTALL
)

# Captures article-one <li> regardless of active/non-active styling
ARTICLE_ONE_RE = re.compile(
    r'(\s*<li[^>]*>\s*<a\s+href="article-one\.html"[\s\S]*?</li>)',
    re.DOTALL
)

# Anchor: the 2021-2025 <li> opening (used for insertion point)
YEAR_2021_ANCHOR = (
    '\n                  <li style="margin: 0; padding: 0">'
    '\n                    <a'
    '\n                      href="2021-2025.html"'
)

# ---------------------------------------------------------------------------
def process(content, fname):
    changed = False

    # 1. Remove deardorff
    new = DEARDORFF_RE.sub('', content)
    if new != content:
        content = new
        changed = True

    # 2. plants → fauna
    if '>plants</a' in content:
        content = content.replace('>plants</a', '>fauna</a')
        changed = True

    # 3+4. Move article one above 2021-2025 and insert new items
    if YEAR_2021_ANCHOR in content:
        # Extract article one block (may or may not be present if already moved)
        m = ARTICLE_ONE_RE.search(content)
        if m:
            article_block = m.group(1)   # includes leading \n + spaces
            # Remove article one from current position
            content = content[:m.start()] + content[m.end():]
            changed = True
        else:
            article_block = nav_li('article-one.html', 'article one')

        # Insert: new items + article one BEFORE 2021-2025
        idx = content.find(YEAR_2021_ANCHOR)
        if idx != -1:
            insert = NEW_PHOTO_ITEMS + article_block
            content = content[:idx] + insert + content[idx:]
            changed = True

    return content, changed


def main():
    print('fix-batch2.py\n')
    n_changed = 0
    with open(os.path.join(REPO_ROOT, 'fix-batch2.log'), 'w') as log:
        for path in HTML_FILES:
            fname = os.path.basename(path)
            with open(path, 'r', encoding='utf-8') as f:
                original = f.read()
            content, changed = process(original, fname)
            if changed:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                n_changed += 1
                log.write(f'CHANGED: {fname}\n')
                print(f'  ✓ {fname}')
            else:
                log.write(f'unchanged: {fname}\n')
        log.write(f'\nTotal changed: {n_changed}\n')
    print(f'\n{n_changed} files changed. Log: fix-batch2.log')


if __name__ == '__main__':
    main()
