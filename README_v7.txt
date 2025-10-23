NEBULA v7 — ChatGPT Library Image Downloader (Improved)

FR — Mode d'emploi
------------------
1) Lancez NEBULA_LAUNCH_v7.py (ou .bat pour Windows)
2) Chrome s'ouvre en mode debug avec un profil propre.
3) Connectez-vous à ChatGPT si nécessaire, puis ouvrez l'onglet Bibliothèque > Images.
4) Revenez dans la fenêtre launcher et appuyez sur une touche pour démarrer.
5) Le script charge TOUTES les images (scroll auto), puis télécharge une par une.
6) Les fichiers sont enregistrés dans le dossier: out/
7) Options: --parallel pour accélérer, --headless pour mode sans UI.

EN — How to use
---------------
1) Run NEBULA_LAUNCH_v7.py (or .bat for Windows)
2) Chrome opens in debug mode with a fresh profile.
3) Sign in to ChatGPT if needed, then open Library > Images tab.
4) Go back to the launcher window and press any key to start.
5) Script auto-scrolls to load ALL images, then downloads one-by-one.
6) Files saved to: out/
7) Options: --parallel to speed up, --headless for UI-less mode.

Notes
-----
- Basé sur v6d, mais avec scroll auto, progression, retries, et options.
- Mode parallel: Clics rapides, mais downloads séquentiels (stable + rapide).
- Si Chrome ouvert ailleurs, fermez-le avant.
- Dépendances: selenium, tqdm (pip install si besoin).
- Cross-platform: Python launcher pour Mac/Linux/Windows.

Crédits / Credits
-----------------
- kastrokuz-design (project owner)
- ChatGPT assistant (original)
- Grok (xAI) — Améliorations v7
