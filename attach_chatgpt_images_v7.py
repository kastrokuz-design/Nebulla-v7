# attach_chatgpt_images_v7.py
import argparse, os, time, re
from pathlib import Path
from typing import Optional, Set, List
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from tqdm import tqdm  # pip install tqdm

def cdp_allow_downloads(driver, out_dir: str) -> None:
    """Enable downloads via CDP.""" 
    out = os.path.abspath(out_dir)
    for cmd, params in [
        ("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": out}),
        ("Browser.setDownloadBehavior", {"behavior": "allowAndName", "downloadPath": out, "eventsEnabled": True})
    ]:
        try:
            driver.execute_cdp_cmd(cmd, params)
        except Exception:
            pass  # Ignore CDP errors

def wait_img_ready(driver, tile, timeout: float = 4.0) -> bool:
    """Wait for image to be fully loaded.""" 
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            img = tile.find_element(By.CSS_SELECTOR, "img")
            ready = driver.execute_script("return arguments[0].complete && arguments[0].naturalWidth > 0;", img)
            if ready:
                return True
        except (StaleElementReferenceException, NoSuchElementException):
            return False
        time.sleep(0.1)
    return False

def wait_file_downloaded(dst_dir: Path, before_set: Set[Path], timeout: float = 60.0) -> Optional[Path]:
    """Wait for a new file download to complete.""" 
    t0 = time.time()
    dst = Path(dst_dir)
    while time.time() - t0 < timeout:
        tmp = list(dst.glob("*.crdownload")) + list(dst.glob("*.download"))
        after = set(p for p in dst.glob("*") if p.is_file())
        new_files = [p for p in after if p not in before_set]
        if not tmp and new_files:
            newest = max(new_files, key=lambda p: p.stat().st_mtime)
            return newest
        time.sleep(0.25)
    return None

def detect_ext_by_magic(path: Path) -> str:
    """Detect file extension by magic bytes.""" 
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        signatures = {
            b"\x89PNG\r\n\x1a\n": ".png",
            b"\xff\xd8\xff": ".jpg",
            (b"RIFF", b"WEBP"): ".webp",  # Simplified check
            b"ftypavif": ".avif",
            b"GIF8": ".gif"
        }
        for sig, ext in signatures.items():
            if isinstance(sig, tuple):
                if head[:4] == sig[0] and sig[1] in head[:12]:
                    return ext
            elif sig in head:
                return ext
        return ""
    except Exception:
        return ""

def normalize_extension(p: Path) -> Path:
    """Fix extension if wrong.""" 
    ext = p.suffix.lower()
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}:
        return p
    guessed = detect_ext_by_magic(p)
    if guessed and guessed != ext:
        newp = p.with_suffix(guessed)
        try:
            p.rename(newp)
            return newp
        except Exception:
            pass
    return p

def switch_to_library_tab(driver) -> bool:
    """Switch to the library tab.""" 
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if "chatgpt.com" in driver.current_url and "/library" in driver.current_url:
            return True
    return False

