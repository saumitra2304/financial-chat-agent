from agents import function_tool
import json
import os
from dotenv import load_dotenv
from python_helpers import get_co_code
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
		company_name: The name of the company (e.g., 'Apple', 'Microsoft', 'Tesla')
	Returns:
		Dictionary of comprehensive TTM ratios and financial metrics
	"""
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Error: Could not find company code for '{company_name}' in TTM ratios fetch.")
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
		print(f"Error fetching TTM ratios: {e}")
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
		print(f"Error: Could not find company code for '{company_name}' in quarterly results fetch.")
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
		print(f"Error fetching quarterly results: {e}")
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
		print(f"Error: Could not find company code for '{company_name}' in profit and loss fetch.")
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
		print(f"Error fetching profit and loss data: {e}")
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
		print(f"Error: Could not find company code for '{company_name}' in balance sheet fetch.")
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
		print(f"Error fetching balance sheet data: {e}")
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
		print(f"Error: Could not find company code for '{company_name}' in cash flow fetch.")
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
		print(f"Error fetching cash flow data: {e}")
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
		print(f"Error: Could not find company code for '{company_name}' in shareholding fetch.")
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
		print(f"Error fetching shareholding data: {e}")
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
		print(f"Error: Could not find company code for '{company_name}' in margin ratios fetch.")
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
		print(f"Error fetching margin ratios: {e}")
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
		print(f"Error: Could not find company code for '{company_name}' in performance ratios fetch.")
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
		print(f"Error fetching solvency ratios: {e}")
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
		print(f"Error: Could not find company code for '{company_name}' in efficiency ratios fetch.")
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
		print(f"Error fetching efficiency ratios: {e}")
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
		print(f"Error: Could not find company code for '{company_name}' in financial stability ratios fetch.")
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
		print(f"Error fetching financial stability ratios: {e}")
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
