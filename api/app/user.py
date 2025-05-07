from bson import ObjectId
from datetime import datetime, timezone
from app.config import config

class UserHandler:
    def __init__(self, db):
        self.users = db.users
        self.connected_users = {}
    
    def get_user(self, user_id):
        user = self.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return True, user
        else:
            return False, None
    
    def connect_user(self, user_id, socket_id):
        print(user_id)
        if self.connected_users.get(user_id):
            self.connected_users[user_id].append(socket_id)
        else:
            self.connected_users[user_id] = [socket_id]
        self.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"last_login": datetime.now(timezone.utc)}})
        return self.connected_users
    
    def disconnect_user(self, socket_id):
        for user_id, sockets in self.connected_users.items():
            if socket_id in sockets:
                sockets.remove(socket_id)
                if not sockets:
                    del self.connected_users[user_id]
                break
      
        return self.connected_users


user_handler = UserHandler(config['db'])