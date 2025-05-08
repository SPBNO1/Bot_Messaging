from app import app
from app.config import FLASK_PORT, FLASK_DEBUG

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=FLASK_DEBUG) 