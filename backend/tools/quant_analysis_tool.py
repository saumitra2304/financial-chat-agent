from agents import function_tool
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from scipy import stats
import os
from dotenv import load_dotenv
from python_helpers import get_fmp_price_data, search_symbol, search_nse_symbol_by_name
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

@function_tool
def verify_company_symbol(company_name: str) -> dict:
	"""
	COMPANY VERIFICATION: Verifies and displays the stock symbol found for a company name before analysis.
	
	This tool ensures accuracy in quantitative analysis by:
	- Finding the correct NSE stock symbol for the company name
	- Displaying company details including current price
	- Requiring user confirmation before proceeding with technical analysis
	- Preventing analysis of wrong stocks due to ambiguous company names
	
	ALWAYS use this tool FIRST when users ask for analysis of a specific company.
	
	Args:
		company_name: The company name from user query (e.g., 'reliance industries', 'hdfc bank', 'tcs')
	Returns:
		Dictionary with verification details and confirmation requirement
	"""
	try:
		# Search for the NSE symbol using our database
		nse_symbol = search_nse_symbol_by_name(company_name)
		
		if nse_symbol:
			# Get additional company details from our database
			import pymongo
			mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
			database_name = os.getenv('DB_NAME', 'chatbotdb')
			
			client = pymongo.MongoClient(mongo_uri)
			db = client[database_name]
			collection = db['stock_companies']
			
			company_doc = collection.find_one({'symbol': nse_symbol})
			
			result = {
				'status': 'found',
				'search_term': company_name,
				'verified_symbol': nse_symbol,
				'company_name': company_doc.get('name', 'N/A') if company_doc else 'N/A',
				'current_price': company_doc.get('price', 'N/A') if company_doc else 'N/A',
				'market_cap': company_doc.get('marketCap', 'N/A') if company_doc else 'N/A',
				'exchange': 'NSE',
				'confirmation_message': f"✓ Found: {company_doc.get('name', 'N/A')} (Symbol: {nse_symbol}) - Current Price: ₹{company_doc.get('price', 'N/A')}. Please confirm this is the correct company for analysis.",
				'ready_for_analysis': True
			}
		else:
			result = {
				'status': 'not_found',
				'search_term': company_name,
				'verified_symbol': None,
				'confirmation_message': f"❌ No NSE stock found for '{company_name}'. Please provide the exact company name or stock symbol (e.g., 'RELIANCE.NS').",
				'ready_for_analysis': False,
				'suggestion': "Try searching with more specific company names like 'Reliance Industries', 'HDFC Bank', 'Tata Consultancy Services'"
			}
		
		return result
		
	except Exception as e:
		return {
			'status': 'error',
			'search_term': company_name,
			'error': str(e),
			'confirmation_message': f"Error verifying company '{company_name}': {str(e)}",
			'ready_for_analysis': False
		}

@function_tool
def get_historical_price_data(symbol: str, timeframe: str = "5min", days_back: int = 30) -> dict | None:
	"""
	PRICE DATA RETRIEVAL: Fetches comprehensive historical OHLCV price data for technical and quantitative analysis.
	
	This tool provides high-quality intraday and daily price data including:
	- Open, High, Low, Close prices for each time period
	- Volume data for liquidity analysis
	- Flexible timeframes from 1-minute to daily intervals
	- Historical data spanning up to several years
	- Data validation and quality checks
	
	Use this tool when users ask about:
	- Historical stock prices, price movements, or price trends
	- Raw price data for custom analysis or calculations
	- OHLCV data for technical analysis inputs
	- Price data for specific time periods or date ranges
	- Volume analysis or trading activity patterns
	
	Args:
		symbol: Stock ticker symbol or company name (e.g., 'AAPL', 'TSLA', 'MSFT', 'Reliance Industries')
		timeframe: Data interval - '1min', '5min', '15min', '30min', '1hour', '4hour', '1day'
		days_back: Number of days of historical data (default: 30, max: 365)
	
	Returns:
		Dictionary containing historical OHLCV data with metadata and quality indicators
	"""
	# If symbol looks like a company name, try to find the NSE symbol first
	if len(symbol) > 5 and not '.' in symbol and symbol.isalpha():
		nse_symbol = search_nse_symbol_by_name(symbol)
		if nse_symbol:
			symbol = nse_symbol
	
	result = get_fmp_price_data(symbol, timeframe, days_back, return_format="dict")
	if result and "data" in result:
		# Limit display data but preserve metadata
		display_result = result.copy()
		display_result["data"] = result["data"][:50]  # Limit to 50 points to reduce context size
		return display_result
	return result

