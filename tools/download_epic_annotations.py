"""
Download official EPIC-KITCHENS-100 annotation CSVs.
Target directory: data/annotations/epic_kitchens/
"""
import os
import urllib.request

FILES = [
    "EPIC_100_verb_classes.csv",
    "EPIC_100_noun_classes.csv",
    "EPIC_100_train.csv",
    "EPIC_100_validation.csv"
]

BASE_URL = "https://raw.githubusercontent.com/epic-kitchens/epic-kitchens-100-annotations/master/"
TARGET_DIR = os.path.join("data", "annotations", "epic_kitchens")

def download_file(filename: str):
    os.makedirs(TARGET_DIR, exist_ok=True)
    target_path = os.path.join(TARGET_DIR, filename)
    url = BASE_URL + filename
    print(f"Downloading {filename} from {url}...")
    urllib.request.urlretrieve(url, target_path)
    size_kb = os.path.getsize(target_path) / 1024
    print(f"Saved {target_path} ({size_kb:.1f} KB)")

def main():
    for f in FILES:
        download_file(f)
    print("All EPIC-KITCHENS-100 annotation files downloaded successfully.")

if __name__ == "__main__":
    main()
