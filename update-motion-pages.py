#!/usr/bin/env python3
"""
update-motion-pages.py
Inserts credits + CSS-columns thumbnail grid + Win98 image viewer into each
motion/group-project page. Re-running is safe: all inserted content is wrapped
in a unique marker div so it is stripped and rebuilt cleanly every time.

Run: python3 update-motion-pages.py
"""

import os
import re
import json

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

FOOTER_MARKER = '<div style="border-top:2px solid #000000;margin-top:28px'

INSERT_START = '<div id="arh-inserts">'
INSERT_END   = '</div><!-- /arh-inserts -->'

IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
COLS = 4  # thumbnail columns


# (slug, html_file, page_title, credits_list)
PAGES = [
    # --- motion pages ---
    ('sanjam', 'sanjam.html', 'San Jamerino Sing-A-Long', [
        ('Director', 'Austin Robert Hermann'),
        ('Music', 'Friendship Park'),
        ('Sound Design', 'Ambrose Yu'),
        ('Producer', 'Christian Lathers'),
        ('Director of Photography', 'Matt Barth'),
        ('Camera Operator', 'Brandon Mata'),
        ('Production Company', 'Riot Films'),
        ('Gaffer/Keygrip', 'Jake Gottman'),
        ('Puppet Builder / Puppeteer',
         'Rachel Reid, Justin Lawes, Mercy Lomelin, Chris Solada, Josh Jouppi, '
         'Collin Leix, John Hughes, Marcus Bakke, Joe Ficorelli, Mike Burdick, '
         'Olivia Blanc, Ver&#243; G&#243;mez, Wendy Eduarte'),
    ]),
    ('all-kinds-of-planes', 'all-kinds-of-planes.html', 'All Kinds of Planes', [
        ('Illustration', 'Carl Johanson'),
        ('Animation', 'Rachel Reid, Mercy Lomelin, Justin Lawes, Jon Riedell, '
                      'Marcus Bakke, Jordan Scott, Austin Robert'),
        ('Sound', 'Ambrose Yu'),
        ('Music', 'Hometown Polka &#8212; Jimmy Bryant with Speedy West'),
        ('Publisher', '<a href="http://www.flyingeyebooks.com" style="color:#00008b;">flyingeyebooks.com</a>'),
    ]),
    ('all-kinds-of-cars', 'all-kinds-of-cars.html', 'All Kinds of Cars', [
        ('Illustration', 'Carl Johanson'),
        ('Animation', 'Justin Lawes, Austin Robert'),
        ('Sound Design', 'Ambrose Yu'),
        ('Music', 'Fire Water Polka &#8212; Freddy Myers &amp; His Trail Rangers'),
        ('Publisher', 'Flying Eye Books'),
    ]),
    ('magic-tricks', 'magic-tricks.html', 'Magic Tricks', []),
    ('figure-01-limestone-cave', 'figure-01-limestone-cave.html', 'Figure 01 \u2014 Limestone Cave', [
        ('Visuals', 'Austin Robert'),
        ('Sound Design', 'Ambrose Yu'),
    ]),
    ('figure-02-earths-layers', 'figure-02-earths-layers.html', 'Figure 02 \u2014 Earth\'s Layers', [
        ('Visuals', 'Austin Robert'),
        ('Song', 'Perrey and Kingsley &#8212; &#8220;The Little Girl from Mars&#8221;'),
        ('Sound Design', 'Ambrose Yu'),
    ]),
    ('figure-03-volcanos', 'figure-03-volcanos.html', 'Figure 03 \u2014 Volcanos', [
        ('Audio', 'Breakmaster Cylinder (Anna Meredith &#8212; Nautilus Remix)'),
        ('Visuals', 'Austin Robert'),
    ]),
    # --- group project pages ---
    ('working-in-teams', 'working-in-teams.html', 'Working in Teams', []),
    ('google-dots', 'google-dots.html', 'Google Dots', []),
    ('fp-blend', 'fp-blend.html', 'FP Blend Live', []),
    ('demyulederby', 'demyulederby.html', 'Demyule Derby', []),
    ('poo-power', 'poo-power.html', 'Poo Power', []),
]


