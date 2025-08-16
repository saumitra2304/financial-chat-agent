"""Core agent orchestrator with MongoDB-based memory management."""

import os
import traceback
from typing import Any, List

from dotenv import load_dotenv

from agents import Agent, Runner, TResponseInputItem
from agents.exceptions import MaxTurnsExceeded

from logger_config import app_logger
from memory.mongo_memory import MongoConversationMemory

# Load environment variables
load_dotenv()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ---- Orchestrator (main) Agent; tools wired below in app.py ----
orchestrator_agent = Agent(
    name="Orchestrator",
    instructions=("""
        You are a helpful financial chatbot. Use the available tools to answer user queries about companies, financial metrics, ratios, statements, and portfolios.

        IMPORTANT: You have access to the full conversation history automatically. When users refer to "previous message", "above", "the two stocks", "those companies", or similar references, use the conversation context to understand what they're referring to. Do NOT say you can't access previous messages - the conversation context is maintained automatically.

        Rules:
        - Always fetch facts via tools; never guess numbers.
        - Use exact company name input for tools; include exchange/country if provided.
        - Combine multiple tools for complex asks and synthesize.
        - Use the portfolio tool for portfolio queries; websearch for news/research/broad asks.
        - Be fast: minimal internal reasoning, early tool calls, concise outputs.
        - Label currency, period (TTM/FY/Q), and data dates when available.
        - If a tool returns no data, say so and suggest alternatives.
        - Cite all tools used at the end.

        Tool selection:
        - Single metric → most specific ratios tool; else TTM ratios.
        - Multiple metrics in one family → that ratios tool.
        - Cross-family comparison → multiple tools and align periods.
        - Statements → profit/loss, balance sheet, cashflow; shareholding for ownership.
        - Quarterly vs TTM vs FY → quarterly results + TTM ratios (+ statements if needed).
        - Broad/news → websearch.

        Disambiguation:
        - If company ambiguous, ask one short clarification question before calling tools.
        - If period unspecified, default to TTM for ratios and latest quarter for quarterly results; state the default.

        Output format:
        1) 1-2 sentence direct answer.
        2) A compact table or bullet list with Period, Value, Unit (and date).
        3) 1-2 insights (trend, context).
        4) "Tools: [list of tools used]".

        Safety:
        - Educational info only; no personalized financial advice or guarantees.

        Reasoning style:
        - Keep thoughts brief; call tools early; then synthesize clearly.
        """
        ),
    model=OPENAI_MODEL,
)

async def run_orchestrator_with_memory(
    user_msg: str, 
    tools: list,
    memory: MongoConversationMemory,
    user_id: str,
    chat_id: str
):
    """Run the orchestrator agent with MongoDB-based memory.
    
    Args:
        user_msg: The user's current message
        tools: List of available tools
        memory: MongoConversationMemory instance
        user_id: Unique user identifier
        chat_id: Unique chat session identifier
    
    Returns:
        The full result object from Runner (has .final_output, .to_input_items()).
    """
    try:
        app_logger.info(f"Setting up orchestrator with {len(tools)} tools for {user_id}/{chat_id}")
        orchestrator_agent.tools = tools
        
        # Get conversation history from MongoDB
        conversation_history = memory.get_conversation_history(user_id, chat_id)
        
        # Add the current user message to the conversation
        conversation_history.append({
            "role": "user",
            "content": user_msg
        })
        
        app_logger.info(f"Running agent with {len(conversation_history)} messages in history")
        
        # Run the agent with the full conversation history
        result = await Runner.run(
            orchestrator_agent,
            input=conversation_history,  # Pass full conversation as TResponseInputItem list
            max_turns=12,  # Increased from 4 to allow more complex financial queries
        )
        
        app_logger.info("Agent completed successfully")
        
        # Store the user message and assistant response in MongoDB
        memory.add_message(user_id, chat_id, "user", user_msg)
        memory.add_message(user_id, chat_id, "assistant", str(result.final_output))
        
        return result
        
    except MaxTurnsExceeded as e:
        app_logger.error(f"Max turns exceeded for {user_id}/{chat_id}: {e}")
        # Store partial result and return a helpful message
        memory.add_message(user_id, chat_id, "user", user_msg)
        error_message = "I apologize, but your query is quite complex and requires more processing steps than I'm currently configured for. Please try breaking it down into smaller, more specific questions."
        memory.add_message(user_id, chat_id, "assistant", error_message)
        
        # Create a mock result object to maintain compatibility
        class MockResult:
            def __init__(self, output):
                self.final_output = output
        
        return MockResult(error_message)
        
    except Exception as e:
        app_logger.error(f"Error in run_orchestrator_with_memory: {e}")
        app_logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Keep the old function for backward compatibility during transition
async def run_orchestrator(input_text: str, tools, context_items: list[Any] | None = None):
    """Legacy function - use run_orchestrator_with_session instead."""
    orchestrator_agent.tools = tools
    result = await Runner.run(
        orchestrator_agent,
        input=input_text,
        context=context_items or [],
        max_turns=12,  # Increased from 4 to match the main function
    )
    return result
