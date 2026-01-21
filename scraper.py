import os
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import json

# 設定
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
JSON_DATA = os.environ["GCP_SA_KEY"]

def main():
    # ニュース取得（例として釣具の最新情報を取得）
    url = "https://www.fimosw.com/news" # 釣りニュースサイトの例
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    news_list = []
    # 記事タイトルとリンクを抽出（サイトの構造に合わせて調整）
    for item in soup.select('h3 a')[:10]:
        title = item.get_text(strip=True)
        link = item.get('href')
        if not link.startswith('http'):
            link = "https://www.fimosw.com" + link
        news_list.append([title, link])

    if not news_list:
        print("ニュースが見つかりませんでした")
        return

    # Google Sheets API 認証
    info = json.loads(JSON_DATA)
    creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    
    # スプレッドシートへ書き込み
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Sheet1")
        
        # 既存の内容をクリアして新しく書き込む
        sheet.clear()
        sheet.update('A1', [['タイトル', 'URL']])
        sheet.update('A2', news_list)
        print("スプレッドシートの更新に成功しました！")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
