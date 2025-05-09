from flask import Flask, request, abort, render_template, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_required, current_user
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent, StickerMessageContent
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from app.config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, LINE_BASIC_ID
from app.services.line_service import LineService
from app.services.auth_service import AuthService
from app.handlers.text_handler import handle_text_message
from app.utils.logger import logger
from app.models.user import db, User
import secrets
import base64
import qrcode
from io import BytesIO
from app.services.auto_reply_service import AutoReplyService
from app.models.auto_reply import AutoReply

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ตั้งค่า Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ตั้งค่า Database
db.init_app(app)

# ตั้งค่า Line Bot
handler = WebhookHandler(LINE_CHANNEL_SECRET)
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
line_bot_api = MessagingApi(ApiClient(configuration))
line_service = LineService()

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # ตรวจสอบการตอบกลับอัตโนมัติ
    auto_reply = AutoReplyService.get_auto_reply(event.message.text)
    if auto_reply:
        if auto_reply.reply_type == 'text':
            line_bot_api.reply_message(
                event.reply_token,
                {"type": "text", "text": auto_reply.reply_content}
            )
        elif auto_reply.reply_type == 'image':
            line_bot_api.reply_message(
                event.reply_token,
                {
                    "type": "image",
                    "originalContentUrl": auto_reply.reply_content,
                    "previewImageUrl": auto_reply.reply_content
                }
            )
        elif auto_reply.reply_type == 'sticker':
            # แยก package_id และ sticker_id จาก reply_content
            package_id, sticker_id = auto_reply.reply_content.split(',')
            line_bot_api.reply_message(
                event.reply_token,
                {
                    "type": "sticker",
                    "packageId": package_id,
                    "stickerId": sticker_id
                }
            )
        return

    # ถ้าไม่มีคำตอบอัตโนมัติ ให้ตอบกลับด้วยข้อความเริ่มต้น
    line_bot_api.reply_message(
        event.reply_token,
        {"type": "text", "text": "ขออภัยค่ะ ไม่พบคำตอบสำหรับข้อความนี้"}
    )

# Register handlers
handler.add(MessageEvent, message=TextMessageContent)(handle_text_message)

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            {"type": "text", "text": "ได้รับรูปภาพของคุณแล้วครับ"}
        )
    except Exception as e:
        logger.error(f"Error handling image message: {str(e)}")

@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            {"type": "text", "text": "ได้รับสติกเกอร์ของคุณแล้วครับ"}
        )
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
    # นับจำนวนการตอบกลับอัตโนมัติ
    auto_replies_count = AutoReply.query.filter_by(created_by=current_user.id).count()
    
    # นับจำนวนข้อความที่ได้รับ (ต้องสร้างโมเดล Message ก่อน)
    messages_count = 0  # จะเพิ่มในภายหลัง
    
    # นับจำนวนผู้ใช้ที่เชื่อมต่อกับ Line
    connected_users = User.query.filter(User.line_user_id.isnot(None)).count()
    
    # ดึงข้อความล่าสุด (ต้องสร้างโมเดล Message ก่อน)
    recent_messages = []  # จะเพิ่มในภายหลัง
    
    return render_template('dashboard.html',
                         auto_replies_count=auto_replies_count,
                         messages_count=messages_count,
                         connected_users=connected_users,
                         recent_messages=recent_messages)

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

@app.route('/auto-reply')
@login_required
def auto_reply():
    auto_replies = AutoReplyService.get_all_auto_replies()
    return render_template('auto_reply.html', auto_replies=auto_replies)

@app.route('/auto-reply/add', methods=['POST'])
@login_required
def add_auto_reply():
    keyword = request.form.get('keyword')
    reply_type = request.form.get('reply_type')
    reply_content = request.form.get('reply_content')
    
    AutoReplyService.create_auto_reply(
        keyword=keyword,
        reply_type=reply_type,
        reply_content=reply_content,
        user_id=current_user.id
    )
    
    flash('เพิ่มการตอบกลับอัตโนมัติสำเร็จ', 'success')
    return redirect(url_for('auto_reply'))

@app.route('/auto-reply/<int:reply_id>')
@login_required
def get_auto_reply(reply_id):
    auto_reply = AutoReply.query.get_or_404(reply_id)
    return jsonify({
        'keyword': auto_reply.keyword,
        'reply_type': auto_reply.reply_type,
        'reply_content': auto_reply.reply_content
    })

@app.route('/auto-reply/<int:reply_id>/edit', methods=['POST'])
@login_required
def edit_auto_reply(reply_id):
    keyword = request.form.get('keyword')
    reply_type = request.form.get('reply_type')
    reply_content = request.form.get('reply_content')
    
    AutoReplyService.update_auto_reply(
        auto_reply_id=reply_id,
        keyword=keyword,
        reply_type=reply_type,
        reply_content=reply_content
    )
    
    flash('แก้ไขการตอบกลับอัตโนมัติสำเร็จ', 'success')
    return redirect(url_for('auto_reply'))

@app.route('/auto-reply/<int:reply_id>/toggle', methods=['POST'])
@login_required
def toggle_auto_reply(reply_id):
    AutoReplyService.toggle_auto_reply(reply_id)
    return jsonify({'success': True})

@app.route('/auto-reply/<int:reply_id>/delete', methods=['POST'])
@login_required
def delete_auto_reply(reply_id):
    AutoReplyService.delete_auto_reply(reply_id)
    return jsonify({'success': True})

@app.route('/')
def index():
    return redirect(url_for('login'))

# Create database tables
with app.app_context():
    db.create_all() 