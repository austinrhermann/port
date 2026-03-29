#!/usr/bin/env python3
"""
build-galleries.py
Rebuilds the photo grid + viewer JS array in each gallery HTML page
from whatever image files are currently in the corresponding Images-* folder.

Usage: python3 build-galleries.py

Images are sorted alphabetically — name files with a numeric prefix to
control display order (e.g. 2016_001.jpg, 2016_002.jpg, ...).

Supported formats: .jpg, .jpeg, .png, .gif
"""

import os
import re

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Map gallery HTML filename → (page title, folder, description paragraph)
GALLERIES = {
    "nature.html":        ("Fauna",       "assets/photography/nature",        "All photos made in home darkroom with a Deardorff Studio camera."),
    "portraits.html":     ("Portraits",   "assets/photography/portraits",     ""),
    "huron.html":         ("Huron",       "assets/photography/huron",         ""),
    "dream-cruise.html":  ("Dream Cruise","assets/photography/dream-cruise",  ""),
    "article-one.html":   ("Article One", "assets/photography/article-one",   "Large-format chromogenic prints of everyday eyewear."),
    "housing.html":       ("Housing",     "assets/photography/housing",        ""),
    "2021-2025.html":     ("2021–2025",   "assets/photography/2021-2025",     ""),
    "2016-2020.html":     ("2016–2020",   "assets/photography/2016-2020",     ""),
    "2011-2015.html":     ("2011–2015",   "assets/photography/2011-2015",     ""),
    "2000-2010.html":     ("2000–2010",   "assets/photography/2000-2010",     ""),
}

IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

CELL_TEMPLATE = '<td style="width:16.666%;vertical-align:top;padding:0;"><div onclick="lbOpen({i})" style="cursor:pointer;border:2px solid;border-color:#808080 #fff #fff #808080;background:#b8b8b0;overflow:hidden;"><img src="{path}" style="width:100%;aspect-ratio:1/1;display:block;object-fit:cover;image-rendering:pixelated;filter:contrast(1.05) saturate(0.85);" loading="lazy"></div></td>'

EMPTY_GRID = '<table id="photo-grid" style="width:100%;border-collapse:separate;border-spacing:6px;margin-top:10px;"><tr><td colspan="6" style="padding:20px;text-align:center;color:#808080;font-size:14px;border:2px solid;border-color:#808080 #fff #fff #808080;background:#b8b8b0;">No photos yet — add images to this folder and run build-galleries.py</td></tr></table>'

def build_grid(images, folder):
    """Build the HTML table grid + viewer script from a list of image filenames."""
    if not images:
        return EMPTY_GRID, "[]", "0"

    cols = 6
    rows = []
    current_row = []

    for i, fname in enumerate(images):
        path = f"{folder}/{fname}"
        cell = CELL_TEMPLATE.format(i=i, path=path)
        current_row.append(cell)
        if len(current_row) == cols:
            rows.append('<tr>' + ''.join(current_row) + '</tr>')
            current_row = []

    # Pad last row if needed
    if current_row:
        while len(current_row) < cols:
            current_row.append('<td style="width:16.666%;vertical-align:top;padding:0;"></td>')
        rows.append('<tr>' + ''.join(current_row) + '</tr>')

    table = '<table id="photo-grid" style="width:100%;border-collapse:separate;border-spacing:6px;margin-top:10px;">' + ''.join(rows) + '</table>'

    imgs_array = '[' + ','.join(f"'{folder}/{fname}'" for fname in images) + ']'
    return table, imgs_array, str(len(images))

