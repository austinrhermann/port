#!/usr/bin/env python3
"""
Create portraits.html, huron.html, dream-cruise.html from nature.html template.
For each new page:
  1. Update <title> tag
  2. Deactivate nature.html nav link → plain link
  3. Activate the new page's nav link → bold/highlight
  4. Update gallery-title text
  5. Clear gallery-desc
  6. Reset photo-grid to empty placeholder
  7. Reset lb to placeholder (build-galleries.py will regenerate)
"""

import os, re

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

PAGES = [
    ("portraits.html",    "Portraits"),
    ("huron.html",        "Huron"),
    ("dream-cruise.html", "Dream Cruise"),
]

ACTIVE_STYLE = (
    'style="\n'
    '                        font-size: 15px;\n'
    '                        color: #000000;\n'
    '                        text-decoration: none;\n'
    '                        display: block;\n'
    '                        padding: 0 0 1px 3px;\n'
    '                        line-height: 1.6;\n'
    '                        font-weight: bold;\n'
    '                        background: #d0d0c8;\n'
    '                        border-left: 3px solid #000000;\n'
    '                      "'
)

INACTIVE_STYLE = (
    'style="\n'
    '                        font-size: 15px;\n'
    '                        color: #00008b;\n'
    '                        text-decoration: underline;\n'
    '                        display: block;\n'
    '                        padding: 0 0 1px 6px;\n'
    '                        line-height: 1.6;\n'
    '                      "'
)

EMPTY_GRID = '<table id="photo-grid" style="width:100%;border-collapse:separate;border-spacing:6px;margin-top:10px;"><tr><td colspan="6" style="padding:20px;text-align:center;color:#808080;font-size:14px;border:2px solid;border-color:#808080 #fff #fff #808080;background:#b8b8b0;">No photos yet \u2014 add images to this folder and run build-galleries.py</td></tr></table>'

EMPTY_LB = '<div id="lb" class="lb-window" style="display:none"></div>'

with open(os.path.join(REPO_ROOT, 'nature.html'), 'r', encoding='utf-8') as f:
    template = f.read()

for filename, title in PAGES:
    html = template

    # 1. Update <title>
    html = re.sub(
        r'(<title>\s*)http://www\.austinroberthermann\.com/nature\.html(.*?</title>)',
        lambda m: m.group(1) + f'http://www.austinroberthermann.com/{filename}' + m.group(2),
        html,
        flags=re.DOTALL
    )

    # 2. Deactivate nature.html nav link
    html = html.replace(
        'href="nature.html"\n'
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
        '                      >fauna</a',
        'href="nature.html"\n'
        '                      style="\n'
        '                        font-size: 15px;\n'
        '                        color: #00008b;\n'
        '                        text-decoration: underline;\n'
        '                        display: block;\n'
        '                        padding: 0 0 1px 6px;\n'
        '                        line-height: 1.6;\n'
        '                      "\n'
        '                      >fauna</a'
    )

    # 3. Activate this page's nav link
    label = title.lower()
    html = html.replace(
        f'href="{filename}"\n'
        '                      style="\n'
        '                        font-size: 15px;\n'
        '                        color: #00008b;\n'
        '                        text-decoration: underline;\n'
        '                        display: block;\n'
        '                        padding: 0 0 1px 6px;\n'
        '                        line-height: 1.6;\n'
        '                      "\n'
        f'                      >{label}</a',
        f'href="{filename}"\n'
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
        f'                      >{label}</a'
    )

    # 4. Update gallery-title
    html = re.sub(
        r'(<div\s+id="gallery-title"[^>]*>\s*)Fauna(\s*</div>)',
        lambda m: m.group(1) + title + m.group(2),
        html,
        flags=re.DOTALL
    )

    # 5. Clear gallery-desc
    html = re.sub(
        r'(<div\s+id="gallery-desc"[^>]*>)[\s\S]*?(</div>)',
        lambda m: m.group(1) + '\n              ' + m.group(2),
        html,
        count=1
    )

    # 6. Replace photo-grid with empty placeholder
    id_pos = html.find('id="photo-grid"')
    if id_pos != -1:
        grid_start = html.rfind('<table', 0, id_pos)
        grid_end = html.find('</table>', id_pos) + len('</table>')
        html = html[:grid_start] + EMPTY_GRID + html[grid_end:]

    # 7. Replace lb block with placeholder
    id_pos2 = html.find('id="lb"')
    if id_pos2 != -1:
        lb_start = html.rfind('<div', 0, id_pos2)
        # Find the end of the lb div + script
        script_end = html.find('</script>', id_pos2)
        if script_end != -1:
            html = html[:lb_start] + EMPTY_LB + html[script_end + len('</script>'):]

    out_path = os.path.join(REPO_ROOT, filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ {filename}')

print('Done.')
