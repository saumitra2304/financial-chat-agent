"""
Professional Quantitative Finance Analysis Tools (Hygiene-Upgraded Version)
"""

import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Union, Any
import warnings
from dotenv import load_dotenv
from agents import function_tool
from python_helpers import get_fmp_price_data, search_symbol, search_nse_symbol_by_name
# Professional Finance Libraries
import QuantLib as ql
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt import CLA, HRPOpt
from arch import arch_model
    
# Scientific Computing and Statistics
from scipy import stats
from scipy.stats import norm, jarque_bera
from math import log, sqrt, exp
from statsmodels.tsa.stattools import acf, coint
import statsmodels.api as sm

# Optional imports with fallbacks
try:
    import pykalman
    PYKALMAN_AVAILABLE = True
except ImportError:
    PYKALMAN_AVAILABLE = False

try:
    from hmmlearn.hmm import GaussianHMM
    HMMLEARN_AVAILABLE = True
except ImportError:
    HMMLEARN_AVAILABLE = False

warnings.filterwarnings('ignore')
load_dotenv()

@function_tool
def verify_stock_for_advanced_analysis(company_name: str) -> dict:
	"""
	ADVANCED STOCK VERIFICATION: Confirms stock symbol and company details before sophisticated quantitative analysis.
	
	This verification tool provides:
	- Precise NSE stock symbol identification
	- Company fundamental details (market cap, current price)
	- Data availability confirmation for advanced analysis
	- User confirmation prompt to ensure correct stock selection
	
	Essential to use FIRST before any advanced quantitative analysis to avoid analyzing wrong companies.
	
	Args:
		company_name: Full company name as mentioned by user (e.g., 'reliance industries limited', 'infosys technologies')
	Returns:
		Detailed verification result with confirmation requirements
	"""
	try:
		# Search for NSE symbol
		nse_symbol = search_nse_symbol_by_name(company_name)
		
		if nse_symbol:
			# Get comprehensive company data
			import pymongo
			mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
			database_name = os.getenv('DB_NAME', 'chatbotdb')
			
			client = pymongo.MongoClient(mongo_uri)
			db = client[database_name]
			collection = db['stock_companies']
			
			company_doc = collection.find_one({'symbol': nse_symbol})
			
			if company_doc:
				# Additional data availability check
				price = company_doc.get('price', 0)
				market_cap = company_doc.get('marketCap', 0)
				volume = company_doc.get('volume', 0)
				
				data_quality = "Excellent" if all([price > 0, market_cap > 0, volume > 0]) else "Limited"
				
				result = {
					'verification_status': 'verified',
					'search_query': company_name,
					'confirmed_symbol': nse_symbol,
					'company_full_name': company_doc.get('name', 'N/A'),
					'current_price': f"₹{price:,.2f}" if price else 'N/A',
					'market_cap': f"₹{market_cap:,.0f}" if market_cap else 'N/A',
					'avg_volume': f"{company_doc.get('avgVolume', 0):,.0f}",
					'data_quality': data_quality,
					'analysis_ready': True,
					'confirmation_prompt': f"📊 VERIFICATION: Found '{company_doc.get('name', 'N/A')}' (Symbol: {nse_symbol}) trading at ₹{price:,.2f}. This company will be used for advanced quantitative analysis. Please confirm this is correct.",
					'next_steps': "Confirmation received. Ready to proceed with sophisticated financial analysis including portfolio optimization, risk modeling, and derivatives pricing."
				}
			else:
				result = {
					'verification_status': 'symbol_found_no_data',
					'search_query': company_name,
					'confirmed_symbol': nse_symbol,
					'confirmation_prompt': f"⚠️ Found symbol {nse_symbol} but limited company data available. Analysis may be restricted.",
					'analysis_ready': False
				}
		else:
			result = {
				'verification_status': 'not_found',
				'search_query': company_name,
				'confirmed_symbol': None,
				'confirmation_prompt': f"❌ Cannot find NSE stock for '{company_name}'. Please provide exact company name or symbol (e.g., 'RELIANCE.NS', 'TCS.NS').",
				'analysis_ready': False,
				'suggestions': [
					"Use full company names: 'Reliance Industries Limited', 'Tata Consultancy Services'",
					"Provide NSE symbols directly: 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'",
					"Check spelling and company name accuracy"
				]
			}
		
		return result
		
	except Exception as e:
		return {
			'verification_status': 'error',
			'search_query': company_name,
			'error_details': str(e),
			'confirmation_prompt': f"❌ Error during verification of '{company_name}': {str(e)}",
			'analysis_ready': False
		}

def resolve_symbol_or_name(input_str: str) -> str:
    """
    Internal helper to resolve company name to stock symbol using NSE database first.
    """
    # If input looks like a company name (long, alphabetic), try NSE search
    if len(input_str) > 5 and not '.' in input_str and input_str.replace(' ', '').isalpha():
        nse_symbol = search_nse_symbol_by_name(input_str)
        if nse_symbol:
            return nse_symbol
    
    # Otherwise return as-is (likely already a symbol)
    return input_str

# -----------------------------------------------------------------------------
# Internal helpers
# -----------------------------------------------------------------------------

def _align_and_clip_returns(df: pd.DataFrame, lookback_days: Optional[int] = None,
                            winsorise: bool = False, return_type: str = "simple") -> pd.Series:
    """
    Align prices to common index, apply optional lookback truncation and winsorisation.
    """
    series = df['Close']

    # Lookback truncation
    if lookback_days is not None and lookback_days < len(series):
        series = series.tail(lookback_days)

    # Convert to returns using proper methodology
    returns = _calculate_proper_returns(series, return_type=return_type, winsorise=winsorise, demean=False)

    return returns


def _calculate_proper_returns(prices: pd.Series, return_type: str = "log", 
                             winsorise: bool = False, demean: bool = False) -> pd.Series:
    """
    Calculate returns using proper financial methodology.
    
    Args:
        prices: Price series
        return_type: "log" (recommended), "simple", or "percent"
        winsorise: Apply winsorization to remove extreme outliers
        demean: Remove mean from returns (only for pure volatility modeling, default: False)
    
    Returns:
        Properly calculated returns series as floats
    """
    if return_type == "log":
        # Log returns: ln(P_t / P_{t-1})
        returns = np.log(prices / prices.shift(1)).dropna()
    elif return_type == "simple":
        # Simple returns: (P_t - P_{t-1}) / P_{t-1}
        returns = prices.pct_change().dropna()
    else:  # percent
        # Percentage returns (NOT recommended for modeling)
        returns = prices.pct_change().dropna() * 100
    
    # Convert to float to ensure proper numerical processing
    returns = returns.astype(float)
    
    # Optional winsorization (industry standard thresholds)
    if winsorise:
        lower = np.percentile(returns, 1.0)  # Industry standard: 1%/99%
        upper = np.percentile(returns, 99.0)
        returns = np.clip(returns, lower, upper)
    
    # Optional demeaning (recommended for volatility modeling)
    if demean and return_type != "percent":
        returns = returns - returns.mean()
    
    return returns


@function_tool
def get_returns_methodology_guide() -> dict:
    """
    RETURNS METHODOLOGY GUIDE: Professional guidance on when to use log returns vs simple returns.
    
    This utility function provides comprehensive guidance on choosing the appropriate
    return calculation methodology for different quantitative finance applications.
    
    Returns:
        Dictionary with detailed methodology recommendations and explanations
    """
    return {
        "returns_methodology_guide": {
            "log_returns_recommended_for": {
                "applications": [
                    "GARCH volatility modeling",
                    "Monte Carlo simulations", 
                    "Time series analysis",
                    "Statistical modeling and inference",
                    "Risk management (VaR, CVaR)",
                    "Options pricing volatility estimation",
                    "Regime detection and structural breaks"
                ],
                "reasons": [
                    "Log returns are normally distributed (better for statistical tests)",
                    "Time-additive: log(1+r1) + log(1+r2) = log((1+r1)*(1+r2))",
                    "Symmetric around zero (50% loss = -69%, 50% gain = +40%)", 
                    "Better statistical properties for parameter estimation",
                    "Required for proper Geometric Brownian Motion modeling"
                ],
                "mathematical_properties": [
                    "r_log = ln(P_t / P_{t-1})",
                    "Sum over time: R_T = Σ r_log_i",
                    "Approximately normal for short intervals",
                    "Stationary under efficient market conditions"
                ]
            },
            
            "simple_returns_recommended_for": {
                "applications": [
                    "Portfolio optimization (Modern Portfolio Theory)",
                    "Asset allocation and rebalancing",
                    "Performance measurement and reporting",
                    "Correlation analysis between assets",
                    "Beta calculation and CAPM applications",
                    "Multi-asset portfolio risk assessment",
                    "Client reporting and presentation"
                ],
                "reasons": [
                    "Cross-sectionally additive: Portfolio return = Σ w_i * r_i",
                    "Intuitive interpretation (10% return means value increased by 10%)",
                    "Standard in portfolio management industry",
                    "Required for proper portfolio weight calculation",
                    "Consistent with accounting and regulatory standards"
                ],
                "mathematical_properties": [
                    "r_simple = (P_t - P_{t-1}) / P_{t-1}",
                    "Portfolio return: R_p = Σ w_i * r_i",
                    "Not normally distributed (right-skewed)",
                    "Bounded below at -100% (cannot lose more than initial investment)"
                ]
            },
            
                         "default_settings_by_function": {
                 "calculate_volatility_metrics": {
                     "default": "log_returns",
                     "rationale": "Volatility modeling requires log returns for proper statistical properties and normality"
                 },
                 "calculate_portfolio_optimization": {
                     "default": "simple_returns", 
                     "rationale": "MPT requires simple returns for cross-asset additivity property"
                 },
                 "calculate_correlation_analysis": {
                     "default": "simple_returns",
                     "rationale": "Correlation analysis uses simple returns for cross-sectional properties"
                 },
                 "calculate_pca_decomposition": {
                     "default": "simple_returns",
                     "rationale": "PCA for correlation analysis uses simple returns"
                 },
                 "calculate_rolling_beta": {
                     "default": "simple_returns",
                     "rationale": "CAPM beta calculation uses simple returns for consistency"
                 },
                 "calculate_factor_exposure_ols": {
                     "default": "simple_returns",
                     "rationale": "Factor regression uses simple returns for interpretability"
                 },
                 "calculate_factor_exposure_pca": {
                     "default": "simple_returns",
                     "rationale": "Factor PCA uses simple returns for correlation analysis"
                 },
                 "calculate_monte_carlo_simulation": {
                     "default": "log_returns",
                     "rationale": "Geometric Brownian Motion requires log-normal price evolution"
                 },
                 "calculate_advanced_statistics": {
                     "default": "log_returns",
                     "rationale": "Statistical analysis prefers log returns for normality testing and distribution analysis"
                 },
                 "calculate_garch_volatility_models": {
                     "default": "log_returns",
                     "rationale": "GARCH models require stationary returns with normal-like properties"
                 },
                 "calculate_autocorrelation_analysis": {
                     "default": "log_returns",
                     "rationale": "Autocorrelation analysis prefers log returns for stationarity"
                 },
                 "calculate_cointegration_test": {
                     "default": "log_returns",
                     "rationale": "Cointegration testing prefers log returns for stationarity"
                 },
                 "calculate_rolling_volatility": {
                     "default": "log_returns",
                     "rationale": "Rolling volatility prefers log returns for statistical properties"
                 },
                 "calculate_var_cvar_analysis": {
                     "default": "log_returns",
                     "rationale": "VaR/CVaR analysis prefers log returns for statistical modeling"
                 },
                 "calculate_markov_regime_detection": {
                     "default": "log_returns",
                     "rationale": "Regime detection prefers log returns for stationarity"
                 },
                 "calculate_options_metrics": {
                     "default": "log_returns", 
                     "rationale": "Black-Scholes model assumes log-normal price distribution"
                 }
             },
            
            "practical_recommendations": {
                "general_rule": "Use simple returns for portfolio applications, log returns for statistical modeling",
                "when_in_doubt": "Simple returns for client-facing work, log returns for internal modeling", 
                "demeaning_guidance": "Only demean returns for pure volatility modeling (GARCH residuals), preserve mean for all other applications",
                "winsorization_standard": "Use 1%/99% percentiles for outlier treatment (industry standard)",
                "performance_impact": "Choice matters most for high-frequency data and extreme market conditions",
                "regulatory_compliance": "Most regulatory frameworks expect simple returns for reporting"
            }
        }
    }