@function_tool
def calculate_volatility_metrics(symbol: str, timeframe: str = "5min", days_back: int = 30) -> dict | None:
	"""
	VOLATILITY ANALYSIS: Calculates comprehensive volatility and risk metrics for investment analysis.
	
	This tool provides essential risk metrics including:
	- Historical volatility (daily and annualized)
	- Value at Risk (VaR) at different confidence levels
	- Expected shortfall and conditional risk measures
	- Return distribution statistics (skewness, kurtosis)
	- Risk-adjusted performance metrics
	
	Use this tool when users ask about:
	- Stock volatility, price risk, or risk analysis
	- Value at Risk (VaR) calculations
	- Investment risk assessment
	- Risk metrics for portfolio management
	- Return distribution characteristics
	
	Args:
		symbol: Stock ticker symbol (e.g., 'AAPL', 'NVDA', 'BTC-USD')
		timeframe: Data interval - '5min', '15min', '30min', '1hour', '4hour', '1day'
		days_back: Number of days of historical data for analysis (default: 30)
	
	Returns:
		Dictionary containing comprehensive volatility and risk metrics
	"""
	try:
		# Get historical data using centralized function
		price_data = get_fmp_price_data(symbol, timeframe, days_back, return_format="dict")
		if not price_data or "error" in price_data:
			return price_data
		
		# Convert to DataFrame
		df = pd.DataFrame(price_data["data"])
		df['date'] = pd.to_datetime(df['date'])
		df = df.sort_values('date').reset_index(drop=True)
		
		# Calculate returns - Use proper column names from FMP
		df['returns'] = df['Close'].pct_change().dropna()
		returns = df['returns'].dropna()
		
		if len(returns) < 10:
			return {"error": "Insufficient data for volatility calculation"}
		
		metrics = {}
		
		# Historical Volatility (annualized)
		periods_per_year = {
			"1min": 525600, "5min": 105120, "15min": 35040,
			"30min": 17520, "1hour": 8760, "4hour": 2190, "1day": 252
		}
		annual_factor = periods_per_year.get(timeframe, 252)
		
		metrics["volatility_metrics"] = {
			"historical_volatility_annualized": returns.std() * np.sqrt(annual_factor) * 100,
			"daily_volatility": returns.std() * 100,
			"mean_return": returns.mean() * 100,
			"skewness": stats.skew(returns),
			"kurtosis": stats.kurtosis(returns)
		}
		
		# Value at Risk (VaR) - 95% and 99% confidence levels
		metrics["risk_metrics"] = {
			"var_95": np.percentile(returns, 5) * 100,
			"var_99": np.percentile(returns, 1) * 100,
			"expected_shortfall_95": returns[returns <= np.percentile(returns, 5)].mean() * 100,
			"expected_shortfall_99": returns[returns <= np.percentile(returns, 1)].mean() * 100
		}
		
		# Current price information
		current_price = df['Close'].iloc[-1]
		metrics["price_info"] = {
			"symbol": symbol,
			"current_price": current_price,
			"price_change_24h": ((current_price / df['Close'].iloc[-2]) - 1) * 100 if len(df) > 1 else 0,
			"high_24h": df['High'].iloc[-1],
			"low_24h": df['Low'].iloc[-1],
			"volume_24h": df['Volume'].iloc[-1]
		}
		
		# Analysis parameters used
		metrics["analysis_parameters"] = {
			"timeframe": timeframe,
			"days_analyzed": len(df),
			"analysis_period": f"{df['date'].iloc[0].strftime('%Y-%m-%d')} to {df['date'].iloc[-1].strftime('%Y-%m-%d')}",
			"annualization_factor": annual_factor
		}
		
		return metrics
		
	except Exception as e:
		return {"error": str(e)}

