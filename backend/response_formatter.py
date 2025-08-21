"""
Response formatter to structure tool responses and metadata for frontend.
"""

import json
from typing import Dict, List, Any

class ResponseFormatter:
    """Formats agent responses to extract metadata."""
    
    @staticmethod
    def extract_parameters_from_tools(result) -> Dict[str, Any]:
        """Extract analysis parameters from tool call results."""
        analysis_parameters = {}
        
        # Check if result has tool calls and their responses
        if hasattr(result, 'messages') and result.messages:
            for message in result.messages:
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        if hasattr(tool_call, 'result') and tool_call.result:
                            tool_result = tool_call.result
                            
                            # Check if tool result is a dict with analysis parameters
                            if isinstance(tool_result, dict) and 'analysis_parameters' in tool_result:
                                tool_name = tool_call.function.name if hasattr(tool_call, 'function') else 'unknown'
                                analysis_parameters[tool_name] = tool_result['analysis_parameters']
        
        return {
            'analysis_parameters': analysis_parameters
        }
    
    @staticmethod
    def format_enhanced_response(result) -> Dict[str, Any]:
        """Format the complete response with text and metadata."""
        
        # Get the text response
        text_response = str(result.final_output) if hasattr(result, 'final_output') else str(result)
        
        # Extract parameters
        param_data = ResponseFormatter.extract_parameters_from_tools(result)
        
        # Prepare the enhanced response
        enhanced_response = {
            'content': text_response,
            'analysis_parameters': param_data.get('analysis_parameters', {}),
            'response_type': 'enhanced' if param_data.get('analysis_parameters') else 'text'
        }
        
        return enhanced_response
