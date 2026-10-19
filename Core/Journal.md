# Journal

## 2026-10-19 — Première session
- Arrivée avec 7 vidéos de référence (@alfred.explique) : objectif = reproduire le format en pixel-art et publier sur TikTok en automatique.
- BOS a analysé les 7 vidéos (structure, rythme, palette, typographie).
- Correction de prémisse : les modèles vidéo (Sora 2, etc.) ne conviennent pas à ce format ; la bonne architecture est un pipeline « motion graphics » (illustrations IA + compositing codé + TTS).
- BOS a construit un renderer fonctionnel et rendu une démo de 24 s + une comparaison de 5 palettes (voir `Output/2026-10-19_tiktok-pixel-story/`).
- Profil, objectif et monétisation : pas encore collectés (questions posées en fin de session).

## 2026-10-19 — Suite de session
- Killian a répondu : compte anonyme (pas de prénom), objectif = revenus TikTok, 30 min/jour, voix synthétique française, full automatique accepté.
- Décision BOS : pipeline full automatique sur GitHub Actions avec validation d'1 min par Killian avant publication, puis bascule en auto-publication quand la confiance est établie.
- Lancement d'une orchestration multi-agents : script fact-checké de la vidéo 1 (inondation de mélasse, Boston 1919) + backlog de sujets vérifiés.
- Le moteur de rendu est déplacé dans `tiktok-pipeline/render/`.
- Correction de Killian : la démo réutilisait des plans des vidéos de référence → inacceptable, il veut 0 plagiat, des créations 100 % originales, une image nette et de belles couleurs. Fichiers supprimés, règle ajoutée dans CLAUDE.md.
- Nouvelle demande : recherche internet sur les comptes qui ont déjà automatisé ce type de vidéos et sur ce qui a déjà été fait, pour se différencier.
- Test image ChatGPT (réservoir de Boston 1919) fourni par Killian : couleurs et composition très réussies, mais faux pixel-art (135 000 couleurs, bords flous) et réservoir historiquement faux (silo haut alors que le vrai faisait 15 m de haut pour 27 m de large). BOS a écrit `tiktok-pipeline/render/pixelize.py` : grille nette + palette limitée ou palette fixe de la chaîne pour garantir la cohérence entre images.
- Test image ChatGPT v2 (prompt corrigé par BOS) : réservoir trapu et large conforme à l'histoire, métro aérien présent, couleurs vives. Après post-traitement grille 160 / 32 couleurs, rendu pixel-art net et cohérent. Limite : la grille 160 efface les rivets ; avec le fichier original 1024 px, viser une grille de 192 à 256.
