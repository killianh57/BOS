#!/usr/bin/env python3
"""Ajoute un repli « sans JavaScript » à la formation (fichier HTML autonome).
Usage : python3 add_nojs.py <entree.html> <sortie.html>
- <html class="no-js"> + script de bascule en tête de <head> (avant le CSS, pas de flash)
- bannière de consigne visible uniquement sans JS, tous les chapitres affichés, menu masqué
Idempotent : ne ré-applique pas si déjà présent."""
import re, sys

src, dst = sys.argv[1], sys.argv[2]
h = open(src, encoding='utf-8').read()
if 'id="rx-nojs-style"' in h:
    print('déjà patché, copie telle quelle'); open(dst, 'w', encoding='utf-8').write(h); sys.exit(0)

# 1) classe no-js sur <html>
m = re.search(r'<html\b([^>]*)>', h)
assert m, '<html> introuvable'
attrs = m.group(1)
if re.search(r'class\s*=', attrs):
    attrs2 = re.sub(r'class\s*=\s*"([^"]*)"', lambda mm: 'class="%s no-js"' % mm.group(1).strip(), attrs, count=1)
else:
    attrs2 = attrs + ' class="no-js"'
h = h[:m.start()] + '<html' + attrs2 + '>' + h[m.end():]

# 2) script de bascule juste après <head>
flip = '<script>document.documentElement.classList.remove("no-js");document.documentElement.classList.add("js");</script>'
h = re.sub(r'(<head\b[^>]*>)', lambda mm: mm.group(1) + flip, h, count=1)

# 3) CSS du repli (avant </head>, donc après tous les styles existants)
css = """
<style id="rx-nojs-style">
.rx-nojs{display:none;}
html.no-js .rx-nojs{display:block;position:relative;z-index:50;background:#0A4B38;color:#F6F2E9;
  padding:20px 26px;font-family:Manrope,'Helvetica Neue',Arial,sans-serif;font-size:15px;line-height:1.65;
  border-bottom:4px solid #C2A567;}
html.no-js .rx-nojs strong,html.no-js .rx-nojs b{color:#E4D6B4;}
html.no-js .rx-nojs .rx-nojs-steps{margin:10px 0 0;padding-left:20px;}
html.no-js .rx-nojs .rx-nojs-steps li{margin:4px 0;}
html.no-js .panel{display:block !important;}
html.no-js .tabs-wrap,html.no-js .print-btn{display:none !important;}
html.no-js body{padding-left:0 !important;}
html.no-js .panel-header{margin-top:40px;}
html.no-js .quiz-wrap::before{content:"Les quiz interactifs nécessitent l’ouverture dans un navigateur (voir la consigne en haut du document).";
  display:block;font-style:italic;color:#8A6D3A;margin-bottom:14px;}
@media print{.rx-nojs{display:none !important;}}
</style>
"""
h = h.replace('</head>', css + '</head>', 1)

# 4) bannière juste après <body>
banner = """
<div class="rx-nojs" role="note">
  <strong>Tu vois la version simplifiée de la formation.</strong> Ce fichier est ouvert dans un aperçu qui ne lance pas
  les fonctions interactives : la navigation par chapitre, les quiz et la sauvegarde de ta progression ne marchent pas ici.
  Tout le contenu reste lisible ci-dessous. Pour la version complète :
  <ol class="rx-nojs-steps">
    <li><b>Enregistre le fichier</b> sur ton appareil (sur iPhone : « Enregistrer dans Fichiers » ; sur ordinateur : « Télécharger »).</li>
    <li><b>Ouvre-le avec un navigateur</b> : Chrome, Safari, Edge ou Firefox (double-clic sur ordinateur, ou « Ouvrir avec » sur téléphone).</li>
    <li>Garde toujours <b>le même fichier au même endroit</b> : c’est lui qui mémorise ta progression.</li>
  </ol>
</div>
"""
h = re.sub(r'(<body\b[^>]*>)', lambda mm: mm.group(1) + banner, h, count=1)

open(dst, 'w', encoding='utf-8').write(h)
print('patché →', dst, '| taille', round(len(h.encode('utf-8'))/1024), 'Ko')
