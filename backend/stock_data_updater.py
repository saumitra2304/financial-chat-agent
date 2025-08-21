"""
Daily Stock Data Updater Service
Fetches all companies from Financial Modeling Prep API and stores in MongoDB
Runs daily at 3:30 IST
"""

import requests
import pandas as pd
import pymongo
from datetime import datetime, timedelta
import pytz
import schedule
import time
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from logger_config import app_logger

# Load environment variables
load_dotenv()

# Use main application logger
logger = app_logger

class StockDataUpdater:
    """Service to update stock data in MongoDB daily"""
    
    def __init__(self):
        self.api_key = os.getenv('FMP_API_KEY')
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        self.database_name = os.getenv('DB_NAME', 'chatbotdb')
        self.collection_name = 'stock_companies'
        
        # API endpoints - focusing only on NSE
        self.endpoints = {
            'nse_stocks': f"https://financialmodelingprep.com/api/v3/symbol/NSE?apikey={self.api_key}",
        }
        
        # Initialize MongoDB connection
        self.client = None
        self.db = None
        self.collection = None
        self.connect_to_mongodb()
        
    def connect_to_mongodb(self):
        """Establish connection to MongoDB"""
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes for better performance
            self.collection.create_index("symbol", unique=True)
            self.collection.create_index("exchange")
            self.collection.create_index("exchange_type")
            self.collection.create_index("region")
            self.collection.create_index("last_updated")
            self.collection.create_index("marketCap")
            self.collection.create_index("price")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def fetch_exchange_data(self, exchange: str) -> Optional[List[Dict]]:
        """Fetch data for a specific exchange"""
        endpoint_key = f"{exchange.lower()}_stocks"
        if endpoint_key not in self.endpoints:
            logger.warning(f"No endpoint configured for exchange: {exchange}")
            return None
        
        url = self.endpoints[endpoint_key]
        
        try:
            logger.info(f"Fetching {exchange} data from FMP API...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                logger.warning(f"No data received from {exchange} API")
                return None
            
            logger.info(f"Successfully fetched {len(data)} companies from {exchange}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {exchange} data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while fetching {exchange} data: {e}")
            return None

    def fetch_all_companies(self) -> Optional[List[Dict]]:
        """Fetch NSE companies from FMP API"""
        
        # Fetch only NSE data
        nse_data = self.fetch_exchange_data('nse')
        
        if not nse_data:
            logger.error("Failed to fetch NSE data")
            return None
        
        # Add exchange info to each company
        for company in nse_data:
            company['source_exchange'] = 'NSE'
        
        logger.info(f"Successfully fetched {len(nse_data)} NSE companies")
        return nse_data
    
    def process_companies_data(self, companies_data: List[Dict]) -> List[Dict]:
        """Process and clean companies data with enhanced financial metrics"""
        processed_companies = []
        
        for company in companies_data:
            try:
                # Extract and clean company data with enhanced fields
                processed_company = {
                    # Basic Info
                    'symbol': company.get('symbol', '').strip(),
                    'name': company.get('name', '').strip(),
                    'exchange': company.get('exchange', '').strip().upper(),
                    'source_exchange': company.get('source_exchange', ''),
                    
                    # Price Data
                    'price': self._safe_float(company.get('price')),
                    'changesPercentage': self._safe_float(company.get('changesPercentage')),
                    'change': self._safe_float(company.get('change')),
                    'dayLow': self._safe_float(company.get('dayLow')),
                    'dayHigh': self._safe_float(company.get('dayHigh')),
                    'yearHigh': self._safe_float(company.get('yearHigh')),
                    'yearLow': self._safe_float(company.get('yearLow')),
                    'open': self._safe_float(company.get('open')),
                    'previousClose': self._safe_float(company.get('previousClose')),
                    
                    # Market Data
                    'marketCap': self._safe_int(company.get('marketCap')),
                    'volume': self._safe_int(company.get('volume')),
                    'avgVolume': self._safe_int(company.get('avgVolume')),
                    'sharesOutstanding': self._safe_int(company.get('sharesOutstanding')),
                    
                    # Technical Indicators
                    'priceAvg50': self._safe_float(company.get('priceAvg50')),
                    'priceAvg200': self._safe_float(company.get('priceAvg200')),
                    
                    # Financial Ratios
                    'eps': self._safe_float(company.get('eps')),
                    'pe': self._safe_float(company.get('pe')),
                    
                    # Additional Info
                    'currency': company.get('currency', ''),
                    'type': company.get('type', 'stock'),
                    'earningsAnnouncement': company.get('earningsAnnouncement'),
                    'timestamp': company.get('timestamp'),
                    
                    # Metadata
                    'last_updated': datetime.utcnow()
                    # Note: date_added will be handled separately in upsert operation
                }
                
                # Skip if symbol is empty
                if not processed_company['symbol']:
                    continue
                
                # Categorize by exchange/region
                symbol = processed_company['symbol']
                exchange = processed_company['exchange']
                source_exchange = processed_company['source_exchange']
                
                # Determine region and exchange type - NSE focused
                if source_exchange == 'NSE' or symbol.endswith('.NS') or exchange == 'NSE':
                    processed_company['region'] = 'India'
                    processed_company['exchange_type'] = 'NSE'
                    processed_company['currency'] = processed_company['currency'] or 'INR'
                else:
                    # This shouldn't happen with NSE-only data, but keep as fallback
                    processed_company['region'] = 'India'
                    processed_company['exchange_type'] = 'NSE'
                    processed_company['currency'] = processed_company['currency'] or 'INR'
                
                # Calculate additional metrics if possible
                if processed_company['price'] and processed_company['yearLow'] and processed_company['yearHigh']:
                    year_range = processed_company['yearHigh'] - processed_company['yearLow']
                    if year_range > 0:
                        processed_company['price_position_in_year'] = (
                            (processed_company['price'] - processed_company['yearLow']) / year_range
                        )
                
                processed_companies.append(processed_company)
                
            except Exception as e:
                logger.warning(f"Error processing company {company.get('symbol', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Processed {len(processed_companies)} companies successfully")
        return processed_companies
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int"""
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    def update_mongodb(self, companies: List[Dict]) -> bool:
        """Update MongoDB with companies data"""
        try:
            logger.info("Starting MongoDB update...")
            
            # Get current timestamp
            update_time = datetime.utcnow()
            
            # Prepare bulk operations
            bulk_ops = []
            
            for company in companies:
                # Create a copy of company data without date_added for $set
                company_data = {k: v for k, v in company.items() if k != 'date_added'}
                
                # Use upsert to update existing or insert new
                bulk_ops.append(
                    pymongo.UpdateOne(
                        {'symbol': company['symbol']},
                        {
                            '$set': {
                                **company_data,
                                'last_updated': update_time
                            },
                            '$setOnInsert': {
                                'date_added': update_time
                            }
                        },
                        upsert=True
                    )
                )
            
            # Execute bulk operations in batches of 1000
            batch_size = 1000
            total_batches = (len(bulk_ops) + batch_size - 1) // batch_size
            
            for i in range(0, len(bulk_ops), batch_size):
                batch = bulk_ops[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                logger.info(f"Processing batch {batch_num}/{total_batches}")
                result = self.collection.bulk_write(batch)
                
                logger.info(f"Batch {batch_num}: "
                           f"Matched: {result.matched_count}, "
                           f"Modified: {result.modified_count}, "
                           f"Upserted: {result.upserted_count}")
            
            # Update metadata collection with last update info
            metadata_collection = self.db['update_metadata']
            metadata_collection.update_one(
                {'type': 'stock_companies_update'},
                {
                    '$set': {
                        'last_update': update_time,
                        'total_companies': len(companies),
                        'update_status': 'success'
                    }
                },
                upsert=True
            )
            
            logger.info("MongoDB update completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating MongoDB: {e}")
            
            # Update metadata with error status
            try:
                metadata_collection = self.db['update_metadata']
                metadata_collection.update_one(
                    {'type': 'stock_companies_update'},
                    {
                        '$set': {
                            'last_update_attempt': datetime.utcnow(),
                            'update_status': 'failed',
                            'error_message': str(e)
                        }
                    },
                    upsert=True
                )
            except:
                pass
            
            return False
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored companies"""
        try:
            total_companies = self.collection.count_documents({})
            
            # Get breakdown by exchange
            pipeline = [
                {
                    '$group': {
                        '_id': '$exchange_type',
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            
            exchange_breakdown = list(self.collection.aggregate(pipeline))
            
            # Get breakdown by region
            region_pipeline = [
                {
                    '$group': {
                        '_id': '$region',
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            
            region_breakdown = list(self.collection.aggregate(region_pipeline))
            
            # Get last update info
            metadata = self.db['update_metadata'].find_one({'type': 'stock_companies_update'})
            
            return {
                'total_companies': total_companies,
                'exchange_breakdown': exchange_breakdown,
                'region_breakdown': region_breakdown,
                'last_update': metadata.get('last_update') if metadata else None,
                'update_status': metadata.get('update_status') if metadata else 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def run_daily_update(self):
        """Main method to run daily update"""
        logger.info("Starting daily stock companies update...")
        
        try:
            # Fetch data from API
            companies_data = self.fetch_all_companies()
            if not companies_data:
                logger.error("Failed to fetch companies data")
                return False
            
            # Process data
            processed_companies = self.process_companies_data(companies_data)
            if not processed_companies:
                logger.error("No companies to process")
                return False
            
            # Update MongoDB
            success = self.update_mongodb(processed_companies)
            
            if success:
                # Print statistics
                stats = self.get_statistics()
                logger.info(f"Update completed successfully. Statistics: {stats}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in daily update: {e}")
            return False
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def update_all_data(self):
        """Main method to update all stock data - to be called by service"""
        return self.run_daily_update()

# This file is now used as a module, no main execution needed
