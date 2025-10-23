# NEBULA_LAUNCH_v7.py
import os
import sys
import subprocess
import tempfile
import shutil
import time

def main():
    print("=" * 70)
    print(" NEBULA v7 — Bibliothèque Images / Library Images")
    print("=" * 70)
    print("FR:\n  1) Lance Chrome en debug avec profil propre.\n  2) Connectez-vous à ChatGPT si besoin.\n  3) Ouvrez 'Bibliothèque > Images'.\n  4) Appuyez sur une touche pour démarrer.\n")
    print("EN:\n  1) Launches Chrome in debug with fresh profile.\n  2) Sign in to ChatGPT if needed.\n  3) Open 'Library > Images' tab.\n  4) Press any key to start.\n")
    print("Options: python attach_chatgpt_images_v7.py --parallel --out out/")
    print("Credits: You + ChatGPT + Grok (xAI)")
    print("=" * 70)

    # Setup
    outdir = os.path.join(os.getcwd(), "out")
    os.makedirs(outdir, exist_ok=True)

    # Find Chrome (cross-platform)
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",    # Win x64
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",  # Win x86
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"),  # Win user
        "google-chrome",  # Linux
        "chrome"  # Fallback
    ]
    chrome = next((p for p in chrome_paths if os.path.exists(p)), "chrome")

    # Temp profile
    tmpdir = tempfile.mkdtemp(prefix="nebula_profile_v7_")
    try:
        url = "https://chatgpt.com/library?tab=images"
        cmd = [chrome, f"--remote-debugging-port=9222", f"--user-data-dir={tmpdir}", "--new-window", url]
        subprocess.Popen(cmd)
        print(f"[INFO] Chrome lancé: {url} (port 9222, profil: {tmpdir})")

        input("Quand prêt (connecté et onglet ouvert), appuyez sur Entrée... / When ready, press Enter...")
        print("[INFO] Démarrage du téléchargement... / Starting download...")

        # Run script
        py_script = os.path.join(os.getcwd(), "attach_chatgpt_images_v7.py")
        cmd = [sys.executable, py_script, "--out", outdir, "--debugger", "127.0.0.1:9222"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        err = result.returncode

        print("=" * 70)
        if err == 0:
            print(f"FR: Terminé ! Fichiers dans: {outdir}")
            print(f"EN: Done! Files in: {outdir}")
        else:
            print(f"FR: Erreur {err}. Log: {result.stderr}")
            print(f"EN: Error {err}. Log: {result.stderr}")
        print("Credits: You + ChatGPT + Grok (xAI)")
        print("=" * 70)
        input("Appuyez sur Entrée pour fermer... / Press Enter to close...")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)  # Cleanup

if __name__ == "__main__":
    main()
