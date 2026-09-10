#!/usr/bin/env python3
"""Build city-corner/index.html — a fully self-contained single file.
Replaces {{TOKEN}} placeholders with base64 data URIs (fonts + images).
"""
import base64
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
IMG = os.path.join(ROOT, 'img')
FONTS = os.path.join(ROOT, 'fonts')

def b64(path, mime):
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()

TOKENS = {
    # fonts
    'FONT_CG500':  (os.path.join(FONTS, 'CormorantGaramond-500.woff2'),  'font/woff2'),
    'FONT_CG600':  (os.path.join(FONTS, 'CormorantGaramond-600.woff2'),  'font/woff2'),
    'FONT_CG500I': (os.path.join(FONTS, 'CormorantGaramond-500i.woff2'), 'font/woff2'),
    'FONT_J400':   (os.path.join(FONTS, 'Jost-400.woff2'),                'font/woff2'),
    'FONT_J500':   (os.path.join(FONTS, 'Jost-500.woff2'),                'font/woff2'),
    'FONT_J600':   (os.path.join(FONTS, 'Jost-600.woff2'),                'font/woff2'),
    # images
    'IMG_HERO':        (os.path.join(IMG, 'hero.jpg'),        'image/jpeg'),
    'IMG_ABOUT_MAIN':  (os.path.join(IMG, 'about-main.jpg'),  'image/jpeg'),
    'IMG_ABOUT_INSET': (os.path.join(IMG, 'about-inset.jpg'), 'image/jpeg'),
    'IMG_G_WOOD':      (os.path.join(IMG, 'g-wood.jpg'),      'image/jpeg'),
    'IMG_G_NEON':      (os.path.join(IMG, 'g-neon.jpg'),      'image/jpeg'),
    'IMG_G_FOOD1':     (os.path.join(IMG, 'g-food1.jpg'),     'image/jpeg'),
    'IMG_G_FOOD2':     (os.path.join(IMG, 'g-food2.jpg'),     'image/jpeg'),
    'IMG_G_MEALS':     (os.path.join(IMG, 'g-meals.jpg'),     'image/jpeg'),
    'IMG_G_DISH6':     (os.path.join(IMG, 'g-dish6.jpg'),     'image/jpeg'),
    'IMG_EXTERIOR':    (os.path.join(IMG, 'exterior.jpg'),    'image/jpeg'),
    'IMG_MENU1':       (os.path.join(IMG, 'menu-1.jpg'),      'image/jpeg'),
    'IMG_MENU2':       (os.path.join(IMG, 'menu-2.jpg'),      'image/jpeg'),
    'IMG_MENU3':       (os.path.join(IMG, 'menu-3.jpg'),      'image/jpeg'),
}

parts = ['part1-head.html', 'part2-header-hero.html', 'part3-about-menu.html', 'part4-rest.html']
html = '\n'.join(open(os.path.join(SRC, p), encoding='utf-8').read() for p in parts)

missing = [t for t in TOKENS if '{{' + t + '}}' not in html]
if missing:
    print('WARN: tokens not found in template:', missing)

for token, (path, mime) in TOKENS.items():
    html = html.replace('{{' + token + '}}', b64(path, mime))

leftover = re.findall(r'\{\{[A-Z0-9_]+\}\}', html)
if leftover:
    print('ERROR: unresolved tokens:', set(leftover)); sys.exit(1)

out = os.path.join(ROOT, 'index.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(out) // 1024
print(f'OK -> {out}  ({size_kb} KB)')

# ---------------------------------------------------------------
# Variant 2: mobile-fast/ — external assets, ~90KB HTML, lazy images.
# Best for real hosting: initial page weight drops from ~2.8MB to ~0.4MB.
# ---------------------------------------------------------------
FAST = os.path.join(ROOT, 'mobile-fast')
os.makedirs(os.path.join(FAST, 'assets', 'img'), exist_ok=True)
os.makedirs(os.path.join(FAST, 'assets', 'fonts'), exist_ok=True)

import shutil
for fname in os.listdir(IMG):
    if fname != 'og-cover.jpg':
        shutil.copy2(os.path.join(IMG, fname), os.path.join(FAST, 'assets', 'img', fname))
for fname in os.listdir(FONTS):
    if fname.endswith('.woff2'):
        shutil.copy2(os.path.join(FONTS, fname), os.path.join(FAST, 'assets', 'fonts', fname))
shutil.copy2(os.path.join(ROOT, 'og-cover.jpg'), os.path.join(FAST, 'og-cover.jpg'))

fast_tokens = {
    'FONT_CG500':  'assets/fonts/CormorantGaramond-500.woff2',
    'FONT_CG600':  'assets/fonts/CormorantGaramond-600.woff2',
    'FONT_CG500I': 'assets/fonts/CormorantGaramond-500i.woff2',
    'FONT_J400':   'assets/fonts/Jost-400.woff2',
    'FONT_J500':   'assets/fonts/Jost-500.woff2',
    'FONT_J600':   'assets/fonts/Jost-600.woff2',
    'IMG_HERO':        'assets/img/hero.jpg',
    'IMG_ABOUT_MAIN':  'assets/img/about-main.jpg',
    'IMG_ABOUT_INSET': 'assets/img/about-inset.jpg',
    'IMG_G_WOOD':      'assets/img/g-wood.jpg',
    'IMG_G_NEON':      'assets/img/g-neon.jpg',
    'IMG_G_FOOD1':     'assets/img/g-food1.jpg',
    'IMG_G_FOOD2':     'assets/img/g-food2.jpg',
    'IMG_G_MEALS':     'assets/img/g-meals.jpg',
    'IMG_G_DISH6':     'assets/img/g-dish6.jpg',
    'IMG_EXTERIOR':    'assets/img/exterior.jpg',
    'IMG_MENU1':       'assets/img/menu-1.jpg',
    'IMG_MENU2':       'assets/img/menu-2.jpg',
    'IMG_MENU3':       'assets/img/menu-3.jpg',
}
fast_html = html
for token, rel in fast_tokens.items():
    fast_html = fast_html.replace('data:font/woff2;base64,' + '', '')  # no-op guard
# replace data URIs back: easier to rebuild from the tokenised template
parts_txt = '\n'.join(open(os.path.join(SRC, p), encoding='utf-8').read() for p in parts)
fast_html = parts_txt
for token, rel in fast_tokens.items():
    fast_html = fast_html.replace('{{' + token + '}}', rel)
if re.findall(r'\{\{[A-Z0-9_]+\}\}', fast_html):
    print('ERROR: fast build unresolved tokens'); sys.exit(1)
fast_out = os.path.join(FAST, 'index.html')
with open(fast_out, 'w', encoding='utf-8') as f:
    f.write(fast_html)
print(f'OK -> {fast_out}  ({os.path.getsize(fast_out) // 1024} KB) + assets/')
