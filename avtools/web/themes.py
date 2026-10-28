"""
Each Otari shop page's look: heading font, crest icon and two palettes (light
for daylight, dark for a dim game table). The page writes a palette out as CSS
custom properties; static/css/shop.css draws everything (and each shop's
ornaments) from them. tests/test_themes.py holds every palette to WCAG AA.

Palette keys:
  bg, bg2      page background and its texture colour (headings sit on these)
  surface      tiles, list rows, header card; surface2 for the details sheet
  ink, soft    body text and secondary text (on bg and both surfaces)
  accent       headings, links, focus ring, the active toggle (on bg and surfaces)
  on_accent    text on an accent-filled button
  line         borders
  deco         the ornament colour (stripes, seals, rays); decorative only

The band (the shop's "material") is the same in light and dark mode: the
running header, the section banners and the footer are all drawn in it.
  band, band2  the band's gradient; band_ink is text on it; trim its edge lines
"""

THEMES = {
    'otari_market': {
        'font': 'Alegreya SC', 'file': 'alegreya-sc', 'weight': 700, 'crest': 'coins',
        'tagline': 'Under the striped awnings',
        'band': dict(band='#5a2410', band2='#7d3517', band_ink='#fbefd9', trim='#e0b45a'),
        'dark': dict(bg='#1c140c', bg2='#2a1d10', surface='#2b2015', surface2='#362818', ink='#f6ead7',
                     soft='#d6c3a5', accent='#f0a845', on_accent='#1c140c', line='#5a4428', deco='#9b3524'),
        'light': dict(bg='#f4ead6', bg2='#ead9b8', surface='#fffaf0', surface2='#fff3dc', ink='#2a1a0c',
                      soft='#5c4429', accent='#8a3c0c', on_accent='#fffaf0', line='#c9ad82', deco='#b8452f'),
    },
    'wrins_wonders': {
        'font': 'Cinzel Decorative', 'file': 'cinzel-decorative', 'weight': 700, 'crest': 'star',
        'tagline': 'Beneath the open dome',
        'band': dict(band='#160f36', band2='#2e1f66', band_ink='#f3edff', trim='#e9d48a'),
        'dark': dict(bg='#0d0b1f', bg2='#1b1240', surface='#1a1535', surface2='#241c48', ink='#efeaff',
                     soft='#c4b8ee', accent='#d7b8ff', on_accent='#160f33', line='#43367a', deco='#fff3b0'),
        'light': dict(bg='#eeeafc', bg2='#ddd3f7', surface='#ffffff', surface2='#f6f2ff', ink='#1d1340',
                      soft='#4a3c78', accent='#5b21b6', on_accent='#ffffff', line='#c3b5ec', deco='#a78bfa'),
    },
    'odd_stories': {
        'font': 'IM Fell English SC', 'file': 'im-fell-english-sc', 'weight': 400, 'crest': 'open-book',
        'tagline': 'Three floors of tales',
        'band': dict(band='#111c38', band2='#22346a', band_ink='#f4ecd6', trim='#d6b45a'),
        'dark': dict(bg='#0f1626', bg2='#162038', surface='#18223a', surface2='#1f2b48', ink='#f1ead8',
                     soft='#c8c0a8', accent='#e3c46f', on_accent='#0f1626', line='#3a4a72', deco='#c9a646'),
        'light': dict(bg='#f3ecd9', bg2='#e7dcc0', surface='#fdf9ee', surface2='#f8f1dd', ink='#1d2238',
                      soft='#4a4a5e', accent='#1e3a8a', on_accent='#ffffff', line='#cbbd99', deco='#b08d2e'),
    },
    'gallentine_deliveries': {
        'font': 'Almendra SC', 'file': 'almendra-sc', 'weight': 400, 'crest': 'horseshoe',
        'tagline': 'Sealed, stamped and on its way',
        'band': dict(band='#14301f', band2='#24482f', band_ink='#f1f5ea', trim='#d8c9a0'),
        'dark': dict(bg='#0f1a13', bg2='#16261b', surface='#1a2a1f', surface2='#213427', ink='#eef3e6',
                     soft='#bfd0b4', accent='#a6d672', on_accent='#0f1a13', line='#3c5a43', deco='#b3261e'),
        'light': dict(bg='#ece3cf', bg2='#dfd1b3', surface='#fbf7ee', surface2='#f4ecdb', ink='#1b2a1e',
                      soft='#4b5a44', accent='#2f5d1e', on_accent='#ffffff', line='#c2b08a', deco='#a3201a'),
    },
    'blades_for_glades': {
        'font': 'Grenze', 'file': 'grenze', 'weight': 700, 'crest': 'crossed-swords',
        'tagline': 'Hot from the forge',
        'band': dict(band='#1f2328', band2='#363b42', band_ink='#f1f2f4', trim='#ff8a3d'),
        'dark': dict(bg='#121417', bg2='#1c1f24', surface='#1e2228', surface2='#272c33', ink='#eef0f2',
                     soft='#b9c0c8', accent='#ff9a4d', on_accent='#121417', line='#48505b', deco='#ff6a1a'),
        'light': dict(bg='#e8eaed', bg2='#d6dadf', surface='#fbfbfc', surface2='#f1f3f5', ink='#16191d',
                      soft='#474f59', accent='#943808', on_accent='#ffffff', line='#b5bcc5', deco='#8a929c'),
    },
    'crows_casks': {
        'font': 'Pirata One', 'file': 'pirata-one', 'weight': 400, 'crest': 'drink',
        'tagline': "Drink to Cayden's health",
        'band': dict(band='#3a2412', band2='#553619', band_ink='#fbeedb', trim='#d9a441'),
        'dark': dict(bg='#1a1009', bg2='#26170c', surface='#2a1b0f', surface2='#352314', ink='#f8ecd8',
                     soft='#dcc4a0', accent='#f5c04a', on_accent='#1a1009', line='#5e3f20', deco='#7a5230'),
        'light': dict(bg='#f1e4cc', bg2='#e3cfa9', surface='#fffaf1', surface2='#f8edd6', ink='#2b1a0b',
                      soft='#5e4326', accent='#7a4204', on_accent='#ffffff', line='#c8a676', deco='#9b6a3c'),
    },
    'crooks_nook': {
        'font': 'Grenze Gotisch', 'file': 'grenze-gotisch', 'weight': 600, 'crest': 'key',
        'tagline': 'Ask quietly. Pay in coin.',
        'band': dict(band='#081114', band2='#17282d', band_ink='#e9f1ef', trim='#d9b54f'),
        'dark': dict(bg='#0a0f12', bg2='#0f1a1e', surface='#131d22', surface2='#19262c', ink='#e8f0ee',
                     soft='#a9bdb8', accent='#e8c35a', on_accent='#0a0f12', line='#2f4249', deco='#1f5f59'),
        'light': dict(bg='#e6ecea', bg2='#d3dedb', surface='#fafcfb', surface2='#eef3f1', ink='#10191c',
                      soft='#3f5156', accent='#0f5c55', on_accent='#ffffff', line='#aebfbb', deco='#7fa8a2'),
    },
    'the_rowdy_rockfish': {
        'font': 'Fondamento', 'file': 'fondamento', 'weight': 400, 'crest': 'candle',
        'tagline': 'A quiet pint by the fire',
        'band': dict(band='#4a2a20', band2='#6a3d2e', band_ink='#fbefe7', trim='#e3b9a1'),
        'dark': dict(bg='#1b1210', bg2='#261a16', surface='#2a1d19', surface2='#33241f', ink='#f7ece4',
                     soft='#d8c2b5', accent='#f39a74', on_accent='#1b1210', line='#5b3f35', deco='#8a5a48'),
        'light': dict(bg='#f6eee6', bg2='#ecdfd2', surface='#fffcf8', surface2='#fbf3ea', ink='#2b1913',
                      soft='#5e463b', accent='#9a3412', on_accent='#ffffff', line='#d6bfae', deco='#c9907a'),
    },
    'otari_fishery': {
        'font': 'Marcellus SC', 'file': 'marcellus-sc', 'weight': 400, 'crest': 'hook',
        'tagline': 'Fresh off the pier',
        'band': dict(band='#082636', band2='#12425a', band_ink='#eaf6fb', trim='#d7b678'),
        'dark': dict(bg='#06161f', bg2='#0a2230', surface='#0d2433', surface2='#123042', ink='#e6f4fa',
                     soft='#a8cbdb', accent='#5fd0e6', on_accent='#06161f', line='#2a5268', deco='#c9a46a'),
        'light': dict(bg='#e3f1f6', bg2='#cde5ee', surface='#fbfeff', surface2='#eef7fa', ink='#08222e',
                      soft='#36586a', accent='#0b5e7e', on_accent='#ffffff', line='#a9cbd8', deco='#b08850'),
    },
    'dawnflower_library': {
        'font': 'Cinzel', 'file': 'cinzel', 'weight': 600, 'crest': 'sunrise',
        'tagline': 'In the light of the Dawnflower',
        'band': dict(band='#5e3206', band2='#94520a', band_ink='#fff6e0', trim='#ffe08a'),
        'dark': dict(bg='#1a120a', bg2='#2a1a0b', surface='#261a10', surface2='#322213', ink='#fff4e0',
                     soft='#e4cfa8', accent='#ffc65a', on_accent='#1a120a', line='#5f4520', deco='#f59e0b'),
        'light': dict(bg='#fdf6e7', bg2='#fbe7bf', surface='#ffffff', surface2='#fff8ea', ink='#2a1a08',
                      soft='#5d4625', accent='#9a4a06', on_accent='#ffffff', line='#e3c98f', deco='#f2b33d'),
    },
}

DEFAULT = 'otari_market'


def theme(slug):
    return {'slug': slug if slug in THEMES else DEFAULT, **THEMES.get(slug, THEMES[DEFAULT])}


def css_vars(palette):
    """'--bg:#...;--ink:#...' for a palette"""
    return ';'.join(f"--{key.replace('_', '-')}:{value}" for key, value in palette.items())


# ---------------------------------------------------------------- contrast (WCAG 2.x)
def _luminance(hex_color):
    channels = [int(hex_color.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    r, g, b = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# (foreground, background) pairs that carry text, so need 4.5:1
TEXT_PAIRS = [(fg, bg) for fg in ('ink', 'soft', 'accent') for bg in ('bg', 'bg2', 'surface', 'surface2')] + [
    ('on_accent', 'accent')]
BAND_PAIRS = [('band_ink', 'band'), ('band_ink', 'band2'), ('trim', 'band'), ('trim', 'band2')]
