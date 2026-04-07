from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")

FILES = [
    "01_facebook_ads.csv",
    "02_google_ads.csv",
    "03_tiktok_ads.csv",
]

for file_name in FILES:
    path = DATA_DIR / file_name
    df = pd.read_csv(path)

    print(f"\n{'=' * 80}")
    print(file_name)
    print(f"{'=' * 80}")
    print("Shape:", df.shape)
    print("Columns:", list(df.columns))
    print("\nDtypes:")
    print(df.dtypes)
    print("\nSample:")
    print(df.head())
    print("\nMissing values:")
    print(df.isna().sum())