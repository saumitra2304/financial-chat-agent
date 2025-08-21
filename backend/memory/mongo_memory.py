"""MongoDB-based conversation memory management."""

import os
from datetime import datetime, timezone
from typing import List, Optional

from pymongo import MongoClient
from bson.objectid import ObjectId

from agents import TResponseInputItem
from logger_config import app_logger


class MongoConversationMemory:
    """MongoDB-based conversation memory storage."""
    
    def __init__(self, connection_string: str = None, db_name: str = None):
        """Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB connection string. If None, uses MONGO_URI env var
            db_name: Database name for storing conversations. If None, uses DB_NAME env var
        """
        if connection_string is None:
            connection_string = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        
        if db_name is None:
            db_name = os.getenv("DB_NAME", "chatbotdb")
        
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.messages = self.db.messages
        
        # Create index for efficient queries
        self.messages.create_index([("user_id", 1), ("chat_id", 1), ("ts", 1)])
        
        app_logger.info(f"MongoDB connection established to {db_name}")
    
    def add_message(
        self, 
        user_id: str, 
        chat_id: str, 
        role: str, 
        content: str
    ) -> str:
        """Add a message to the conversation.
        
        Args:
            user_id: Unique user identifier
            chat_id: Unique chat session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            Inserted message ID
        """
        message = {
            "user_id": user_id,
            "chat_id": chat_id,
            "role": role,
            "text": content,
            "ts": datetime.now(timezone.utc)
        }
        
        result = self.messages.insert_one(message)
        app_logger.info(f"Added {role} message for {user_id}/{chat_id}: {content[:50]}...")
        
        return str(result.inserted_id)
    
    def get_conversation_history(
        self, 
        user_id: str, 
        chat_id: str, 
        limit: int = 50
    ) -> List[TResponseInputItem]:
        """Get conversation history for a user/chat session.
        
        Args:
            user_id: Unique user identifier
            chat_id: Unique chat session identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages in TResponseInputItem format
        """
        cursor = self.messages.find(
            {"user_id": user_id, "chat_id": chat_id}
        ).sort("ts", 1).limit(limit)
        
        conversation = []
        for msg in cursor:
            conversation.append({
                "role": msg["role"],
                "content": msg["text"]
            })
        
        app_logger.info(f"Retrieved {len(conversation)} messages for {user_id}/{chat_id}")
        return conversation
    
    def clear_conversation(self, user_id: str, chat_id: str) -> int:
        """Clear all messages for a specific conversation.
        
        Args:
            user_id: Unique user identifier
            chat_id: Unique chat session identifier
            
        Returns:
            Number of deleted messages
        """
        result = self.messages.delete_many(
            {"user_id": user_id, "chat_id": chat_id}
        )
        
        app_logger.info(f"Cleared {result.deleted_count} messages for {user_id}/{chat_id}")
        return result.deleted_count
    
    def get_conversation_count(self, user_id: str, chat_id: str) -> int:
        """Get the number of messages in a conversation.
        
        Args:
            user_id: Unique user identifier
            chat_id: Unique chat session identifier
            
        Returns:
            Number of messages in the conversation
        """
        count = self.messages.count_documents(
            {"user_id": user_id, "chat_id": chat_id}
        )
        
        return count
    
    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[dict]:
        """Get recent conversations for a user.
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of recent conversation metadata
        """
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": {"chat_id": "$chat_id"},
                "last_message": {"$max": "$ts"},
                "message_count": {"$sum": 1}
            }},
            {"$sort": {"last_message": -1}},
            {"$limit": limit}
        ]
        
        conversations = list(self.messages.aggregate(pipeline))
        app_logger.info(f"Retrieved {len(conversations)} recent conversations for {user_id}")
        
        return [
            {
                "chat_id": conv["_id"]["chat_id"],
                "last_message": conv["last_message"],
                "message_count": conv["message_count"]
            }
            for conv in conversations
        ]
    
    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            app_logger.info("MongoDB connection closed")


# Global instance
mongo_memory: Optional[MongoConversationMemory] = None


def get_mongo_memory() -> MongoConversationMemory:
    """Get or create the global MongoDB memory instance."""
    global mongo_memory
    
    if mongo_memory is None:
        mongo_memory = MongoConversationMemory()
    
    return mongo_memory