def get_images(slug):
    folder = os.path.join(REPO_ROOT, 'assets', 'motion', slug)
    if not os.path.isdir(folder):
        return []
    return sorted([
        f for f in os.listdir(folder)
        if os.path.splitext(f.lower())[1] in IMG_EXTENSIONS and not f.startswith('.')
    ])


def build_lb_css():
    """Win98 lightbox CSS — same classes as nature.html, stage capped at 800px."""
    return (
        '<style>'
        '.lb-window{display:none;border:2px solid;border-color:#fff #808080 #808080 #fff;}'
        '.lb-titlebar{background:#000080;color:#fff;padding:2px 6px;display:flex;'
        'align-items:center;justify-content:space-between;font-size:12px;font-weight:bold;'
        "font-family:'Times New Roman',serif;user-select:none;}"
        '.lb-titlebar-btns{display:flex;gap:2px;}'
        '.lb-titlebar-btn{background:#c0c0c0;color:#000;border:1px solid;'
        'border-color:#fff #808080 #808080 #fff;font-size:10px;padding:0 4px;'
        "line-height:14px;cursor:pointer;font-family:'Times New Roman',serif;}"
        '.lb-toolbar{background:#c0c0c0;border-bottom:1px solid #808080;padding:2px 4px;'
        "display:flex;align-items:center;gap:4px;font-family:'Times New Roman',serif;font-size:13px;}"
        '.lb-btn{cursor:pointer;padding:1px 8px;border:2px solid;'
        'border-color:#fff #808080 #808080 #fff;background:#c0c0c0;font-size:13px;'
        "font-family:'Times New Roman',serif;-webkit-font-smoothing:none;}"
        '.lb-btn:hover,.lb-btn:active{border-color:#808080 #fff #fff #808080;}'
        '.lb-stage{background:#b8b8b8;padding:5px;display:flex;align-items:center;'
        'justify-content:center;overflow:hidden;height:800px;box-sizing:border-box;}'
        '.lb-stage img{display:block;width:100%;height:100%;object-fit:contain;'
        'image-rendering:auto;filter:contrast(1.05) saturate(0.85);}'
        '</style>'
    )


def build_image_grid(slug, images):
    """CSS-columns masonry grid with clickable thumbnails (Win98 sunken border)."""
    if not images:
        return ''

    thumb_style = (
        'cursor:pointer;border:2px solid;border-color:#808080 #fff #fff #808080;'
        'background:#b8b8b0;overflow:hidden;'
    )
    img_style = (
        'width:100%;height:auto;display:block;'
        'image-rendering:auto;filter:contrast(1.05) saturate(0.85);'
    )
    item_style = 'break-inside:avoid;margin-bottom:6px;'

    items = []
    for idx, fname in enumerate(images):
        src = f'assets/motion/{slug}/{fname}'
        items.append(
            f'<div style="{item_style}">'
            f'<div onclick="lbOpen({idx})" style="{thumb_style}">'
            f'<img src="{src}" alt="" style="{img_style}" loading="lazy">'
            f'</div>'
            f'</div>'
        )

    return (
        f'<div id="motion-grid" style="column-count:{COLS};column-gap:6px;margin-top:16px;">'
        + ''.join(items)
        + '</div>'
        # Viewer overlays this container — see build_viewer for the wrapping div
    )


