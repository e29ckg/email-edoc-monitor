import os
from utils.email_checker import check_email_once
from utils.document_checker import check_documents_once
from utils.telegram import notify
from utils.logger import log

def process_emails():
    email_results = check_email_once()   

def process_documents():
    doc_results = check_documents_once()
    
def main():
    log("🚀 เริ่มตรวจสอบอีเมลและเอกสาร")

    try:
        if os.getenv("NOTIFY_EMAIL", "true").lower() == "true":
            process_emails()
        if os.getenv("NOTIFY_DOCUMENT", "true").lower() == "true":
            process_documents()
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดใน main loop: {e}")

    log("✅ ตรวจสอบเสร็จสิ้น ระบบจะปิดตัวเอง")

if __name__ == "__main__":
    main()