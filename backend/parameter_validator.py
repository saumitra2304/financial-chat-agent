"""
Parameter validation and default suggestion utilities for financial analysis.
This module provides validation and default parameter suggestions for various financial analysis tools.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import re


class ParameterValidator:
    """Validates and suggests default parameters for financial analysis functions."""
    
    # Default parameters for different analysis types
    DEFAULT_PARAMS = {
        "portfolio_optimization": {
            "time_period_years": 3,
            "risk_free_rate": 0.07,  # 7% based on Indian G-Sec yields
            "optimization_method": "efficient_frontier",
            "days_back": 1260,  # ~5 years of trading days
            "description": "Modern Portfolio Theory analysis"
        },
        "technical_analysis": {
            "short_ma": 20,
            "long_ma": 50,
            "rsi_period": 14,
            "bollinger_period": 20,
            "bollinger_std": 2,
            "description": "Technical indicator analysis"
        },
        "risk_analysis": {
            "confidence_level": 0.95,
            "time_horizon_days": 252,  # 1 year
            "monte_carlo_simulations": 1000,
            "description": "Risk metrics and Value-at-Risk analysis"
        },
        "fundamental_analysis": {
            "periods": 4,  # Last 4 quarters
            "comparison_type": "yoy",  # Year-over-year
            "description": "Fundamental financial analysis"
        }
    }
    
    @classmethod
    def validate_portfolio_request(cls, symbols: List[str], **kwargs) -> Tuple[bool, Dict[str, Any], str]:
        """
        Validate portfolio optimization request and suggest defaults.
        
        Returns:
            (is_valid, suggested_params, message)
        """
        if not symbols or len(symbols) < 2:
            return False, {}, "❌ Portfolio optimization requires at least 2 stocks. Please provide multiple stock names."
        
        defaults = cls.DEFAULT_PARAMS["portfolio_optimization"]
        missing_params = []
        suggestions = {}
        
        # Check for time period
        if not kwargs.get('time_period') and not kwargs.get('days_back'):
            missing_params.append("time period")
            suggestions['days_back'] = defaults['days_back']
        
        # Check for risk-free rate
        if not kwargs.get('risk_free_rate'):
            missing_params.append("risk-free rate")
            suggestions['risk_free_rate'] = defaults['risk_free_rate']
        
        # Check for optimization method
        if not kwargs.get('optimization_method'):
            suggestions['optimization_method'] = defaults['optimization_method']
        
        if missing_params:
            message = f"""
📊 **Portfolio Optimization Parameter Check**

For accurate Modern Portfolio Theory analysis of {', '.join(symbols)}, I need some additional parameters:

**Missing Parameters:**
{chr(10).join(f'• **{param.title()}**' for param in missing_params)}

**Suggested Defaults:**
• **Time Period**: {defaults['time_period_years']} years of historical data ({defaults['days_back']} trading days)
  - *Rationale: Captures multiple market cycles and provides statistical significance*
  
• **Risk-Free Rate**: {defaults['risk_free_rate']:.1%} (Current 10-year Government Security yield)
  - *Rationale: Used as baseline for Sharpe ratio calculation*
  
• **Optimization Method**: {defaults['optimization_method'].replace('_', ' ').title()}
  - *Rationale: Maximizes risk-adjusted returns*

**Would you like me to proceed with these defaults, or would you prefer to specify custom values?**
"""
            return False, suggestions, message
        
        return True, kwargs, "✅ All required parameters provided."
    
    @classmethod
    def validate_technical_analysis_request(cls, symbols: List[str], **kwargs) -> Tuple[bool, Dict[str, Any], str]:
        """Validate technical analysis request and suggest defaults."""
        defaults = cls.DEFAULT_PARAMS["technical_analysis"]
        suggestions = {}
        missing_params = []
        
        # Check for key technical parameters
        if not kwargs.get('time_period') and not kwargs.get('days'):
            missing_params.append("time period")
            suggestions['days'] = 252  # 1 year
        
        if not kwargs.get('indicators'):
            missing_params.append("indicators")
            suggestions['indicators'] = ["SMA", "RSI", "Bollinger Bands", "MACD"]
        
        if missing_params:
            message = f"""
