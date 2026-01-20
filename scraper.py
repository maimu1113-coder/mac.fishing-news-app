import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. 認証設定 (GitHubのSecretsから読み込み)
def get_gspread_client():
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # GitHubのSettingsで設定する秘密鍵を読み込む
    service_account_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    return gspread.authorize(creds)

def main():
    try:
        gc = get_gspread_client()
        # スプレッドシートの名前を「釣具ニュース」に設定してください
        sh = gc.open("釣具ニュース")
        worksheet = sh.get_worksheet(0)

        # 巡回するメーカーの設定
        targets = [
            {"brand": "シマノ", "url": "https://fish.shimano.com/ja-JP/news.html", "selector": ".news-list-item"},
            {"brand": "ダイワ", "url": "https://www.daiwa.com/jp/fishing/news/index.html", "selector": ".news-list li"},
            {"brand": "ジャッカル", "url": "https://www.jackall.co.jp/saltwater/news/", "selector": "article"}
        ]
        
        new_rows = []
        for t in targets:
            res = requests.get(t["url"], timeout=15)
            soup = BeautifulSoup(res.content, "html.parser")
            items = soup.select(t["selector"])[:3] # 最新3件
            
            for item in items:
                title = item.get_text(strip=True)
                # スプレッドシートに書き込む形式に整理
                new_rows.append([
                    t["brand"], 
                    title, 
                    t["url"], 
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                ])
        
        if new_rows:
            # 2行目（見出しの下）にデータを挿入
            worksheet.insert_rows(new_rows, 2)
            print(f"{len(new_rows)}件の更新に成功しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
