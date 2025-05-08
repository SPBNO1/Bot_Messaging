from flask import Flask, request, abort
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent, StickerMessageContent
from app.config import LINE_CHANNEL_SECRET
from app.services.line_service import LineService
from app.handlers.text_handler import handle_text_message
from app.utils.logger import logger

app = Flask(__name__)
line_service = LineService()

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