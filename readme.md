📄 README.md
# 📬 Email & Document Monitor for COJ

ระบบตรวจสอบอีเมลจาก Outlook Web และหนังสือเข้าจากระบบ e-office ของกรมราชการ พร้อมแจ้งเตือนผ่าน Telegram อัตโนมัติ

---

## ✅ คุณสมบัติ

- ตรวจสอบอีเมลใหม่จาก Outlook Web Access (OWA)
- ตรวจสอบหนังสือเข้า 5 รายการล่าสุดจากระบบ e-office
- แจ้งเตือนผ่าน Telegram เฉพาะรายการใหม่
- ใช้ cache เพื่อหลีกเลี่ยงการแจ้งซ้ำ
- รองรับ headless mode หรือเปิดเบราว์เซอร์จริงผ่าน `.env`
- พร้อม deploy ด้วย Task Scheduler หรือ batch file

---

## 📁 โครงสร้างโปรเจกต์


email-monitor/ ├── .env ├── main.py ├── requirements.txt ├── run_monitor.bat ├── setup_monitor.bat ├── cache/ │   ├── notified_subjects.json │   └── notified_documents.json ├── utils/ │   ├── telegram.py │   ├── email_checker.py │   └── document_checker.py

---

## ⚙️ การติดตั้ง

1. ติดตั้ง Python 3.10+
2. รัน `setup_monitor.bat` เพื่อสร้าง virtual environment และติดตั้ง dependencies
3. ตั้งค่า `.env` ด้วยข้อมูลของคุณ

```env
EMAIL_USER=your_email@coj.go.th
EMAIL_PASS=your_password
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
OWA_URL=https://webmail.workd.go.th/owa
DOCUMENT_URL=http://e-office.coj.intra/ESB/login.xhtml
SHOW_BROWSER=false



🚀 การใช้งาน
- รัน run_monitor.bat เพื่อเริ่มตรวจสอบทันที
- หรือใช้ Task Scheduler ตั้งเวลาให้รันอัตโนมัติทุกวัน

🧠 ข้อแนะนำ
- หากต้องการดูการทำงานของ Selenium → ตั้ง SHOW_BROWSER=true ใน .env
- หากต้องการ deploy บนเครื่องอื่น → copy ทั้งโฟลเดอร์และรัน setup_monitor.bat

📦 Dependencies
- selenium
- webdriver-manager
- python-dotenv
- requests
ติดตั้งผ่าน:
pip install -r requirements.txt



📬 ตัวอย่างข้อความแจ้งเตือน
📬 ตรวจสอบอีเมลล่าสุด เวลา 09:00 น.
1️⃣ <b>สำนักบริหารทรัพย์สิน</b>
🔒 บัญชีนวัตกรรมไทย
📅 10-10-2568 17:00



🛡️ ความปลอดภัย
- ข้อมูลลับเก็บไว้ใน .env และไม่ควร push ขึ้น Git
- เพิ่ม .env, cache/, และ venv/ ลงใน .gitignore

👨‍💻 ผู้พัฒนา
พัฒนาโดย [phayao] — Fullstack Architect
ระบบนี้ออกแบบมาเพื่อใช้งานจริงในสภาพแวดล้อมราชการ พร้อมความยืดหยุ่นและความปลอดภัยระดับ production
