"""
Stock Symbol Verification and Confirmation Tools
Ensures accurate company identification before financial analysis
"""

from agents import function_tool
import os
from python_helpers import search_nse_symbol_by_name
from dotenv import load_dotenv

load_dotenv()

@function_tool
def search_and_confirm_stock(company_name: str) -> dict:
	"""
	STOCK IDENTIFICATION & CONFIRMATION: Searches for company and requests user confirmation before analysis.
	
	This tool prevents analysis errors by:
	- Searching NSE database for company names
	- Displaying found company details with current price
	- Explicitly asking user to confirm the correct company
	- Providing clear next steps for analysis
	
	Use this tool FIRST whenever a user mentions a company name for analysis.
	
	Args:
		company_name: The company name mentioned by the user (use exact words from user query)
	Returns:
		Dictionary with search results and confirmation requirements
	"""
	try:
		# Search for the NSE symbol
		nse_symbol = search_nse_symbol_by_name(company_name)
		
		if nse_symbol:
			# Get company details from MongoDB
			import pymongo
			mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
			database_name = os.getenv('DB_NAME', 'chatbotdb')
			
			client = pymongo.MongoClient(mongo_uri)
			db = client[database_name]
			collection = db['stock_companies']
			
			company_doc = collection.find_one({'symbol': nse_symbol})
			
			if company_doc:
				current_price = company_doc.get('price', 'N/A')
				market_cap = company_doc.get('marketCap', 'N/A')
				full_name = company_doc.get('name', 'N/A')
				
				# Format market cap for display
				if isinstance(market_cap, (int, float)) and market_cap > 0:
					if market_cap >= 1e12:
						market_cap_display = f"₹{market_cap/1e12:.2f} trillion"
					elif market_cap >= 1e9:
						market_cap_display = f"₹{market_cap/1e9:.2f} billion"
					elif market_cap >= 1e7:
						market_cap_display = f"₹{market_cap/1e7:.2f} crores"
					else:
						market_cap_display = f"₹{market_cap:,.0f}"
				else:
					market_cap_display = "N/A"
				
				return {
					'status': 'found',
					'user_query': company_name,
					'found_symbol': nse_symbol,
					'company_name': full_name,
					'current_price': f"₹{current_price:,.2f}" if isinstance(current_price, (int, float)) else str(current_price),
					'market_cap': market_cap_display,
					'exchange': 'NSE (National Stock Exchange)',
					'confirmation_required': True,
					'message': f"""
🔍 STOCK FOUND: 
Company: {full_name}
Symbol: {nse_symbol}
Current Price: ₹{current_price:,.2f} (as available)
Market Cap: {market_cap_display}

❓ CONFIRMATION NEEDED: Is this the correct company you want to analyze? 

✅ If YES: I can proceed with the requested analysis
❌ If NO: Please provide the exact company name or stock symbol
					""".strip(),
					'ready_for_analysis': True
				}
			else:
				return {
					'status': 'symbol_without_data',
					'user_query': company_name,
					'found_symbol': nse_symbol,
					'message': f"Found symbol {nse_symbol} for '{company_name}' but no detailed company data available. Analysis may be limited.",
					'confirmation_required': True,
					'ready_for_analysis': False
				}
		else:
			# Provide helpful suggestions
			suggestions = []
			if 'reliance' in company_name.lower():
				suggestions.append("Try: 'Reliance Industries Limited' or 'RELIANCE.NS'")
			if 'tata' in company_name.lower():
				suggestions.append("Try: 'Tata Consultancy Services' or 'TCS.NS'")
			if 'hdfc' in company_name.lower():
				suggestions.append("Try: 'HDFC Bank Limited' or 'HDFCBANK.NS'")
			if 'infosys' in company_name.lower():
				suggestions.append("Try: 'Infosys Limited' or 'INFY.NS'")
			
			return {
				'status': 'not_found',
				'user_query': company_name,
				'found_symbol': None,
				'message': f"""
❌ NO STOCK FOUND for '{company_name}'

💡 SUGGESTIONS:
• Use the complete company name (e.g., 'Reliance Industries Limited')
• Provide the NSE stock symbol (e.g., 'RELIANCE.NS')  
• Check spelling and company name accuracy

{chr(10).join(f'• {suggestion}' for suggestion in suggestions) if suggestions else ''}
				""".strip(),
				'confirmation_required': False,
				'ready_for_analysis': False,
				'suggestions': suggestions
			}
			
	except Exception as e:
		return {
			'status': 'error',
			'user_query': company_name,
			'error': str(e),
			'message': f"Error searching for '{company_name}': {str(e)}",
			'confirmation_required': False,
			'ready_for_analysis': False
		}

@function_tool  
def proceed_with_confirmed_symbol(confirmed_symbol: str, analysis_type: str = "comprehensive") -> dict:
	"""
	ANALYSIS INITIATION: Confirms the stock symbol and provides analysis readiness status.
	
	Use this tool after the user has confirmed the correct stock symbol to indicate readiness for analysis.
	
	Args:
		confirmed_symbol: The stock symbol confirmed by the user (e.g., 'RELIANCE.NS', 'TCS.NS')
		analysis_type: Type of analysis to perform ('fundamental', 'technical', 'comprehensive', 'quantitative')
	Returns:
		Dictionary confirming analysis readiness and next steps
	"""
	try:
		# Validate the symbol format
		if not confirmed_symbol.endswith('.NS'):
			if '.' not in confirmed_symbol:
				confirmed_symbol = confirmed_symbol + '.NS'
		
		# Get company details for final confirmation
		import pymongo
		mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
		database_name = os.getenv('DB_NAME', 'chatbotdb')
		
		client = pymongo.MongoClient(mongo_uri)
		db = client[database_name]
		collection = db['stock_companies']
		
		company_doc = collection.find_one({'symbol': confirmed_symbol})
		
		if company_doc:
			return {
				'status': 'ready_for_analysis',
				'confirmed_symbol': confirmed_symbol,
				'company_name': company_doc.get('name', 'N/A'),
				'analysis_type': analysis_type,
				'message': f"✅ CONFIRMED: Ready to perform {analysis_type} analysis for {company_doc.get('name', 'N/A')} ({confirmed_symbol})",
				'next_action': f"Proceeding with {analysis_type} analysis using the appropriate financial analysis tools."
			}
		else:
			return {
				'status': 'symbol_not_found',
				'confirmed_symbol': confirmed_symbol,
				'message': f"⚠️ Symbol {confirmed_symbol} not found in database. Analysis may use external data sources.",
				'ready_for_analysis': True
			}
			
	except Exception as e:
		return {
			'status': 'error',
			'confirmed_symbol': confirmed_symbol,
			'error': str(e),
			'message': f"Error confirming symbol {confirmed_symbol}: {str(e)}",
			'ready_for_analysis': False
		}
