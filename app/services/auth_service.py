from flask_login import login_user, logout_user, current_user
from app.models.user import User, db
from datetime import datetime

class AuthService:
    @staticmethod
    def register_user(username, email, password, line_user_id=None):
        try:
            user = User(
                username=username,
                email=email,
                line_user_id=line_user_id
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def login_user(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            return user
        return None

    @staticmethod
    def logout_user():
        logout_user()

    @staticmethod
    def get_user_by_line_id(line_user_id):
        return User.query.filter_by(line_user_id=line_user_id).first()

    @staticmethod
    def link_line_account(user_id, line_user_id):
        user = User.query.get(user_id)
        if user:
            user.line_user_id = line_user_id
            db.session.commit()
            return user
        return None 