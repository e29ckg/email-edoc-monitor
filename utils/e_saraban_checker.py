# document_checker.py
import time, json, random, os, requests
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from utils.logger import log

load_dotenv()
show_browser = os.getenv("SHOW_BROWSER", "false").lower() == "true"
CACHE_FILE = "cache/notified_esaraban.json"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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

def check_esaraban_once():
    document_url = os.getenv("ESARABAN_URL")
    username = os.getenv("ESARABAN_USER")
    password = os.getenv("ESARABAN_PASS")

    if not document_url or not username or not password:
        log("❌ ไม่พบข้อมูล EOFFICE_URL / USER / PASS ใน .env")
        return []

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
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-login/div/div/div[2]/div/div[2]/form/div[1]/dx-text-box/div/div[1]/input")))
        driver.find_element(By.XPATH, "/html/body/app-root/app-login/div/div/div[2]/div/div[2]/form/div[1]/dx-text-box/div/div[1]/input").send_keys(username)
        driver.find_element(By.XPATH, "/html/body/app-root/app-login/div/div/div[2]/div/div[2]/form/div[2]/dx-text-box/div/div[1]/input").send_keys(password)
        driver.find_element(By.XPATH, "/html/body/app-root/app-login/div/div/div[2]/div/div[2]/form/div[4]/dx-button-improve/dx-button/div/span").click()
        time.sleep(15)

        send_telegram_photo(driver, caption="✅ ระบบสารบรรณจังหวัด")
        return []

    except Exception as e:
        log(f"⚠️ ไม่สามารถโหลดเอกสารจาก e-sarabun ได้: {e}")

    finally:
        driver.quit()

    return []