import datetime
import jwt
import bcrypt
from flask import Blueprint, request, jsonify
from app.config import config


user_db = config['db'].users

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'message': 'Missing credentials'}), 400
    
    user = user_db.find_one({"username": username})
    if not user or not check_password(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    user_db.update_one({"_id": user['_id']}, {"$set": {"last_login": datetime.datetime.now(datetime.timezone.utc)}})
    user_id = str(user['_id'])

    token = jwt.encode({
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=10000)
    }, config['secret_key'], algorithm='HS256')

    return jsonify({'token': token, 'message': 'SUCCESS'}), 200


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'message': 'Missing credentials'}), 400

    if user_db.find_one({"username": username}):
        return jsonify({'message': 'Username already exists'}), 400

    user = {"username": username, "password": hash_password(password)}
    result = user_db.insert_one(user)
    user_id = str(result.inserted_id)

    token = jwt.encode({
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=10000)
    }, config['secret_key'], algorithm='HS256')
    
    return jsonify({'token': token, 'message': 'SUCCESS'}), 200