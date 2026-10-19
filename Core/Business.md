# Business

**Stade :** pré-lancement (idée + références, rien de publié)
**Dernière MAJ :** 2026-10-19

## Projet
Chaîne TikTok « faceless » de storytelling en pixel-art, sur le modèle du compte @alfred.explique :
- Vidéos verticales ~2 min, voix off française, illustrations pixel-art sur fond noir avec halo chaud (jaune dominant), grosses captions animées, petites étiquettes encadrées avec flèches, HUD (année, compteurs).
- Sujets visés : histoires vraies WTF/humour (sans être beauf), histoire, actualité.
- Ambition : production + publication **automatisées**, même qualité d'image que la référence ou mieux.

## Modèle à copier (référence)
@alfred.explique — 7 vidéos analysées : Tour de Pise, Lac Peigneur (1980), le moustique, Reg Spiers (l'homme qui s'est expédié en colis), Edmond Albius (vanille), Barry Marshall (ulcère), le faux Paris de 1918.
Structure récurrente : hook en 1 phrase + chiffre → contexte → « Mais attendez… » (twist) → escalade → chute/leçon → « La prochaine fois… ».
Rythme : une illustration + une caption toutes les 2 à 4 s (≈ 35-45 plans par vidéo).

## Persona (à valider)
Audience TikTok francophone 18-35 ans qui consomme du contenu « culture / histoires incroyables » (type Alfred, Feldup, Hugo Décrypte formats courts).

## Offre / Monétisation
Non défini. Options : Creator Rewards Program (France éligible, vidéos > 1 min), placements de marques, affiliation, ou la chaîne comme vitrine d'un service.

## Marketing
Canal unique : TikTok. Rien publié à ce jour.

## Finances
Budget outils non défini. Coût de production estimé par vidéo (API) : ~1-3 € hors abonnement de publication.

## Équipe
Solo + BOS.

## Outils (cible)
Pipeline codé par BOS : script (LLM) → illustrations pixel-art (API image) → voix (TTS) → compositing (Python/ffmpeg, renderer `Output/2026-10-19_tiktok-pixel-story/pipeline/render.py`) → publication (API tierce TikTok).
