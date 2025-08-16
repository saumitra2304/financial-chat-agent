import os, json
from typing import List, Dict
from pymongo import MongoClient
from agents import function_tool
from dotenv import load_dotenv

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "chatbotdb")

def _col(name: str):
    return MongoClient(MONGO_URI)[DB_NAME][name]

load_dotenv()
@function_tool
def get_user_portfolio(user_id: str) -> str:
    """
    Return the user's current portfolio positions from MongoDB.

    Args:
        user_id: your app's user identifier

    Returns:
        JSON with holdings: [{ticker, qty, avg_price}] and optional cash
    """
    doc = _col("portfolios").find_one({"user_id": user_id}) or {}
    holdings = doc.get("holdings", [])
    cash = doc.get("cash", 0.0)
    return json.dumps({"user_id": user_id, "cash": cash, "holdings": holdings})
