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
	Fetches key metrics and TTM ratios for a company using the DailyRatios API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of TTM ratios and metrics, or None if not found.
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
	Fetches quarterly results for a company using the QuarterlyResults API.
	Args:
		company_name: The name of the company.
	Returns:
		Dictionary of quarterly results, or None if not found.
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