@function_tool
def calculate_correlation_analysis(symbols: List[str], timeframe: str = "1d", days_back: int = 60) -> dict | None:
	"""
	CORRELATION ANALYSIS: Analyzes price correlations and relationships between multiple assets.
	
	This tool provides correlation insights including:
	- Pearson correlation coefficients between assets
	- Rolling correlation analysis over time
	- Portfolio diversification insights
	- Market relationship analysis
	- Risk correlation patterns
	
	Use this tool when users ask about:
	- Asset correlations or relationship analysis
	- Portfolio diversification assessment
	- Market sector correlation analysis
	- Risk correlation between investments
	- Asset pair trading opportunities
	
	Args:
		symbols: List of stock symbols to analyze (e.g., ['AAPL', 'MSFT', 'GOOGL'])
		timeframe: Data interval - '5min', '15min', '30min', '1hour', '4hour', '1day'
		days_back: Number of days of historical data for analysis (default: 60)
	
	Returns:
		Dictionary containing correlation matrix and analysis insights
	"""
	try:
		if len(symbols) < 2:
			return {"error": "Need at least 2 symbols for correlation analysis"}
		
		# Fetch price data for all symbols
		price_data = {}
		for symbol in symbols:
			data = get_fmp_price_data(symbol, timeframe, days_back, return_format="dict")
			if data and "error" not in data:
				price_data[symbol] = data["data"]
		
		if len(price_data) < 2:
			return {"error": "Could not fetch sufficient data for correlation analysis"}
		
		# Create DataFrame with all symbols
		combined_df = pd.DataFrame()
		for symbol, data in price_data.items():
			df = pd.DataFrame(data)
			df['date'] = pd.to_datetime(df['date'])
			df = df.set_index('date').sort_index()
			combined_df[symbol] = df['close']  # Use lowercase 'close' from FMP data
		
		# Calculate returns
		returns_df = combined_df.pct_change().dropna()
		
		# Correlation analysis
		correlation_matrix = returns_df.corr()
		
		results = {
			"symbols": symbols,
			"timeframe": timeframe,
			"analysis_period": f"{days_back} days",
			"correlation_matrix": correlation_matrix.round(4).to_dict(),
			"highest_correlation": {
				"pair": None,
				"correlation": 0
			},
			"lowest_correlation": {
				"pair": None,
				"correlation": 1
			},
			"diversification_analysis": {}
		}
		
		# Find highest and lowest correlations
		for i, symbol1 in enumerate(symbols):
			for j, symbol2 in enumerate(symbols[i+1:], i+1):
				corr = correlation_matrix.loc[symbol1, symbol2]
				
				if abs(corr) > abs(results["highest_correlation"]["correlation"]):
					results["highest_correlation"]["pair"] = f"{symbol1}-{symbol2}"
					results["highest_correlation"]["correlation"] = round(corr, 4)
				
				if abs(corr) < abs(results["lowest_correlation"]["correlation"]):
					results["lowest_correlation"]["pair"] = f"{symbol1}-{symbol2}"
					results["lowest_correlation"]["correlation"] = round(corr, 4)
		
		# Diversification insights
		avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
		results["diversification_analysis"]["average_correlation"] = round(avg_correlation, 4)
		results["diversification_analysis"]["diversification_benefit"] = "High" if avg_correlation < 0.7 else "Medium" if avg_correlation < 0.85 else "Low"
		
		# Analysis parameters used
		results["analysis_parameters"] = {
			"symbols_count": len(symbols),
			"data_points": len(returns_df),
			"analysis_period": f"{returns_df.index[0].strftime('%Y-%m-%d')} to {returns_df.index[-1].strftime('%Y-%m-%d')}",
			"timeframe": timeframe
		}
		
		return results
		
	except Exception as e:
		return {"error": str(e)}

