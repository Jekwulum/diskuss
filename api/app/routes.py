from flask import Blueprint, request, jsonify
from app.config import config
from app.utils import token_required
from app.user import user_handler
from app.messages import message_handler

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

@routes_bp.route('/discussions', methods=['GET'])
@token_required
def get_discussions():
    """Get discussions for the user."""
    user_id = request.user["user_id"]
    print(user_id)
    discussions = message_handler.get_discussions(user_id)
    
    return jsonify({"message": "Discussions retrieved successfully", "data": discussions}), 200