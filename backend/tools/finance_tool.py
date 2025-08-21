from agents import function_tool
import json
import os
from dotenv import load_dotenv
from python_helpers import get_co_code, search_nse_symbol_by_name
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

load_dotenv()
api_key = os.getenv("CMOTS_API_KEY")
fmp_api_key = os.getenv("FMP_API_KEY")
fmp_base_url = os.getenv("FMP_BASE_URL", "https://financialmodelingprep.com")
BASE_URL = os.getenv("CMOTS_BASE_URL", "https://insbaapis.cmots.com")
API_SUFFIX = os.getenv("CMOTS_API_SUFFIX", "C")

@function_tool
def confirm_stock_symbol(company_name: str) -> dict:
	"""
	STOCK SYMBOL CONFIRMATION: Searches for and displays the stock symbol found for a company name, asking user to confirm.
	
	This tool helps ensure accuracy by:
	- Searching for the company in our NSE database
	- Displaying the found company name and symbol
	- Asking the user to confirm this is the correct company
	- Preventing analysis of wrong companies due to name ambiguity
	
	Use this tool FIRST when users ask about any specific company analysis to ensure you're analyzing the correct stock.
	
	Args:
		company_name: The company name mentioned by the user (e.g., 'reliance industries', 'tata steel', 'infosys')
	Returns:
		Dictionary with found symbol, company name, and confirmation status
	"""
	try:
		# Search for the NSE symbol
		nse_symbol = search_nse_symbol_by_name(company_name)
		
		if nse_symbol:
			# Get the full company details from the database
			import pymongo
			mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
			database_name = os.getenv('DB_NAME', 'chatbotdb')
			
			client = pymongo.MongoClient(mongo_uri)
			db = client[database_name]
			collection = db['stock_companies']
			
			company_doc = collection.find_one({'symbol': nse_symbol})
			
			if company_doc:
				result = {
					'search_term': company_name,
					'found_symbol': nse_symbol,
					'found_company_name': company_doc.get('name', 'N/A'),
					'current_price': company_doc.get('price', 'N/A'),
					'confirmation_required': True,
					'message': f"Found: {company_doc.get('name', 'N/A')} (Symbol: {nse_symbol}). Please confirm this is the correct company before proceeding with analysis."
				}
			else:
				result = {
					'search_term': company_name,
					'found_symbol': nse_symbol,
					'found_company_name': 'Unknown',
					'confirmation_required': True,
					'message': f"Found symbol {nse_symbol} for '{company_name}'. Please confirm this is correct."
				}
		else:
			result = {
				'search_term': company_name,
				'found_symbol': None,
				'found_company_name': None,
				'confirmation_required': False,
				'message': f"No NSE stock found for '{company_name}'. Please check the company name or provide the exact stock symbol."
			}
		
		return result
		
	except Exception as e:
		return {
			'error': str(e),
			'message': f"Error searching for company '{company_name}': {str(e)}"
		}

def get_company_identifiers(company_name: str) -> dict:
	"""
	Internal helper function to get company identifiers from multiple sources.
	Returns both CMOTS co_code and NSE symbol if available.
	"""
	result = {
		'co_code': None,
		'nse_symbol': None,
		'company_name': company_name
	}
	
	# Try to get CMOTS co_code
	try:
		co_code = get_co_code(company_name, api_key)
		if co_code:
			result['co_code'] = co_code
	except Exception as e:
		pass
	
	# Try to get NSE symbol from our database
	try:
		nse_symbol = search_nse_symbol_by_name(company_name)
		if nse_symbol:
			result['nse_symbol'] = nse_symbol
	except Exception as e:
		pass
	
	return result

@function_tool
def get_ttm_ratios(company_name: str) -> dict | None:
	"""
	FUNDAMENTAL ANALYSIS: Fetches comprehensive TTM (Trailing Twelve Months) financial ratios and key metrics.
	
	This tool provides essential fundamental analysis data including:
	- Profitability ratios (ROE, ROA, profit margins, EBITDA margins)
	- Liquidity ratios (current ratio, quick ratio, cash ratio)
	- Efficiency ratios (asset turnover, inventory turnover, receivables turnover)
	- Leverage ratios (debt-to-equity, interest coverage, debt ratios)
	- Valuation ratios (P/E, P/B, P/S, EV/EBITDA)
	- Growth metrics and financial health indicators
	
	Use this tool when users ask about:
	- Company financial health, profitability, or financial performance
	- Fundamental analysis, financial ratios, or valuation metrics
	- Balance sheet strength, liquidity, or debt analysis
	- Comparing financial metrics across companies
	
	Args:
		company_name: The name of the company (e.g., 'Apple', 'Microsoft', 'Tesla', 'Reliance Industries')
	Returns:
		Dictionary of comprehensive TTM ratios and financial metrics
	"""
	# Get company identifiers (both CMOTS co_code and NSE symbol)
	identifiers = get_company_identifiers(company_name)
	co_code = identifiers['co_code']
	nse_symbol = identifiers['nse_symbol']
	
	if not co_code:
		return None
		
	url = f"{BASE_URL}/api/DailyRatios/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None