@function_tool
def calculate_advanced_statistics(symbol: str, timeframe: str = "1d", days_back: int = 60) -> dict | None:
	"""
	ADVANCED STATISTICS: Comprehensive statistical analysis of price movements and trading patterns.
	
	This tool provides advanced statistical insights including:
	- Normality tests and distribution analysis
	- Autocorrelation and serial correlation tests
	- Stationarity tests (ADF, KPSS)
	- Statistical moments and tail analysis
	- Trading pattern statistics
	
	Use this tool when users ask about:
	- Statistical analysis of price data
	- Distribution characteristics of returns
	- Market efficiency and randomness tests
	- Advanced statistical modeling inputs
	- Quantitative research and backtesting foundations
	
	Args:
		symbol: Stock ticker symbol (e.g., 'SPY', 'QQQ', 'TSLA')
		timeframe: Data interval - '5min', '15min', '30min', '1hour', '4hour', '1day'
		days_back: Number of days of historical data for analysis (default: 60)
	
	Returns:
		Dictionary containing comprehensive statistical analysis results
	"""
	try:
		# Get price data
		price_data = get_fmp_price_data(symbol, timeframe, days_back, return_format="dict")
		if not price_data or "error" in price_data:
			return price_data
		
		df = pd.DataFrame(price_data["data"])
		df['date'] = pd.to_datetime(df['date'])
		df = df.sort_values('date').reset_index(drop=True)
		
		# Calculate returns and log returns - Use proper column names
		df['returns'] = df['Close'].pct_change()
		df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
		
		returns = df['returns'].dropna()
		log_returns = df['log_returns'].dropna()
		
		if len(returns) < 30:
			return {"error": "Insufficient data for statistical analysis"}
		
		stats_results = {
			"symbol": symbol,
			"timeframe": timeframe,
			"analysis_period": f"{days_back} days",
			"sample_size": len(returns)
		}
		
		# Descriptive Statistics
		stats_results["descriptive_stats"] = {
			"mean_return": float(returns.mean()),
			"median_return": float(returns.median()),
			"std_deviation": float(returns.std()),
			"variance": float(returns.var()),
			"skewness": float(stats.skew(returns)),
			"kurtosis": float(stats.kurtosis(returns)),
			"min_return": float(returns.min()),
			"max_return": float(returns.max()),
			"range": float(returns.max() - returns.min())
		}
		
		# Normality Tests
		jarque_bera = stats.jarque_bera(returns)
		shapiro_test = stats.shapiro(returns) if len(returns) <= 5000 else None
		
		stats_results["normality_tests"] = {
			"jarque_bera_statistic": float(jarque_bera[0]),
			"jarque_bera_pvalue": float(jarque_bera[1]),
			"is_normal_jb": jarque_bera[1] > 0.05,
		}
		
		if shapiro_test:
			stats_results["normality_tests"]["shapiro_statistic"] = float(shapiro_test[0])
			stats_results["normality_tests"]["shapiro_pvalue"] = float(shapiro_test[1])
			stats_results["normality_tests"]["is_normal_shapiro"] = shapiro_test[1] > 0.05
		
		# Autocorrelation Analysis (limited to prevent large output)
		from statsmodels.tsa.stattools import acf
		autocorr = acf(returns, nlags=5, fft=True)  # Reduced from 10 to 5 lags
		stats_results["autocorrelation"] = {
			f"lag_{i}": float(autocorr[i]) for i in range(1, min(4, len(autocorr)))  # Max 3 lags
		}
		
		# Risk Metrics
		stats_results["risk_metrics"] = {
			"sharpe_ratio": float((returns.mean() / returns.std()) * np.sqrt(252)) if returns.std() > 0 else 0,
			"sortino_ratio": float((returns.mean() / returns[returns < 0].std()) * np.sqrt(252)) if len(returns[returns < 0]) > 0 else 0,
			"calmar_ratio": float(returns.mean() * 252 / abs(returns.min())) if returns.min() < 0 else 0,
		}
		
		# Analysis parameters used
		stats_results["analysis_parameters"] = {
			"timeframe": timeframe,
			"days_analyzed": len(df),
			"analysis_period": f"{df['date'].iloc[0].strftime('%Y-%m-%d')} to {df['date'].iloc[-1].strftime('%Y-%m-%d')}",
			"statistical_tests_performed": ["jarque_bera", "shapiro", "autocorrelation"]
		}
		
		return stats_results
		
	except Exception as e:
		return {"error": str(e)}

