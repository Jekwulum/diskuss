from bson import ObjectId
from datetime import datetime, timezone
from app.config import config

class UserHandler:
    def __init__(self, db):
        self.users = db.users
        self.connected_users = []
    
    def get_user(self, user_id):
        user = self.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return True, user
        else:
            return False, None
        
    def connect_user(self, user_id, socket_id):
        # add to connected users with the user_id as key and socket_id as value in a dict
        for user in self.connected_users:
            if user.get(user_id):
                user[user_id].append(socket_id)
                break
        else:
            self.connected_users.append({user_id: [socket_id]})

        self.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"last_login": datetime.now(timezone.utc)}})
        return self.connected_users
    
    def disconnect_user(self, socket_id):
        self.connected_users = {key: [sid for sid in value if sid != socket_id] for key, value in self.connected_users.items()}
        return self.connected_users
    
    def get_user_socket_ids(self, user_id):
        for user in self.connected_users:
            if user.get(user_id):
                return user[user_id]
        return []


user_handler = UserHandler(config['db'])