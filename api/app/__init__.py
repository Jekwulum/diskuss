import os
from flask import Flask
from flask_cors import CORS

from app.config import config
from app.auth import auth_bp
from app.events import socketio
from app.config import get_db

def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = config['secret_key']

  CORS(app)
  app.register_blueprint(auth_bp, url_prefix='/api/auth')

  get_db()

  socketio.init_app(app)

  return app