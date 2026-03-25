#!/usr/bin/env python3
"""
Remove text-decoration: underline from nav section headers (MOTION, PHOTOGRAPHY, BUILDING/OTHER)
and rename BUILDING/OTHER → BUILDING sitewide.
"""
import os, glob

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
HTML_FILES = sorted(glob.glob(os.path.join(REPO_ROOT, '*.html')))

OLD_STYLE = (
    '                    color: #00008b;\n'
    '                    text-decoration: underline;\n'
    '                    border-bottom: 1px solid #a0a0a0;\n'
)
NEW_STYLE = (
    '                    color: #00008b;\n'
    '                    border-bottom: 1px solid #a0a0a0;\n'
)

n_changed = 0
for path in HTML_FILES:
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()
    content = original
    content = content.replace(OLD_STYLE, NEW_STYLE)
    content = content.replace('>BUILDING/OTHER</a', '>BUILDING</a')
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        n_changed += 1
        print(f'  ✓ {os.path.basename(path)}')

print(f'\n{n_changed} files changed.')
