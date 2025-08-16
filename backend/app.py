"""FastAPI application for the financial chat agent."""

import os
import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import WebSearchTool

from agents_core import run_orchestrator_with_memory
from logger_config import app_logger
from memory.mongo_memory import get_mongo_memory
from tools.finance_tool import (
    get_balance_sheet,
    get_cashflow,
    get_cashflow_ratios,
    get_efficiency_ratios,
    get_financial_stability_ratios,
    get_growth_ratios,
    get_margin_ratios,
    get_profit_loss,
    get_quarterly_results,
    get_shareholding,
    get_solvency_ratios,
    get_ttm_ratios,
    get_valuation_ratios,
)
from tools.portfolio_tool import get_user_portfolio

app = FastAPI(title="Agentic Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

class ChatRequest(BaseModel):
    user_id: str
    chat_id: str
    message: str

# Global MongoDB memory instance
mongo_memory = get_mongo_memory()

@app.post("/chat")
async def chat(req: ChatRequest):
    """Handle chat requests with MongoDB-based memory.
    
    Args:
        req: ChatRequest containing user_id, chat_id, and message
        
    Returns:
        Dictionary with the agent's response
    """
    user_id, chat_id, user_msg = req.user_id, req.chat_id, req.message

    try:
        app_logger.info(f"Processing message from {user_id}/{chat_id}: {user_msg[:100]}...")

        # Build tools list
        tools = [
            get_ttm_ratios,
            get_quarterly_results,
            get_profit_loss,
            get_balance_sheet,
            get_cashflow,
            get_shareholding,
            get_margin_ratios,
            get_solvency_ratios,
            get_efficiency_ratios,
            get_financial_stability_ratios,
            get_valuation_ratios,
            get_cashflow_ratios,
            get_growth_ratios,
            get_user_portfolio,
            WebSearchTool()
        ]
        app_logger.info(f"Tools loaded: {len(tools)} tools")

        # Run orchestrator with MongoDB-based memory
        result = await run_orchestrator_with_memory(
            user_msg=user_msg,
            tools=tools,
            memory=mongo_memory,
            user_id=user_id,
            chat_id=chat_id
        )
        answer = str(result.final_output)
        app_logger.info(f"Generated response: {answer[:100]}...")
        
    except Exception as e:
        app_logger.error(f"Error in chat endpoint: {e}")
        app_logger.error(f"Traceback: {traceback.format_exc()}")
        answer = f"Sorry, I encountered an error processing your request: {str(e)}"

    return {"answer": answer}

# Health check
@app.get("/health")
def health():
    """Health check endpoint.
    
    Returns:
        Dictionary indicating the API is operational
    """
    return {"ok": True}


# Conversation management endpoints
@app.get("/conversations/{user_id}")
async def get_user_conversations(user_id: str, limit: int = 10):
    """Get recent conversations for a user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of conversations to return
        
    Returns:
        List of recent conversations
    """
    try:
        conversations = mongo_memory.get_recent_conversations(user_id, limit)
        return {"conversations": conversations}
    except Exception as e:
        app_logger.error(f"Error getting conversations for {user_id}: {e}")
        return {"error": str(e)}


@app.get("/conversation/{user_id}/{chat_id}")
async def get_conversation_history(user_id: str, chat_id: str, limit: int = 50):
    """Get conversation history for a specific chat.
    
    Args:
        user_id: User identifier
        chat_id: Chat session identifier
        limit: Maximum number of messages to return
        
    Returns:
        Conversation history
    """
    try:
        history = mongo_memory.get_conversation_history(user_id, chat_id, limit)
        count = mongo_memory.get_conversation_count(user_id, chat_id)
        return {
            "user_id": user_id,
            "chat_id": chat_id,
            "total_messages": count,
            "messages": history
        }
    except Exception as e:
        app_logger.error(f"Error getting conversation {user_id}/{chat_id}: {e}")
        return {"error": str(e)}


@app.delete("/conversation/{user_id}/{chat_id}")
async def clear_conversation(user_id: str, chat_id: str):
    """Clear a specific conversation.
    
    Args:
        user_id: User identifier
        chat_id: Chat session identifier
        
    Returns:
        Number of deleted messages
    """
    try:
        deleted_count = mongo_memory.clear_conversation(user_id, chat_id)
        return {
            "user_id": user_id,
            "chat_id": chat_id,
            "deleted_messages": deleted_count
        }
    except Exception as e:
        app_logger.error(f"Error clearing conversation {user_id}/{chat_id}: {e}")
        return {"error": str(e)}