def build_viewer(slug, images, page_title):
    """Win98 image viewer window + JS. Grid hides on open; Vimeo/desc/credits stay."""
    if not images:
        return ''

    srcs = [f'assets/motion/{slug}/{f}' for f in images]
    imgs_json = json.dumps(srcs)
    title_js  = json.dumps(f'\U0001f4f7 {page_title}')
    count     = len(images)

    viewer_html = (
        '<div id="lb" class="lb-window" style="position:absolute;top:0;left:0;width:100%;">'
        '<div class="lb-titlebar">'
        f'<span id="lb-title">\U0001f4f7 {page_title}</span>'
        '<div class="lb-titlebar-btns">'
        '<span class="lb-titlebar-btn">_</span>'
        '<span class="lb-titlebar-btn" onclick="window.open(imgs[cur],\'_blank\')" title="Open full size">&#x25A1;</span>'
        '<span class="lb-titlebar-btn" onclick="lbClose()">&#x2715;</span>'
        '</div></div>'
        '<div class="lb-toolbar">'
        '<span class="lb-btn" onclick="lbPrev()">&#9664;</span>'
        f'<span id="lb-counter" style="padding:0 6px;font-family:\'Times New Roman\',serif;'
        f'font-size:13px;-webkit-font-smoothing:none;">1 / {count}</span>'
        '<span class="lb-btn" onclick="lbNext()">&#9654;</span>'
        '</div>'
        '<div class="lb-stage"><img id="lb-img" src="" alt=""></div>'
        '</div>'
    )

    script = (
        '<script>'
        f'var imgs={imgs_json};'
        'var cur=0;'
        'function lbOpen(i){'
        '  cur=i;'
        '  document.getElementById("motion-grid").style.visibility="hidden";'
        '  var lb=document.getElementById("lb");'
        '  lb.style.display="block";'
        '  lb.scrollIntoView({behavior:"smooth",block:"nearest"});'
        '  lbShow();'
        '}'
        'function lbShow(){'
        '  document.getElementById("lb-img").src=imgs[cur];'
        '  document.getElementById("lb-counter").textContent=(cur+1)+" / "+imgs.length;'
        f'  document.getElementById("lb-title").textContent={title_js}+" \u2014 "+(cur+1)+" / "+imgs.length;'
        '}'
        'function lbClose(){'
        '  document.getElementById("lb").style.display="none";'
        '  document.getElementById("motion-grid").style.visibility="";'
        '}'
        'function lbNext(){cur=(cur+1)%imgs.length;lbShow();}'
        'function lbPrev(){cur=(cur-1+imgs.length)%imgs.length;lbShow();}'
        'document.addEventListener("keydown",function(e){'
        '  if(document.getElementById("lb").style.display==="none")return;'
        '  if(e.key==="ArrowRight")lbNext();'
        '  if(e.key==="ArrowLeft")lbPrev();'
        '  if(e.key==="Escape")lbClose();'
        '});'
        '</script>'
    )

    return viewer_html + script


def build_credits(credits_list):
    if not credits_list:
        return ''
    rows = []
    for label, value in credits_list:
        rows.append(
            f'<tr>'
            f'<td style="font-weight:bold;padding-right:14px;white-space:nowrap;vertical-align:top;'
            f"font-family:'Times New Roman',serif;-webkit-font-smoothing:none;"
            f'text-rendering:optimizeSpeed;font-size:14px;line-height:1.7;color:#000000;">'
            f'{label}</td>'
            f'<td style="font-family:\'Times New Roman\',serif;-webkit-font-smoothing:none;'
            f'text-rendering:optimizeSpeed;font-size:14px;line-height:1.7;color:#333333;">'
            f'{value}</td>'
            f'</tr>'
        )
    return (
        '<div style="margin-top:22px;border-top:1px solid #a0a0a0;padding-top:10px;">'
        '<table style="border-collapse:collapse;">'
        + ''.join(rows)
        + '</table></div>'
    )


def fix_blink_and_strip_lb_css(content):
    """Fix lb CSS accidentally injected inside @keyframes blink."""
    content = re.sub(
        r'(@keyframes blink\{0%,100%\{opacity:1\})\.lb-window\{.*?\}(50%\{opacity:0\}\})',
        r'\1\2',
        content,
        flags=re.DOTALL
    )
    return content


