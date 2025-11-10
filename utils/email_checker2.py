import time, json, random, os, socket, urllib.parse, requests
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

# โหลดค่า .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
email = os.getenv("EMAIL_USER2")
password = os.getenv("EMAIL_PASS2")
url = os.getenv("OWA_URL2")

show_browser = os.getenv("SHOW_BROWSER", "false").lower() == "true"
CACHE_FILE = "cache/notified_subjects.json"
MAX_EMAILS = int(os.getenv("MAX_EMAILS", "5"))
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "true").lower() == "true"
cookies_path = "cache/cookies2.json"

def check_dns(url):
    try:
        hostname = urllib.parse.urlparse(url).hostname
        socket.gethostbyname(hostname)
        return True
    except Exception as e:
        log(f"❌ DNS resolve ไม่ได้: {e}")
        return False

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
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6700.90 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6700.90 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6700.90 Safari/537.36 Edg/129.0.6700.90"
    ]
    return random.choice(user_agents)

def accept_cookies(driver):
    """
    กดยอมรับการใช้คุกกี้ ถ้ามี banner ปรากฏ
    """
    try:
        # ตัวอย่าง locator ของปุ่มยอมรับคุกกี้
        if safe_click(driver, (By.XPATH, "/html/body/app-root/app-login-layout/app-cookies-banner/div/div[2]/div[2]/p-button/button/span")):
            time.sleep(1)
            safe_click(driver, (By.XPATH, "/html/body/app-root/app-login-layout/app-cookies-banner/app-confirm-dialog[1]/p-dialog/div/div/div[3]/div/div/p-button[2]/button"))
            log("🍪 กดยอมรับคุกกี้เรียบร้อย")
            return True
        elif safe_click(driver, (By.XPATH, "/html/body/app-root/app-login-layout/app-cookies-banner/div/p-button/button/span")):
            log("🍪 Accepted cookies successfully")
            return True
    except Exception as e:
        log(f"⚠️ ไม่มี banner คุกกี้ให้กด: {e}")
    return False

def safe_click(driver, locator, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        try:
            element.click()
            return True
        except:
            try:
                overlay = driver.find_element(By.CSS_SELECTOR, "div.fixed.z-[9999]")
                driver.execute_script("arguments[0].style.display='none';", overlay)
            except:
                pass
            driver.execute_script("arguments[0].click();", element)
            return True
    except Exception as e:
        print(f"❌ safe_click ล้มเหลว: {e}")
        return False
    
def check_login(driver):
    """
    ตรวจสอบว่า session ปัจจุบันอยู่ในหน้า login หรือไม่
    ถ้าใช่ → คืนค่า False (ยังไม่ได้ login)
    ถ้าไม่ใช่ → คืนค่า True (login แล้ว)
    """
    try:
        current_url = driver.current_url
        if "workd.go.th/auth/login" in current_url:
            log("⚠️ อยู่ในหน้า login → ยังไม่ได้เข้าสู่ระบบ")
            return False
        else:
            log("✅ ไม่อยู่ในหน้า login → เข้าสู่ระบบแล้ว")
            return True
    except Exception as e:
        log(f"❌ ตรวจสอบ login ล้มเหลว: {e}")
        return False
    
# -------------------------------
# ฟังก์ชัน manage_cookies
# -------------------------------
def manage_cookies(driver, cookies_path, wait, email, password):
    logged_in = False
    if os.path.exists(cookies_path):
        try:
            with open(cookies_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            driver.refresh()

            log("🍪 โหลด cookies แล้วลองเข้าใช้งาน")
            try:
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, "/html/body/app-root/app-secure-layout/header/div/div/div[2]/div/button/div")
                ))
                log("✅ พบข้อความ 'บัญชีของคุณ' — เข้าสู่ระบบสำเร็จ")
                return True
            except:
                log("⚠️ cookies ใช้ไม่ได้ ต้อง login ใหม่")
                try:
                    os.remove(cookies_path)
                    log("🗑️ ลบ cookies.json ที่หมดอายุเรียบร้อย")
                except Exception as e:
                    log(f"⚠️ ลบ cookies.json ไม่สำเร็จ: {e}")
        except Exception as e:
            log(f"⚠️ โหลด cookies ไม่สำเร็จ: {e}")

    # ถ้า cookies ใช้ไม่ได้ → login ใหม่
    try:
        wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(email)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.p-password-input[placeholder='รหัสผ่าน']")
        )).send_keys(password)
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.bg-amber-600.text-white")
        )).click()
        time.sleep(2)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/app-root/app-secure-layout/header/div/div/div[2]/div/button/div")
        )).click()
        log("✅ Login ใหม่สำเร็จ")

        with open(cookies_path, "w", encoding="utf-8") as f:
            json.dump(driver.get_cookies(), f, ensure_ascii=False, indent=2)
        log(f"🍪 บันทึก cookies ลง {cookies_path} เรียบร้อย")

        logged_in = True
    except Exception as e:
        log(f"❌ Login ใหม่ล้มเหลว: {e}")

    return logged_in

# -------------------------------
# ปรับ check_email_once()
# -------------------------------
def check_email_once():
    if not email or not password or not url:
        log("❌ ไม่พบข้อมูล EMAIL_USER / EMAIL_PASS / OWA_URL ใน .env")
        return []

    if not check_dns(url):
        return []

    prefs = {"profile.default_content_setting_values.notifications": 2}
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
    
    try:
        driver.get("https://workd.go.th/portal")
        # logged_in = manage_cookies(driver, cookies_path, wait, email, password)
        # กดยอมรับคุกกี้ ถ้ามี
        accept_cookies(driver)
        time.sleep(5)

        # 🔎 ตรวจสอบ login อีกครั้งด้วย check_login()
        if not check_login(driver):
            log("⚠️ ต้อง login ใหม่")
            logged_in = manage_cookies(driver, cookies_path, wait, email, password)

        if not logged_in:
            log("❌ ไม่สามารถเข้าสู่ระบบได้")
            return []
        # กดยอมรับคุกกี้ ถ้ามี
        time.sleep(5)
        # หลัง login → คลิกเข้าใช้งาน
        safe_click(driver, (By.XPATH, "/html/body/app-root/app-secure-layout/main/app-portal-page/div[1]/div[2]/div/app-service-container/p-card/div/div/div[2]/div/p-card/div/div/div[2]/div/p-button/button/span"))

        time.sleep(15)
        driver.switch_to.window(driver.window_handles[-1])

        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.zimbra-client_mail_mainWrapper")
        ))
        log("✅ เข้าสู่ระบบอีเมลสำเร็จ")
        time.sleep(5)
        send_telegram_photo(driver, caption="✅ เข้าสู่ระบบอีเมล {} สำเร็จ".format(email))      
        safe_click(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div[3]/div"))
        time.sleep(1)
        safe_click(driver, (By.XPATH, "/html/body/div[3]/div/div/div/button[2]"))
        time.sleep(2)
        return []
    finally:
        driver.quit()

    return []