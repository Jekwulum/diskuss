from datetime import datetime, timezone
from bson import ObjectId
from app.config import config
from app.utils import serialize_datetime_fields


class MessageHandler:
    """Handles message-related operations."""

    def __init__(self, db):
        self.users = db.users
        self.messages = db.messages
        self.discussions = db.discussions

    def create_or_get_discussion(self, user_id, data=None, is_group=False, participants=None):
        # data -> {discussion_id, recipient_id}
        """Create or retrieve a discussion between two users."""
        try:
            if data and data.get("discussion_id"):
                discussion = self.discussions.find_one({"_id": data["discussion_id"]})
            else:
                if not participants:
                    participants = sorted([str(user_id), str(data["recipient_id"])])
                else:
                    participants = sorted([str(user_id)] + participants)
                discussion = self.discussions.find_one({"participants": participants})

                if not discussion:
                    discussion = {
                        "participants": participants,
                        "is_group": is_group,
                        "messages": [],
                    }
                    inserted = self.discussions.insert_one(discussion)
                    discussion = self.discussions.find_one(
                        {"_id": inserted.inserted_id}
                    )
            discussion["_id"] = str(discussion["_id"])
            return True, {
                "message": "Sucessfuly retrieved discussion",
                "data": discussion,
            }

        except Exception as e:
            print(f"Error retrieving discussion: {e}")
            return False, {"message": "Error retrieving discussion."}

    def get_discussions(self, user_id):
        """Retrieve discussions for a specific user, with last message and participant info."""
        # Find discussions where user is a participant
        discussions_cursor = self.discussions.find(
            {"participants": {"$in": [str(user_id)]}},
            {
                "participants": 1,
                "is_group": 1,
                "messages": {"$slice": -1},  # Only fetch the last message
            }
        ).sort("timestamp", 1)

        result = []
        user_ids_to_fetch = set()

        discussions = list(discussions_cursor)
        
        # Collect all user_ids from all discussions
        for d in discussions:
            for pid in d.get("participants", []):
                user_ids_to_fetch.add(pid)

        # Bulk fetch user profiles
        users_map = {
            str(user["_id"]): user
            for user in self.users.find(
                {"_id": {"$in": [ObjectId(uid) for uid in user_ids_to_fetch]}},
                {"username": 1, "last_login": 1}
            )
        }

        # For each discussion, build response object
        for d in discussions:
            d["_id"] = str(d["_id"])
            d["is_group"] = d.get("is_group", False)

            # Format participants
            d["participants"] = [
                {
                    "_id": pid,
                    "username": users_map.get(pid, {}).get("username", ""),
                    "last_login": users_map.get(pid, {}).get("last_login", "").isoformat()
                    if users_map.get(pid, {}).get("last_login") else ""
                }
                for pid in d.get("participants", [])
            ]

            # Format last message
            last_msg = d.get("messages", [{}])
            if len(last_msg) > 0:
                last_msg = last_msg[0]
            else: last_msg = ""

            if isinstance(last_msg, ObjectId):
                msg_doc = self.messages.find_one({"_id": last_msg})
            else:
                msg_doc = last_msg

            if msg_doc:
                msg_doc["_id"] = str(msg_doc["_id"])
                msg_doc = serialize_datetime_fields(msg_doc)
                d["last_message"] = msg_doc
                d["last_message_timestamp"] = msg_doc.get("timestamp", "")
            else:
                d["last_message"] = {}
                d["last_message_timestamp"] = {}

            # Remove raw messages field
            d.pop("messages", None)

            result.append(d)

        # Sort discussions by the timestamp of the last message (descending order)
        result.sort(key=lambda x: x.get("last_message_timestamp", ""), reverse=True)

        return result

    def get_discussion_messages(self, discussion_id, limit=20, offset=0):
        """Retrieve messages for a specific discussion with optional pagination."""
        try:
            discussion = self.discussions.find_one({"_id": ObjectId(discussion_id)})
            if not discussion:
                return False, {"message": "Discussion not found."}

            messages_cursor = (
                self.messages.find({"discussion_id": discussion_id})
                .sort("timestamp", 1)
            )
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
            recipient_id = data.get("recipient_id", None) # modify to obtain this from the discussion
            text = data.get("text")

            if not all([discussion_id, sender_id, text]):
                return False, {"message": "Missing required fields.", "code": 404}

            discussion = self.discussions.find_one({"_id": ObjectId(discussion_id)})
            if not discussion:
                return False, {"message": "Discussion not found."}
            
            if not recipient_id:
                participants = discussion.get("participants", [])
                if sender_id in participants:
                    participants.remove(sender_id)
                recipient_id = participants[0] if participants else None

                if not recipient_id:
                    return False, {"message": "No recipient found."}

            message = {
                "discussion_id": discussion_id,
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "text": text,
                "timestamp": datetime.now(),
            }
            self.messages.insert_one(message)
            # limit by 50 messages
            self.discussions.update_one(
                {"_id": ObjectId(discussion_id)},
                {"$push": {"messages": message["_id"]}},
            )
            messages_cursor = (
                self.messages.find({"discussion_id": discussion_id})
                .sort("timestamp", 1)
            )
            messages = []

            for msg in messages_cursor:
                msg["_id"] = str(msg["_id"])
                msg["discussion_id"] = str(msg["discussion_id"])
                msg["sender_id"] = str(msg["sender_id"])
                msg["recipient_id"] = str(msg["recipient_id"])
                msg["timestamp"] = msg["timestamp"].isoformat()  # Optional: ISO string
                messages.append(msg)

            return True, {
                "message": "Successful.",
                "data": messages,
                "code": 200,
            }
        except Exception as e:
            print(f"Error sending message: {e}")
            return False, {"message": f"Error sending message: {e}", "code": 500}

    def update_message(self, message_id, data):
        """Update message"""
        # data -> {text}
        try:
            update_data = {"$set": data}
            result = self.messages.update_one(
                {"_id": ObjectId(message_id)}, update_data
            )
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
            self.discussions.update_one(
                {"_id": ObjectId(message.discussion_id)},
                {"$pull": {"messages": message_id}},
            )

            return True, {"message": "Message deleted successfully."}
        except Exception as e:
            print(f"Error deleting message: {e}")
            return False, {"message": "Error deleting message.", "code": 500}


message_handler = MessageHandler(config["db"])
