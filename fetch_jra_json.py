import json
from pathlib import Path
import pandas as pd

# ==========================================
# 1. 保存先ディレクトリ（dataフォルダ）の準備
# ==========================================
# フォルダが存在しない場合は自動で作成します（既にあれば何もしません）
data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. JSONファイルの保存（綺麗にインデント・日本語対応）
# ==========================================
json_file_path = data_dir / "jra_payout.json"

# サンプルデータ（辞書やリスト）
sample_json_data = {
    "race_id": "202606010111",
    "payouts": [
        {"bet_type": "win", "horse_number": 5, "yen": 320},
        {"bet_type": "place", "horse_number": 5, "yen": 130}
    ]
}

# データをファイルに書き込む
with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(
        sample_json_data, 
        f, 
        ensure_ascii=False, # 日本語をUnicodeエスケープ（\uXXXX）させずにそのまま保存
        indent=4            # 読みやすいようにインデントを整える
    )

print(f"JSONを保存しました: {json_file_path}")


# ==========================================
# 3. CSVファイルの保存（Pandas・Excel対応）
# ==========================================
csv_file_path = data_dir / "jra_results.csv"

# サンプルデータ（DataFrame）
df = pd.DataFrame([
    {"race_id": "202606010111", "rank": 1, "horse_name": "テイエムオペラオー"},
    {"race_id": "202606010111", "rank": 2, "horse_name": "メイショウドトウ"}
])

# CSVとして保存
df.to_csv(
    csv_file_path, 
    index=False,        # 余計なインデックス列を出力しない
    encoding="utf-8-sig" # WindowsのExcelで開いたときに日本語が文字化けしないようにする魔法の指定
)

print(f"CSVを保存しました: {csv_file_path}")
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
