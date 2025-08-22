"""FastAPI application for the financial chat agent."""

import os
import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import WebSearchTool

from agents_core import run_orchestrator_with_memory
from response_formatter import ResponseFormatter
from logger_config import app_logger
from memory.mongo_memory import get_mongo_memory
from tools.finance_tool import (
    confirm_stock_symbol,
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
from tools.advanced_quant_tools import (
    verify_stock_for_advanced_analysis,
    get_returns_methodology_guide,
    get_portfolio_optimization_objectives_guide,
    get_historical_price_data as adv_get_historical_price_data,
    calculate_volatility_metrics as adv_calculate_volatility_metrics,
    calculate_correlation_analysis as adv_calculate_correlation_analysis,
    calculate_advanced_statistics as adv_calculate_advanced_statistics,
    calculate_monte_carlo_simulation as adv_calculate_monte_carlo_simulation,
    calculate_options_metrics,
    calculate_portfolio_optimization,
    calculate_garch_volatility_models,
    calculate_pca_decomposition,
    calculate_rolling_beta,
    calculate_autocorrelation_analysis,
    calculate_cointegration_test,
    calculate_kalman_spread,
    calculate_rolling_volatility,
    calculate_drawdown_series,
    calculate_var_cvar_analysis,
    calculate_markov_regime_detection,
    calculate_factor_exposure_ols,
    calculate_factor_exposure_pca,
)
from tools.enhanced_technical_analysis import (
    calculate_comprehensive_technical_analysis,
    analyze_candlestick_patterns,
)
from tools.stock_verification_tool import (
    search_and_confirm_stock,
    proceed_with_confirmed_symbol,
)
from tool_orchestrator import tool_orchestrator
from stock_updater_service import start_stock_updater_service, stop_stock_updater_service

app = FastAPI(title="Agentic Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Start stock updater service on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    app_logger.info("Starting up Financial Chat Agent...")
    
    # Start stock data updater service
    try:
        start_stock_updater_service()
        app_logger.info("Stock updater service started successfully")
    except Exception as e:
        app_logger.error(f"Failed to start stock updater service: {e}")
        # Don't fail startup if stock updater fails

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown"""
    app_logger.info("Shutting down Financial Chat Agent...")
    
    try:
        stop_stock_updater_service()
        app_logger.info("Stock updater service stopped")
    except Exception as e:
        app_logger.error(f"Error stopping stock updater service: {e}")

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

        # Enhance user query with tool orchestration guidance
        enhanced_user_msg = tool_orchestrator.get_analysis_prompt_enhancement(user_msg)
        
        if enhanced_user_msg != user_msg:
            app_logger.info(f"Enhanced query with tool orchestration guidance")

        # Build tools list
        tools = [
            # Stock Verification Tools (USE FIRST for company analysis)
            search_and_confirm_stock,
            proceed_with_confirmed_symbol,
            confirm_stock_symbol,
            verify_stock_for_advanced_analysis,
            # Professional Methodology Guides (IMPORTANT: Use for proper return methodology and optimization objectives)
            get_returns_methodology_guide,
            get_portfolio_optimization_objectives_guide,
            # Fundamental Analysis Tools
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
            # Company verification and options tools
            verify_stock_for_advanced_analysis,
            calculate_options_metrics,
            # Professional Quantitative Finance Tools
            adv_get_historical_price_data,
            adv_calculate_volatility_metrics,
            adv_calculate_correlation_analysis,
            adv_calculate_advanced_statistics,
            adv_calculate_monte_carlo_simulation,
            calculate_portfolio_optimization,
            calculate_garch_volatility_models,
            # Enhanced Technical Analysis with Charts (replaces basic technical indicators)
            calculate_comprehensive_technical_analysis,
            analyze_candlestick_patterns,
            WebSearchTool()
        ]
        app_logger.info(f"Tools loaded: {len(tools)} tools")

        # Run orchestrator with MongoDB-based memory using enhanced message
        result = await run_orchestrator_with_memory(
            user_msg=enhanced_user_msg,
            tools=tools,
            memory=mongo_memory,
            user_id=user_id,
            chat_id=chat_id
        )
        
        # Format the response with metadata
        enhanced_response = ResponseFormatter.format_enhanced_response(result)
        
        app_logger.info("Generated response successfully")
        
        return enhanced_response
        
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
