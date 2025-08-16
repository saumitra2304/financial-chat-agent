from agents import function_tool
import yfinance as yf
import json
import os
from dotenv import load_dotenv
from python_helpers import get_co_code
import requests


load_dotenv()
api_key = os.getenv("CMOTS_API_KEY")
BASE_URL = os.getenv("CMOTS_BASE_URL", "https://insbaapis.cmots.com")
API_SUFFIX = os.getenv("CMOTS_API_SUFFIX", "C")

@function_tool
def get_ttm_ratios(company_name: str) -> dict | None:
	"""
	Fetches key metrics and yearly ratios for a company using the YearlyRatio API.
	Args:
		co_code: The company code.
		api_key: The Bearer token for authorization.
	Returns:
		Dictionary of yearly ratios and metrics, or None if not found.
	"""
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching yearly ratios: {e}")
		return None

@function_tool
def get_quarterly_results(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None

@function_tool
def get_balance_sheet(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None

@function_tool
def get_cashflow(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None

@function_tool
def get_shareholding(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
		return None
	url = f"{BASE_URL}/api/ShareholdingMorethanonePerDetails/{int(co_code)}/{API_SUFFIX}"
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
def get_margin_ratios(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None

@function_tool
def get_solvency_ratios(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None

@function_tool
def get_efficiency_ratios(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None

@function_tool
def get_financial_stability_ratios(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None
	
@function_tool
def get_valuation_ratios(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None

@function_tool
def get_cashflow_ratios(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None

@function_tool
def get_growth_ratios(company_name: str) -> dict | None:
	"""
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
	"""
	
	co_code = get_co_code(company_name, api_key)
	if not co_code:
		print(f"Could not find co_code for company: {company_name}")
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
		print(f"Error fetching quarterly results: {e}")
		return None