@function_tool
def get_portfolio_optimization_objectives_guide() -> dict:
    """
    PORTFOLIO OPTIMIZATION OBJECTIVES GUIDE: Professional guidance on optimization objectives.
    
    This utility function provides comprehensive guidance on choosing the appropriate
    optimization objective for different investment goals and risk preferences.
    
    Returns:
        Dictionary with detailed objective descriptions and use cases
    """
    return {
        "portfolio_optimization_objectives": {
            "max_sharpe": {
                "description": "Maximize risk-adjusted returns (Sharpe ratio)",
                "formula": "max (E[r] - rf) / σ",
                "best_for": [
                    "General portfolio optimization",
                    "Risk-conscious investors",
                    "Long-term investment strategies",
                    "Balanced risk-return profile"
                ],
                "characteristics": [
                    "Balances return and risk equally",
                    "Penalizes both low returns and high volatility",
                    "Most commonly used objective in practice",
                    "Works well across different market conditions"
                ]
            },
            
            "min_volatility": {
                "description": "Minimize portfolio volatility (Global Minimum Variance)",
                "formula": "min σ^2 = w^T Σ w",
                "best_for": [
                    "Conservative investors",
                    "Capital preservation strategies",
                    "Risk-averse portfolios",
                    "Defensive allocation during market stress"
                ],
                "characteristics": [
                    "Focuses purely on risk reduction",
                    "May sacrifice returns for stability",
                    "Often results in highly diversified portfolios",
                    "Suitable for low-risk tolerance investors"
                ]
            },
            
            "max_return": {
                "description": "Maximize expected portfolio returns",
                "formula": "max w^T μ",
                "best_for": [
                    "Aggressive growth strategies",
                    "High risk tolerance investors",
                    "Bull market conditions",
                    "Speculative allocations"
                ],
                "characteristics": [
                    "Ignores risk considerations",
                    "May result in concentrated portfolios",
                    "Subject to estimation error in expected returns",
                    "Requires high conviction in return forecasts"
                ]
            },
            
            "min_drawdown": {
                "description": "Minimize maximum historical drawdown",
                "formula": "min max((Peak - Trough) / Peak)",
                "best_for": [
                    "Drawdown-sensitive strategies",
                    "Institutional investors with risk limits",
                    "Pension funds and endowments",
                    "Strategies requiring capital preservation"
                ],
                "characteristics": [
                    "Focuses on downside risk management",
                    "Historical data dependent",
                    "May not prevent future drawdowns",
                    "Computationally intensive optimization"
                ]
            },
            
            "min_cvar": {
                "description": "Minimize Conditional Value at Risk (Expected Shortfall)",
                "formula": "min E[r | r ≤ VaR_α]",
                "best_for": [
                    "Risk management focused strategies",
                    "Tail risk minimization",
                    "Regulatory compliance (Basel III)",
                    "Extreme event protection"
                ],
                "characteristics": [
                    "Coherent risk measure",
                    "Addresses tail risk explicitly",
                    "More sophisticated than VaR",
                    "Requires careful return distribution modeling"
                ]
            },
            
            "efficient_return": {
                "description": "Minimize risk for a target return level",
                "formula": "min σ^2 subject to E[r] = r_target",
                "best_for": [
                    "Target return strategies",
                    "Liability matching portfolios",
                    "Benchmark relative strategies",
                    "Goal-based investing"
                ],
                "characteristics": [
                    "Risk minimization with return constraint",
                    "Requires realistic return targets",
                    "May be infeasible for extreme targets",
                    "Classic mean-variance optimization approach"
                ]
            }
        },
        
        "objective_selection_guide": {
            "risk_tolerance": {
                "conservative": ["min_volatility", "min_drawdown", "min_cvar"],
                "moderate": ["max_sharpe", "efficient_return"],
                "aggressive": ["max_return", "max_sharpe"]
            },
            
            "market_conditions": {
                "bull_market": ["max_return", "max_sharpe"],
                "bear_market": ["min_volatility", "min_drawdown"],
                "high_volatility": ["min_volatility", "min_cvar"],
                "stable_market": ["max_sharpe", "efficient_return"]
            },
            
            "investment_horizon": {
                "short_term": ["min_volatility", "min_drawdown"],
                "medium_term": ["max_sharpe", "efficient_return"],
                "long_term": ["max_return", "max_sharpe"]
            },
            
            "practical_recommendations": {
                "default_choice": "max_sharpe - Best balance for most investors",
                "institutional": "min_drawdown or min_cvar for risk management",
                "retail": "max_sharpe or min_volatility for simplicity",
                "advanced_users": "All objectives available based on specific needs"
            }
        }
    }


# -----------------------------------------------------------------------------
# CORE TOOLS (UPGRADED)
# -----------------------------------------------------------------------------

@function_tool
def get_historical_price_data(symbol: str, timeframe: str = "5min",
                              days_back: int = 30) -> dict | None:
    # Resolve company name to symbol if needed
    resolved_symbol = resolve_symbol_or_name(symbol)
    
    result = get_fmp_price_data(resolved_symbol, timeframe, days_back, return_format="dict")
    if result and "data" in result:
        result["data"] = result["data"][:50]  # truncate for context safety
        return result
    return result


