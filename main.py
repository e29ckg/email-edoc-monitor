import os
from utils.email_checker import check_email_once
from utils.document_checker import check_documents_once
from utils.e_saraban_checker import check_esaraban_once
from utils.telegram import notify
from utils.logger import log

def process_emails():
    """ตรวจสอบอีเมลใหม่"""
    try:
        email_results = check_email_once()
        if email_results:
            notify("📧 พบอีเมลใหม่", email_results)
        else:
            log("ℹ️ ไม่พบอีเมลใหม่")
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดในการตรวจสอบอีเมล: {e}")

def process_documents():
    """ตรวจสอบเอกสารใหม่"""
    try:
        doc_results = check_documents_once()
        if doc_results:
            notify("📄 พบเอกสารใหม่", doc_results)
        else:
            log("ℹ️ ไม่พบเอกสารใหม่")
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดในการตรวจสอบเอกสาร: {e}")

def process_esarabun():
    """ตรวจสอบเอกสารใหม่"""
    try:
        doc_results = check_esaraban_once()
        if doc_results:
            notify("📄 พบเอกสารใหม่", doc_results)
        else:
            log("ℹ️ ไม่พบเอกสารใหม่")
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดในการตรวจสอบเอกสาร: {e}")

def main():
    log("🚀 เริ่มตรวจสอบอีเมลและเอกสาร")

    try:
        process_emails()
        process_documents()
        process_esarabun()
    except Exception as e:
        log(f"❌ เกิดข้อผิดพลาดใน main loop: {e}")

    log("✅ ตรวจสอบเสร็จสิ้น ระบบจะปิดตัวเอง")

if __name__ == "__main__":
    main()