import os
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import json

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
        for item in items[:15]:
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

        info = json.loads(JSON_DATA)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Sheet1")
        
        sheet.clear()
        sheet.update('A1', [['タイトル', 'URL']])
        sheet.update('A2', news_list)
        print(f"成功！{len(news_list)}件のニュースを書き込みました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
