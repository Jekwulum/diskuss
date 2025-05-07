import json
from functools import wraps
from flask import request
from flask_socketio import emit, disconnect
from app.sockets import socketio
from app.utils import decode_jwt_token
from app.messages import message_handler
from app.user import user_handler


def socket_jwt_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            # Try to get token from query string first, then headers
            token = request.headers.get("Authorization")

            if not token:
                print("No token in headers, checking query string")
                emit("error", {"message": "Missing token"})
                disconnect()
                return False

            # Decode token
            user_data, error_message = decode_jwt_token(token)
            if error_message:
                print(f"Token decoding failed: {error_message}")
                emit("error", {"message": error_message})
                disconnect()
                return False

            request.user = user_data

        except Exception as e:
            print(f"Exception in socket_jwt_required: {e}")
            emit("error", {"message": "Authentication failed"})
            disconnect()
            return False

        return f(*args, **kwargs)
    return wrapped


@socketio.on("connect")
def handle_connect():
    token = request.headers.get("Authorization")

    if not token:
        print("Missing token")
        return False

    user_data, error_message = decode_jwt_token(token)
    if error_message:
        print(f"Token error: {error_message}")
        return False 

    user_handler.connect_user(user_data["user_id"], request.sid)
    print(f"Connected users: {user_handler.connected_users}")

@socketio.on("disconnect")
def handle_disconnect():
    user_handler.disconnect_user(request.sid)
    print(f"User {request.sid} disconnected")
    print(f"Connected users: {user_handler.connected_users}")

@socketio.on("start_discussion")
@socket_jwt_required
def start_discussion(data):
    user_id = request.user["user_id"]
    data = json.loads(data) if isinstance(data, str) else data
    status, discussion = message_handler.create_or_get_discussion(user_id, data)
    
    if status:
        emit("start_discussion", discussion)
    else:
        emit("error", {"message": "error starting discussion"})

@socketio.on("get_discussions")
@socket_jwt_required
def get_discussions(data):
    discussions = message_handler.get_discussions(request.user["user_id"])
    print(discussions)
    emit("get_discussions", discussions)

@socketio.on("send_message")
@socket_jwt_required
def handle_send_message(data):
    user = request.user
    data = json.loads(data) if isinstance(data, str) else data
    if user["user_id"] == data["recipient_id"]:
        emit("error", {"message": "You cannot send a message to yourself"})
        return False

    status, result = message_handler.send_message({**data, "sender_id": user['user_id']})
    # emit("send_message", "Hi")
    if not status:
        emit("error", result)
        return False

    # Send back to sender
    emit("send_message", result, room=request.sid)
    # emit to recipient by getting recipient's socket_ids if the recipient_id is in the connected users
    recipient_socket_ids  = user_handler.connected_users.get(data["recipient_id"], None)
    if recipient_socket_ids:
        for socket_id in recipient_socket_ids:
            # emit to recipient
            emit("send_message", result, room=socket_id)

@socketio.on("get_discussion_messages")
@socket_jwt_required
def get_discussion_messages(data):
    data = json.loads(data) if isinstance(data, str) else data
    if not data.get("discussion_id", None):
        emit("error", {"message": "Missing discussion_id"})
        return False
    
    status, messages = message_handler.get_discussion_messages(data.get("discussion_id"), int(data.get("limit", 20)), int(data.get("offset", 0)))
    if status:
        emit("get_discussion_messages", messages)
    else:
        emit("error", {"message": "error getting messages"})