def strip_old_content(content):
    """
    Remove all previously-inserted content.
    Primary: wrapper div  <div id="arh-inserts"> ... </div><!-- /arh-inserts -->
    Legacy:  old table grids, old credits divs, orphaned break-inside divs,
             column-count divs without wrapper, lb viewer+script.
    """
    # --- Primary wrapper (current format) ---
    while INSERT_START in content:
        s = content.index(INSERT_START)
        e = content.index(INSERT_END, s) + len(INSERT_END)
        content = content[:s] + content[e:]

    # --- Legacy: old table grids ---
    for marker in [
        '<table id="photo-grid" style="width:100%;border-collapse:separate;border-spacing:6px',
        '<table style="width:100%;border-collapse:separate;border-spacing:6px',
    ]:
        while marker in content:
            gs = content.index(marker)
            depth, i = 0, gs
            while i < len(content):
                if content[i:i+7] == '<table ':
                    depth += 1; i += 7
                elif content[i:i+7] == '</table':
                    depth -= 1
                    if depth == 0:
                        content = content[:gs] + content[i + len('</table>'):]
                        break
                else:
                    i += 1
            else:
                break

    # --- Legacy: old credits divs ---
    credits_marker = '<div style="margin-top:22px;border-top:1px solid #a0a0a0;'
    while credits_marker in content:
        cs = content.index(credits_marker)
        ce = content.index('</table></div>', cs) + len('</table></div>')
        content = content[:cs] + content[ce:]

    # --- Legacy: orphaned break-inside:avoid image divs ---
    content = re.sub(
        r'(?:<div style="break-inside:avoid;margin-bottom:6px;">.*?</div>\s*)+',
        '',
        content,
        flags=re.DOTALL
    )

    # --- Legacy: unwrapped column-count div ---
    col_marker = '<div style="column-count:'
    while col_marker in content:
        gs = content.index(col_marker)
        depth, i = 0, gs
        while i < len(content):
            if content[i:i+5] == '<div ':
                depth += 1; i += 5
            elif content[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    content = content[:gs] + content[i + 6:]
                    break
            else:
                i += 1
        else:
            break

    # --- Legacy: lb viewer div + script ---
    if '<div id="lb" class="lb-window">' in content:
        lb_start = content.index('<div id="lb" class="lb-window">')
        script_end = content.index('</script>', lb_start) + len('</script>')
        content = content[:lb_start] + content[script_end:]

    return content


def process_page(slug, html_file, page_title, credits_list):
    path = os.path.join(REPO_ROOT, html_file)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    images = get_images(slug)

    # 1. Fix broken blink CSS
    content = fix_blink_and_strip_lb_css(content)

    # 2. Strip all previously-inserted content
    content = strip_old_content(content)

    # 3. Build: CSS + credits + [grid + viewer in position:relative container]
    # The relative container keeps page height stable when toggling grid/viewer.
    grid_and_viewer = (
        '<div style="position:relative;min-height:800px;">'
        + build_image_grid(slug, images)
        + build_viewer(slug, images, page_title)
        + '</div>'
    )
    inner = build_lb_css() + build_credits(credits_list) + grid_and_viewer
    insert = INSERT_START + inner + INSERT_END

    # 4. Insert before footer bar
    if FOOTER_MARKER not in content:
        print(f'  WARNING: footer marker not found in {html_file}')
        return

    content = content.replace(FOOTER_MARKER, insert + FOOTER_MARKER, 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'  {html_file}: {len(images)} images'
          + (f', {len(credits_list)} credit rows' if credits_list else ''))


def main():
    print('update-motion-pages.py\n')
    for slug, html_file, page_title, credits_list in PAGES:
        process_page(slug, html_file, page_title, credits_list)
    print('\nDone.')


if __name__ == '__main__':
    main()
