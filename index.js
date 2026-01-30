import { google } from "googleapis";

const auth = new google.auth.GoogleAuth({
  credentials: JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON),
  scopes: ["https://www.googleapis.com/auth/spreadsheets"]
});

const sheets = google.sheets({ version: "v4", auth });
const spreadsheetId = process.env.SPREADSHEET_ID;

async function main() {
  try {
    const now = new Date().toLocaleString("ja-JP", { timeZone: "Asia/Tokyo" });
    // テスト用のデータ
    const values = [[now, "釣りニュース巡回", "GitHub Actions 成功！"]];

    await sheets.spreadsheets.values.append({
      spreadsheetId,
      range: "Sheet1!A:C", // ※シート名が「Sheet1」の場合
      valueInputOption: "RAW",
      requestBody: { values }
    });
    console.log("✅ 書き込み完了！");
  } catch (err) {
    console.error("❌ エラー:", err);
    process.exit(1);
  }
}
main();
