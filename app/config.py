import os
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

# Line Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# Flask Configuration
FLASK_PORT = int(os.getenv('PORT', 8080))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Validate required environment variables
if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise ValueError("กรุณาตั้งค่า LINE_CHANNEL_ACCESS_TOKEN และ LINE_CHANNEL_SECRET ใน .env file") 