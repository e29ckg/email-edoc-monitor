from dotenv import load_dotenv
import os
from utils.email_checker import check_email_loop
from utils.document_checker import check_documents

load_dotenv()

# โหลดค่าจาก .env
EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")
OWA_URL = os.getenv("OWA_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DOCUMENT_URL = os.getenv("DOCUMENT_URL")
DOCUMENT_USER = os.getenv("DOCUMENT_USER")
DOCUMENT_PASS = os.getenv("DOCUMENT_PASS")

# ตรวจอีเมลทันที
check_email_loop(
    email=EMAIL,
    password=PASSWORD,
    url=OWA_URL,
    check_times=[],  # ✅ เวลาว่าง = ตรวจทันที
    telegram_token=TELEGRAM_TOKEN,
    telegram_chat_id=TELEGRAM_CHAT_ID
)

# ตรวจเอกสารทันที
check_documents(
    document_url=DOCUMENT_URL,
    username=DOCUMENT_USER,
    password=DOCUMENT_PASS,
    telegram_token=TELEGRAM_TOKEN,
    telegram_chat_id=TELEGRAM_CHAT_ID

)