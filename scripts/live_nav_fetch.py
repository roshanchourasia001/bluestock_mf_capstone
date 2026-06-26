import requests
import pandas as pd
from pathlib import Path
import time

RAW = Path("data/raw")

SCHEMES = {
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_LargeCap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip",
    "125497": "HDFC_Top100",
}

BASE_URL = "https://api.mfapi.in/mf/{}"

print("=" * 50)
print("LIVE NAV FETCH — mfapi.in")
print("=" * 50)

all_nav = []

for code, name in SCHEMES.items():
    try:
        url = BASE_URL.format(code)
        response = requests.get(url, timeout=10)
        data = response.json()

        meta     = data.get("meta", {})
        nav_data = data.get("data", [])

        print(f"\n✅ {name} ({code})")
        print(f"   Fund : {meta.get('scheme_name', 'N/A')}")
        print(f"   Rows : {len(nav_data)}")

        df = pd.DataFrame(nav_data)
        df['amfi_code'] = code
        df['fund_name'] = name

        out = RAW / f"live_nav_{code}_{name}.csv"
        df.to_csv(out, index=False)
        print(f"   Saved: {out}")

        all_nav.append(df)
        time.sleep(0.5)

    except Exception as e:
        print(f"❌ {name} failed: {e}")

if all_nav:
    combined = pd.concat(all_nav, ignore_index=True)
    combined.to_csv(RAW / "live_nav_all_schemes.csv", index=False)
    print(f"\n📊 Combined: {len(combined)} rows saved!")

print("\n🎉 Done!")