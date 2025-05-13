import jwt
from functools import wraps
from bson import ObjectId
from flask import request
from app.config import config

def decode_jwt_token(token):
    if not token:
        return None, 'No token provided'
    
    try:
        data = jwt.decode(token, config['secret_key'], algorithms=["HS256"])
        return data, None
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'
    
def token_required(f):
    """Decorator to check if a token is provided in the request."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization").split(" ")[-1] if request.headers.get("Authorization") else None
        if not token:
            return {"message": "Token is missing"}, 401

        user_data, error_message = decode_jwt_token(token)
        if not user_data:
            return {"message": error_message}, 401
        
        request.user = user_data
        return f(*args, **kwargs)
    
    return decorated
    
def serialize_mongo_doc(doc):
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, list):
            doc[key] = [str(item) if isinstance(item, ObjectId) else item for item in value]
    return doc

from datetime import datetime, timezone

def serialize_datetime_fields(doc):
    """Recursively convert all datetime fields in a dict to ISO 8601 strings."""
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
        elif isinstance(v, dict):
            serialize_datetime_fields(v)
    return doc
