#!/usr/bin/env python3.13
"""Chapitre Étiquettes : photo de la vraie étiquette à droite de l'exemple + corrections de l'exemple."""
import base64, io, sys
from PIL import Image, ImageOps

src, img_path, dst = sys.argv[1], sys.argv[2], sys.argv[3]
h = open(src, encoding='utf-8').read()

im = ImageOps.exif_transpose(Image.open(img_path)).convert('RGB')
W, H = im.size
if W > 640:
    im = im.resize((640, int(H * 640 / W)), Image.LANCZOS)
buf = io.BytesIO(); im.save(buf, 'JPEG', quality=80, optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()
print('photo', (W, H), '→', im.size, round(len(buf.getvalue()) / 1024), 'Ko')

a = h.index("<h3>La grammaire d'une étiquette</h3>")
c = h.index('<div class="callout">', a)
b = h.index('</div>', c) + len('</div>')
old_example = h[a:b]
assert 'TF · 7215 · 166 · 38' in old_example and old_example.count('<div class="callout">') == 1, 'bloc exemple inattendu'
new_example = f"""<h3>La grammaire d'une étiquette</h3>
  <figure class="etq-fig">
    <img src="data:image/jpeg;base64,{b64}" alt="Étiquette Lacoste : t-shirt femme TF7215 00 166, taille 40, bleu marine, 100 % coton">
    <figcaption>Étiquette de col : coupe Relaxed fit, taille 40. Étiquette volante : référence, code-barres, taille, coloris, matière.</figcaption>
  </figure>
  <p>Exemple lu sur l'étiquette ci-contre : <strong>TF7215 00 166 · 40 · bleu marine-166 · 100% coton</strong></p>
  <ul>
    <li><strong>Type de produit</strong> — <code>T</code> pour t-shirt, <code>F</code> pour femme → <strong>TF</strong> = t-shirt femme</li>
    <li><strong>Référence produit</strong> — <strong>7215</strong> (donc le t-shirt femme modèle 7215), suivie du code <strong>00</strong> qui s'écrit toujours entre le modèle et le coloris</li>
    <li><strong>Coloris</strong> — <strong>166</strong> = bleu marine (écrit « bleu marine-166 » sur l'étiquette)</li>
    <li><strong>Taille</strong> — <strong>40</strong> = M femme</li>
    <li><strong>Matières</strong> — <strong>100% coton</strong></li>
  </ul>
  <div class="callout">
    <p>On est donc avec le t-shirt femme 7215 en couleur bleu marine, taille 40, en 100% coton.</p>
  </div>
  <div class="etq-clear"></div>"""
h = h[:a] + new_example + h[b:]

style = """<style id="etq-style">
.etq-fig{float:right;width:270px;max-width:42%;margin:0 0 18px 30px;}
.etq-fig img{width:100%;height:auto;display:block;border-radius:6px;box-shadow:0 10px 30px rgba(5,32,24,.14);}
.etq-fig figcaption{font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-size:14px;line-height:1.35;color:#8A6D3A;text-align:center;margin-top:8px;}
.etq-clear{clear:both;}
@media (max-width:700px){.etq-fig{float:none;width:240px;max-width:100%;margin:12px auto 18px;}}
@media print{.etq-fig{width:150px;float:right;margin:0 0 8pt 12pt;}.etq-fig img{box-shadow:none;border:1px solid #999;}}
</style>
"""
h = h.replace('</head>', style + '</head>', 1)
open(dst, 'w', encoding='utf-8').write(h)
print('ok →', dst, round(len(h.encode('utf-8')) / 1024), 'Ko')
