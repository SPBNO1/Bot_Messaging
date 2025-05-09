from flask import Flask, request, abort, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent, StickerMessageContent
from app.config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, LINE_BASIC_ID
from app.services.line_service import LineService
from app.services.auth_service import AuthService
from app.handlers.text_handler import handle_text_message
from app.utils.logger import logger
from app.models.user import db
import secrets
import base64
import qrcode
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # เปลี่ยนเป็นค่า secret key ของคุณ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ตั้งค่า Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ตั้งค่า Database
db.init_app(app)

# ตั้งค่า Line Service
line_service = LineService()

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logger.info("Request body: %s", body)

    try:
        line_service.handle_webhook(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        abort(500)

    return 'OK'

# Register handlers
line_service.handler.add(MessageEvent, message=TextMessageContent)(handle_text_message)

@line_service.handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    try:
        line_service.reply_text(event.reply_token, "ได้รับรูปภาพของคุณแล้วครับ")
    except Exception as e:
        logger.error(f"Error handling image message: {str(e)}")

@line_service.handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event):
    try:
        line_service.reply_text(event.reply_token, "ได้รับสติกเกอร์ของคุณแล้วครับ")
    except Exception as e:
        logger.error(f"Error handling sticker message: {str(e)}")

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            AuthService.register_user(username, email, password)
            flash('ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('เกิดข้อผิดพลาดในการลงทะเบียน', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = AuthService.login_user(username, password)
        if user:
            flash('เข้าสู่ระบบสำเร็จ!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    AuthService.logout_user()
    flash('ออกจากระบบสำเร็จ', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/connect-line')
@login_required
def connect_line():
    # สร้าง unique token สำหรับการเชื่อมต่อ
    connection_token = secrets.token_urlsafe(32)
    session['line_connection_token'] = connection_token
    
    # สร้าง QR Code สำหรับการเชื่อมต่อ
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"https://line.me/R/ti/p/{LINE_BASIC_ID}")
    qr.make(fit=True)
    
    # สร้าง QR Code image
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('connect_line.html', 
                         qr_code_base64=qr_code_base64)

@app.route('/line-callback')
def line_callback():
    token = request.args.get('token')
    line_user_id = request.args.get('userId')
    
    if token and line_user_id and token == session.get('line_connection_token'):
        # เชื่อมต่อ Line ID กับผู้ใช้
        AuthService.link_line_account(current_user.id, line_user_id)
        flash('เชื่อมต่อกับ Line สำเร็จ!', 'success')
        return redirect(url_for('dashboard'))
    
    flash('การเชื่อมต่อล้มเหลว กรุณาลองใหม่อีกครั้ง', 'error')
    return redirect(url_for('dashboard'))

# Create database tables
with app.app_context():
    db.create_all() 