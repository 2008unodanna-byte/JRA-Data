import datetime
import json
import os
import requests

current_date = (
    datetime.datetime.utcnow() + datetime.timedelta(hours=9)
).strftime("%Y%m%d")
print(f"🚀 JRAデータ自動収集を開始します: 対象日 {current_date}")

os.makedirs("data", exist_ok=True)
json_path = f"data/{current_date}.json"

url = f"https://netkeiba.com{current_date}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        print(f"⚠️ データの取得に失敗しました (Status: {response.status_code})")
        raise ValueError("Data source offline")

    raw_data = response.json()
    formatted_data = {"races": []}

    for race_id, race_info in raw_data.get("results", {}).items():
        venue = race_info.get("venue", "中山")
        race_num = int(race_info.get("race_number", 1))

        payback = {
            "win": [
                {
                    "horse_number": int(t["horse_number"]),
                    "payout": int(t["payout"]),
                    "popularity": int(t["popularity"]),
                }
                for t in race_info.get("win", [])
            ],
            "place": [
                {
                    "horse_number": int(f["horse_number"]),
                    "payout": int(f["payout"]),
                    "popularity": int(f["popularity"]),
                }
                for f in race_info.get("place", [])
            ],
        }

        formatted_data["races"].append(
            {"venue": venue, "race_number": race_num, "payback": payback}
        )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)

    print(f"🎉 自動生成成功！: {json_path} を保存しました。")

except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
