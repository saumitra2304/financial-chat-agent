"""
Stock Companies Tool
Provides access to stock companies data stored in MongoDB
"""

import pymongo
from typing import List, Dict, Optional
import os
from datetime import datetime
from dotenv import load_dotenv
from logger_config import app_logger

# Load environment variables
load_dotenv()

class StockCompaniesDB:
    """Interface to query stock companies data from MongoDB"""
    
    def __init__(self):
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        self.database_name = os.getenv('DB_NAME', 'chatbotdb')
        self.collection_name = 'stock_companies'
        
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            app_logger.info(f"Connected to MongoDB database: {self.database_name}")
        except Exception as e:
            app_logger.error(f"Failed to connect to MongoDB for stock companies: {e}")
            self.client = None
            self.db = None
            self.collection = None

def search_companies(query: str, limit: int = 10) -> List[Dict]:
    """
    Search for NSE companies by name or symbol with enhanced data.
    
    Args:
        query: Company name or symbol to search for
        limit: Maximum number of results to return
    
    Returns:
        List of matching NSE companies with their details including price data
    """
    try:
        db = StockCompaniesDB()
        if not db.collection:
            return [{"error": "Database connection failed"}]
        
        # Build search filter for NSE companies only
        search_filter = {
            '$and': [
                {
                    '$or': [
                        {'symbol': {'$regex': query, '$options': 'i'}},
                        {'name': {'$regex': query, '$options': 'i'}}
                    ]
                },
                {
                    'exchange_type': 'NSE'  # Only NSE companies
                }
            ]
        }
        
        # Execute search with enhanced fields
        results = list(db.collection.find(
            search_filter,
            {
                'symbol': 1,
                'name': 1,
                'exchange_type': 1,
                'region': 1,
                'currency': 1,
                'type': 1,
                'price': 1,
                'changesPercentage': 1,
                'marketCap': 1,
                'volume': 1,
                'pe': 1,
                'eps': 1,
                'last_updated': 1,
                '_id': 0
            }
        ).limit(limit))
        
        if not results:
            return [{"message": f"No companies found matching '{query}'"}]
        
        # Format results for better readability
        formatted_results = []
        for company in results:
            formatted_company = company.copy()
            
            # Format market cap
            if company.get('marketCap'):
                market_cap = company['marketCap']
                if market_cap >= 1e12:
                    formatted_company['marketCapFormatted'] = f"${market_cap/1e12:.2f}T"
                elif market_cap >= 1e9:
                    formatted_company['marketCapFormatted'] = f"${market_cap/1e9:.2f}B"
                elif market_cap >= 1e6:
                    formatted_company['marketCapFormatted'] = f"${market_cap/1e6:.2f}M"
            
            # Format volume
            if company.get('volume'):
                volume = company['volume']
                if volume >= 1e6:
                    formatted_company['volumeFormatted'] = f"{volume/1e6:.2f}M"
                elif volume >= 1e3:
                    formatted_company['volumeFormatted'] = f"{volume/1e3:.2f}K"
            
            formatted_results.append(formatted_company)
        
        app_logger.info(f"Found {len(results)} companies matching '{query}'")
        return formatted_results
        
    except Exception as e:
        app_logger.error(f"Error searching companies: {e}")
        return [{"error": str(e)}]

def get_companies_by_exchange(limit: int = 20) -> List[Dict]:
    """
    Get NSE companies (since we only have NSE data).
    
    Args:
        limit: Maximum number of results to return
    
    Returns:
        List of NSE companies
    """
    return get_nse_companies(limit)

