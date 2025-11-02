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
from utils.telegram import send_photo
import socket, urllib.parse
import requests


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def check_dns(url):
    try:
        hostname = urllib.parse.urlparse(url).hostname
        socket.gethostbyname(hostname)
        return True
    except Exception as e:
        log(f"❌ DNS resolve ไม่ได้: {e}")
        return False


load_dotenv()
show_browser = os.getenv("SHOW_BROWSER", "false").lower() == "true"
CACHE_FILE = "cache/notified_subjects.json"

MAX_EMAILS = int(os.getenv("MAX_EMAILS", "5"))
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "true").lower() == "true"

def send_telegram_photo(driver, caption=""):
    screenshot_path = "cache/screenshot.png"
    driver.save_screenshot(screenshot_path)
    try:
        with open(screenshot_path, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
                files={"photo": f},
                timeout=20
            )
        print(">>> ส่ง screenshot ไป Telegram แล้ว")
    except Exception as e:
        print(f"ไม่สามารถส่ง screenshot Telegram: {e}")

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

    if not check_dns(url):
        return []

    prefs = {
        "profile.default_content_setting_values.notifications": 2  # 1=allow, 2=block
    }
    options = webdriver.ChromeOptions()
    if not show_browser:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent={get_random_user_agent()}")
    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    cookies_path = "cache/cookies.json"
    logged_in = False

    try:
        driver.get(url)

        # if os.path.exists(cookies_path):
            # try:
            #     with open(cookies_path, "r", encoding="utf-8") as f:
            #         cookies = json.load(f)
            #         for cookie in cookies:
            #             driver.add_cookie(cookie)
            #     driver.refresh()
            #     log("🍪 โหลด cookies แล้วลองเข้าใช้งาน")

            #     # ตรวจสอบว่ามี element ที่บ่งบอกว่า login แล้ว
            #     try:
            #         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='option']")))
            #         logged_in = True
            #         log("✅ ใช้ cookies login สำเร็จ")
            #     except:
            #         log("⚠️ cookies ใช้ไม่ได้ ต้อง login ใหม่")
            # except Exception as e:
            #     log(f"⚠️ โหลด cookies ไม่สำเร็จ: {e}")

        # ถ้า cookies ใช้ไม่ได้ → login ปกติ
        # if not logged_in:

        try:
            driver.refresh()
            wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(email)
            time.sleep(1)
            wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.ID, 'loginButton'))).click()
            time.sleep(5)  # รอโหลดหน้า
            
            driver.get('https://mail.workd.go.th/modern/email/Inbox')
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//main[contains(@class,'zimbra-client_app_main')]")
            ))

            log("✅ เข้าสู่ระบบอีเมลสำเร็จ")

            # ถ่าย screenshot
            send_telegram_photo(driver, caption="✅ เข้าสู่ระบบอีเมลสำเร็จ")

            # บันทึก cookies ใหม่
            # with open(cookies_path, "w", encoding="utf-8") as f:
            #     json.dump(driver.get_cookies(), f, ensure_ascii=False, indent=2)
            # log(f"🍪 บันทึก cookies ลง {cookies_path} เรียบร้อย")

            logged_in = True
        except Exception as e:
            log(f"⚠️ เข้าสู่ระบบล้มเหลว: {e}")

    

    finally:
        driver.quit()
    return []
        