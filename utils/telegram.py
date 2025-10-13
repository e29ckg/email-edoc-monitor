import os
import requests
from utils.logger import log

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def notify(items, source="unknown"):
    if not TOKEN or not CHAT_ID:
        log("❌ ไม่พบ TELEGRAM_TOKEN หรือ CHAT_ID")
        return

    emoji = {
        "email": "📧",
        "document": "📄"
    }.get(source, "🔔")

    for idx, item in enumerate(items, start=1):
        title = item.get("title", "(ไม่มีหัวข้อ)")
        timestamp = item.get("timestamp") or item.get("receive_date") or item.get("doc_date") or "(ไม่มีเวลา)"
        sender = item.get("sender", "(ไม่พบผู้ส่ง)")

        msg = (
            f"{emoji} แจ้งเตือนจาก {source}\n"
            f"{idx}️⃣ <b>{title}</b>\n"
            f"👤 จาก: {sender}\n"
            f"🕒 เวลา: {timestamp}"
        )

        # เพิ่มรายละเอียดสำหรับ document
        if source == "document":
            msg += f"\n📁 เลขรับ: {item.get('register', '-')}\n🏢 หน่วยงาน: {item.get('sender', '-')}\n📎 ไฟล์: {item.get('file_name', '-')}"
        
        # ส่งข้อความ
        try:
            res = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
            )
            if not res.ok:
                log(f"⚠️ ส่ง Telegram ไม่สำเร็จ: {res.text}")
        except Exception as e:
            log(f"⚠️ Telegram error: {e}")