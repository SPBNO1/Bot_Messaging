# Line Bot ด้วย Python

Line Bot ที่สร้างด้วย Python และ Flask พร้อมระบบจัดการโค้ดที่เป็นระเบียบ

## คุณสมบัติ

- ตอบกลับข้อความอัตโนมัติ
- รองรับการรับส่งรูปภาพและสติกเกอร์
- มีคำสั่งพิเศษ: สวัสดี, ช่วยเหลือ, เกี่ยวกับ
- ระบบ logging ที่ดี
- โครงสร้างโค้ดที่เป็นระเบียบ

## การติดตั้ง

1. **ติดตั้ง Python และ pip**
   - ดาวน์โหลดและติดตั้ง Python จาก [python.org](https://www.python.org/downloads/)
   - ตรวจสอบการติดตั้ง:
     ```bash
     python --version
     pip --version
     ```

2. **โคลนโปรเจค**
   ```bash
   git clone [URL ของโปรเจค]
   cd [ชื่อโฟลเดอร์โปรเจค]
   ```

3. **สร้างและเปิดใช้งาน Virtual Environment**
   ```bash
   # สร้าง virtual environment
   python -m venv .venv

   # เปิดใช้งาน virtual environment
   # สำหรับ Windows
   .venv\Scripts\activate
   # สำหรับ macOS/Linux
   source .venv/bin/activate
   ```

4. **ติดตั้ง Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **ตั้งค่า Environment Variables**
   - สร้างไฟล์ `.env` ในโฟลเดอร์หลักของโปรเจค
   - เพิ่มค่าต่อไปนี้:
     ```
     LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
     LINE_CHANNEL_SECRET=your_channel_secret
     PORT=8080
     FLASK_DEBUG=False
     ```

## การตั้งค่า Line Bot

1. **สร้าง Line Bot**
   - ไปที่ [LINE Developers Console](https://developers.line.biz/console/)
   - สร้าง Provider และ Channel ใหม่
   - เลือก Channel Type เป็น "Messaging API"

2. **ตั้งค่า Channel**
   - ในหน้า Channel Settings:
     - คัดลอก Channel Secret
     - สร้าง Channel Access Token (Long-lived)
     - นำค่าทั้งสองไปใส่ในไฟล์ `.env`

3. **ตั้งค่า Webhook**
   - ติดตั้ง ngrok:
     ```bash
     # สำหรับ macOS
     brew install ngrok
     ```
   - รัน ngrok:
     ```bash
     ngrok http 8080
     ```
   - คัดลอก URL ที่ได้ (เช่น https://xxxx-xxx-xxx-xxx-xxx.ngrok.io)
   - ไปที่ LINE Developers Console
   - ตั้งค่า Webhook URL เป็น: `https://[your-ngrok-url]/callback`
   - เปิด "Use webhook"
   - ปิด "Auto-reply messages"
   - ปิด "Greeting messages"

## การรัน Bot

1. **รัน Bot**
   ```bash
   python run.py
   ```

2. **ทดสอบ Bot**
   - เพิ่ม Bot เป็นเพื่อนใน LINE
   - ส่งข้อความทดสอบ:
     - "สวัสดี"
     - "ช่วยเหลือ"
     - "เกี่ยวกับ"
     - ข้อความอื่นๆ

## โครงสร้างโปรเจค

```
project/
├── .env                    # ไฟล์เก็บค่า environment variables
├── requirements.txt        # ไฟล์รายการ dependencies
├── run.py                 # ไฟล์สำหรับรันแอพพลิเคชัน
├── app/
│   ├── __init__.py        # ไฟล์หลักของแอพพลิเคชัน
│   ├── config.py          # ไฟล์การตั้งค่า
│   ├── handlers/          # โฟลเดอร์เก็บ handlers
│   │   ├── text_handler.py
│   │   ├── image_handler.py
│   │   └── sticker_handler.py
│   ├── services/          # โฟลเดอร์เก็บ services
│   │   └── line_service.py
│   └── utils/             # โฟลเดอร์เก็บ utilities
│       └── logger.py
```

## การแก้ไขปัญหา

1. **Bot ไม่ตอบกลับ**
   - ตรวจสอบว่า ngrok ยังทำงานอยู่
   - ตรวจสอบ Webhook URL ว่าถูกต้อง
   - ตรวจสอบ Channel Access Token และ Channel Secret

2. **Error 401 Unauthorized**
   - ตรวจสอบ Channel Access Token ว่าถูกต้อง
   - ลองสร้าง Channel Access Token ใหม่

3. **Error 404 Not Found**
   - ตรวจสอบว่า ngrok URL ถูกต้อง
   - ตรวจสอบว่า bot กำลังทำงานอยู่

## การพัฒนาต่อยอด

1. **เพิ่มฐานข้อมูล**
   - เพิ่ม SQLAlchemy หรือ MongoDB
   - เก็บข้อมูลผู้ใช้และประวัติการสนทนา

2. **เพิ่มฟีเจอร์**
   - เพิ่มการจัดการรูปภาพและสติกเกอร์
   - เพิ่มระบบ authentication
   - เพิ่มการเชื่อมต่อกับ API อื่นๆ

3. **ปรับปรุงความปลอดภัย**
   - เพิ่มการตรวจสอบสิทธิ์
   - เพิ่มการเข้ารหัสข้อมูล

## License

MIT License