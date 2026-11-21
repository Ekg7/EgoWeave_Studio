"""
Download official EPIC-KITCHENS-100 TSM checkpoint (93.1 MB).
Destination: weights/epic_kitchens/tsm_rgb.ckpt
"""

import os
import sys
import urllib.request

TSM_URL = "https://www.dropbox.com/s/5yxnzubch7b6niu/tsm_rgb.ckpt?dl=1"
TARGET_DIR = os.path.join("weights", "epic_kitchens")
TARGET_PATH = os.path.join(TARGET_DIR, "tsm_rgb.ckpt")

def download_tsm():
    os.makedirs(TARGET_DIR, exist_ok=True)
    if os.path.exists(TARGET_PATH) and os.path.getsize(TARGET_PATH) == 97616687:
        print(f"TSM checkpoint already exists and verified ({os.path.getsize(TARGET_PATH)} bytes): {TARGET_PATH}")
        return

    print(f"Downloading TSM checkpoint from {TSM_URL}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(TSM_URL, headers=headers)
    
    with urllib.request.urlopen(req) as resp, open(TARGET_PATH, "wb") as out_file:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024  # 1 MB chunks
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            pct = (downloaded / total * 100) if total else 0
            sys.stdout.write(f"\rDownloaded {downloaded / (1024*1024):.1f} MB / {total / (1024*1024):.1f} MB ({pct:.1f}%)")
            sys.stdout.flush()

    print(f"\nSuccessfully downloaded and saved to {TARGET_PATH} ({os.path.getsize(TARGET_PATH)} bytes).")

if __name__ == "__main__":
    download_tsm()
