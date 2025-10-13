# document_checker.py
import time, json, random, os
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
CACHE_FILE = "cache/notified_documents.json"

MAX_DOCUMENTS = int(os.getenv("MAX_DOCUMENTS", "5"))
NOTIFY_DOCUMENT = os.getenv("NOTIFY_DOCUMENT", "true").lower() == "true"

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

def check_documents_once():
    document_url = os.getenv("DOCUMENT_URL")
    username = os.getenv("DOCUMENT_USER")
    password = os.getenv("DOCUMENT_PASS")

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

    new_entries = []

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
        rows = driver.find_elements(By.CSS_SELECTOR, 'tbody#listForm\\:dataTable_data > tr')[:MAX_DOCUMENTS]

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
                log(f"⚠️ ดึงข้อมูลแถวไม่สำเร็จ: {e}")

        element = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/a[2]")))
        element.click()
        time.sleep(3)
        element = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"j_idt43\"]")))
        element.click()
        time.sleep(3)

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(notified), f, ensure_ascii=False)
        if new_entries and NOTIFY_DOCUMENT:
            return new_entries

    except Exception as e:
        log(f"⚠️ ไม่สามารถโหลดเอกสารจาก e-office ได้: {e}")

    finally:
        driver.quit()

    return new_entries