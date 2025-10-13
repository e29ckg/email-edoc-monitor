# email_checker.py
import time, json, random, os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from utils.logger import log

load_dotenv()
show_browser = os.getenv("SHOW_BROWSER", "false").lower() == "true"
CACHE_FILE = "cache/notified_subjects.json"

MAX_EMAILS = int(os.getenv("MAX_EMAILS", "5"))
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "true").lower() == "true"

def get_random_user_agent():
    user_agents = [
        # Windows 11 + Chrome 129
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6700.90 Safari/537.36",

        # Windows 10 + Firefox 128
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",

        # macOS 14 + Safari 18
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",

        # Linux + Chrome 129
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6700.90 Safari/537.36",

        # Windows 11 + Edge 129
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6700.90 Safari/537.36 Edg/129.0.6700.90"
    ]
    return random.choice(user_agents)

def check_email_once():
    email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    url = os.getenv("OWA_URL")

    if not email or not password or not url:
        log("❌ ไม่พบข้อมูล OUTLOOK_EMAIL / PASSWORD / URL ใน .env")
        return []

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

    new_items = []

    try:
        driver.get(url)

        # เข้าสู่ระบบ
        try:
            wait.until(EC.presence_of_element_located((By.ID, 'userNameInput'))).send_keys(email)
            wait.until(EC.presence_of_element_located((By.ID, 'passwordInput'))).send_keys(password)
            wait.until(EC.element_to_be_clickable((By.ID, "submitButton"))).click()
            time.sleep(5)
        except Exception as e:
            log(f"⚠️ เข้าสู่ระบบล้มเหลว: {e}")

        # โหลด inbox
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='option']")))
            emails = driver.find_elements(By.CSS_SELECTOR, "div[role='option']")[:MAX_EMAILS]

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
                    new_items.append({
                        "title": subject,
                        "sender": sender,
                        "timestamp": date
                    })
                    notified_subjects.add(key)

            # อัปเดต cache
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(list(notified_subjects), f, ensure_ascii=False)

            if new_items and NOTIFY_EMAIL:
                return new_items

        except Exception as e:
            log(f"⚠️ ไม่สามารถโหลด inbox ได้: {e}")

        # ออกจากระบบ
        try:
            driver.get("https://webmail.workd.go.th/owa/logoff.owa")
            time.sleep(3)
        except:
            pass

    finally:
        driver.quit()
        
    return new_items