📈 **Technical Analysis Parameter Check**

For comprehensive technical analysis of {', '.join(symbols)}, I can use these defaults:

**Default Settings:**
• **Time Period**: 1 year (252 trading days)
• **Moving Averages**: {defaults['short_ma']}-day and {defaults['long_ma']}-day
• **RSI Period**: {defaults['rsi_period']} days
• **Bollinger Bands**: {defaults['bollinger_period']}-day period with {defaults['bollinger_std']} standard deviations

**Would you like to proceed with these standard technical indicators?**
"""
            return False, suggestions, message
        
        return True, kwargs, "✅ Technical analysis parameters validated."
    
    @classmethod
    def validate_symbols(cls, symbols: List[str]) -> Tuple[bool, List[str], str]:
        """
        Validate stock symbols and suggest corrections if needed.
        
        Returns:
            (is_valid, cleaned_symbols, message)
        """
        if not symbols:
            return False, [], "❌ No stock symbols provided. Please specify company names or stock symbols."
        
        cleaned_symbols = []
        issues = []
        
        for symbol in symbols:
            # Clean up symbol
            cleaned = symbol.strip().upper()
            
            # Check if it's likely a partial name that needs expansion
            if len(cleaned.split()) == 1 and len(cleaned) < 4 and not cleaned.endswith('.NS'):
                issues.append(f"'{symbol}' - might need full company name")
            
            cleaned_symbols.append(cleaned)
        
        if issues:
            message = f"""
⚠️ **Symbol Verification Needed**

Some symbols might need clarification:
{chr(10).join(f'• {issue}' for issue in issues)}

**For accurate analysis, please provide:**
- Full company names (e.g., "Reliance Industries" not just "Reliance")
- Or complete NSE symbols (e.g., "RELIANCE.NS", "TCS.NS")

**Proceed anyway or provide more specific names?**
"""
            return False, cleaned_symbols, message
        
        return True, cleaned_symbols, "✅ Symbols validated."
    
    @classmethod  
    def get_analysis_defaults(cls, analysis_type: str) -> Dict[str, Any]:
        """Get default parameters for a specific analysis type."""
        return cls.DEFAULT_PARAMS.get(analysis_type, {}).copy()
    
    @classmethod
    def format_parameter_suggestion(cls, analysis_type: str, symbols: List[str], **user_params) -> str:
        """Format a parameter suggestion message for the user."""
        defaults = cls.get_analysis_defaults(analysis_type)
        
        if not defaults:
            return "✅ No additional parameters needed."
        
        message_parts = [
            f"📋 **{defaults.get('description', analysis_type.title())} - Parameter Setup**",
            f"",
            f"For analysis of: {', '.join(symbols)}",
            f"",
            f"**Recommended Settings:**"
        ]
        
        for key, value in defaults.items():
            if key not in ['description'] and key not in user_params:
                if isinstance(value, float):
                    message_parts.append(f"• **{key.replace('_', ' ').title()}**: {value:.2%}" if 'rate' in key else f"• **{key.replace('_', ' ').title()}**: {value}")
                else:
                    message_parts.append(f"• **{key.replace('_', ' ').title()}**: {value}")
        
        message_parts.extend([
            "",
            "**Would you like to proceed with these defaults or modify any parameters?**"
        ])
        
        return "\n".join(message_parts)


# Quick validation functions for common use cases
def validate_mpt_request(symbols: List[str], **kwargs) -> Tuple[bool, Dict, str]:
    """Quick validation for Modern Portfolio Theory requests."""
    return ParameterValidator.validate_portfolio_request(symbols, **kwargs)

def validate_technical_request(symbols: List[str], **kwargs) -> Tuple[bool, Dict, str]:
    """Quick validation for technical analysis requests."""
    return ParameterValidator.validate_technical_analysis_request(symbols, **kwargs)

def suggest_defaults(analysis_type: str, symbols: List[str], **user_params) -> str:
    """Quick default parameter suggestion."""
    return ParameterValidator.format_parameter_suggestion(analysis_type, symbols, **user_params)
