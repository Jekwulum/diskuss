from flask import Blueprint, request, jsonify
from app.config import config
from app.utils import token_required
from app.user import user_handler
from app.messages import message_handler
import json

routes_bp = Blueprint('diskuss', __name__)

@routes_bp.route('/me', methods=['GET'])
@token_required
def get_user():
    """Get user details."""
    user_id = request.user["user_id"]
    status, user = user_handler.get_user(user_id)
    
    if not status:
        return jsonify({"message": "User not found"}), 404
    
    user["_id"] = str(user["_id"])
    del user["password"]
    return jsonify({"message": "User retrieved successfully", "data": user}), 200

@routes_bp.route('/users', methods=['GET'])
@token_required
def search_users():
    """Search for users by username."""
    # username in request query
    username = request.args.get("username")
    if not username:
        return jsonify({"message": "Username is required"}), 400
    users = user_handler.get_users_by_username(username)
    return jsonify({"message": "Users retrieved successfully", "data": users}), 200

@routes_bp.route('/discussions', methods=['GET'])
@token_required
def get_discussions():
    """Get discussions for the user."""
    user_id = request.user["user_id"]
    discussions = message_handler.get_discussions(user_id)
    
    return jsonify({"message": "Discussions retrieved successfully", "data": discussions}), 200

@routes_bp.route('/discussions', methods=['POST'])
@token_required
def create_or_get_discussion():
    """Create a new discussion or retrieve existing"""
    user_id = request.user["user_id"]
    data = json.loads(request.data) if request.data else {}
    print(f"Data: {data}")
    if not data.get("participants"):
        return jsonify({"message": "Participants are required"}), 400
    
    status, response = message_handler.create_or_get_discussion(user_id=user_id, participants=data["participants"])
    if not status:
        return jsonify(response), 400
    return jsonify(response), 200
