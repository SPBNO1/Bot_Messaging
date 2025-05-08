from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent,
    ImageMessageContent, StickerMessageContent
)
import os
from dotenv import load_dotenv
import logging

# โหลด environment variables
load_dotenv()

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ดึงค่า token และ secret จาก environment variables
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise ValueError("กรุณาตั้งค่า LINE_CHANNEL_ACCESS_TOKEN และ LINE_CHANNEL_SECRET ใน .env file")

# ตั้งค่า Line Bot API
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logger.info("Request body: %s", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        logger.error("Error occurred: %s", str(e))
        abort(500)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    try:
        msg = event.message.text
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"คุณพิมพ์ว่า: {msg}")]
                )
            )
    except Exception as e:
        logger.error("Error handling text message: %s", str(e))

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="ได้รับรูปภาพของคุณแล้วครับ")]
                )
            )
    except Exception as e:
        logger.error("Error handling image message: %s", str(e))

@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event):
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="ได้รับสติกเกอร์ของคุณแล้วครับ")]
                )
            )
    except Exception as e:
        logger.error("Error handling sticker message: %s", str(e))

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
