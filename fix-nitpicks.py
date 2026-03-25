#!/usr/bin/env python3
"""
fix-nitpicks.py
Applies 7 targeted sitewide fixes to the portfolio.

Run: python3 fix-nitpicks.py
"""

import os
import re
import glob

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
HTML_FILES = sorted(glob.glob(os.path.join(REPO_ROOT, '*.html')))


# ---------------------------------------------------------------------------
# Fix 1: Remove visitor counter + last-updated footer div from all pages
# ---------------------------------------------------------------------------
def remove_footer_counter(content):
    search_str = 'border-top: 2px solid #000000'
    start = 0
    while True:
        idx = content.find(search_str, start)
        if idx == -1:
            break
        # Walk back to the opening <div
        div_start = content.rfind('<div', 0, idx)
        if div_start == -1:
            start = idx + 1
            continue
        # Find matching closing </div> via depth counter
        depth = 0
        i = div_start
        div_end = -1
        while i < len(content):
            if content[i:i+4] == '<div':
                depth += 1
                i += 4
            elif content[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    div_end = i + 6
                    break
                i += 6
            else:
                i += 1
        if div_end == -1:
            start = idx + 1
            continue
        div_content = content[div_start:div_end]
        if 'visitors' in div_content and 'last updated' in div_content:
            # Strip leading whitespace/newline before the div
            pre = div_start
            while pre > 0 and content[pre - 1] in ' \t':
                pre -= 1
            if pre > 0 and content[pre - 1] == '\n':
                pre -= 1
            content = content[:pre] + content[div_end:]
        else:
            start = div_end
    return content


# ---------------------------------------------------------------------------
# Fix 2: Add hits.seeyoufarm.com counter to contact.html
# ---------------------------------------------------------------------------
HITS_BADGE = (
    '\n              <div style="margin-top: 20px;">'
    '\n                <a href="https://hits.seeyoufarm.com">'
    '\n                  <img'
    '\n                    src="https://hits.seeyoufarm.com/api/count/incr/badge.svg'
    '?url=https%3A%2F%2Faustinroberthermann.com'
    '&amp;count_bg=%23000080&amp;title_bg=%23c0c0c0'
    '&amp;icon=&amp;icon_color=%23E7E7E7&amp;title=visitors&amp;edge_flat=false"'
    '\n                    style="image-rendering: pixelated; -webkit-font-smoothing: none;"'
    '\n                  />'
    '\n                </a>'
    '\n              </div>'
)

def add_hits_counter(content):
    # After fix 1 the footer div is gone; insert badge before </td> that closes content cell
    marker = '</table>\n            </td>'
    if marker in content:
        content = content.replace(marker, '</table>' + HITS_BADGE + '\n            </td>', 1)
    return content


# ---------------------------------------------------------------------------
# Fix 3: Remove fashion nav <li> blocks; replace fashion <td> in index.html
# ---------------------------------------------------------------------------
FASHION_LI_RE = re.compile(
    r'\s*<li style="margin: 0; padding: 0">\s*<a\s+href="fashion\.html"[\s\S]*?</li>',
    re.DOTALL
)

FASHION_TD_OLD = '''\
                  <td style="width: 25%; vertical-align: top; padding: 0">
                    <a
                      href="fashion.html"
                      style="
                        display: block;
                        text-decoration: none;
                        color: #000000;
                        border: 2px solid;
                        border-color: #808080 #fff #fff #808080;
                        background: #b8b8b8;
                        overflow: hidden;
                      "
                    >
                      <div style="aspect-ratio: 5/4; background: #b8b8b8"></div>
                      <div
                        style="
                          font-size: 14px;
                          padding: 3px 5px;
                          border-top: 1px solid #a0a0a0;
                          background: #c0c0c0;
                          white-space: nowrap;
                          overflow: hidden;
                          text-overflow: ellipsis;
                        "
                      >
                        fashion
                      </div>
                    </a>
                  </td>'''

FASHION_TD_NEW = '                  <td></td>'

def remove_fashion(content, is_index=False):
    content = FASHION_LI_RE.sub('', content)
    if is_index:
        content = content.replace(FASHION_TD_OLD, FASHION_TD_NEW)
    return content


# ---------------------------------------------------------------------------
# Fix 4: Move magic-tricks <li> to after figure-01 <li>
# ---------------------------------------------------------------------------
MT_LI_RE = re.compile(
    r'(\s*<li style="margin: 0; padding: 0">\s*<a\s+href="magic-tricks\.html"[\s\S]*?</li>)',
    re.DOTALL
)
F01_LI_RE = re.compile(
    r'(<li style="margin: 0; padding: 0">\s*<a\s+href="figure-01-limestone-cave\.html"[\s\S]*?</li>)',
    re.DOTALL
)

def reorder_magic_tricks(content):
    m = MT_LI_RE.search(content)
    if not m:
        return content
    mt_block = m.group(1)
    content = content[:m.start()] + content[m.end():]
    m2 = F01_LI_RE.search(content)
    if not m2:
        return content
    content = content[:m2.end()] + mt_block + content[m2.end():]
    return content


# ---------------------------------------------------------------------------
# Fix 5: sound.html — activate BUILDING/OTHER link, remove OTHER duplicate
# ---------------------------------------------------------------------------

# Entire <li> block in BUILDING/OTHER (plain, non-active) — replace with active
SOUND_PLAIN_LI = (
    '                  <li style="margin: 0; padding: 0">\n'
    '                    <a\n'
    '                      href="sound.html"\n'
    '                      style="\n'
    '                        font-size: 15px;\n'
    '                        color: #00008b;\n'
    '                        text-decoration: underline;\n'
    '                        display: block;\n'
    '                        padding: 0 0 1px 6px;\n'
    '                        line-height: 1.6;\n'
    '                      "\n'
    '                      >music/audio</a\n'
    '                    >\n'
    '                  </li>'
)

SOUND_ACTIVE_LI = (
    '                  <li style="margin: 0; padding: 0">\n'
    '                    <a\n'
    '                      href="sound.html"\n'
    '                      style="\n'
    '                        font-size: 15px;\n'
    '                        color: #000000;\n'
    '                        text-decoration: none;\n'
    '                        display: block;\n'
    '                        padding: 0 0 1px 3px;\n'
    '                        line-height: 1.6;\n'
    '                        font-weight: bold;\n'
    '                        background: #d0d0c8;\n'
    '                        border-left: 3px solid #000000;\n'
    '                      "\n'
    '                      >music/audio</a\n'
    '                    >\n'
    '                  </li>'
)

# Entire <li> block in OTHER (active-styled duplicate) — remove entirely
SOUND_OTHER_DUP_LI = (
    '                  <li style="margin: 0; padding: 0">\n'
    '                    <a\n'
    '                      href="sound.html"\n'
    '                      style="\n'
    '                        font-size: 15px;\n'
    '                        color: #000000;\n'
    '                        text-decoration: none;\n'
    '                        display: block;\n'
    '                        padding: 0 0 1px 3px;\n'
    '                        line-height: 1.6;\n'
    '                        font-weight: bold;\n'
    '                        background: #d0d0c8;\n'
    '                        border-left: 3px solid #000000;\n'
    '                      "\n'
    '                      >music/audio</a\n'
    '                    >\n'
    '                  </li>'
)

def fix_sound_nav(content):
    # Remove the OTHER section duplicate first (exact match on original content)
    content = content.replace('\n' + SOUND_OTHER_DUP_LI, '', 1)
    # Then activate the BUILDING/OTHER link
    content = content.replace(SOUND_PLAIN_LI, SOUND_ACTIVE_LI, 1)
    return content


# ---------------------------------------------------------------------------
# Fix 6: index.html — fix broken magic tricks gif src
# ---------------------------------------------------------------------------
BROKEN_GIF = 'assets/motion/magic-tricks/7d50e43c-e773-491c-89fa-cc990f13da2c_car_5x4.gif'
FIXED_GIF  = 'assets/motion/magic-tricks/bcf65247-c3f3-4e47-b57a-1a4182dee9d0_rw_600.gif'

def fix_index_magic_gif(content):
    return content.replace(BROKEN_GIF, FIXED_GIF)


# ---------------------------------------------------------------------------
# Fix 7: photography-hub.html — fix dead links and year labels
# ---------------------------------------------------------------------------
PHUB_FIXES = [
    # href fixes
    ('href="2020.html"',     'href="2021-2025.html"'),
    ('href="2019-1.html"',   'href="2016-2020.html"'),
    ('href="2000-2017.html"','href="2000-2010.html"'),
    # alt fixes
    ('alt="2020\u20132021"', 'alt="2021\u20132025"'),
    ('alt="2018\u20132019"', 'alt="2016\u20132020"'),
    ('alt="2011\u20132017"', 'alt="2011\u20132015"'),
    ('alt="2006\u20132010"', 'alt="2000\u20132010"'),
    # label text fixes (surrounded by newlines + spaces)
    ('                        2020\u20132021\n', '                        2021\u20132025\n'),
    ('                        2018\u20132019\n', '                        2016\u20132020\n'),
    ('                        2011\u20132017\n', '                        2011\u20132015\n'),
    ('                        2006\u20132010\n', '                        2000\u20132010\n'),
]

def fix_photography_hub(content):
    for old, new in PHUB_FIXES:
        content = content.replace(old, new)
    return content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print('fix-nitpicks.py\n')

    changed = []
    skipped = []

    for path in HTML_FILES:
        fname = os.path.basename(path)
        if fname == 'fashion.html':
            continue  # will be deleted separately

        with open(path, 'r', encoding='utf-8') as f:
            original = f.read()

        content = original
        content = remove_footer_counter(content)
        content = remove_fashion(content, is_index=(fname == 'index.html'))
        content = reorder_magic_tricks(content)

        if fname == 'sound.html':
            content = fix_sound_nav(content)

        if fname == 'index.html':
            content = fix_index_magic_gif(content)

        if fname == 'contact.html':
            content = add_hits_counter(content)

        if fname == 'photography-hub.html':
            content = fix_photography_hub(content)

        if content != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            changed.append(fname)
            print(f'  ✓ {fname}')
        else:
            skipped.append(fname)

    print(f'\n{len(changed)} files updated, {len(skipped)} unchanged.')

    # Fix 3: remove fashion entry from download-cdn.py
    cdn_path = os.path.join(REPO_ROOT, 'download-cdn.py')
    with open(cdn_path, 'r', encoding='utf-8') as f:
        cdn = f.read()
    cdn_new = re.sub(r'\n    "fashion":\s*"assets/motion/fashion",?', '', cdn)
    if cdn_new != cdn:
        with open(cdn_path, 'w', encoding='utf-8') as f:
            f.write(cdn_new)
        print('  ✓ download-cdn.py: fashion entry removed')

    print('\nNext: delete fashion.html')
    print('  rm fashion.html')
    print('\nDone.')


if __name__ == '__main__':
    main()
