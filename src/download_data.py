from pathlib import Path
from urllib.request import urlretrieve

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "01_facebook_ads.csv": "https://raw.githubusercontent.com/ej29-r3d/Marketing-Analytics-Assignments/main/marketing-analyst-assignment/01_facebook_ads.csv",
    "02_google_ads.csv": "https://raw.githubusercontent.com/ej29-r3d/Marketing-Analytics-Assignments/main/marketing-analyst-assignment/02_google_ads.csv",
    "03_tiktok_ads.csv": "https://raw.githubusercontent.com/ej29-r3d/Marketing-Analytics-Assignments/main/marketing-analyst-assignment/03_tiktok_ads.csv",
}


def main() -> None:
    for filename, url in FILES.items():
        output_path = DATA_DIR / filename
        print(f"Downloading {filename}...")
        urlretrieve(url, output_path)
        print(f"Saved to {output_path}")

    print("\nDone. Files now in ./data")


if __name__ == "__main__":
    main()