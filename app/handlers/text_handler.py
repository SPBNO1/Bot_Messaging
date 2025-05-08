from linebot.v3.webhooks import MessageEvent, TextMessageContent
from app.services.line_service import LineService
from app.utils.logger import logger

line_service = LineService()

def handle_text_message(event):
    try:
        msg = event.message.text
        # ตัวอย่างการเพิ่มความซับซ้อน: ตรวจสอบคำสั่งพิเศษ
        if msg.lower() == "สวัสดี":
            reply = "สวัสดีครับ! มีอะไรให้ช่วยไหมครับ?"
        elif msg.lower() == "ช่วยเหลือ":
            reply = "คำสั่งที่ใช้ได้:\n- สวัสดี\n- ช่วยเหลือ\n- เกี่ยวกับ"
        elif msg.lower() == "เกี่ยวกับ":
            reply = "นี่คือ Line Bot ตัวอย่างที่สร้างด้วย Python"
        else:
            reply = f"คุณพิมพ์ว่า: {msg}"
        
        line_service.reply_text(event.reply_token, reply)
    except Exception as e:
        logger.error(f"Error handling text message: {str(e)}") 