from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from app.config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from app.utils.logger import logger

class LineService:
    def __init__(self):
        self.configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
        self.handler = WebhookHandler(LINE_CHANNEL_SECRET)

    def handle_webhook(self, body, signature):
        try:
            self.handler.handle(body, signature)
            return True
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return False

    def reply_text(self, reply_token, text):
        try:
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text=text)]
                    )
                )
            return True
        except Exception as e:
            logger.error(f"Error replying message: {str(e)}")
            return False 