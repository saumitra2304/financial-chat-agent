import requests
from rapidfuzz import fuzz
from concurrent.futures import ThreadPoolExecutor

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