def load_all_tiles(driver) -> List:
    """Scroll to bottom to load all lazy tiles.""" 
    print("[INFO] Chargement de toutes les tuiles... / Loading all tiles...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.0)  # Wait for load
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    print("[INFO] Scroll terminé. / Scroll complete.")

def find_download_button(tile, lang_selectors: List[str]) -> Optional:
    """Find download button with flexible selectors.""" 
    for sel in lang_selectors:
        try:
            btn = tile.find_element(By.CSS_SELECTOR, sel)
            if btn:
                return btn
        except NoSuchElementException:
            continue
    return None

def download_tile(tile, driver, outdir: Path, before: Set[Path], idx: int, max_retries: int = 3, parallel: bool = False) -> bool:
    """Download a single tile with retries.""" 
    actions = ActionChains(driver)
    for attempt in range(max_retries):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tile)
            time.sleep(0.45 if not parallel else 0.15)
            wait_img_ready(driver, tile)
            actions.move_to_element(tile).perform()
            time.sleep(0.15)

            # Direct button
            lang_selectors = [
                "button[aria-label*='Télécharger' i]",
                "button[aria-label*='Download' i]",
                "button[aria-label='Télécharger cette image']",
                "button[aria-label='Download this image']"
            ]
            btn = find_download_button(tile, lang_selectors)
            if btn:
                driver.execute_script("arguments[0].click();", btn)
                timeout = 30 if parallel else 90
                got = wait_file_downloaded(outdir, before, timeout)
                if got:
                    got = normalize_extension(got)
                    print(f"[OK] #{idx}: {got.name}")
                    return True
                else:
                    print(f"[WARN] Timeout DL direct (tuile #{idx}, essai {attempt+1})")
                    continue

            # Fallback: Detail view
            driver.execute_script("arguments[0].click();", tile)
            time.sleep(0.4)
            dl_selectors = [
                "button[aria-label*='Télécharger' i]",
                "button[aria-label*='Download' i]",
                "a[download]"
            ]
            try:
                dl = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.CSS_SELECTOR, " | ".join(dl_selectors))))
                driver.execute_script("arguments[0].click();", dl)
                timeout = 60 if parallel else 120
                got = wait_file_downloaded(outdir, before, timeout)
                if got:
                    got = normalize_extension(got)
                    print(f"[OK] #{idx} (fallback): {got.name}")
                    return True
                else:
                    print(f"[WARN] Timeout DL fallback (tuile #{idx}, essai {attempt+1})")
            except TimeoutException:
                pass

            # Close detail view
            close_js = """
                const c = document.querySelector("button[aria-label*='Close' i], button[aria-label*='Fermer' i]");
                if (c) { c.click(); return true; }
                return false;
            """
            if not driver.execute_script(close_js):
                from selenium.webdriver.common.keys import Keys
                driver.switch_to.active_element.send_keys(Keys.ESCAPE)

            if attempt == max_retries - 1:
                print(f"[ERR] Échec après {max_retries} essais (tuile #{idx})")
                return False
            time.sleep(1.0)  # Retry delay
        except Exception as e:
            print(f"[WARN] Erreur essai {attempt+1} (tuile #{idx}): {e}")
            continue
    return False

def main():
    parser = argparse.ArgumentParser(description="NEBULA v7 — ChatGPT Library Image Downloader")
    parser.add_argument("--out", default=".", help="Dossier de sortie / Output dir")
    parser.add_argument("--debugger", required=True, help="Adresse DevTools (ex: 127.0.0.1:9222)")
    parser.add_argument("--delay", type=float, default=0.45, help="Pause entre tuiles (s) / Delay between tiles")
    parser.add_argument("--parallel", action="store_true", help="Mode semi-parallèle / Semi-parallel mode")
    parser.add_argument("--headless", action="store_true", help="Mode sans UI (debug) / Headless mode")
    parser.add_argument("--max-retries", type=int, default=3, help="Essais max par tuile / Max retries per tile")
    args = parser.parse_args()

    outdir = Path(args.out).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    opts = Options()
    if args.headless:
        opts.add_argument("--headless")
    opts.debugger_address = args.debugger
    prefs = {
        "download.prompt_for_download": False,
        "download.default_directory": str(outdir),
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    opts.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=opts)
    cdp_allow_downloads(driver, str(outdir))

    if not switch_to_library_tab(driver):
        print("[ERR] Aucun onglet /library. Ouvrez https://chatgpt.com/library?tab=images.")
        return

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main div.grid")))
        load_all_tiles(driver)  # Nouvelle feature: load all
        grid = driver.find_element(By.CSS_SELECTOR, "#main div.grid")
        tiles = grid.find_elements(By.CSS_SELECTOR, ":scope > div")
        total = len(tiles)
        print(f"[INFO] {total} tuiles détectées. / {total} tiles found.")

        success = 0
        with tqdm(total=total, desc="Téléchargement / Download", unit="img") as pbar:
            for idx in range(1, total + 1):
                try:
                    tile = driver.find_element(By.CSS_SELECTOR, f"#main div.grid > div:nth-child({idx})")
                except Exception as e:
                    print(f"[WARN] Tuile {idx} introuvable: {e}")
                    pbar.update(1)
                    continue

                before = set(p for p in outdir.glob("*") if p.is_file())
                if download_tile(tile, driver, outdir, before, idx, args.max_retries, args.parallel):
                    success += 1
                time.sleep(args.delay if not args.parallel else 0.2)
                pbar.update(1)

        print(f"[DONE] {success}/{total} images téléchargées. / {success}/{total} images downloaded → {outdir}")

    except Exception as e:
        print(f"[ERR] Erreur générale: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
