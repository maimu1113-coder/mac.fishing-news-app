import os
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import json

def main():
    print("--- 釣りニュース取得開始 ---")
    # 取得先をより安定した「ニュース一覧」に変更
    url = "https://www.fimosw.com/news"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' # 文字化け防止
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        # サイト内の「記事タイトル」と思われるリンクを幅広く探す
        # aタグの中で、hrefに "/news/" が含まれるものを抽出
        for a_tag in soup.find_all('a', href=True):
            title = a_tag.get_text(strip=True)
            link = a_tag['href']
            
            # 文字数が多く、ニュース記事っぽいものだけを拾う
            if len(title) > 10 and "/news/" in link:
                if not link.startswith('http'):
                    link = "https://www.fimosw.com" + link
                
                # 重複チェック
                if [title, link] not in news_list:
                    news_list.append([title, link])
            
            if len(news_list) >= 20: # 最大20件
                break
        
        if not news_list:
            print("再試行中：別のタグを探します...")
            # 念のためh3タグなどもチェック
            for h in soup.find_all(['h3', 'h4']):
                a = h.find('a')
                if a:
                    news_list.append([a.text.strip(), "https://www.fimosw.com" + a['href']])

        if not news_list:
            print("ニュースが見つかりませんでした。サイトの構造が変わった可能性があります。")
            return

        print(f"{len(news_list)}件のニュースを発見しました！")

        # Google Sheets への書き込み
        SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
        JSON_DATA = os.environ["GCP_SA_KEY"]
        info = json.loads(JSON_DATA)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        client = gspread.authorize(creds)
        sh = client.open_by_key(SPREADSHEET_ID)
        
        # 一番左のシートに書き込む
        sheet = sh.get_worksheet(0)
        sheet.clear()
        sheet.update('A1', [["タイトル", "URL"]])
        sheet.update('A2', news_list)
        
        print("スプレッドシートへの書き込みが完了しました！")

    except Exception as e:
        print(f"エラー発生: {e}")

if __name__ == "__main__":
    main()
