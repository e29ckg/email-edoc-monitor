import time, json, random, os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils.telegram import send_telegram
from dotenv import load_dotenv

load_dotenv()
show_browser = os.getenv("SHOW_BROWSER", "false").lower() == "true"

CACHE_FILE = "cache/notified_documents.json"

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.78 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6530.45 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6600.12 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6700.90 Safari/537.36"
    ]
    return random.choice(user_agents)

def format_document_notification(entries):
    lines = [f"📬 รายการหนังสือเข้า 5 รายการล่าสุด ({datetime.now().strftime('%d/%m/%Y %H:%M')}):\n"]
    for idx, doc in enumerate(entries, start=1):
        lines.append(
            f"{idx}️⃣ <b>{doc['title']}</b>\n"
            f"📁 เลขรับ: {doc['register']}\n"
            f"📄 เลขที่หนังสือ: {doc['doc_no']}\n"
            f"🏢 หน่วยงาน: {doc['sender']}\n"
            f"🗓 เอกสาร: {doc['doc_date']}\n"
            f"📥 รับ: {doc['receive_date']}\n"
            f"👤 เจ้าหน้าที่: {doc['officer']}\n"
            f"📎 ไฟล์: {doc['file_name']}\n"
        )
    return "\n".join(lines)

def check_documents(document_url, username, password, telegram_token, telegram_chat_id):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            notified = set(json.load(f))
    except:
        notified = set()

    options = webdriver.ChromeOptions()
    if not show_browser:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent={get_random_user_agent()}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(document_url)
        time.sleep(3)
        wait.until(EC.presence_of_element_located((By.ID, "loginForm:username")))
        driver.find_element(By.ID, "loginForm:username").send_keys(username)
        driver.find_element(By.ID, "loginForm:password").send_keys(password)
        driver.find_element(By.ID, "loginForm:cmdLogin").click()
        time.sleep(5)

        driver.get('http://e-office.coj.intra/ESB/imd001')
        time.sleep(5)

        wait.until(EC.presence_of_element_located((By.ID, "listForm:dataTable_data")))
        rows = driver.find_elements(By.CSS_SELECTOR, 'tbody#listForm\\:dataTable_data > tr')[:5]

        new_entries = []
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                register = cells[3].text.strip()
                doc_no = cells[4].text.strip()
                title = cells[5].text.strip()
                sender = cells[6].text.strip()
                doc_date = cells[8].text.strip()
                receive_date = cells[9].text.strip()
                officer = cells[10].text.strip()
                file_name = cells[11].find_element(By.TAG_NAME, "a").get_attribute("title")

                key = f"{register}-{doc_no}-{title}"
                if key not in notified:
                    new_entries.append({
                        "register": register,
                        "doc_no": doc_no,
                        "title": title,
                        "sender": sender,
                        "doc_date": doc_date,
                        "receive_date": receive_date,
                        "officer": officer,
                        "file_name": file_name
                    })
                    notified.add(key)
            except Exception as e:
                print("⚠️ ดึงข้อมูลแถวไม่สำเร็จ:", e)

        if new_entries:
            message = format_document_notification(new_entries)
            send_telegram(telegram_token, telegram_chat_id, message)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(list(notified), f, ensure_ascii=False)
        else:
            msg = f"✅ ไม่มีหนังสือเข้าใหม่เวลา {datetime.now().strftime('%H:%M')}"
            print(msg)
            send_telegram(telegram_token, telegram_chat_id, msg)

    except Exception as e:
        print("⚠️ ไม่สามารถโหลดเอกสาร:", e)
        send_telegram(telegram_token, telegram_chat_id, "⚠️ ไม่สามารถโหลดเอกสารจาก e-office ได้")
    finally:
        driver.quit()