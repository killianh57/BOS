#!/usr/bin/env python3
"""
Post-traitement "vrai pixel-art" : transforme une image IA de style pixel (pixels flous, dégradés,
des milliers de couleurs) en pixel-art net : grille régulière, palette limitée, bords durs.

Usage :
  python3 pixelize.py in.png out.png [--grid 160] [--colors 32] [--palette brand] [--scale 6]
  --grid    : largeur de la grille en "gros pixels" (128 = très rétro, 192 = détaillé)
  --colors  : nombre de couleurs si palette adaptative
  --palette : "adaptive" (calculée sur l'image) ou "brand" (palette fixe de la chaîne -> cohérence entre images)
  --scale   : facteur d'agrandissement final en plus proche voisin (net, sans flou)
"""
import sys
from PIL import Image, ImageFilter, ImageEnhance

# Palette fixe provisoire (nuit profonde + ambre/corail/turquoise). Sera remplacée par la palette validée.
BRAND = [
    "0b1026", "141b3d", "1f2a5c", "2e3f7f", "3f5aa6", "6c8fd1", "a9c6ee",   # bleus nuit -> ciel
    "e9f1f7", "fff4dc", "f6d38b", "f4a64a", "e0702e", "b8442a", "7a2a22",   # neige, crème, ambre, corail, brique
    "4a1c1c", "2a1414", "1d6f72", "2fa3a0", "7fd6c8", "5b4a3a", "8c7560",   # brun foncé, turquoise, bois
    "c2a98a", "3a3a46", "6b6b78",                                            # pierre, gris acier
]

def brand_palette_image():
    pal = []
    for h in BRAND: pal += [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    pal += pal[:3] * (256 - len(BRAND))
    p = Image.new("P", (1, 1)); p.putpalette(pal); return p

def pixelize(im, grid=160, colors=32, palette="adaptive", scale=6):
    im = im.convert("RGB")
    w, h = im.size; gh = round(h * grid / w)
    # 1) réduction par moyenne de bloc (BOX) = un gros pixel par cellule de grille
    small = im.resize((grid, gh), Image.BOX)
    # 2) léger renfort de contraste et de saturation (les couleurs "pop" après quantification)
    small = ImageEnhance.Color(small).enhance(1.12)
    small = ImageEnhance.Contrast(small).enhance(1.06)
    # 3) palette limitée, sans tramage (aplats nets)
    if palette == "brand":
        q = small.quantize(palette=brand_palette_image(), dither=Image.Dither.NONE)
    else:
        q = small.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    # 4) agrandissement plus proche voisin = grille parfaitement nette
    return q.convert("RGB").resize((grid * scale, gh * scale), Image.NEAREST)

if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    out = pixelize(Image.open(a[0]), opt("--grid", 160), opt("--colors", 32), opt("--palette", "adaptive"), opt("--scale", 6))
    out.save(a[1]); print("ok", a[1], out.size)
