import os
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import json

# GitHubのSecretsから読み込み
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
JSON_DATA = os.environ["GCP_SA_KEY"]

def main():
    print("--- 釣りニュース取得開始 ---")
    url = "https://www.fimosw.com/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        items = soup.find_all('h3')
        for item in items[:20]: # 20件取得
            a_tag = item.find('a')
            if a_tag:
                title = a_tag.get_text(strip=True)
                link = a_tag.get('href')
                if not link.startswith('http'):
                    link = "https://www.fimosw.com" + link
                news_list.append([title, link])
        
        if not news_list:
            print("ニュースが見つかりませんでした")
            return

        # 認証
        info = json.loads(JSON_DATA)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        client = gspread.authorize(creds)
        
        # スプレッドシートを開く
        sh = client.open_by_key(SPREADSHEET_ID)
        
        # 「News」シートを取得、なければ作成
        try:
            sheet = sh.worksheet("News")
        except:
            sheet = sh.add_worksheet(title="News", rows="100", cols="5")
        
        # 【重要】一度シートの内容と書式を完全にリセット
        sheet.clear()
        
        # 1行目からデータを流し込む
        data = [["タイトル", "URL"]] + news_list
        sheet.update('A1', data)
        
        print(f"成功！{len(news_list)}件のニュースを1行目から書き込みました。")

    except Exception as e:
        print(f"エラー発生: {e}")

if __name__ == "__main__":
    main()
