import time, json, random, os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.telegram import send_telegram
from dotenv import load_dotenv

load_dotenv()
show_browser = os.getenv("SHOW_BROWSER", "false").lower() == "true"

CACHE_FILE = "cache/notified_subjects.json"

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.78 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6530.45 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6600.12 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6700.90 Safari/537.36"
    ]
    return random.choice(user_agents)

def format_email_notification(subjects):
    lines = [f"📬 ตรวจสอบอีเมลล่าสุด เวลา {datetime.now().strftime('%H:%M')} น.\n"]
    for idx, item in enumerate(subjects, start=1):
        subject, sender, date = item
        lines.append(f"{idx}️⃣ <b>{sender}</b>\n🔒 {subject}\n📅 {date}\n")
    return "\n".join(lines)

def check_email_loop(email, password, url, check_times, telegram_token, telegram_chat_id):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            notified_subjects = set(json.load(f))
    except:
        notified_subjects = set()

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
        driver.get(url)

        try:
            wait.until(EC.presence_of_element_located((By.ID, 'userNameInput'))).send_keys(email)
            wait.until(EC.presence_of_element_located((By.ID, 'passwordInput'))).send_keys(password)
            wait.until(EC.element_to_be_clickable((By.ID, "submitButton"))).click()
            time.sleep(5)
        except:
            pass

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='option']")))
            emails = driver.find_elements(By.CSS_SELECTOR, "div[role='option']")[:10]

            new_items = []
            for email in emails:
                try:
                    sender = email.find_element(By.CLASS_NAME, "lvHighlightFromClass").text.strip()
                except:
                    sender = "(ไม่พบผู้ส่ง)"
                try:
                    subject = email.find_element(By.CLASS_NAME, "lvHighlightSubjectClass").text.strip()
                except:
                    subject = "(ไม่มีหัวข้อ)"
                try:
                    date = email.find_element(By.CLASS_NAME, "_lvv_M").text.strip()
                except:
                    date = "(ไม่มีวันที่)"

                key = f"{subject} — {sender} — {date}"
                if key not in notified_subjects:
                    new_items.append((subject, sender, date))
                    notified_subjects.add(key)

            if new_items:
                message = format_email_notification(new_items)
                send_telegram(telegram_token, telegram_chat_id, message)
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(list(notified_subjects), f, ensure_ascii=False)
            else:
                msg = f"✅ ไม่มีอีเมลใหม่เวลา {datetime.now().strftime('%H:%M')}"
                print(msg)
                send_telegram(telegram_token, telegram_chat_id, msg)

            time.sleep(5)
            driver.get("https://webmail.workd.go.th/owa/logoff.owa")
            time.sleep(3)

        except Exception as e:
            print("⚠️ ไม่สามารถโหลด inbox ได้:", e)
            send_telegram(telegram_token, telegram_chat_id, "⚠️ ไม่สามารถโหลด inbox ได้")

    finally:
        driver.quit()