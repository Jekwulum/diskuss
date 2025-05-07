import jwt
from bson import ObjectId
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
    
def serialize_mongo_doc(doc):
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, list):
            doc[key] = [str(item) if isinstance(item, ObjectId) else item for item in value]
    return doc