@function_tool
def calculate_volatility_metrics(symbol: str, timeframe: str = "1d", days_back: int = 252,
                                 winsorise: bool = False, return_type: str = "log",
                                 volatility_models: List[str] = ["historical", "ewma", "garch"]) -> dict | None:
    """
    ADVANCED VOLATILITY ANALYSIS: Professional volatility measurement with multiple methodologies.
    
    This tool provides comprehensive volatility analysis including:
    - Multiple volatility estimation methods (Historical, EWMA, GARCH)
    - User choice between log returns (better for statistical modeling) and simple returns (industry standard)
    - Volatility clustering detection and modeling
    - Risk-adjusted volatility metrics
    - Volatility forecasting and regime analysis
    
    Args:
        symbol: Stock ticker symbol for volatility analysis
        timeframe: Data frequency (1d, 4hour, 1hour, etc.)
        days_back: Historical data period for analysis
        winsorise: Apply winsorization to remove extreme outliers
        use_log_returns: Use log returns (better for modeling) vs simple returns (industry standard, default)
        volatility_models: List of models to calculate ["historical", "ewma", "garch"]
    
    Returns:
        Dictionary with multiple volatility measures, risk metrics, and analysis
    """
    # Resolve company name to symbol if needed
    resolved_symbol = resolve_symbol_or_name(symbol)
    
    df = get_fmp_price_data(resolved_symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch price data for {resolved_symbol}"}

    # Calculate proper returns - volatility analysis preserves expected returns for proper risk-return analysis
    prices = df['Close']
    returns = _calculate_proper_returns(prices, return_type=return_type, winsorise=winsorise, demean=False)
    
    if len(returns) < 20:
        return {"error": "Insufficient data for volatility calculation"}

    # Annualization factors for different timeframes
    annual_factor_map = {
        "1min": 525600, "5min": 105120, "15min": 35040,
        "30min": 17520, "1hour": 8760, "4hour": 2190,
        "1day": 252, "1d": 252
    }
    annual_factor = annual_factor_map.get(timeframe, 252)
    
    try:
        results = {
            "symbol": resolved_symbol,
            "analysis_parameters": {
                "timeframe": timeframe,
                "observations": len(returns),
                "data_period": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
                "return_methodology": f"{return_type}_returns",
                "winsorized": winsorise,
                "annualization_factor": annual_factor
            }
        }
        
        volatility_measures = {}
        
        # 1. Historical Volatility (Standard Method)
        if "historical" in volatility_models:
            historical_vol_daily = returns.std()
            historical_vol_annual = historical_vol_daily * np.sqrt(annual_factor)
            
            volatility_measures["historical"] = {
                "daily_volatility": round(float(historical_vol_daily * 100), 4),
                "annualized_volatility": round(float(historical_vol_annual * 100), 4),
                "volatility_of_volatility": round(float(returns.rolling(21).std().std() * 100), 4)
            }
        
        # 2. Exponentially Weighted Moving Average (EWMA)
        if "ewma" in volatility_models:
            lambda_decay = 0.94  # RiskMetrics standard
            ewma_var = returns.var()
            ewma_series = []
            
            for i, ret in enumerate(returns):
                if i == 0:
                    ewma_var = ret**2
                else:
                    ewma_var = lambda_decay * ewma_var + (1 - lambda_decay) * ret**2
                ewma_series.append(np.sqrt(ewma_var))
            
            current_ewma_vol = ewma_series[-1] if ewma_series else 0
            annual_ewma_vol = current_ewma_vol * np.sqrt(annual_factor)
            
            volatility_measures["ewma"] = {
                "current_daily_volatility": round(float(current_ewma_vol * 100), 4),
                "current_annualized_volatility": round(float(annual_ewma_vol * 100), 4),
                "lambda_parameter": lambda_decay
            }
        
        # 3. GARCH Volatility (if requested and data sufficient)
        if "garch" in volatility_models and len(returns) >= 100:
            try:
                garch_model = arch_model(returns * 100, vol="GARCH", p=1, q=1)
                garch_fitted = garch_model.fit(disp="off", show_warning=False)
                
                current_garch_vol = garch_fitted.conditional_volatility.iloc[-1]
                annual_garch_vol = current_garch_vol * np.sqrt(annual_factor)
                
                volatility_measures["garch"] = {
                    "current_daily_volatility": round(float(current_garch_vol), 4),
                    "current_annualized_volatility": round(float(annual_garch_vol), 4),
                    "model_aic": round(float(garch_fitted.aic), 4),
                    "persistence": "High" if garch_fitted.params.iloc[1] + garch_fitted.params.iloc[2] > 0.95 else "Moderate"
                }
            except:
                volatility_measures["garch"] = {"error": "GARCH fitting failed - insufficient data or convergence issues"}
        
        # Statistical Properties of Returns
        statistical_properties = {
            "mean_return_daily": round(float(returns.mean() * 100), 4),
            "mean_return_annualized": round(float(returns.mean() * annual_factor * 100), 4),
            "skewness": round(float(stats.skew(returns)), 4),
            "kurtosis": round(float(stats.kurtosis(returns)), 4),
            "jarque_bera_pvalue": round(float(stats.jarque_bera(returns)[1]), 4),
            "returns_normal": bool(stats.jarque_bera(returns)[1] > 0.05)
        }
        
        # Volatility Clustering Analysis
        abs_returns = np.abs(returns)
        volatility_clustering = {
            "autocorr_abs_returns_lag1": round(float(abs_returns.autocorr(lag=1)), 4),
            "autocorr_abs_returns_lag5": round(float(abs_returns.autocorr(lag=5)), 4),
            "volatility_clustering_detected": bool(abs_returns.autocorr(lag=1) > 0.1)
        }
        
        # Risk Metrics
        var_95 = np.percentile(returns, 5) * 100
        var_99 = np.percentile(returns, 1) * 100
        cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100
        
        risk_metrics = {
            "value_at_risk_95_daily": round(float(var_95), 4),
            "value_at_risk_99_daily": round(float(var_99), 4),
            "conditional_var_95_daily": round(float(cvar_95), 4),
            "maximum_daily_loss": round(float(returns.min() * 100), 4),
            "maximum_daily_gain": round(float(returns.max() * 100), 4)
        }
        
        results.update({
            "volatility_measures": volatility_measures,
            "statistical_properties": statistical_properties,
            "volatility_clustering": volatility_clustering,
            "risk_metrics": risk_metrics
        })
        
        return results
        
    except Exception as e:
        return {"error": f"Volatility analysis failed: {str(e)}"}


@function_tool
def calculate_correlation_analysis(symbols: List[str], timeframe: str = "1d", days_back: int = 252,
                                   winsorise: bool = False, return_type: str = "simple") -> dict | None:
    """
    CORRELATION ANALYSIS: Professional correlation measurement between multiple assets.
    
    This tool provides comprehensive correlation analysis including:
    - Pearson correlation coefficients between asset pairs
    - User choice between log returns and simple returns
    - Statistical significance testing of correlations
    - Correlation matrix visualization data
    - Identification of highest and lowest correlations
    
    Args:
        symbols: List of stock symbols for correlation analysis
        timeframe: Data frequency (1d, 4hour, 1hour, etc.)
        days_back: Historical data period for analysis
        winsorise: Apply winsorization to remove extreme outliers
        use_log_returns: Use log returns vs simple returns (default: False, simple returns standard for correlation analysis)
    
    Returns:
        Dictionary with correlation matrix and key correlation insights
    """
    # Resolve company names to symbols if needed
    resolved_symbols = [resolve_symbol_or_name(sym) for sym in symbols]
    
    price_df = pd.DataFrame()
    for sym in resolved_symbols:
        df = get_fmp_price_data(sym, timeframe, days_back, return_format="dataframe")
        if df is not None and not df.empty:
            price_df[sym] = df["Close"]

    if price_df.empty:
        return {"error": "Could not fetch data"}

    # Align by dropping rows where all are NaN
    price_df = price_df.dropna(how="all").dropna()

    # Calculate returns using chosen methodology - correlation analysis uses simple returns for cross-sectional properties
    returns = pd.DataFrame()
    for col in price_df.columns:
        returns[col] = _calculate_proper_returns(price_df[col], return_type=return_type, winsorise=winsorise, demean=False)

    returns = returns.dropna()
    
    if returns.empty or len(returns) < 10:
        return {"error": "Insufficient return data for correlation analysis"}

    corr = returns.corr()
    
    # Find highest and lowest correlations
    highest, lowest = None, None
    high_val, low_val = -1, 1
    
    for i, s1 in enumerate(resolved_symbols):
        for s2 in resolved_symbols[i+1:]:
            if s1 in corr.index and s2 in corr.columns:
                cval = corr.loc[s1, s2]
                if abs(cval) > abs(high_val):
                    high_val, highest = cval, f"{s1}-{s2}"
                if abs(cval) < abs(low_val):
                    low_val, lowest = cval, f"{s1}-{s2}"

    # Calculate average correlation and dispersion
    corr_values = []
    for i in range(len(corr)):
        for j in range(i+1, len(corr)):
            if not pd.isna(corr.iloc[i, j]):
                corr_values.append(corr.iloc[i, j])
    
    avg_correlation = np.mean(corr_values) if corr_values else 0
    correlation_std = np.std(corr_values) if corr_values else 0

    return {
        "symbols": resolved_symbols,
        "analysis_parameters": {
            "return_methodology": f"{return_type}_returns",
            "observations": len(returns),
            "timeframe": timeframe,
            "winsorized": winsorise
        },
        "correlation_matrix": corr.round(4).to_dict(),
        "correlation_summary": {
            "highest_correlation": {"pair": highest, "correlation": round(float(high_val), 4)},
            "lowest_correlation": {"pair": lowest, "correlation": round(float(low_val), 4)},
            "average_correlation": round(float(avg_correlation), 4),
            "correlation_dispersion": round(float(correlation_std), 4)
        }
    }


@function_tool
def calculate_advanced_statistics(symbol: str, timeframe: str = "1d", days_back: int = 252,
                                  winsorise: bool = False, return_type: str = "log") -> dict | None:
    """
    ADVANCED STATISTICAL ANALYSIS: Comprehensive statistical testing and distribution analysis.
    
    This tool provides detailed statistical analysis of return distributions including:
    - Descriptive statistics (mean, variance, skewness, kurtosis)
    - Normality testing (Jarque-Bera test)
    - Autocorrelation analysis  
    - Distribution diagnostics and model validation
    - User choice between log returns and simple returns
    
    Args:
        symbol: Stock ticker symbol for analysis
        timeframe: Data frequency (1d, 4hour, 1hour, etc.)
        days_back: Historical data period for analysis
        winsorise: Apply winsorization to remove extreme outliers
        use_log_returns: Use log returns vs simple returns (default: False, simple returns for general statistics)
    
    Returns:
        Dictionary with comprehensive statistical analysis results
    """
    # Resolve company name to symbol if needed
    resolved_symbol = resolve_symbol_or_name(symbol)
    
    df = get_fmp_price_data(resolved_symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch price data for {resolved_symbol}"}

    # Calculate returns using chosen methodology - statistical analysis uses actual returns for proper distribution testing
    prices = df['Close']
    returns = _calculate_proper_returns(prices, return_type=return_type, winsorise=winsorise, demean=False)
    
    if len(returns) < 30:
        return {"error": "Insufficient data for statistical analysis"}

    try:
        # Statistical tests
        jb_stat, jb_pvalue = stats.jarque_bera(returns)
        
        # Autocorrelation analysis  
        autocorr = acf(returns, nlags=5, fft=True)
        
        # Additional statistical tests
        shapiro_stat, shapiro_pvalue = stats.shapiro(returns[:5000] if len(returns) > 5000 else returns)  # Shapiro limited to 5000 obs
        
        return {
            "symbol": resolved_symbol,
            "analysis_parameters": {
                "return_methodology": f"{return_type}_returns",
                "observations": len(returns),
                "timeframe": timeframe,
                "winsorized": winsorise
            },
            "descriptive_stats": {
                "mean_return": round(float(returns.mean() * 100), 4),  # Convert to percentage
                "std_deviation": round(float(returns.std() * 100), 4),
                "skewness": round(float(stats.skew(returns)), 4),
                "kurtosis": round(float(stats.kurtosis(returns)), 4),
                "minimum_return": round(float(returns.min() * 100), 4),
                "maximum_return": round(float(returns.max() * 100), 4)
            },
            "normality_tests": {
                "jarque_bera_statistic": round(float(jb_stat), 4),
                "jarque_bera_pvalue": round(float(jb_pvalue), 6),
                "is_normal_jb": bool(jb_pvalue > 0.05),
                "shapiro_wilk_statistic": round(float(shapiro_stat), 4),
                "shapiro_wilk_pvalue": round(float(shapiro_pvalue), 6),
                "is_normal_sw": bool(shapiro_pvalue > 0.05)
            },
            "autocorrelation": {
                f"lag_{i}": round(float(autocorr[i]), 4) for i in range(1, min(6, len(autocorr)))
            },
            "distribution_characteristics": {
                "excess_kurtosis": round(float(stats.kurtosis(returns)), 4),
                "is_leptokurtic": bool(stats.kurtosis(returns) > 0),
                "is_platykurtic": bool(stats.kurtosis(returns) < 0),
                "is_left_skewed": bool(stats.skew(returns) < 0),
                "is_right_skewed": bool(stats.skew(returns) > 0)
            }
        }
        
    except Exception as e:
        return {"error": f"Statistical analysis failed: {str(e)}"}


@function_tool
def calculate_monte_carlo_simulation(symbol: str, forecast_days: int = 10, simulations: int = 1000,
                                     confidence_level: float = 0.95, winsorise: bool = False,
                                     return_type: str = "log", 
                                     include_volatility_clustering: bool = True, random_seed: Optional[int] = None) -> dict | None:
    """
    ADVANCED MONTE CARLO SIMULATION: Professional price forecasting with proper statistical methods.
    
    This tool provides sophisticated Monte Carlo price simulation including:
    - Proper log-normal price evolution modeling (when using log returns)
    - Geometric Brownian Motion implementation
    - Statistical validation and confidence intervals
    - Optional volatility clustering (GARCH-based)
    - Multiple simulation scenarios and stress testing
    
    Args:
        symbol: Stock ticker symbol for simulation
        forecast_days: Number of days to forecast (default: 10)
        simulations: Number of simulation paths (default: 1000, minimum: 100)
        confidence_level: Confidence level for intervals (default: 0.95)
        winsorise: Apply winsorization to historical returns
        use_log_returns: Use log returns for proper GBM modeling (recommended for simulations, default: True)
        include_volatility_clustering: Account for volatility clustering effects
        random_seed: Optional random seed for reproducibility (default: None for truly random)
    
    Returns:
        Dictionary with price forecasts, confidence intervals, and risk metrics
    """
    # Resolve company name to symbol if needed
    resolved_symbol = resolve_symbol_or_name(symbol)
    
    df = get_fmp_price_data(resolved_symbol, "1d", 252, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch price data for {resolved_symbol}"}

    # Calculate proper returns using new helper function
    prices = df["Close"]
    current_price = prices.iloc[-1]
    
    # Monte Carlo simulation uses historical drift and volatility parameters from actual returns
    returns = _calculate_proper_returns(prices, return_type=return_type, winsorise=winsorise, demean=False)
    
    if len(returns) < 50:
        return {"error": "Insufficient historical data for reliable simulation"}
    
    # Validate simulation parameters
    if simulations < 100:
        simulations = 100
    if simulations > 10000:
        simulations = 10000  # Prevent excessive computation
    
    # Calculate statistical parameters
    mu = returns.mean()  # Drift
    sigma = returns.std()  # Volatility
    
    # Statistical validation
    if sigma == 0:
        return {"error": "Zero volatility detected - simulation not meaningful"}
    
    try:
        # Set random seed only if specified for reproducibility
        if random_seed is not None:
            np.random.seed(random_seed)
        
        results = []
        daily_returns_simulated = []
        
        # Monte Carlo simulation using Geometric Brownian Motion
        for sim in range(simulations):
            price_path = [current_price]
            returns_path = []
            
            for day in range(forecast_days):
                if return_type == "log":
                    # Log-normal model: S(t+1) = S(t) * exp((μ - σ²/2)Δt + σ√ΔtZ)
                    dt = 1.0  # Daily time step
                    drift = (mu - 0.5 * sigma**2) * dt
                    shock = sigma * np.sqrt(dt) * np.random.standard_normal()
                    next_price = price_path[-1] * np.exp(drift + shock)
                    daily_return = np.log(next_price / price_path[-1])
                else:
                    # Simple return model with drift
                    daily_return = np.random.normal(mu, sigma)
                    next_price = price_path[-1] * (1 + daily_return)
                
                price_path.append(next_price)
                returns_path.append(daily_return)
            
            results.append(price_path[-1])  # Final price
            daily_returns_simulated.extend(returns_path)
        
        # Calculate confidence intervals
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bound = np.percentile(results, lower_percentile)
        upper_bound = np.percentile(results, upper_percentile)
        expected_price = np.mean(results)
        
        # Risk metrics
        prob_loss = np.mean([p < current_price for p in results]) * 100
        prob_gain_10pct = np.mean([p > current_price * 1.1 for p in results]) * 100
        max_simulated_price = np.max(results)
        min_simulated_price = np.min(results)
        
        # Calculate Value at Risk (VaR)
        returns_distribution = [(p - current_price) / current_price for p in results]
        var_5pct = np.percentile(returns_distribution, 5) * 100
        var_1pct = np.percentile(returns_distribution, 1) * 100
        
        simulation_results = {
            "symbol": resolved_symbol,
            "simulation_parameters": {
                "forecast_horizon_days": forecast_days,
                "number_of_simulations": simulations,
                "confidence_level": confidence_level,
                "current_price": round(float(current_price), 2),
                "historical_data_points": len(returns),
                "return_methodology": f"{return_type}_returns"
            },
            
            "price_forecasts": {
                "expected_price": round(float(expected_price), 2),
                "confidence_interval_lower": round(float(lower_bound), 2),
                "confidence_interval_upper": round(float(upper_bound), 2),
                "price_range_min": round(float(min_simulated_price), 2),
                "price_range_max": round(float(max_simulated_price), 2)
            },
            
            "statistical_parameters": {
                "historical_drift_daily": round(float(mu), 6),
                "historical_volatility_daily": round(float(sigma), 6),
                "historical_volatility_annualized": round(float(sigma * np.sqrt(252)), 4),
                "annualized_expected_return": round(float(mu * 252), 4)
            },
            
            "risk_metrics": {
                "probability_of_loss_pct": round(float(prob_loss), 2),
                "probability_gain_10pct_pct": round(float(prob_gain_10pct), 2),
                "value_at_risk_5pct": round(float(var_5pct), 2),
                "value_at_risk_1pct": round(float(var_1pct), 2),
                "expected_return_pct": round(float((expected_price - current_price) / current_price * 100), 2)
            }
        }
        
        return simulation_results
        
    except Exception as e:
        return {"error": f"Monte Carlo simulation failed: {str(e)}"}


@function_tool
def calculate_portfolio_optimization(symbols: List[str], optimization_method: str = "efficient_frontier",
                                     risk_model: str = "sample_cov", days_back: int = 1260,
                                     lookback_days: Optional[int] = None,
                                     risk_free_rate: float = 0.0,
                                     winsorise: bool = False,
                                     min_weight: float = 0.0,
                                     max_weight: float = 1.0,
                                     optimization_objective: str = "max_sharpe", return_type: str = "simple") -> dict | None:
    """
    ADVANCED PORTFOLIO OPTIMIZATION: Professional portfolio construction with statistical rigor.
    
    This tool provides sophisticated portfolio optimization including:
    - Multiple optimization methods (Mean-Variance, HRP)
    - Consistent arithmetic returns throughout (EF standard)
    - Proper data alignment across assets (common overlap period)
    - Correct percentage-based drawdown calculations
    - Daily VaR/CVaR metrics with proper labeling (positive loss convention)
    - Raw weight consistency between optimization and risk calculations
    - Statistical validation and backtesting
    - Constraint handling and weight bounds
    - Risk factor analysis and attribution
    
    IMPORTANT: Uses arithmetic (simple) returns consistently throughout for proper Modern 
    Portfolio Theory implementation. All risk metrics, optimization inputs, and performance 
    calculations use the same return methodology for coherent results.
    
    Args:
        symbols: List of stock symbols for portfolio construction
        optimization_method: "efficient_frontier", "cla", "hrp"
        risk_model: Risk covariance estimation method
        days_back: Historical data period (default: ~5 years)
        lookback_days: Specific lookback override
        risk_free_rate: Risk-free rate for Sharpe ratio calculation
        winsorise: Apply winsorization to returns (per asset to preserve relative volatilities)
        min_weight/max_weight: Portfolio weight constraints
        optimization_objective: "max_sharpe", "min_volatility", "max_return", "min_drawdown", "min_cvar", "efficient_return"
    
    Returns:
        Comprehensive portfolio optimization results with weights and metrics
        Note: VaR/CVaR are daily expected loss percentages; drawdown is percentage-based
    """
    # Resolve company names to symbols if needed
    resolved_symbols = [resolve_symbol_or_name(sym) for sym in symbols]
    
    price_df = pd.DataFrame()
    data_quality_info = {}
    
    for sym in resolved_symbols:
        df = get_fmp_price_data(sym, "1d", days_back, return_format="dataframe")
        if df is not None and not df.empty:
            price_df[sym] = df["Close"]
            data_quality_info[sym] = {
                "data_points": len(df),
                "start_date": df.index[0].strftime('%Y-%m-%d'),
                "end_date": df.index[-1].strftime('%Y-%m-%d')
            }
        else:
            data_quality_info[sym] = {"error": "No data available"}

    if price_df.empty:
        return {"error": "Could not fetch price data for any symbols"}
    
    # Check for sufficient overlap
    if len(price_df.columns) < 2:
        return {"error": "Need at least 2 assets for portfolio optimization"}

    if lookback_days is not None:
        price_df = price_df.tail(lookback_days)

    # Remove periods with missing data to avoid look-ahead bias 
    # Use complete data only for unbiased covariance estimation
    price_df = price_df.dropna(how="all")
    price_df = price_df.dropna()  # Remove any remaining NaN values
    
    if len(price_df) < 60:
        return {"error": "Insufficient overlapping price history for optimization"}
    
    # Calculate returns using proper methodology - MPT requires simple returns for cross-sectional additivity
    returns = pd.DataFrame()
    for col in price_df.columns:
        returns[col] = _calculate_proper_returns(price_df[col], return_type=return_type, winsorise=winsorise, demean=False)
    
    returns = returns.dropna()
    
    if returns.empty or len(returns) < 30:
        return {"error": "Insufficient return data for optimization"}
    
    try:
        # Calculate annualized expected returns and covariance matrix directly from returns
        # This ensures consistency between optimization inputs and risk metric calculations
        mu = returns.mean() * 252  # Annualized arithmetic mean
        
        # Calculate covariance matrix using specified method on returns (not prices)
        if risk_model == "sample_cov":
            cov = returns.cov() * 252  # Annualized sample covariance
        elif risk_model == "ledoit_wolf":
            # Use Ledoit-Wolf shrinkage on returns covariance
            from sklearn.covariance import LedoitWolf
            lw = LedoitWolf()
            cov_matrix = lw.fit(returns.values).covariance_
            cov = pd.DataFrame(cov_matrix, index=returns.columns, columns=returns.columns) * 252
        elif risk_model == "oracle_approximation":
            # Fallback to sample covariance for oracle approximation
            cov = returns.cov() * 252
        else:
            cov = returns.cov() * 252
        
        # Perform optimization based on method and objective
        if optimization_method == "efficient_frontier":
            ef = EfficientFrontier(mu, cov, weight_bounds=(min_weight, max_weight))
            
            # Apply optimization objective (don't subtract risk_free_rate from mu since it's passed to methods)
            if optimization_objective == "max_sharpe":
                weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
            elif optimization_objective == "min_volatility":
                weights = ef.min_volatility()
            elif optimization_objective == "max_return":
                # Target the maximum possible return within constraints
                max_ret = mu.max()
                try:
                    weights = ef.efficient_return(target_return=max_ret * 0.95)  # 95% of max to ensure feasibility
                except:
                    weights = ef.max_sharpe(risk_free_rate=risk_free_rate)  # Fallback
            elif optimization_objective == "efficient_return":
                # Target a reasonable return level
                target_ret = mu.mean() + mu.std()
                try:
                    weights = ef.efficient_return(target_return=target_ret)
                except:
                    weights = ef.max_sharpe(risk_free_rate=risk_free_rate)  # Fallback
            elif optimization_objective == "min_cvar":
                # Minimize Conditional VaR - approximated with min volatility 
                # (for true CVaR optimization, consider EfficientCVaR if available)
                weights = ef.min_volatility()
            else:  # Default to max_sharpe
                weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
                
            perf = ef.portfolio_performance(risk_free_rate=risk_free_rate, verbose=False)
            clean_w = ef.clean_weights()
            
        elif optimization_method == "cla":
            cla = CLA(mu, cov, weight_bounds=(min_weight, max_weight))
            weights = cla.max_sharpe()
            clean_w = cla.clean_weights()
            perf = cla.portfolio_performance(risk_free_rate=risk_free_rate)
            
        elif optimization_method == "hrp":
            hrp = HRPOpt(returns)
            clean_w = hrp.optimize()
            
            # Calculate performance for HRP using same returns
            port_ret = (returns * pd.Series(clean_w, index=returns.columns)).sum(axis=1)
            annual_ret = port_ret.mean() * 252
            annual_vol = port_ret.std() * np.sqrt(252)
            sharpe = (annual_ret - risk_free_rate) / annual_vol if annual_vol > 0 else 0
            perf = (annual_ret, annual_vol, sharpe)
            
        else:
            return {"error": f"Unsupported optimization method: {optimization_method}"}
        
        # Handle minimum drawdown optimization as post-processing
        if optimization_objective == "min_drawdown":
            # Grid search over efficient frontier to find minimum drawdown portfolio
            try:
                ef_temp = EfficientFrontier(mu, cov, weight_bounds=(min_weight, max_weight))
                
                # Generate efficient frontier points
                ret_range = np.linspace(mu.min(), mu.max(), 20)
                best_weights = clean_w
                min_drawdown = float('inf')
                
                for target_ret in ret_range:
                    try:
                        ef_temp = EfficientFrontier(mu, cov, weight_bounds=(min_weight, max_weight))
                        temp_weights = ef_temp.efficient_return(target_return=target_ret)
                        temp_clean_w = ef_temp.clean_weights()
                        
                        # Calculate drawdown for this portfolio using raw weights for consistency
                        temp_weights_series = pd.Series(temp_clean_w, index=returns.columns, dtype=float).fillna(0.0)
                        temp_weights_series = temp_weights_series.clip(lower=0)
                        if not np.isclose(temp_weights_series.sum(), 1.0):
                            temp_weights_series = temp_weights_series / temp_weights_series.sum()
                        temp_port_returns = (returns * temp_weights_series).sum(axis=1)
                        temp_cumulative = (temp_port_returns + 1).cumprod()
                        temp_drawdown = 1 - (temp_cumulative / temp_cumulative.cummax())
                        temp_dd = temp_drawdown.max()
                        
                        if temp_dd < min_drawdown:
                            min_drawdown = temp_dd
                            best_weights = temp_clean_w
                    except:
                        continue
                
                clean_w = best_weights
                # Recalculate performance metrics for the min drawdown portfolio using same returns
                weights_series = pd.Series(clean_w, index=returns.columns)
                portfolio_returns_temp = (returns * weights_series).sum(axis=1)
                annual_ret = portfolio_returns_temp.mean() * 252
                annual_vol = portfolio_returns_temp.std() * np.sqrt(252)
                sharpe = (annual_ret - risk_free_rate) / annual_vol if annual_vol > 0 else 0
                perf = (annual_ret, annual_vol, sharpe)
                
            except Exception as e:
                pass  # Use original optimization if min_drawdown fails
        
        # Portfolio analytics
        portfolio_return, portfolio_volatility, sharpe_ratio = perf
        
        # Build a weight series for risk stats using raw weights when available
        # (clean_weights() rounds small weights to zero, causing drift vs EF's internal weights)
        if optimization_method == "efficient_frontier":
            w_series = pd.Series(ef.weights, index=returns.columns, dtype=float)
        elif optimization_method == "cla":
            w_series = pd.Series(cla.weights, index=returns.columns, dtype=float)
        else:  # HRP returns a dict; ensure all tickers present
            w_series = pd.Series(clean_w, index=returns.columns, dtype=float).fillna(0.0)

        # Guard against tiny negatives and rounding drift
        w_series = w_series.clip(lower=0)
        if not np.isclose(w_series.sum(), 1.0):
            w_series = w_series / w_series.sum()
        
        # Calculate additional risk metrics using raw weights for consistency
        portfolio_returns = (returns * w_series).sum(axis=1)
        
        # Risk metrics (using positive loss convention for clarity)
        var_95_daily = -np.percentile(portfolio_returns, 5) * 100
        cvar_95_daily = -portfolio_returns[portfolio_returns <= np.percentile(portfolio_returns, 5)].mean() * 100
        
        # Maximum drawdown (percentage) using consistent returns
        cumulative = (1 + portfolio_returns).cumprod()
        drawdown = 1 - (cumulative / cumulative.cummax())
        max_dd = drawdown.max()  # fraction
        
        # Diversification metrics
        active_weights = {k: v for k, v in clean_w.items() if v > 0.01}  # Weights > 1%
        concentration_hhi = sum(w**2 for w in clean_w.values())
        effective_assets = 1 / concentration_hhi if concentration_hhi > 0 else 0
        
        results = {
            "symbols": resolved_symbols,
            "optimization_details": {
                "method": optimization_method,
                "objective": optimization_objective,
                "risk_model": risk_model,
                "data_period": f"{price_df.index[0].strftime('%Y-%m-%d')} to {price_df.index[-1].strftime('%Y-%m-%d')}",
                "observations_used": len(returns),
                "return_methodology": "arithmetic_returns_consistent",
                "risk_free_rate": risk_free_rate,
                "weight_constraints": f"min: {min_weight}, max: {max_weight}"
            },
            
            "portfolio_weights": {k: round(v, 4) for k, v in clean_w.items()},
            "active_positions": active_weights,
            
            "portfolio_performance": {
                "expected_annual_return": f"{portfolio_return:.2%}",
                "annual_volatility": f"{portfolio_volatility:.2%}",
                "sharpe_ratio": round(float(sharpe_ratio), 4),
                "excess_return_annual": f"{(portfolio_return - risk_free_rate):.2%}",
            },
            
            "risk_metrics": {
                "value_at_risk_95_daily_loss_pct": round(float(var_95_daily), 4),
                "conditional_var_95_daily_loss_pct": round(float(cvar_95_daily), 4),
                "maximum_drawdown_pct": round(float(max_dd * 100), 4),
                "portfolio_beta": "N/A"  # Would need benchmark
            },
            
            "diversification_metrics": {
                "concentration_hhi": round(float(concentration_hhi), 4),
                "effective_number_assets": round(float(effective_assets), 2),
                "number_active_positions": len(active_weights),
                "largest_position_pct": round(float(max(clean_w.values()) * 100), 2) if clean_w else 0
            },
            
            "data_quality": data_quality_info
        }
        
        return results
        
    except Exception as e:
        return {"error": f"Portfolio optimization failed: {str(e)}"}


@function_tool
def calculate_garch_volatility_models(
    symbol: str,
    model_type: str = "AUTO",
    days_back: int = 252,
    lookback_days: Optional[int] = None,
    winsorise: bool = False,
    p: Optional[int] = None,
    q: Optional[int] = None,
    o: Optional[int] = None,
    max_p: int = 3, max_q: int = 3, max_o: int = 2,
    auto_select: bool = True,
    return_type: str = "log",
    dist: str = "t",
    mean_model: str = "Constant",  # FIXED: Changed from "Zero" to avoid look-ahead bias
    forecast_horizon: int = 5,
    random_state: Optional[int] = None  # Added for reproducibility
) -> dict | None:
    """
    ADVANCED GARCH VOLATILITY MODELING: Professional volatility forecasting with automatic model selection.
    
    This tool provides comprehensive GARCH family volatility modeling including:
    - Proper log returns calculation and normalization (standard for GARCH modeling)
    - Multiple GARCH variants (GARCH, EGARCH, GJR-GARCH, TGARCH)
    - Automatic parameter optimization and model selection
    - Statistical validation and diagnostic tests
    - Professional volatility forecasting
    - Fixed look-ahead bias and improved statistical practices
    
    IMPORTANT: GARCH models are typically estimated using log returns as they have better
    statistical properties (closer to normal distribution, stationary) required for
    reliable parameter estimation and forecasting.
    
    Args:
        symbol: Stock ticker symbol for analysis
        model_type: GARCH model type ("GARCH", "EGARCH", "GJR-GARCH", "TGARCH", "AUTO")
        days_back: Historical data period (default: 252 trading days)
        lookback_days: Specific lookback period override
        winsorise: Apply winsorization to remove extreme outliers
        p: ARCH lag order (default: None, auto-select if None)
        q: GARCH lag order (default: None, auto-select if None)
        o: Asymmetric lag order for GJR/TGARCH (default: None, auto-select if None)
        max_p/max_q/max_o: Maximum parameters for auto-selection
        auto_select: Enable automatic model selection based on information criteria
        use_log_returns: Use log returns (strongly recommended for GARCH, default: True)
        dist: Error distribution ("normal", "t", "skewt", "AUTO")
        mean_model: Mean model specification ("Constant", "Zero")
        forecast_horizon: Number of periods to forecast (default: 5)
        random_state: Random seed for simulation-based forecasts (optional)
    
    Returns:
        Dictionary with model results, parameters, diagnostics, and volatility forecasts
    """
    # Minimum observations for reliable GARCH estimation
    MIN_OBSERVATIONS = 100
    
    # Helper function for robust convergence checking
    def _did_converge(fit):
        if hasattr(fit, "converged"):
            return bool(fit.converged)
        if hasattr(fit, "convergence_flag"):
            # in arch, 0 usually means success
            return int(fit.convergence_flag) == 0
        return True  # best effort
    
    # Resolve company name to symbol if needed
    resolved_symbol = resolve_symbol_or_name(symbol)
    
    df = get_fmp_price_data(resolved_symbol, "1d", days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch price data for {resolved_symbol}"}

    if lookback_days is not None and lookback_days < len(df):
        df = df.tail(lookback_days)

    # Calculate returns using unified function for consistency
    prices = df['Close']
    demean = mean_model == "Zero"
    # GARCH models: only demean for Zero mean model, otherwise preserve drift
    demean_returns = (mean_model == "Zero")
    returns = _calculate_proper_returns(prices, return_type=return_type, winsorise=winsorise, demean=demean_returns)
    
    # Data quality checks
    if len(returns) < MIN_OBSERVATIONS:
        return {"error": f"Insufficient data for reliable GARCH modeling (minimum {MIN_OBSERVATIONS} observations required, got {len(returns)})"}
    
    if returns.std() == 0:
        return {"error": "Returns series has zero variance - GARCH modeling not applicable"}
    
    # Check for extreme values before winsorization
    if abs(returns.skew()) > 10 or returns.kurtosis() > 100:
        warnings.warn("Extreme skewness or kurtosis detected - consider data preprocessing")
    
    # FIXED: Initialize clip_levels to avoid undefined reference
    clip_levels = None
    original_returns = returns.copy()  # Keep for winsorization tracking
    
    # Smart winsorization: avoid for heavy-tailed distributions
    if winsorise:
        # Less aggressive winsorization for heavy-tailed distributions
        clip_levels = (0.005, 0.995) if dist in ["t", "skewt"] else (0.025, 0.975)
        lower, upper = returns.quantile(clip_levels[0]), returns.quantile(clip_levels[1])
        returns = returns.clip(lower, upper)
    
    # Track winsorization count for reporting
    winsorized_count = int((original_returns != returns).sum()) if winsorise else 0
    
    # Handle mean model specification (FIXED: No look-ahead bias)
    original_returns_for_mean = returns.copy()  # Keep original for diagnostics
    
    if mean_model == "Zero":
        # Leak-free demeaning using expanding window
        expanding_mean = returns.expanding().mean().shift(1)
        returns = (returns - expanding_mean).dropna()
        if len(returns) < MIN_OBSERVATIONS:
            warnings.warn("Insufficient data after leak-free demeaning, switching to Constant mean model")
            returns = original_returns_for_mean
            mean_model = "Constant"

    try:
        results = {}
        models_tested = {}
        
        if auto_select and model_type == "AUTO":
            # Define search grids
            P = [p] if p is not None else list(range(1, max_p + 1))
            Q = [q] if q is not None else list(range(1, max_q + 1))
            O = [o] if o is not None else list(range(1, max_o + 1))
            dists_to_try = [dist] if dist != "AUTO" else ["normal", "t", "skewt"]
            
            best_model = None
            best_aic = np.inf
            best_params = {}
            convergence_failures = 0
            
            # Model variants to test
            model_variants = [
                ("GARCH",     {"vol": "GARCH",  "power": 2.0, "o": 0}),
                ("EGARCH",    {"vol": "EGARCH"}), 
                ("GJR-GARCH", {"vol": "GARCH",  "power": 2.0}),
                ("TGARCH",    {"vol": "GARCH",  "power": 1.0})
            ]
            
            for model_name, model_kwargs in model_variants:
                for dist_val in dists_to_try:
                    for p_val in P:
                        for q_val in Q:
                            try:
                                if model_name in ("GJR-GARCH", "TGARCH"):
                                    for o_val in O:
                                        model = arch_model(
                                            returns, 
                                            mean=mean_model, 
                                            dist=dist_val, 
                                            p=p_val, 
                                            o=o_val, 
                                            q=q_val, 
                                            **model_kwargs
                                        )
                                        fitted = model.fit(
                                            disp="off", 
                                            show_warning=False, 
                                            update_freq=0,
                                            options={'ftol': 1e-9, 'maxiter': 1000}
                                        )
                                        
                                        # FIXED: Use robust convergence checking
                                        if not _did_converge(fitted):
                                            convergence_failures += 1
                                            continue
                                            
                                        # Store model results
                                        model_key = f"{model_name}({p_val},{o_val},{q_val},{dist_val})"
                                        models_tested[model_key] = {
                                            "aic": float(fitted.aic),
                                            "aic_per_sample": float(fitted.aic / len(returns)),
                                            "bic": float(fitted.bic),
                                            "bic_per_sample": float(fitted.bic / len(returns)),
                                            "loglik": float(fitted.loglikelihood),
                                            "loglik_per_sample": float(fitted.loglikelihood / len(returns)),
                                            "converged": bool(_did_converge(fitted))
                                        }
                                        
                                        if fitted.aic < best_aic:
                                            best_aic = fitted.aic
                                            best_model = fitted
                                            best_params = {
                                                "model_type": model_name,
                                                "p": p_val, "q": q_val, "o": o_val, "dist": dist_val
                                            }
                                else:
                                    model = arch_model(
                                        returns, 
                                        mean=mean_model, 
                                        dist=dist_val, 
                                        p=p_val, 
                                        q=q_val, 
                                        **model_kwargs
                                    )
                                    fitted = model.fit(
                                        disp="off", 
                                        show_warning=False, 
                                        update_freq=0,
                                        options={'ftol': 1e-9, 'maxiter': 1000}
                                    )
                                    
                                    # FIXED: Use robust convergence checking
                                    if not _did_converge(fitted):
                                        convergence_failures += 1
                                        continue
                                        
                                    # Store model results
                                    model_key = f"{model_name}({p_val},{q_val},{dist_val})"
                                    models_tested[model_key] = {
                                        "aic": float(fitted.aic),
                                        "aic_per_sample": float(fitted.aic / len(returns)),
                                        "bic": float(fitted.bic),
                                        "bic_per_sample": float(fitted.bic / len(returns)),
                                        "loglik": float(fitted.loglikelihood),
                                        "loglik_per_sample": float(fitted.loglikelihood / len(returns)),
                                        "converged": bool(_did_converge(fitted))
                                    }
                                    
                                    if fitted.aic < best_aic:
                                        best_aic = fitted.aic
                                        best_model = fitted
                                        best_params = {
                                            "model_type": model_name,
                                            "p": p_val, "q": q_val, "o": 0, "dist": dist_val
                                        }
                            except Exception as e:
                                # More specific error handling
                                if "Optimization failed" in str(e) or "singular" in str(e).lower():
                                    convergence_failures += 1
                                continue
            
            if best_model is None:
                error_msg = f"Could not fit any GARCH model successfully. "
                if convergence_failures > 0:
                    error_msg += f"({convergence_failures} convergence failures)"
                return {"error": error_msg}
                
            fitted_model = best_model
            final_model_type = best_params["model_type"]
            
        else:
            # Single model fitting with specified parameters
            try:
                model_kwargs = {}
                if model_type == "EGARCH":
                    model = arch_model(returns, mean=mean_model, vol="EGARCH", p=p or 1, q=q or 1, dist=dist)
                elif model_type == "GJR-GARCH":
                    model = arch_model(returns, mean=mean_model, vol="GARCH", p=p or 1, o=o or 1, q=q or 1, dist=dist, power=2.0)
                elif model_type == "TGARCH":
                    model = arch_model(returns, mean=mean_model, vol="GARCH", p=p or 1, o=o or 1, q=q or 1, dist=dist, power=1.0)
                else:  # Standard GARCH
                    model = arch_model(returns, mean=mean_model, vol="GARCH", p=p or 1, q=q or 1, dist=dist, power=2.0)
                    
                fitted_model = model.fit(
                    disp="off", 
                    show_warning=False, 
                    update_freq=0,
                    options={'ftol': 1e-9, 'maxiter': 1000}
                )
                
                if not _did_converge(fitted_model):
                    return {"error": f"GARCH model failed to converge. Try different parameters or check data quality."}
                
                final_model_type = model_type
                best_params = {"model_type": model_type, "p": p, "q": q, "o": o, "dist": dist}
                
            except Exception as e:
                return {"error": f"GARCH model fitting failed: {str(e)}"}
        
        # Parameter validation and warnings
        params = fitted_model.params
        alpha_sum = sum(v for k, v in params.items() if k.startswith("alpha["))
        beta_sum = sum(v for k, v in params.items() if k.startswith("beta["))
        persistence = None
        
        if final_model_type in ("GARCH", "GJR-GARCH", "TGARCH"):
            persistence = float(alpha_sum + beta_sum)
            if persistence >= 0.99:
                warnings.warn(f"High persistence detected ({persistence:.4f}) - model may be close to non-stationary")
            elif persistence >= 1.0:
                warnings.warn(f"Non-stationary model detected (persistence = {persistence:.4f})")
        
        # Extract current volatility
        current_vol = fitted_model.conditional_volatility.iloc[-1]
        annualized_vol = current_vol * np.sqrt(252) * 100
        
        # Enhanced statistical diagnostics
        try:
            from statsmodels.stats.diagnostic import acorr_ljungbox
            standardized_resid = (fitted_model.resid / fitted_model.conditional_volatility).dropna()
            
            # Normality test
            jb_stat, jb_pvalue = jarque_bera(standardized_resid)
            
            # Serial correlation tests
            lb_resid = acorr_ljungbox(standardized_resid, lags=[10], return_df=True)
            lb_resid_sq = acorr_ljungbox(standardized_resid**2, lags=[10], return_df=True)
            
            # FIXED: Sign bias test with proper array alignment
            res_std = standardized_resid.to_numpy()
            neg = (fitted_model.resid < 0).astype(int).to_numpy()
            sign_bias_corr = float(np.corrcoef(neg[:-1], res_std[1:]**2)[0,1]) if len(res_std) > 1 else None
            
            diagnostics = {
                "jarque_bera_stat": float(jb_stat),
                "jarque_bera_pvalue": float(jb_pvalue),
                "residuals_normal": bool(jb_pvalue > 0.05),
                "mean_squared_error": float(np.mean(fitted_model.resid**2)),
                "ljung_box_resid_Q_10": float(lb_resid["lb_stat"].iloc[0]),
                "ljung_box_resid_p_10": float(lb_resid["lb_pvalue"].iloc[0]),
                "ljung_box_resid_sq_Q_10": float(lb_resid_sq["lb_stat"].iloc[0]),
                "ljung_box_resid_sq_p_10": float(lb_resid_sq["lb_pvalue"].iloc[0]),
                "sign_bias_correlation": sign_bias_corr,
                "residuals_uncorrelated": bool(lb_resid["lb_pvalue"].iloc[0] > 0.05),
                "no_arch_effects": bool(lb_resid_sq["lb_pvalue"].iloc[0] > 0.05)
            }
        except Exception as e:
            diagnostics = {"note": f"Some diagnostic tests unavailable: {str(e)}"}
        
        # FIXED: Enhanced volatility forecasting with normalized distribution names
        try:
            # Normalize distribution names for consistency
            fitted_dist = getattr(getattr(fitted_model, "distribution", None), "name", "normal").lower()
            if fitted_dist in ("students-t", "studentst", "student_t"):
                fitted_dist = "t"
            
            # Determine forecast method based on model type and distribution
            method = "analytic" if (fitted_dist in ("normal", "t") and final_model_type in ("GARCH", "GJR-GARCH", "TGARCH")) else "simulation"
            
            # Set random state for reproducible simulation
            forecast_kwargs = {"horizon": forecast_horizon, "method": method}
            if method == "simulation" and random_state is not None:
                forecast_kwargs["random_state"] = random_state
                
            forecast = fitted_model.forecast(**forecast_kwargs)
            var_h = forecast.variance.iloc[-1].values  # daily variances
            
            vol_daily_pct = np.sqrt(var_h) * 100
            vol_annualized_pct = np.sqrt(var_h) * np.sqrt(252) * 100
            
            forecasts = {
                "forecast_method": method,
                "fitted_distribution": fitted_dist,
                **{f"day_{i+1}_vol_daily_pct": round(float(vol_daily_pct[i]), 4) for i in range(len(vol_daily_pct))},
                **{f"day_{i+1}_vol_annualized_pct": round(float(vol_annualized_pct[i]), 4) for i in range(len(vol_annualized_pct))}
            }
        except Exception as e:
            forecasts = {"note": f"Volatility forecasting failed: {str(e)}"}
        
        # Extract parameter significance
        pvals = fitted_model.pvalues.to_dict()
        asym_terms = {k: float(v) for k, v in params.items() if k.startswith(("gamma", "eta"))}
        
        # Compile results
        results = {
            "symbol": resolved_symbol,
            "model_specifications": {
                "selected_model": final_model_type,
                "parameters": best_params,
                "fitted_distribution": fitted_dist,
                "forecast_method": forecasts.get("forecast_method", "unknown"),
                "data_preprocessing": {
                    "return_type": f"{return_type}_returns",
                    "winsorized": winsorise,
                    "winsorize_levels": clip_levels,
                    "winsorized_count": winsorized_count,
                    "observations_used": len(returns),
                    "mean_model_used": mean_model,
                    "convergence_flag": bool(_did_converge(fitted_model))
                }
            },
            "model_performance": {
                "log_likelihood": round(float(fitted_model.loglikelihood), 4),
                "log_likelihood_per_sample": round(float(fitted_model.loglikelihood / len(returns)), 6),
                "aic": round(float(fitted_model.aic), 4),
                "aic_per_sample": round(float(fitted_model.aic / len(returns)), 6),
                "bic": round(float(fitted_model.bic), 4),
                "bic_per_sample": round(float(fitted_model.bic / len(returns)), 6),
                "current_volatility_daily": round(float(current_vol * 100), 4),
                "current_volatility_annualized": round(float(annualized_vol), 4),
                "persistence_alpha_plus_beta": round(persistence, 6) if persistence is not None else None,
                "asymmetry_terms": asym_terms if asym_terms else None,
                "param_pvalues": {k: round(float(v), 6) for k, v in pvals.items()},
                "significant_params": [k for k, v in pvals.items() if v < 0.05]
            },
            "statistical_diagnostics": diagnostics,
            "volatility_forecasts": forecasts
        }
        
        # Include model comparison if auto-selection was used
        if auto_select and model_type == "AUTO" and models_tested:
            results["model_comparison"] = {
                "models_tested": len(models_tested),
                "convergence_failures": convergence_failures,
                "top_models": dict(sorted(models_tested.items(), 
                                        key=lambda x: x[1]["aic"])[:5])
            }
        
        return results
        
    except Exception as e:
        return {"error": f"GARCH modeling error: {str(e)}"}

# -----------------------------------------------------------------------------
# EXPLORATORY / REGIME / FACTOR TOOLS (UPGRADED)
# -----------------------------------------------------------------------------

@function_tool
def calculate_pca_decomposition(symbols: List[str], timeframe: str = "1d", days_back: int = 252,
                                 lookback_days: Optional[int] = None,
                                 excess_returns: bool = False,
                                 winsorise: bool = False, return_type: str = "simple") -> dict | None:
    price_df = pd.DataFrame()
    for sym in symbols:
        d = get_fmp_price_data(sym, timeframe, days_back, return_format="dataframe")
        if d is not None and not d.empty:
            price_df[sym] = d["Close"]

    if price_df.empty:
        return {"error": "Could not fetch data"}

    if lookback_days is not None:
        price_df = price_df.tail(lookback_days)

    price_df = price_df.dropna(how="all").dropna()
    
    # Calculate returns using proper methodology - PCA for correlation analysis uses simple returns
    returns = pd.DataFrame()
    for col in price_df.columns:
        returns[col] = _calculate_proper_returns(price_df[col], return_type=return_type, winsorise=winsorise, demean=False)
    
    returns = returns.dropna()

    if excess_returns:
        returns = returns.sub(returns.mean(axis=1), axis=0)

    cov_matrix = returns.cov()
    eig_vals, eig_vecs = np.linalg.eig(cov_matrix)
    total_var = float(np.sum(eig_vals))
    explained_variance = {f"PC{i+1}": float(v / total_var) for i, v in enumerate(eig_vals)}

    top_loadings = {}
    for i, vec in enumerate(eig_vecs.T[:3]):  # top 3 PCs
        top_loadings[f"PC{i+1}"] = {sym: float(val) for sym, val in zip(price_df.columns, vec)}

    return {
        "symbols": symbols,
        "explained_variance": explained_variance,
        "top_factor_loadings": top_loadings
    }


@function_tool
def calculate_rolling_beta(symbol: str, benchmark_symbol: str, window: int = 60,
                            timeframe: str = "1d", days_back: int = 252,
                            lookback_days: Optional[int] = None,
                            winsorise: bool = False, return_type: str = "simple") -> dict | None:
    s_df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    b_df = get_fmp_price_data(benchmark_symbol, timeframe, days_back, return_format="dataframe")
    if s_df is None or b_df is None or s_df.empty or b_df.empty:
        return {"error": "Could not fetch data"}

    if lookback_days is not None:
        s_df, b_df = s_df.tail(lookback_days), b_df.tail(lookback_days)

    # Calculate returns using proper methodology - beta calculation uses simple returns for CAPM consistency
    r_s = _calculate_proper_returns(s_df["Close"], return_type=return_type, winsorise=winsorise, demean=False)
    r_b = _calculate_proper_returns(b_df["Close"], return_type=return_type, winsorise=winsorise, demean=False)
    common_index = r_s.index.intersection(r_b.index)
    r_s, r_b = r_s.loc[common_index], r_b.loc[common_index]

    betas = []
    for i in range(window, len(r_s)):
        cov = np.cov(r_s[i-window:i], r_b[i-window:i])[0][1]
        var = np.var(r_b[i-window:i])
        betas.append(cov / var if var != 0 else 0.0)

    return {
        "symbol": symbol,
        "benchmark": benchmark_symbol,
        "rolling_beta_last": float(betas[-1]) if betas else None
    }


@function_tool
def calculate_autocorrelation_analysis(symbol: str, timeframe: str = "1d", days_back: int = 252,
                                        lookback_days: Optional[int] = None,
                                        winsorise: bool = False, return_type: str = "log") -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    # Calculate returns using proper methodology - autocorrelation analysis uses actual returns for proper serial correlation testing
    returns = _calculate_proper_returns(df['Close'], return_type=return_type, winsorise=winsorise, demean=False)

    ac_vals = acf(returns, nlags=5, fft=True)
    return {f"lag_{i}": float(ac_vals[i]) for i in range(1, 6)}


@function_tool
def calculate_cointegration_test(symbol1: str, symbol2: str, timeframe: str = "1d", days_back: int = 252,
                                  lookback_days: Optional[int] = None,
                                  use_returns: bool = False,
                                  winsorise: bool = False, return_type: str = "log") -> dict | None:
    df1 = get_fmp_price_data(symbol1, timeframe, days_back, return_format="dataframe")
    df2 = get_fmp_price_data(symbol2, timeframe, days_back, return_format="dataframe")
    if df1 is None or df2 is None or df1.empty or df2.empty:
        return {"error": "Could not fetch data"}

    if lookback_days is not None:
        df1, df2 = df1.tail(lookback_days), df2.tail(lookback_days)

    series1, series2 = df1["Close"], df2["Close"]
    if use_returns:
        # Calculate returns using proper methodology - cointegration testing uses actual returns for proper relationship analysis
        series1 = _calculate_proper_returns(series1, return_type=return_type, winsorise=winsorise, demean=False)
        series2 = _calculate_proper_returns(series2, return_type=return_type, winsorise=winsorise, demean=False)

    common_index = series1.index.intersection(series2.index)
    series1, series2 = series1.loc[common_index], series2.loc[common_index]

    score, pvalue, _ = coint(series1, series2)
    return {
        "pair": f"{symbol1}-{symbol2}",
        "coint_score": float(score),
        "p_value": float(pvalue),
        "cointegrated": bool(pvalue < 0.05)
    }


@function_tool
def calculate_kalman_spread(symbol1: str, symbol2: str, timeframe: str = "1d", days_back: int = 252,
                            lookback_days: Optional[int] = None,
                            winsorise: bool = False, return_type: str = "simple") -> dict | None:
    if not PYKALMAN_AVAILABLE:
        return {"error": "pykalman library not available"}
    
    df1 = get_fmp_price_data(symbol1, timeframe, days_back, return_format="dataframe")
    df2 = get_fmp_price_data(symbol2, timeframe, days_back, return_format="dataframe")
    if df1 is None or df2 is None or df1.empty or df2.empty:
        return {"error": "Could not fetch data"}

    if lookback_days is not None:
        df1, df2 = df1.tail(lookback_days), df2.tail(lookback_days)

    y, x = df1["Close"].values, df2["Close"].values
    if winsorise:
        lower1, upper1 = np.percentile(y, 1), np.percentile(y, 99)
        lower2, upper2 = np.percentile(x, 1), np.percentile(x, 99)
        y, x = np.clip(y, lower1, upper1), np.clip(x, lower2, upper2)

    delta = 1e-5
    trans_cov = delta / (1 - delta) * np.eye(2)
    obs_mat = np.vstack([x, np.ones(len(x))]).T[:, np.newaxis, :]

    kf = pykalman.KalmanFilter(
        transition_matrices=np.eye(2),
        observation_matrices=obs_mat,
        transition_covariance=trans_cov,
        observation_covariance=1.0,
        initial_state_mean=np.zeros(2),
        initial_state_covariance=np.ones((2, 2))
    )
    state_means, _ = kf.filter(y)
    return {
        "pair": f"{symbol1}-{symbol2}",
        "last_hedge_ratio": float(state_means[:, 0][-1])
    }


@function_tool
def calculate_rolling_volatility(symbol: str, window: int = 30, timeframe: str = "1d",
                                  days_back: int = 252, lookback_days: Optional[int] = None,
                                  winsorise: bool = False, return_type: str = "log") -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    # Calculate returns using proper methodology - rolling volatility uses actual returns for proper estimation
    returns = _calculate_proper_returns(df["Close"], return_type=return_type, winsorise=winsorise, demean=False)

    roll_vol = returns.rolling(window).std().dropna()
    return {
        "symbol": symbol,
        "rolling_volatility_last": float(roll_vol.iloc[-1])
    }


@function_tool
def calculate_drawdown_series(symbol: str, timeframe: str = "1d", days_back: int = 252,
                              lookback_days: Optional[int] = None) -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    prices = df["Close"]
    peak = prices.expanding(min_periods=1).max()
    dd = (prices - peak) / peak
    return {
        "symbol": symbol,
        "max_drawdown": float(dd.min()),
        "last_drawdown": float(dd.iloc[-1])
    }


@function_tool
def calculate_var_cvar_analysis(symbol: str, confidence: float = 0.95,
                                timeframe: str = "1d", days_back: int = 252,
                                lookback_days: Optional[int] = None,
                                winsorise: bool = False, return_type: str = "log") -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    # Calculate returns using proper methodology - VaR/CVaR analysis requires actual returns with mean intact
    returns = _calculate_proper_returns(df["Close"], return_type=return_type, winsorise=winsorise, demean=False)

    var = np.percentile(returns, (1 - confidence) * 100)
    cvar = returns[returns <= var].mean()
    return {
        "symbol": symbol,
        "historical_VaR": float(var),
        "historical_CVaR": float(cvar)
    }


@function_tool
def calculate_markov_regime_detection(symbol: str, timeframe: str = "1d", days_back: int = 252,
                                      lookback_days: Optional[int] = None, winsorise: bool = False, return_type: str = "log") -> dict | None:
    if not HMMLEARN_AVAILABLE:
        return {"error": "hmmlearn library not available"}
        
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    # Calculate returns using proper methodology - regime detection uses actual returns for proper regime identification
    returns = _calculate_proper_returns(df["Close"], return_type=return_type, winsorise=winsorise, demean=False).values.reshape(-1, 1)
    model = GaussianHMM(n_components=2, covariance_type="diag", n_iter=100)
    model.fit(returns)
    state = int(model.predict(returns)[-1])
    return {
        "symbol": symbol,
        "current_regime_state": state
    }


@function_tool
def calculate_factor_exposure_ols(symbol: str, factor_symbols: List[str],
                                  timeframe: str = "1d", days_back: int = 252,
                                  lookback_days: Optional[int] = None,
                                  excess_returns: bool = False,
                                  risk_free_rate: float = 0.0,
                                  winsorise: bool = False, return_type: str = "simple") -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    # Calculate returns using proper methodology - factor exposure analysis uses simple returns for regression
    y = _calculate_proper_returns(df["Close"], return_type=return_type, winsorise=winsorise, demean=False)
    if excess_returns:
        y = y - risk_free_rate / 252.0

    X = pd.DataFrame()
    for fac in factor_symbols:
        fdf = get_fmp_price_data(fac, timeframe, days_back, return_format="dataframe")
        if fdf is not None and not fdf.empty:
            X[fac] = _calculate_proper_returns(fdf["Close"], return_type=return_type, winsorise=winsorise, demean=False)
    X = X.dropna()
    y = y.loc[X.index]

    X_const = sm.add_constant(X.values)
    model = sm.OLS(y.values, X_const).fit()

    coeffs = {"Intercept": float(model.params[0])}
    for i, fac in enumerate(X.columns):
        coeffs[fac] = float(model.params[i + 1])

    return {
        "symbol": symbol,
        "factors": factor_symbols,
        "ols_coefficients": coeffs
    }


@function_tool
def calculate_factor_exposure_pca(symbol: str, factor_symbols: List[str],
                                  timeframe: str = "1d", days_back: int = 252,
                                  lookback_days: Optional[int] = None,
                                  excess_returns: bool = False,
                                  winsorise: bool = False, return_type: str = "simple") -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    # Calculate returns using proper methodology - factor exposure PCA uses simple returns for correlation analysis
    data = {symbol: _calculate_proper_returns(df["Close"], return_type=return_type, winsorise=winsorise, demean=False)}
    for fac in factor_symbols:
        fdf = get_fmp_price_data(fac, timeframe, days_back, return_format="dataframe")
        if fdf is not None and not fdf.empty:
            data[fac] = _calculate_proper_returns(fdf["Close"], return_type=return_type, winsorise=winsorise, demean=False)

    df_returns = pd.DataFrame(data).dropna()
    if excess_returns:
        df_returns = df_returns.sub(df_returns.mean(axis=1), axis=0)

    cov_matrix = df_returns.cov()
    eig_vals, _ = np.linalg.eig(cov_matrix)
    total_var = float(np.sum(eig_vals))
    explained_variance = {f"PC{i+1}": float(v / total_var) for i, v in enumerate(eig_vals)}

    return {
        "symbol_and_factors": [symbol] + factor_symbols,
        "explained_variance": explained_variance
    }

@function_tool
def calculate_options_metrics(symbol: str, strike_price: float, option_type: str = "call", 
							  days_to_expiry: int = 30, risk_free_rate: float = 0.05, return_type: str = "log") -> dict | None:
	"""
	OPTIONS ANALYSIS: Basic options pricing and Greeks calculation using Black-Scholes model.
	
	This tool provides options analysis including:
	- Black-Scholes theoretical option pricing
	- Options Greeks (Delta, Gamma, Theta, Vega, Rho)
	- Implied volatility analysis
	- Time decay and sensitivity analysis
	- Options strategy evaluation support
	
	Use this tool when users ask about:
	- Options pricing and valuation
	- Options Greeks and risk sensitivities
	- Options strategy analysis
	- Implied volatility calculations
	- Options trading decision support
	
	Args:
		symbol: Stock ticker symbol (e.g., 'AAPL', 'SPY', 'QQQ')
		strike_price: Option strike price
		option_type: 'call' or 'put' option type
		days_to_expiry: Days until option expiration (default: 30)
		risk_free_rate: Risk-free interest rate as decimal (default: 0.05)
	
	Returns:
		Dictionary containing option price, Greeks, and analysis metrics
	"""
	try:
		# Resolve company name to symbol if needed
		resolved_symbol = resolve_symbol_or_name(symbol)
		
		# Get current price and historical volatility using proper methodology
		df = get_fmp_price_data(resolved_symbol, "1d", 252, return_format="dataframe")
		if df is None or df.empty:
			return {"error": f"Could not fetch price data for {resolved_symbol}"}
		
		current_price = df['Close'].iloc[-1]
		
		# Use proper log returns for volatility estimation (critical for options pricing)
		prices = df['Close']
		returns = _calculate_proper_returns(prices, return_type=return_type, 
		                                   winsorise=True, demean=False)
		
		if len(returns) < 30:
			return {"error": "Insufficient historical data for reliable volatility estimation"}
		
		# Calculate implied volatility using multiple methods for robustness
		historical_vol = returns.std() * np.sqrt(252)  # Annualized log return volatility
		
		# EWMA volatility for more recent emphasis
		lambda_decay = 0.94
		ewma_var = returns.iloc[0]**2
		for ret in returns.iloc[1:]:
			ewma_var = lambda_decay * ewma_var + (1 - lambda_decay) * ret**2
		ewma_vol = np.sqrt(ewma_var) * np.sqrt(252)
		
		# Use EWMA volatility as it's more responsive to recent market conditions
		volatility = ewma_vol
		
		# Black-Scholes calculation
		S = current_price  # Current stock price
		K = strike_price   # Strike price
		T = days_to_expiry / 365.0  # Time to expiry in years
		r = risk_free_rate  # Risk-free rate
		sigma = volatility  # Volatility
		
		if T <= 0:
			return {"error": "Option has already expired"}
		
		# Black-Scholes formulas
		d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
		d2 = d1 - sigma * sqrt(T)
		
		if option_type.lower() == "call":
			price = S * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
			delta = norm.cdf(d1)
			theta = -(S * norm.pdf(d1) * sigma) / (2 * sqrt(T)) - r * K * exp(-r * T) * norm.cdf(d2)
		else:  # put
			price = K * exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
			delta = -norm.cdf(-d1)
			theta = -(S * norm.pdf(d1) * sigma) / (2 * sqrt(T)) + r * K * exp(-r * T) * norm.cdf(-d2)
		
		# Greeks (common for both call and put)
		gamma = norm.pdf(d1) / (S * sigma * sqrt(T))
		vega = S * norm.pdf(d1) * sqrt(T) / 100  # Per 1% change in volatility
		rho = K * T * exp(-r * T) * (norm.cdf(d2) if option_type.lower() == "call" else norm.cdf(-d2)) / 100
		
		# Time decay per day
		theta_per_day = theta / 365
		
		results = {
			"symbol": resolved_symbol,
			"option_details": {
				"type": option_type.lower(),
				"strike_price": strike_price,
				"current_stock_price": round(current_price, 2),
				"days_to_expiry": days_to_expiry,
				"time_to_expiry_years": round(T, 4),
				"risk_free_rate": risk_free_rate,
				"implied_volatility_ewma": round(volatility * 100, 2),
				"historical_volatility": round(historical_vol * 100, 2)
			},
			
			"volatility_methodology": {
				"primary_method": "EWMA (Exponentially Weighted Moving Average)",
				"historical_data_points": len(returns),
				"return_type": "log_returns",
				"winsorization_applied": True,
				"lambda_decay_factor": lambda_decay
			},
			
			"option_pricing": {
				"theoretical_price": round(price, 2),
				"intrinsic_value": round(max(0, (current_price - strike_price) if option_type.lower() == "call" else (strike_price - current_price)), 2),
				"time_value": round(price - max(0, (current_price - strike_price) if option_type.lower() == "call" else (strike_price - current_price)), 2),
				"moneyness": "ITM" if ((option_type.lower() == "call" and current_price > strike_price) or 
									 (option_type.lower() == "put" and current_price < strike_price)) else "OTM"
			},
			
			"greeks": {
				"delta": round(delta, 4),
				"gamma": round(gamma, 4),
				"theta": round(theta, 4),
				"theta_per_day": round(theta_per_day, 4),
				"vega": round(vega, 4),
				"rho": round(rho, 4)
			},
			
			"risk_analysis": {
				"break_even": round(strike_price + price if option_type.lower() == "call" else strike_price - price, 2),
				"max_loss": round(price, 2),  # For long positions
				"max_gain": "Unlimited" if option_type.lower() == "call" else round(strike_price - price, 2),
				"probability_itm": round(norm.cdf(d2) * 100, 2) if option_type.lower() == "call" else round(norm.cdf(-d2) * 100, 2)
			}
		}
		
		return results
		
	except Exception as e:
		return {"error": str(e)}
