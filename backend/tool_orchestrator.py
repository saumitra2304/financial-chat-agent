"""
Tool orchestration helper for comprehensive financial analysis.
Helps the agent understand which tools to use for different types of analysis.
"""

from typing import Dict, List, Set
import re

class ToolOrchestrator:
    """Organizes tools into categories for comprehensive analysis."""
    
    def __init__(self):
        self.tool_categories = {
            'fundamental_analysis': {
                'get_ttm_ratios',
                'get_quarterly_results', 
                'get_profit_loss',
                'get_balance_sheet',
                'get_cashflow',
                'get_valuation_ratios',
                'get_efficiency_ratios',
                'get_solvency_ratios',
                'get_growth_ratios',
                'get_margin_ratios',
                'get_financial_stability_ratios',
                'get_cashflow_ratios',
                'get_shareholding'
            },
            'quantitative_analysis': {
                'adv_get_historical_price_data',
                'adv_calculate_volatility_metrics',
                'adv_calculate_correlation_analysis', 
                'adv_calculate_advanced_statistics',
                'adv_calculate_monte_carlo_simulation',
                'calculate_options_metrics',
                'calculate_portfolio_optimization',
                'calculate_garch_volatility_models',
                'calculate_pca_decomposition',
                'calculate_rolling_beta',
                'calculate_autocorrelation_analysis',
                'calculate_cointegration_test',
                'calculate_kalman_spread',
                'calculate_rolling_volatility',
                'calculate_drawdown_series',
                'calculate_var_cvar_analysis',
                'calculate_markov_regime_detection',
                'calculate_factor_exposure_ols',
                'calculate_factor_exposure_pca'
            },
            'technical_analysis': {
                'calculate_comprehensive_technical_analysis',
                'analyze_candlestick_patterns',
                'create_stock_charts',
                'adv_get_historical_price_data'
            },
            'portfolio_analysis': {
                'get_user_portfolio',
                'create_portfolio_charts',
                'calculate_portfolio_optimization',
                'adv_calculate_correlation_analysis'
            },
            'visualization': {
                'create_stock_charts',
                'create_portfolio_charts', 
                'create_correlation_chart',
                'create_risk_return_chart'
            },
            'research': {
                'WebSearchTool'
            }
        }
        
        # Keywords that should trigger comprehensive analysis
        self.comprehensive_triggers = {
            'fundamental_analysis': [
                'fundamental analysis', 'fundamental', 'financials', 'financial analysis',
                'balance sheet', 'income statement', 'cash flow', 'ratios',
                'profitability', 'liquidity', 'solvency', 'efficiency'
            ],
            'quantitative_analysis': [
                'quantitative analysis', 'quant analysis', 'statistical analysis',
                'statistics', 'volatility', 'correlation', 'monte carlo',
                'risk analysis', 'var', 'cvar', 'garch', 'beta', 'drawdown'
            ],
            'technical_analysis': [
                'technical analysis', 'chart analysis', 'price analysis',
                'candlestick', 'patterns', 'indicators', 'moving averages'
            ],
            'complete_analysis': [
                'complete analysis', 'comprehensive analysis', 'full analysis',
                'detailed analysis', 'in-depth analysis', 'thorough analysis',
                'everything about', 'all data', 'complete picture'
            ]
        }
    
    def get_required_tools_for_query(self, user_query: str) -> Dict[str, Set[str]]:
        """
        Analyze user query and return required tools for comprehensive analysis.
        
        Args:
            user_query: The user's request
            
        Returns:
            Dictionary mapping analysis types to required tool sets
        """
        query_lower = user_query.lower()
        required_tools = {}
        
        # Check for complete/comprehensive analysis requests
        if any(trigger in query_lower for trigger in self.comprehensive_triggers['complete_analysis']):
            # Return ALL tool categories for complete analysis
            required_tools['fundamental_analysis'] = self.tool_categories['fundamental_analysis']
            required_tools['quantitative_analysis'] = self.tool_categories['quantitative_analysis'] 
            required_tools['technical_analysis'] = self.tool_categories['technical_analysis']
            required_tools['visualization'] = self.tool_categories['visualization']
            required_tools['research'] = self.tool_categories['research']
            return required_tools
        
        # Check for specific analysis type requests
        for analysis_type, triggers in self.comprehensive_triggers.items():
            if analysis_type != 'complete_analysis':
                if any(trigger in query_lower for trigger in triggers):
                    required_tools[analysis_type] = self.tool_categories[analysis_type]
        
        # If portfolio mentioned, add portfolio tools
        if any(word in query_lower for word in ['portfolio', 'holdings', 'allocation']):
            required_tools['portfolio_analysis'] = self.tool_categories['portfolio_analysis']
        
        # If visualization/charts mentioned, add visualization tools
        if any(word in query_lower for word in ['chart', 'graph', 'plot', 'visualize']):
            required_tools['visualization'] = self.tool_categories['visualization']
            
        # If news/research mentioned, add research tools  
        if any(word in query_lower for word in ['news', 'research', 'latest', 'recent']):
            required_tools['research'] = self.tool_categories['research']
        
        return required_tools
    
    def get_analysis_prompt_enhancement(self, user_query: str) -> str:
        """
        Generate an enhanced prompt that guides the agent to use appropriate tools.
        
        Args:
            user_query: The user's original query
            
        Returns:
            Enhanced prompt with tool usage guidance
        """
        required_tools = self.get_required_tools_for_query(user_query)
        
        if not required_tools:
            return user_query
        
        enhancement = f"\n\nBased on your request, you should provide comprehensive analysis using these tool categories:\n"
        
        for analysis_type, tools in required_tools.items():
            enhancement += f"\n{analysis_type.upper().replace('_', ' ')}:\n"
            for tool in sorted(tools):
                enhancement += f"- {tool}\n"
        
        enhancement += f"\nEnsure you use ALL the tools listed above for a complete and thorough analysis. Don't skip any tools - the user expects comprehensive coverage.\n"
        
        return user_query + enhancement

# Global instance
tool_orchestrator = ToolOrchestrator()