def build_viewer_script(title, images, folder):
    """Build the Win95 viewer HTML + script block."""
    imgs_array = '[' + ','.join(f"'{folder}/{fname}'" for fname in images) + ']'
    count = len(images)
    counter_text = f"1 / {count}" if count > 0 else "0 / 0"
    escaped_title = title.replace("'", "\\'")

    return (
        f'<div id="lb" class="lb-window">'
        f'<div class="lb-titlebar"><span id="lb-title">&#x1F4F7; Image Viewer</span>'
        f'<div class="lb-titlebar-btns">'
        f'<span class="lb-titlebar-btn">_</span>'
        f'<span class="lb-titlebar-btn" onclick="window.open(imgs[cur],\'_blank\')" title="Open full size">&#x25A1;</span>'
        f'<span class="lb-titlebar-btn" onclick="lbClose()">&#x2715;</span>'
        f'</div></div>'
        f'<div class="lb-toolbar">'
        f'<span class="lb-btn" onclick="lbPrev()">&#9664;</span>'
        f'<span id="lb-counter" style="padding:0 6px;font-family:\'Times New Roman\',serif;font-size:13px;-webkit-font-smoothing:none;">{counter_text}</span>'
        f'<span class="lb-btn" onclick="lbNext()">&#9654;</span>'
        f'</div>'
        f'<div class="lb-stage"><img id="lb-img" src="" alt="" loading="lazy" decoding="async"></div>'
        f'</div>'
        f'<script>var imgs={imgs_array};var cur=0;'
        f'function lbFit(){{var lb=document.getElementById(\'lb\');var stage=lb.querySelector(\'.lb-stage\');var img=document.getElementById(\'lb-img\');var top=stage.getBoundingClientRect().top;var h=\'calc(100vh - \'+(top+5)+\'px)\';var imgH=\'calc(100vh - \'+(top+15)+\'px)\';stage.style.height=h;stage.style.maxHeight=\'\';img.style.maxHeight=imgH;img.style.width=\'auto\';img.style.maxWidth=\'calc(100% - 10px)\';function fit(){{if(img.naturalWidth>img.naturalHeight){{stage.style.height=\'auto\';stage.style.maxHeight=h;}}}}if(img.complete&&img.naturalWidth>0){{fit();}}else{{img.onload=fit;}}}}'
        f'function lbOpen(i){{cur=i;document.getElementById(\'photo-grid\').style.display=\'none\';var t=document.getElementById(\'gallery-title\');if(t)t.style.display=\'none\';var d=document.getElementById(\'gallery-desc\');if(d)d.style.display=\'none\';document.getElementById(\'lb\').style.display=\'block\';window.scrollTo(0,0);lbShow();requestAnimationFrame(lbFit);}}'
        f'function lbShow(){{document.getElementById(\'lb-img\').src=imgs[cur];document.getElementById(\'lb-counter\').textContent=(cur+1)+\' / \'+imgs.length;document.getElementById(\'lb-title\').textContent=\'\\uD83D\\uDCF7 {escaped_title} \\u2014 \'+(cur+1)+\' / \'+imgs.length;}}'
        f'function lbClose(){{document.getElementById(\'lb\').style.display=\'none\';var t=document.getElementById(\'gallery-title\');if(t)t.style.display=\'\';var d=document.getElementById(\'gallery-desc\');if(d)d.style.display=\'\';document.getElementById(\'photo-grid\').style.display=\'table\';}}'
        f'function lbNext(){{cur=(cur+1)%imgs.length;lbShow();requestAnimationFrame(lbFit);}}'
        f'function lbPrev(){{cur=(cur-1+imgs.length)%imgs.length;lbShow();requestAnimationFrame(lbFit);}}'
        f'document.addEventListener(\'keydown\',function(e){{var lb=document.getElementById(\'lb\');if(lb.style.display===\'none\')return;if(e.key===\'ArrowRight\')lbNext();if(e.key===\'ArrowLeft\')lbPrev();if(e.key===\'Escape\')lbClose();}});</script>'
    )

def update_gallery(html_file, title, folder_rel, description):
    """Rebuild the grid and viewer section of a gallery HTML file."""
    html_path = os.path.join(REPO_ROOT, html_file)

    if not os.path.exists(html_path):
        print(f"  ⚠️  {html_file} not found, skipping")
        return

    folder_abs = os.path.join(REPO_ROOT, folder_rel)
    os.makedirs(folder_abs, exist_ok=True)

    # Get sorted image files from folder (alphabetical = numeric prefix order)
    images = sorted([
        f for f in os.listdir(folder_abs)
        if os.path.splitext(f.lower())[1] in IMG_EXTENSIONS and not f.startswith('.')
    ])

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    grid_html, imgs_array, count = build_grid(images, folder_rel)
    viewer_html = build_viewer_script(title, images, folder_rel)

    # --- REPLACE GRID ---
    # Find <table ... id="photo-grid" ... (handles multi-line tags)
    id_pos = html.find('id="photo-grid"')
    if id_pos == -1:
        print(f"  ⚠️  Could not find photo-grid table in {html_file}")
        return
    grid_start = html.rfind('<table', 0, id_pos)
    if grid_start == -1:
        print(f"  ⚠️  Could not find photo-grid table in {html_file}")
        return

    # Find the closing </table> that matches this <table>
    depth = 0
    i = grid_start
    grid_end = -1
    while i < len(html):
        if html[i:i+6].lower() == '<table':
            depth += 1
            i += 6
        elif html[i:i+8].lower() == '</table>':
            depth -= 1
            if depth == 0:
                grid_end = i + 8
                break
            i += 8
        else:
            i += 1

    if grid_end == -1:
        print(f"  ⚠️  Could not find end of photo-grid table in {html_file}")
        return

    html = html[:grid_start] + grid_html + html[grid_end:]

    # --- REPLACE VIEWER + SCRIPT ---
    # Find <div id="lb" class="lb-window">  ...  </script>
    lb_start = html.find('<div id="lb" class="lb-window">')
    if lb_start == -1:
        # Insert viewer right after the grid
        grid_end_new = html.find(grid_html) + len(grid_html)
        html = html[:grid_end_new] + viewer_html + html[grid_end_new:]
    else:
        # Find </script> after lb-window
        script_end_marker = '</script>'
        script_end = html.find(script_end_marker, lb_start)
        if script_end != -1:
            script_end += len(script_end_marker)
            html = html[:lb_start] + viewer_html + html[script_end:]

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  ✓ {html_file}: {len(images)} images")

def main():
    print("build-galleries.py — rebuilding gallery pages from local image folders\n")
    for html_file, (title, folder, description) in GALLERIES.items():
        update_gallery(html_file, title, folder, description)
    print("\nDone.")

if __name__ == "__main__":
    main()