def get_nse_companies(limit: int = 50) -> List[Dict]:
    """
    Get NSE listed companies with current market data.
    
    Args:
        limit: Maximum number of results to return
    
    Returns:
        List of NSE companies with price and market data
    """
    try:
        db = StockCompaniesDB()
        if not db.collection:
            return [{"error": "Database connection failed"}]
        
        # Sort by market cap descending to get largest companies first
        results = list(db.collection.find(
            {
                '$or': [
                    {'symbol': {'$regex': r'\.NS$'}},
                    {'exchange_type': 'NSE'}
                ]
            },
            {
                'symbol': 1,
                'name': 1,
                'exchange_type': 1,
                'currency': 1,
                'price': 1,
                'changesPercentage': 1,
                'change': 1,
                'marketCap': 1,
                'volume': 1,
                'pe': 1,
                'eps': 1,
                'dayLow': 1,
                'dayHigh': 1,
                'yearLow': 1,
                'yearHigh': 1,
                'last_updated': 1,
                '_id': 0
            }
        ).sort('marketCap', -1).limit(limit))
        
        if not results:
            return [{"message": "No NSE companies found"}]
        
        # Format results
        formatted_results = []
        for company in results:
            formatted_company = company.copy()
            
            # Add formatted fields
            if company.get('marketCap'):
                market_cap = company['marketCap']
                if market_cap >= 1e12:
                    formatted_company['marketCapFormatted'] = f"₹{market_cap/1e12:.2f}T"
                elif market_cap >= 1e7:  # 1 crore
                    formatted_company['marketCapFormatted'] = f"₹{market_cap/1e7:.2f}Cr"
                elif market_cap >= 1e5:  # 1 lakh
                    formatted_company['marketCapFormatted'] = f"₹{market_cap/1e5:.2f}L"
            
            formatted_results.append(formatted_company)
        
        app_logger.info(f"Found {len(results)} NSE companies")
        return formatted_results
        
    except Exception as e:
        app_logger.error(f"Error getting NSE companies: {e}")
        return [{"error": str(e)}]

def get_company_details(symbol: str) -> Dict:
    """
    Get detailed information about a specific company.
    
    Args:
        symbol: Company symbol (e.g., 'RELIANCE.NS', 'AAPL')
    
    Returns:
        Company details dictionary
    """
    try:
        db = StockCompaniesDB()
        if not db.collection:
            return {"error": "Database connection failed"}
        
        # Search for the company
        company = db.collection.find_one(
            {'symbol': {'$regex': f'^{symbol}', '$options': 'i'}},
            {'_id': 0}
        )
        
        if not company:
            return {"error": f"Company with symbol '{symbol}' not found"}
        
        app_logger.info(f"Found company details for {symbol}")
        return company
        
    except Exception as e:
        app_logger.error(f"Error getting company details: {e}")
        return {"error": str(e)}

def get_database_stats() -> Dict:
    """
    Get statistics about the companies database.
    
    Returns:
        Database statistics
    """
    try:
        db = StockCompaniesDB()
        if not db.collection:
            return {"error": "Database connection failed"}
        
        # Get total count
        total_companies = db.collection.count_documents({})
        
        # Get breakdown by exchange
        pipeline = [
            {
                '$group': {
                    '_id': '$exchange_type',
                    'count': {'$sum': 1},
                    'avg_market_cap': {'$avg': '$marketCap'},
                    'total_market_cap': {'$sum': '$marketCap'}
                }
            },
            {
                '$sort': {'count': -1}
            }
        ]
        
        exchange_breakdown = list(db.collection.aggregate(pipeline))
        
        # Get breakdown by region
        region_pipeline = [
            {
                '$group': {
                    '_id': '$region',
                    'count': {'$sum': 1},
                    'avg_market_cap': {'$avg': '$marketCap'},
                    'total_market_cap': {'$sum': '$marketCap'}
                }
            },
            {
                '$sort': {'count': -1}
            }
        ]
        
        region_breakdown = list(db.collection.aggregate(region_pipeline))
        
        # Get price range statistics
        price_stats_pipeline = [
            {
                '$match': {'price': {'$ne': None}}
            },
            {
                '$group': {
                    '_id': None,
                    'avg_price': {'$avg': '$price'},
                    'min_price': {'$min': '$price'},
                    'max_price': {'$max': '$price'},
                    'companies_with_price': {'$sum': 1}
                }
            }
        ]
        
        price_stats = list(db.collection.aggregate(price_stats_pipeline))
        
        # Get last update info
        metadata = db.db['update_metadata'].find_one({'type': 'stock_companies_update'})
        
        stats = {
            'total_companies': total_companies,
            'exchange_breakdown': exchange_breakdown,
            'region_breakdown': region_breakdown,
            'price_statistics': price_stats[0] if price_stats else {},
            'last_update': metadata.get('last_update') if metadata else None,
            'update_status': metadata.get('update_status') if metadata else 'unknown'
        }
        
        app_logger.info("Retrieved database statistics")
        return stats
        
    except Exception as e:
        app_logger.error(f"Error getting database stats: {e}")
        return {"error": str(e)}