@function_tool
def get_quarterly_results(company_name: str) -> dict | None:
	"""
	EARNINGS ANALYSIS: Fetches detailed quarterly earnings results and financial statements.
	
	This tool provides comprehensive quarterly financial data including:
	- Revenue, profit, and earnings per share trends
	- Income statement line items by quarter
	- Year-over-year and quarter-over-quarter growth rates
	- Segment-wise revenue breakdown (if available)
	- Seasonal patterns and earnings quality metrics
	- Beat/miss analysis vs. analyst expectations
	
	Use this tool when users ask about:
	- Quarterly earnings, revenue, or profit trends
	- Company financial performance over time
	- Earnings growth, revenue growth, or quarterly comparisons
	- Financial statement analysis or earnings quality
	- How the company performed in recent quarters
	
	Args:
		company_name: The name of the company (e.g., 'Apple', 'Google', 'Amazon')
	Returns:
		Dictionary of detailed quarterly financial results and trends
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		return None
	url = f"{BASE_URL}/api/QuarterlyResults/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None
	
@function_tool
def get_profit_loss(company_name: str) -> dict | None:
	"""
	Fetches profit and loss statement for a company using the ProftandLoss API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of profit and loss data, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		return None
	url = f"{BASE_URL}/api/ProftandLoss/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None

@function_tool
def get_balance_sheet(company_name: str) -> dict | None:
	"""
	Fetches balance sheet for a company using the Balancesheet API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of balance sheet data, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		return None
	url = f"{BASE_URL}/api/Balancesheet/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None

@function_tool
def get_cashflow(company_name: str) -> dict | None:
	"""
	Fetches cash flow statement for a company using the CashFlow API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of cash flow data, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		return None
	url = f"{BASE_URL}/api/CashFlow/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None

@function_tool
def get_shareholding(company_name: str) -> dict | None:
	"""
	Fetches shareholding pattern for a company using the ShareholdingMorethanonePerDetails API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of shareholding data, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		return None
	url = f"{BASE_URL}/api/ShareholdingMorethanonePerDetails/{int(co_code)}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None

@function_tool
def get_margin_ratios(company_name: str) -> dict | None:
	"""
	Fetches margin ratios for a company using the MarginRatios API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of margin ratios, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		return None
	url = f"{BASE_URL}/api/MarginRatios/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None

@function_tool
def get_performance_ratios(company_name: str) -> dict | None:
	"""
	Fetches performance ratios for a company using the PerformanceRatios API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of performance ratios, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		return None
	url = f"{BASE_URL}/api/PerformanceRatios/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None

@function_tool
def get_efficiency_ratios(company_name: str) -> dict | None:
	"""
	Fetches efficiency ratios for a company using the EfficiencyRatios API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of efficiency ratios, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		return None
	url = f"{BASE_URL}/api/EfficiencyRatios/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None

@function_tool
def get_financial_stability_ratios(company_name: str) -> dict | None:
	"""
	Fetches financial stability ratios for a company using the FinancialStabilityRatios API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of financial stability ratios, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		return None
	url = f"{BASE_URL}/api/FinancialStabilityRatios/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		return None
	
@function_tool
def get_valuation_ratios(company_name: str) -> dict | None:
	"""
	Fetches valuation ratios for a company using the ValuationRatios API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of valuation ratios, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Error: Could not find company code for '{company_name}' in valuation ratios fetch.")
		return None
	url = f"{BASE_URL}/api/ValuationRatios/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		print(f"Error fetching valuation ratios: {e}")
		return None

@function_tool
def get_cashflow_ratios(company_name: str) -> dict | None:
	"""
	Fetches cash flow ratios for a company using the CashFlowRatios API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of cash flow ratios, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Error: Could not find company code for '{company_name}' in cash flow ratios fetch.")
		return None
	url = f"{BASE_URL}/api/CashFlowRatios/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		print(f"Error fetching cash flow ratios: {e}")
		return None

@function_tool
def get_growth_ratios(company_name: str) -> dict | None:
	"""
	Fetches growth ratios for a company using the GrowthRatio API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of growth ratios, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Error: Could not find company code for '{company_name}' in growth ratios fetch.")
		return None
	url = f"{BASE_URL}/api/GrowthRatio/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		print(f"Error fetching growth ratios: {e}")
		return None

@function_tool
def get_solvency_ratios(company_name: str) -> dict | None:
	"""
	Fetches solvency ratios for a company using the SolvencyRatios API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of solvency ratios, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Error: Could not find company code for '{company_name}' in solvency ratios fetch.")
		return None
	url = f"{BASE_URL}/api/RatiosSolvency/{int(co_code)}/{API_SUFFIX}"
	headers = {"Authorization": f"Bearer {api_key}"}
	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.raise_for_status()
		result = response.json()
		if result.get("success") and result.get("data"):
			return result["data"]
		return None
	except Exception as e:
		print(f"Error fetching growth ratios: {e}")
		return None
