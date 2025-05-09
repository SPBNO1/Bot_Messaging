from app.models.auto_reply import AutoReply
from app.models.user import db
from datetime import datetime

class AutoReplyService:
    @staticmethod
    def create_auto_reply(keyword, reply_type, reply_content, user_id):
        """สร้างการตอบกลับอัตโนมัติใหม่"""
        auto_reply = AutoReply(
            keyword=keyword,
            reply_type=reply_type,
            reply_content=reply_content,
            created_by=user_id
        )
        db.session.add(auto_reply)
        db.session.commit()
        return auto_reply

    @staticmethod
    def get_auto_reply(keyword):
        """ค้นหาการตอบกลับอัตโนมัติจากคำค้นหา"""
        return AutoReply.query.filter_by(
            keyword=keyword,
            is_active=True
        ).first()

    @staticmethod
    def get_all_auto_replies():
        """ดึงการตอบกลับอัตโนมัติทั้งหมด"""
        return AutoReply.query.all()

    @staticmethod
    def update_auto_reply(auto_reply_id, keyword=None, reply_type=None, reply_content=None, is_active=None):
        """อัพเดทการตอบกลับอัตโนมัติ"""
        auto_reply = AutoReply.query.get(auto_reply_id)
        if auto_reply:
            if keyword is not None:
                auto_reply.keyword = keyword
            if reply_type is not None:
                auto_reply.reply_type = reply_type
            if reply_content is not None:
                auto_reply.reply_content = reply_content
            if is_active is not None:
                auto_reply.is_active = is_active
            auto_reply.updated_at = datetime.utcnow()
            db.session.commit()
        return auto_reply

    @staticmethod
    def delete_auto_reply(auto_reply_id):
        """ลบการตอบกลับอัตโนมัติ"""
        auto_reply = AutoReply.query.get(auto_reply_id)
        if auto_reply:
            db.session.delete(auto_reply)
            db.session.commit()
            return True
        return False

    @staticmethod
    def toggle_auto_reply(auto_reply_id):
        """เปิด/ปิดการใช้งานการตอบกลับอัตโนมัติ"""
        auto_reply = AutoReply.query.get(auto_reply_id)
        if auto_reply:
            auto_reply.is_active = not auto_reply.is_active
            db.session.commit()
            return auto_reply
        return None 