def get_top_gainers(exchange: str = "NSE", limit: int = 10) -> List[Dict]:
    """
    Get top gaining stocks by percentage change.
    
    Args:
        exchange: Exchange to filter by ('NSE', 'NASDAQ', 'NYSE', 'all')
        limit: Number of top gainers to return
    
    Returns:
        List of top gaining stocks
    """
    try:
        db = StockCompaniesDB()
        if not db.collection:
            return [{"error": "Database connection failed"}]
        
        # Build filter
        match_filter = {'changesPercentage': {'$ne': None, '$gt': 0}}
        
        if exchange.upper() != "ALL":
            if exchange.upper() in ['NSE', 'BSE', 'NASDAQ', 'NYSE']:
                match_filter['exchange_type'] = exchange.upper()
        
        results = list(db.collection.find(
            match_filter,
            {
                'symbol': 1,
                'name': 1,
                'price': 1,
                'changesPercentage': 1,
                'change': 1,
                'volume': 1,
                'marketCap': 1,
                'exchange_type': 1,
                '_id': 0
            }
        ).sort('changesPercentage', -1).limit(limit))
        
        app_logger.info(f"Found {len(results)} top gainers for {exchange}")
        return results
        
    except Exception as e:
        app_logger.error(f"Error getting top gainers: {e}")
        return [{"error": str(e)}]


def get_top_losers(exchange: str = "NSE", limit: int = 10) -> List[Dict]:
    """
    Get top losing stocks by percentage change.
    
    Args:
        exchange: Exchange to filter by ('NSE', 'NASDAQ', 'NYSE', 'all')
        limit: Number of top losers to return
    
    Returns:
        List of top losing stocks
    """
    try:
        db = StockCompaniesDB()
        if not db.collection:
            return [{"error": "Database connection failed"}]
        
        # Build filter
        match_filter = {'changesPercentage': {'$ne': None, '$lt': 0}}
        
        if exchange.upper() != "ALL":
            if exchange.upper() in ['NSE', 'BSE', 'NASDAQ', 'NYSE']:
                match_filter['exchange_type'] = exchange.upper()
        
        results = list(db.collection.find(
            match_filter,
            {
                'symbol': 1,
                'name': 1,
                'price': 1,
                'changesPercentage': 1,
                'change': 1,
                'volume': 1,
                'marketCap': 1,
                'exchange_type': 1,
                '_id': 0
            }
        ).sort('changesPercentage', 1).limit(limit))
        
        app_logger.info(f"Found {len(results)} top losers for {exchange}")
        return results
        
    except Exception as e:
        app_logger.error(f"Error getting top losers: {e}")
        return [{"error": str(e)}]


def get_high_volume_stocks(exchange: str = "NSE", limit: int = 10) -> List[Dict]:
    """
    Get stocks with highest trading volume.
    
    Args:
        exchange: Exchange to filter by ('NSE', 'NASDAQ', 'NYSE', 'all')
        limit: Number of high volume stocks to return
    
    Returns:
        List of high volume stocks
    """
    try:
        db = StockCompaniesDB()
        if not db.collection:
            return [{"error": "Database connection failed"}]
        
        # Build filter
        match_filter = {'volume': {'$ne': None, '$gt': 0}}
        
        if exchange.upper() != "ALL":
            if exchange.upper() in ['NSE', 'BSE', 'NASDAQ', 'NYSE']:
                match_filter['exchange_type'] = exchange.upper()
        
        results = list(db.collection.find(
            match_filter,
            {
                'symbol': 1,
                'name': 1,
                'price': 1,
                'changesPercentage': 1,
                'volume': 1,
                'avgVolume': 1,
                'marketCap': 1,
                'exchange_type': 1,
                '_id': 0
            }
        ).sort('volume', -1).limit(limit))
        
        # Add volume ratio (current volume / avg volume) if available
        for stock in results:
            if stock.get('volume') and stock.get('avgVolume') and stock['avgVolume'] > 0:
                stock['volumeRatio'] = stock['volume'] / stock['avgVolume']
        
        app_logger.info(f"Found {len(results)} high volume stocks for {exchange}")
        return results
        
    except Exception as e:
        app_logger.error(f"Error getting high volume stocks: {e}")
        return [{"error": str(e)}]
