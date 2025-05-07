from dotenv import load_dotenv
from app import create_app, socketio

load_dotenv()

app = create_app()

if __name__ == "__main__":
  socketio.run(app, host='0.0.0.0', port=5100, debug=True)