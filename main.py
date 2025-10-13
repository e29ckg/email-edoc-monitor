from utils.email_checker import check_email_once
from utils.document_checker import check_documents_once
from utils.telegram import notify
from utils.logger import log

def main():
    log("🚀 เริ่มตรวจสอบอีเมลและเอกสาร")

    # ตรวจสอบอีเมลใหม่
    email_results = check_email_once()
    if email_results:
        log(f"📧 พบอีเมลใหม่จำนวน {len(email_results)} ฉบับ")
        notify(email_results, source="email")
    else:
        log("📭 ไม่พบอีเมลใหม่")

    # ตรวจสอบเอกสารใหม่
    doc_results = check_documents_once()
    if doc_results:
        log(f"📄 พบเอกสารใหม่จำนวน {len(doc_results)} รายการ")
        notify(doc_results, source="document")
    else:
        log("📁 ไม่พบเอกสารใหม่")

    log("✅ ตรวจสอบเสร็จสิ้น ระบบจะปิดตัวเอง")

if __name__ == "__main__":
    main()