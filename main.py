import os
from utils.email_checker import check_email_once
from utils.email_checker2 import check_email_once as check_emails2_once
from utils.document_checker import check_documents_once
from utils.e_saraban_checker import check_esaraban_once
from utils.telegram import notify
from utils.logger import log

def process_emails():
    try:
       check_email_once()       
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดในการตรวจสอบอีเมล: {e}")

def process_emails2():
    try:
        check_emails2_once()        
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดในการตรวจสอบอีเมล: {e}")

def process_documents():
    try:
        check_documents_once()        
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดในการตรวจสอบเอกสาร: {e}")

def process_esarabun():
    try:
        check_esaraban_once()        
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดในการตรวจสอบเอกสาร: {e}")

def main():
    log("🚀 เริ่มตรวจสอบ")

    try:
        process_emails()
        process_emails2()
        # process_documents()
        process_esarabun()
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดใน main loop: {e}")

    log("✅ ตรวจสอบเสร็จสิ้น ระบบจะปิดตัวเอง")

if __name__ == "__main__":
    main()