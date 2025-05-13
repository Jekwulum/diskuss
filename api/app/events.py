import json
from functools import wraps
from flask import request, session
from flask_socketio import emit, disconnect
from app.sockets import socketio
from app.utils import decode_jwt_token
from app.messages import message_handler
from app.user import user_handler


def socket_jwt_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            token = request.headers.get("Authorization")
            if not token:
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
def handle_connect(auth):
    try:
        token = request.headers.get("Authorization") or auth.get("token")

        if not token:
            print("Missing token")
            return False

        user_data, error_message = decode_jwt_token(token)
        if error_message:
            print(f"Token error: {error_message}")
            return False

        _, user = user_handler.get_user(user_data["user_id"])
        session["user"] = {**user, "user_id": str(user["_id"])}
        user_handler.connect_user(user_data["user_id"], request.sid)
        print(f"Connected users: {user_handler.connected_users}")
    except Exception as e:
        print(f"Error in handle_connect: {e}")
        emit("error", {"message": "Connection failed"})
        return False


@socketio.on("disconnect")
def handle_disconnect():
    user_handler.disconnect_user(request.sid)
    print(f"User {request.sid} disconnected")
    print(f"Connected users: {user_handler.connected_users}")


@socketio.on("start_discussion")
@socket_jwt_required
def start_discussion(data):
    user_id = session.get("user")["user_id"]
    if not user_id:
        emit("error", {"message": "Missing user_id"})
        return False

    data = json.loads(data) if isinstance(data, str) else data
    status, discussion = message_handler.create_or_get_discussion(user_id, data)

    if status:
        emit("start_discussion", discussion)
    else:
        emit("error", {"message": "error starting discussion"})


@socketio.on("get_discussions")
def get_discussions(data):
    user_id = session.get("user")["user_id"]
    discussions = message_handler.get_discussions(user_id)
    emit("get_discussions", discussions)


@socketio.on("send_message")
# @socket_jwt_required
def handle_send_message(data):
    # user = request.user
    user = session.get("user")
    data = json.loads(data) if isinstance(data, str) else data

    status, result = message_handler.send_message(
        {**data, "sender_id": user["user_id"]}
    )
    # emit("send_message", "Hi")
    if not status:
        emit("error", result)
        return False

    # emit to socket ids of both sender and recipient
    sender_socket_ids = user_handler.get_user_socket_ids(user["user_id"])
    for socket_id in sender_socket_ids:
        emit("receive_message", result, room=socket_id)

    if data.get("recipient_id"):
        recipient_socket_ids = user_handler.get_user_socket_ids(data["recipient_id"])
        for socket_id in recipient_socket_ids:
            emit("receive_message", result, room=socket_id)


@socketio.on("get_discussion_messages")
# @socket_jwt_required
def get_discussion_messages(data):
    print("here")
    data = json.loads(data) if isinstance(data, str) else data
    if not data.get("discussion_id", None):
        emit("error", {"message": "Missing discussion_id"})
        return False

    status, messages = message_handler.get_discussion_messages(
        data.get("discussion_id"),
        int(data.get("limit", 20)),
        int(data.get("offset", 0)),
    )
    if status:
        emit("get_discussion_messages", messages)
    else:
        emit("error", {"message": "error getting messages"})
