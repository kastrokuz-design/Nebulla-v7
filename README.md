# 🚀 Nebulla v7 – ChatGPT Library Image Downloader  

**Nebulla v7** est un outil pour **télécharger automatiquement toutes les images de la Bibliothèque ChatGPT**.  
Il ouvre Chrome en mode debug, scrolle automatiquement jusqu’en bas pour charger toutes les images, puis les télécharge une par une.  

**Nebulla v7 is a tool to automatically download all images from your ChatGPT Library.**  
It launches Chrome in debug mode, auto-scrolls to the bottom to load all images, then downloads them one by one.  

---

## 📦 Contenu / Contents
- `README_v7.txt` → mode d’emploi / instructions  
- `NEBULA_LAUNCH_v7.py` → launcher cross-platform (Mac/Linux/Win)  
- `NEBULA_LAUNCH_v7.bat` → launcher Windows (double-click)  
- `attach_chatgpt_images_v7.py` → Selenium worker (scroll + download)  

---

## ⚠️ IMPORTANT
- **FR** : NE PAS MINIMISER la fenêtre Chrome pendant le téléchargement.  
  Le scroll automatique nécessite que la fenêtre reste **VISIBLE** à l’écran.  

- **EN** : DO NOT MINIMIZE the Chrome window during download.  
  The auto-scroll requires the window to remain **VISIBLE** on screen.  

---

## 🔧 Prérequis / Requirements
- [Google Chrome](https://www.google.com/chrome/)  
- [Python 3.9+](https://www.python.org/downloads/)  
- Modules Python / Python modules :  
  ```bash
  pip install selenium tqdm
