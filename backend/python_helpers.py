import requests
from rapidfuzz import fuzz
from concurrent.futures import ThreadPoolExecutor
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

def search_symbol(query: str) -> str | None:
	"""
	Search for stock symbol using Financial Modeling Prep API.
	Args:
		query: The company name or partial symbol to search for.
	Returns:
		The best matching symbol if found, else None.
	"""
	fmp_api_key = os.getenv("FMP_API_KEY")
	if not fmp_api_key:
		print("FMP API key not configured")
		return None
		
	try:
		url = f"https://financialmodelingprep.com/api/v3/search"
		params = {
			'query': query,
			'limit': 10,
			'apikey': fmp_api_key
		}
		
		response = requests.get(url, params=params, timeout=15)
		response.raise_for_status()
		data = response.json()
		
		if not data:
			return None
			
		# Return the first (best) match symbol
		return data[0].get('symbol')
		
	except Exception as e:
		print(f"Error searching symbol: {e}")
		return None

def get_fmp_price_data(symbol: str, timeframe: str = "1d", days_back: int = 252, return_format: str = "dict") -> dict | pd.DataFrame | None:
	"""
	Centralized function to get price data from Financial Modeling Prep API.
	
	Args:
		symbol: Stock symbol (will be searched if not exact)
		timeframe: Data interval - '1min', '5min', '15min', '30min', '1hour', '4hour', '1day'
		days_back: Number of days of historical data
		return_format: 'dict' for raw data, 'dataframe' for pandas DataFrame
		
	Returns:
		Price data in requested format or None if error
	"""
	fmp_api_key = os.getenv("FMP_API_KEY")
	fmp_base_url = os.getenv("FMP_BASE_URL", "https://financialmodelingprep.com")
	
	if not fmp_api_key:
		return {"error": "FMP API key not configured"} if return_format == "dict" else None
	
	try:
		# Search for symbol if needed
		if not symbol or len(symbol) < 2:
			return {"error": "Invalid symbol"} if return_format == "dict" else None
			
		# Try to use symbol as-is first, then search if needed
		search_result = search_symbol(symbol)
		if search_result:
			symbol = search_result
		
		# Get historical data based on timeframe
		if timeframe == "1d" or timeframe == "1day":
			# Use daily historical prices
			url = f"{fmp_base_url}/api/v3/historical-price-full/{symbol}"
			params = {'apikey': fmp_api_key}
		else:
			# Use intraday data
			from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
			to_date = datetime.now().strftime('%Y-%m-%d')
			
			url = f"{fmp_base_url}/api/v3/historical-chart/{timeframe}/{symbol}"
			params = {
				'apikey': fmp_api_key,
				'from': from_date,
				'to': to_date
			}
		
		response = requests.get(url, params=params, timeout=15)
		response.raise_for_status()
		data = response.json()
		
		if not data:
			return {"error": f"No data found for symbol {symbol}"} if return_format == "dict" else None
		
		# Extract historical data
		if timeframe == "1d" or timeframe == "1day":
			historical_data = data.get('historical', [])[:days_back]
		else:
			historical_data = data
		
		if not historical_data:
			return {"error": f"No historical data for {symbol}"} if return_format == "dict" else None
		
		if return_format == "dataframe":
			# Convert to DataFrame for pandas_ta
			df = pd.DataFrame(historical_data)
			if 'date' in df.columns:
				df['date'] = pd.to_datetime(df['date'])
				df = df.set_index('date').sort_index()
			
			# Standardize column names
			if 'open' in df.columns:
				df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
			
			return df
		else:
			# Return as dict
			return {
				"symbol": symbol,
				"timeframe": timeframe,
				"days_back": days_back,
				"data_points": len(historical_data),
				"data": historical_data,
				"source": "Financial Modeling Prep"
			}
		
	except Exception as e:
		print(f"Error fetching FMP price data: {e}")
		return {"error": str(e)} if return_format == "dict" else None

def get_co_code(company_name: str, api_key: str) -> float | None:
	"""
	Asynchronously calls the CompanyMaster API and returns the co_code for the closest matching company name using rapidfuzz.
	Args:
		company_name: The name of the company to search for.
		api_key: The Bearer token for authorization.
	Returns:
		The co_code (float) if found, else None.
	"""
	url = "https://insbaapis.cmots.com/api/CompanyMaster"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		data = response.json().get("data", [])
		names = [item["companyname"] for item in data if "companyname" in item]
		# Parallel fuzzy matching using ThreadPoolExecutor
		def score(name):
			return fuzz.WRatio(company_name, name)
		with ThreadPoolExecutor() as executor:
			scores = list(executor.map(score, names))
		best_idx = max(range(len(scores)), key=lambda i: scores[i], default=None)
		if best_idx is not None and scores[best_idx] >= 60:
			match_name = names[best_idx]
			return next((item.get("co_code") for item in data if item["companyname"] == match_name), None)
		return None
	except Exception as e:
		print(f"Error fetching co_code: {e}")
		return None