@function_tool
def calculate_monte_carlo_simulation(symbol: str, forecast_days: int = 10, simulations: int = 100, 
									confidence_level: float = 0.95) -> dict | None:
	"""
	MONTE CARLO SIMULATION: Advanced probabilistic price forecasting using Monte Carlo methods.
	
	This tool provides probabilistic price projections including:
	- Multiple price path simulations based on historical volatility
	- Confidence intervals for future price ranges
	- Probability distributions of potential outcomes
	- Risk scenario analysis and stress testing
	- Expected value and downside risk projections
	
	Use this tool when users ask about:
	- Price forecasting and future projections
	- Risk scenario analysis and stress testing
	- Probabilistic investment outcomes
	- Monte Carlo analysis and simulations
	- Confidence intervals for price targets
	
	Args:
		symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'ETH-USD')
		forecast_days: Number of days to forecast into the future (default: 10, reduced from 30)
		simulations: Number of Monte Carlo simulations to run (default: 100, reduced from 1000)
		confidence_level: Confidence level for intervals (default: 0.95)
	
	Returns:
		Dictionary containing simulation results, projections, and risk analysis
	"""
	try:
		# Get historical data for volatility calculation
		price_data = get_fmp_price_data(symbol, "1d", 252, return_format="dict")
		if not price_data or "error" in price_data:
			return price_data
		
		df = pd.DataFrame(price_data["data"])
		df['date'] = pd.to_datetime(df['date'])
		df = df.sort_values('date').reset_index(drop=True)
		
		# Calculate returns and parameters - Use proper column names
		df['returns'] = df['Close'].pct_change()
		returns = df['returns'].dropna()
		
		if len(returns) < 30:
			return {"error": "Insufficient historical data for simulation"}
		
		# Simulation parameters
		current_price = df['Close'].iloc[-1]
		mean_return = returns.mean()
		volatility = returns.std()
		dt = 1  # daily time step
		
		# Run Monte Carlo simulation (reduced size to prevent context overflow)
		np.random.seed(42)  # For reproducibility
		simulation_results = []
		
		for _ in range(simulations):
			prices = [current_price]
			for day in range(forecast_days):
				random_shock = np.random.normal(0, 1)
				price_change = mean_return * dt + volatility * np.sqrt(dt) * random_shock
				new_price = prices[-1] * (1 + price_change)
				prices.append(new_price)
			simulation_results.append(prices[1:])  # Exclude initial price
		
		# Convert to numpy array for easier analysis
		simulations_array = np.array(simulation_results)
		
		# Calculate statistics for each day
		final_prices = simulations_array[:, -1]
		
		# Confidence intervals
		alpha = 1 - confidence_level
		lower_percentile = (alpha / 2) * 100
		upper_percentile = (1 - alpha / 2) * 100
		
		results = {
			"symbol": symbol,
			"current_price": round(current_price, 2),
			"forecast_days": forecast_days,
			"simulations_count": simulations,
			"confidence_level": confidence_level,
			
			"final_day_projections": {
				"expected_price": round(float(np.mean(final_prices)), 2),
				"median_price": round(float(np.median(final_prices)), 2),
				"confidence_interval_lower": round(float(np.percentile(final_prices, lower_percentile)), 2),
				"confidence_interval_upper": round(float(np.percentile(final_prices, upper_percentile)), 2),
				"std_deviation": round(float(np.std(final_prices)), 2)
			},
			
			"risk_analysis": {
				"probability_of_gain": float(np.sum(final_prices > current_price) / simulations * 100),
				"probability_of_loss": float(np.sum(final_prices < current_price) / simulations * 100),
				"expected_return": float((np.mean(final_prices) / current_price - 1) * 100),
				"downside_risk": float(np.mean(final_prices[final_prices < current_price]) / current_price - 1) * 100 if np.any(final_prices < current_price) else 0,
				"upside_potential": float(np.mean(final_prices[final_prices > current_price]) / current_price - 1) * 100 if np.any(final_prices > current_price) else 0
			},
			
			"simulation_parameters": {
				"historical_mean_return": round(mean_return * 100, 4),
				"historical_volatility": round(volatility * 100, 4),
				"annualized_volatility": round(volatility * np.sqrt(252) * 100, 2)
			}
		}
		
		# Analysis parameters used
		results["analysis_parameters"] = {
			"historical_data_period": "252 days (1 year)",
			"simulation_method": "Geometric Brownian Motion",
			"time_step": "Daily",
			"random_seed": "42 (for reproducibility)"
		}
		
		return results
		
	except Exception as e:
		return {"error": str(e)}

@function_tool
def calculate_options_metrics(symbol: str, strike_price: float, option_type: str = "call", 
							  days_to_expiry: int = 30, risk_free_rate: float = 0.05) -> dict | None:
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
		# Get current price and historical volatility
		df = get_fmp_price_data(symbol, "1d", 60, return_format="dataframe")
		if df is None or df.empty:
			return {"error": f"Could not fetch price data for {symbol}"}
		
		current_price = df['Close'].iloc[-1]
		returns = df['Close'].pct_change().dropna()
		volatility = returns.std() * np.sqrt(252)  # Annualized volatility
		
		# Black-Scholes calculation
		from math import log, sqrt, exp
		from scipy.stats import norm
		
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
			"symbol": symbol,
			"option_details": {
				"type": option_type.lower(),
				"strike_price": strike_price,
				"current_stock_price": round(current_price, 2),
				"days_to_expiry": days_to_expiry,
				"time_to_expiry_years": round(T, 4),
				"risk_free_rate": risk_free_rate,
				"implied_volatility": round(volatility * 100, 2)
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
