import requests

def send_telegram(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print("❌ ส่ง Telegram ไม่สำเร็จ:", response.text)
    except Exception as e:
        print("⚠️ เกิดข้อผิดพลาดในการส่ง Telegram:", e)