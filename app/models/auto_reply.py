from app.models.user import db
from datetime import datetime

class AutoReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False)  # คำค้นหาที่จะตอบกลับ
    reply_type = db.Column(db.String(20), nullable=False)  # ประเภทการตอบกลับ (text, image, sticker)
    reply_content = db.Column(db.Text, nullable=False)  # เนื้อหาการตอบกลับ
    is_active = db.Column(db.Boolean, default=True)  # สถานะการใช้งาน
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ผู้สร้าง
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AutoReply {self.keyword}>' 