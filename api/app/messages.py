from datetime import datetime
from bson import ObjectId
from app.config import config
from app.utils import serialize_mongo_doc

class MessageHandler:
    """Handles message-related operations."""
    def __init__(self, db):
        self.messages = db.messages
        self.discussions = db.discussions
    
    def create_or_get_discussion(self, user_id, data, is_group=False):
        # data -> {discussion_id, recipient_id}
        """Create or retrieve a discussion between two users."""
        try:
            if (data.get("discussion_id")):
                discussion = self.discussions.find_one({"_id": data["discussion_id"]})
            else:
                participants = sorted([str(user_id), str(data["recipient_id"])])
                discussion = self.discussions.find_one({"participants": participants})

                if not discussion:
                    discussion = {
                        "participants": participants,
                        "is_group": is_group,
                        "messages": []
                    }
                    inserted = self.discussions.insert_one(discussion)
                    discussion = self.discussions.find_one({"_id": inserted.inserted_id})
            discussion["_id"] = str(discussion["_id"])
            return True, {"message": "Sucessfuly retrieved discussion", "data": discussion}
        
        except Exception as e:
            print(f"Error retrieving discussion: {e}")
            return False, {"message": "Error retrieving discussion."} 
    
    def get_discussions(self, user_id):
        """Retrieve discussions for a specific user."""
        discussions = self.discussions.find({"participants": {"$in": [str(user_id)]}})
        
        result = []
        for d in discussions:
            d["_id"] = str(d["_id"])
            d["participants"] = [str(pid) for pid in d["participants"]]

            if "messages" in d:
                d["messages"] = [str(mid) if isinstance(mid, ObjectId) else mid for mid in d["messages"]]
            result.append(d)
        
        return result
    
    def get_discussion_messages(self, discussion_id, limit=20, offset=0):
        """Retrieve messages for a specific discussion with optional pagination."""
        try:
            discussion = self.discussions.find_one({"_id": ObjectId(discussion_id)})
            if not discussion:
                return False, {"message": "Discussion not found."}
            
            messages_cursor = self.messages.find({"discussion_id": discussion_id}).sort("timestamp", -1).skip(offset).limit(limit)
            messages = []

            for msg in messages_cursor:
                msg["_id"] = str(msg["_id"])
                msg["discussion_id"] = str(msg["discussion_id"])
                msg["sender_id"] = str(msg["sender_id"])
                msg["recipient_id"] = str(msg["recipient_id"])
                msg["timestamp"] = msg["timestamp"].isoformat()  # Optional: ISO string
                messages.append(msg)
            return True, messages
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return False, {"message": "Error retrieving messages."}

    def send_message(self, data):
        """Send a message to a discussion."""
        try:
            discussion_id = data.get("discussion_id")
            sender_id = data.get("sender_id")
            recipient_id = data.get("recipient_id")
            text = data.get("text")

            if not all([discussion_id, sender_id, recipient_id, text]):
                return False, {"message": "Missing required fields.", "code": 404}
            
            discussion = self.discussions.find_one({"_id": ObjectId(discussion_id)})
            if not discussion:
                return False, {"message": "Discussion not found."}
            
            message = {
                "discussion_id": discussion_id,
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "text": text,
                "timestamp": datetime.now()
            }
            self.messages.insert_one(message)
            # limit by 50 messages
            self.discussions.update_one({"_id": ObjectId(discussion_id)}, {"$push": {"messages": message["_id"]}})
            messages_cursor = self.messages.find({"discussion_id": discussion_id}).sort("timestamp", -1).limit(50)
            messages = []

            for msg in messages_cursor:
                msg["_id"] = str(msg["_id"])
                msg["discussion_id"] = str(msg["discussion_id"])
                msg["sender_id"] = str(msg["sender_id"])
                msg["recipient_id"] = str(msg["recipient_id"])
                msg["timestamp"] = msg["timestamp"].isoformat()  # Optional: ISO string
                messages.append(msg)

            return True, {"message": "Message sent successfully.", "data": messages, "code": 200}
        except Exception as e:
            print(f"Error sending message: {e}")
            return False, {"message": f"Error sending message: {e}", "code": 500}
        

    def update_message(self, message_id, data):
        """Update message"""
        # data -> {text}
        try:
            update_data = {"$set": data}
            result = self.messages.update_one({"_id": ObjectId(message_id)}, update_data)
            if result.matched_count == 0:
                return False, {"message": "Message not found.", "code": 404}
            return True, {"message": "Message updated successfully."}
        except Exception as e:
            print(f"Error updating message: {e}")
            return False, {"message": "Error updating message.", "code": 500}


    def delete_message(self, message_id):
        """Delete message"""
        try:
            message = self.messages.find_one({"_id": ObjectId(message_id)})
            if not message:
                return False, {"message": "Message not found", "code": 404}
            
            self.messages.delete_one({"_id": ObjectId(message_id)})
            self.discussions.update_one({"_id": ObjectId(message.discussion_id)}, {"$pull": {"messages": message_id}})
            
            return True, {"message": "Message deleted successfully."}
        except Exception as e:
            print(f"Error deleting message: {e}")
            return False, {"message": "Error deleting message.", "code": 500}
    

message_handler = MessageHandler(config['db'])