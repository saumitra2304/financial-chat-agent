"""
Professional Quantitative Finance Analysis Tools
Using industry-standard libraries: QuantLib, PyPortfolioOpt, arch, riskfolio-lib, scikit-learn, etc.
"""

import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Union, Any
import warnings
from dotenv import load_dotenv
from agents import function_tool
from python_helpers import get_fmp_price_data, search_symbol

# Professional Finance Libraries
import QuantLib as ql
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt import CLA, HRPOpt, objective_functions
# import riskfolio as rp  # Temporarily disabled due to dependency conflicts
from arch import arch_model

# Machine Learning Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
# from tsfresh import extract_features, select_features  # Temporarily disabled
# from tsfresh.utilities.dataframe_functions import impute

# Scientific Computing
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
load_dotenv()

# API Configuration removed - using centralized helper

def _get_price_data_for_portfolio(symbols: List[str], timeframe: str = "1d", days_back: int = 1260) -> pd.DataFrame | None:
    """Get price data for multiple symbols using FMP API."""
    try:
        all_data = {}
        for symbol in symbols:
            df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
            if df is not None and not df.empty:
                all_data[symbol] = df['Close']
        
        if not all_data:
            return None
            
        # Combine all symbols into one DataFrame
        combined_df = pd.DataFrame(all_data)
        return combined_df.dropna()
        
    except Exception as e:
        print(f"Error fetching portfolio data: {e}")
        return None

@function_tool
def calculate_portfolio_optimization(symbols: List[str], optimization_method: str = "efficient_frontier", 
                                   risk_model: str = "sample_cov", days_back: int = 1260) -> dict | None:
    """
    PORTFOLIO OPTIMIZATION: Professional portfolio optimization using PyPortfolioOpt with intelligent symbol search.
    
    This tool provides institutional-grade portfolio optimization including:
    - Modern Portfolio Theory (Efficient Frontier)
    - Critical Line Algorithm (CLA) for exact solutions
    - Hierarchical Risk Parity (HRP) for better diversification
    - Multiple risk models (sample covariance, exponential covariance, semicovariance)
    - Sharpe ratio maximization with realistic risk-free rates
    - Automatic symbol resolution for company names
    
    Use this tool when users ask about:
    - Portfolio optimization, asset allocation, or portfolio construction
    - Optimal portfolio weights, efficient frontier, or risk-return trade-offs
    - Diversification strategies or portfolio rebalancing
    - Modern portfolio theory or quantitative portfolio management
    - Risk-adjusted returns or Sharpe ratio optimization
    
    Args:
        symbols: List of stock symbols or company names (e.g., ['AAPL', 'MSFT', 'Reliance Industries'])
        optimization_method: 'efficient_frontier' (Markowitz), 'cla' (Critical Line), 'hrp' (Risk Parity)
        risk_model: 'sample_cov' (historical), 'exp_cov' (exponential), 'semicovariance' (downside risk)
        days_back: Number of days for historical data (default: 1260 for ~5 years)
    
    Returns:
        Dictionary containing optimized weights, expected returns, risk metrics, and Sharpe ratio
    """
    try:
        # Fetch price data for all symbols using centralized function
        price_df = _get_price_data_for_portfolio(symbols, "1d", days_back)
        
        if price_df is None or price_df.empty:
            return {"error": "Could not fetch price data for portfolio symbols"}
        
        # Calculate expected returns and risk model with better error handling
        try:
            # Use a more robust expected returns calculation for longer time periods
            mu = expected_returns.mean_historical_return(price_df, frequency=252)
            
            # For longer historical periods, use a more conservative approach
            # Remove extreme outliers and ensure reasonable returns
            mu_filtered = mu.copy()
            
            # Cap extremely high returns (above 200% annually) and floor negative returns
            mu_filtered = mu_filtered.clip(lower=0.01, upper=2.0)  # 1% to 200% annually
            
            # Ensure we have meaningful positive expected returns
            if mu_filtered.max() <= 0.02:  # If all returns are below 2%
                # Use a more robust calculation with geometric mean
                returns = price_df.pct_change().dropna()
                geometric_returns = (1 + returns).prod(axis=0) ** (252 / len(returns)) - 1
                mu_filtered = geometric_returns.clip(lower=0.02, upper=2.0)
            
            mu = mu_filtered
            
        except Exception as e:
            print(f"Error calculating expected returns: {e}")
            # Fallback to geometric mean of returns with reasonable bounds
            returns = price_df.pct_change().dropna()
            try:
                geometric_returns = (1 + returns).prod(axis=0) ** (252 / len(returns)) - 1
                mu = geometric_returns.clip(lower=0.02, upper=1.0)  # 2% to 100% annually
            except:
                # Final fallback: use simple mean with minimum viable returns
                mu = (returns.mean() * 252).clip(lower=0.03, upper=0.5)  # 3% to 50% annually
        
        if risk_model == "sample_cov":
            S = risk_models.sample_cov(price_df, frequency=252)
        elif risk_model == "semicovariance":
            S = risk_models.semicovariance(price_df, frequency=252)
        elif risk_model == "exp_cov":
            S = risk_models.exp_cov(price_df, frequency=252)
        else:
            S = risk_models.sample_cov(price_df, frequency=252)
        
        # Portfolio optimization with better error handling
        if optimization_method == "efficient_frontier":
            ef = EfficientFrontier(mu, S)
            # Use a very conservative risk-free rate (1% for global markets)
            risk_free_rate = 0.01
            ef.risk_free_rate = risk_free_rate
            weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
            cleaned_weights = ef.clean_weights()
            performance = ef.portfolio_performance(verbose=True, risk_free_rate=risk_free_rate)
            
        elif optimization_method == "cla":
            cla = CLA(mu, S)
            weights = cla.max_sharpe()
            cleaned_weights = cla.clean_weights()
            performance = cla.portfolio_performance(verbose=True)
            
        elif optimization_method == "hrp":
            hrp = HRPOpt(price_df.pct_change().dropna())
            weights = hrp.optimize()
            cleaned_weights = weights
            returns = price_df.pct_change().dropna()
            portfolio_return = (returns * pd.Series(weights)).sum(axis=1)
            performance = (
                portfolio_return.mean() * 252,
                portfolio_return.std() * np.sqrt(252),
                portfolio_return.mean() * 252 / (portfolio_return.std() * np.sqrt(252))
            )
        
        return {
            "optimization_method": optimization_method,
            "risk_model": risk_model,
            "symbols": list(price_df.columns),
            "data_points": len(price_df),
            "date_range": f"{price_df.index.min().date()} to {price_df.index.max().date()}",
            "expected_returns": {symbol: f"{ret:.2%}" for symbol, ret in mu.items()},
            "weights": cleaned_weights,
            "expected_annual_return": f"{performance[0]:.2%}",
            "annual_volatility": f"{performance[1]:.2%}",
            "sharpe_ratio": round(performance[2], 4),
            "total_weight": round(sum(cleaned_weights.values()), 6),
            "risk_free_rate": "2.0%"
        }
        
    except Exception as e:
        print(f"Error in portfolio optimization: {e}")
        return {"error": str(e)}

@function_tool
def calculate_garch_volatility_models(symbol: str, model_type: str = "GARCH", days_back: int = 252) -> dict | None:
    """
    Advanced volatility modeling using GARCH family models from arch library.
    
    Args:
        symbol: Stock symbol
        model_type: 'GARCH', 'EGARCH', 'GJR-GARCH'
        days_back: Number of days for historical data
    
    Returns:
        Dictionary containing GARCH model results and forecasts
    """
    try:
        # Get price data using centralized function
        df = get_fmp_price_data(symbol, "1d", days_back, return_format="dataframe")
        if df is None or df.empty:
            return {"error": f"Could not fetch price data for {symbol}"}
        returns = df['Close'].pct_change().dropna() * 100  # Convert to percentage
        
        # Fit GARCH model
        if model_type == "GARCH":
            model = arch_model(returns, vol='Garch', p=1, q=1, dist='normal')
        elif model_type == "EGARCH":
            model = arch_model(returns, vol='EGARCH', p=1, q=1, dist='normal')
        elif model_type == "GJR-GARCH":
            model = arch_model(returns, vol='GARCH', p=1, o=1, q=1, dist='normal')
        else:
            model = arch_model(returns, vol='Garch', p=1, q=1, dist='normal')
        
        # Fit the model
        fitted_model = model.fit(disp='off')
        
        # Generate forecasts
        forecast = fitted_model.forecast(horizon=30)
        
        # Calculate model diagnostics
        log_likelihood = fitted_model.loglikelihood
        aic = fitted_model.aic
        bic = fitted_model.bic
        
        return {
            "symbol": symbol,
            "model_type": model_type,
            "model_summary": {
                "log_likelihood": round(log_likelihood, 4),
                "aic": round(aic, 4),
                "bic": round(bic, 4),
                "num_observations": len(returns)
            },
            "current_volatility": f"{fitted_model.conditional_volatility[-1]:.2f}%",
            "mean_volatility": f"{fitted_model.conditional_volatility.mean():.2f}%",
            "volatility_forecast_30d": {
                "mean": f"{forecast.variance.iloc[-1, 0]**0.5:.2f}%",
                "values": [f"{val**0.5:.2f}%" for val in forecast.variance.iloc[-1, :5]]
            },
            "parameters": {param: round(float(value), 6) for param, value in fitted_model.params.items()}
        }
        
    except Exception as e:
        print(f"Error in GARCH modeling: {e}")
        return {"error": str(e)}

@function_tool
def calculate_quantlib_options_pricing(symbol: str, strike_price: float = None, option_type: str = "call", 
                                     days_to_expiry: int = 30, risk_free_rate: float = 0.05) -> dict | None:
    """
    Professional options pricing using QuantLib library.
    
    Args:
        symbol: Stock symbol
        strike_price: Option strike price (defaults to current price)
        option_type: 'call' or 'put'
        days_to_expiry: Days until option expiration
        risk_free_rate: Risk-free interest rate
    
    Returns:
        Dictionary containing Black-Scholes pricing and Greeks
    """
    try:
        # Get current price and volatility using centralized function
        df = get_fmp_price_data(symbol, "1d", 60, return_format="dataframe")
        if df is None or df.empty:
            return {"error": f"Could not fetch price data for {symbol}"}
        
        current_price = df['Close'].iloc[-1]
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        
        if strike_price is None:
            strike_price = current_price
        
        # Set up QuantLib objects
        calculation_date = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = calculation_date
        
        # Market data
        spot_price = current_price
        strike = strike_price
        expiry_date = calculation_date + ql.Period(days_to_expiry, ql.Days)
        
        # QuantLib objects
        payoff = ql.PlainVanillaPayoff(
            ql.Option.Call if option_type.lower() == "call" else ql.Option.Put,
            strike
        )
        exercise = ql.EuropeanExercise(expiry_date)
        option = ql.VanillaOption(payoff, exercise)
        
        # Market data handles
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
        risk_free_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(calculation_date, risk_free_rate, ql.Actual365Fixed())
        )
        volatility_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(calculation_date, ql.NullCalendar(), volatility, ql.Actual365Fixed())
        )
        
        # Pricing engine
        bs_process = ql.BlackScholesProcess(spot_handle, risk_free_ts, volatility_ts)
        engine = ql.AnalyticEuropeanEngine(bs_process)
        option.setPricingEngine(engine)
        
        # Calculate price and Greeks
        option_price = option.NPV()
        delta = option.delta()
        gamma = option.gamma()
        theta = option.theta()
        vega = option.vega()
        rho = option.rho()
        
        # Implied volatility calculation
        try:
            implied_vol = option.impliedVolatility(option_price, bs_process)
        except:
            implied_vol = volatility
        
        return {
            "symbol": symbol,
            "option_type": option_type,
            "current_spot_price": round(spot_price, 2),
            "strike_price": round(strike, 2),
            "days_to_expiry": days_to_expiry,
            "risk_free_rate": f"{risk_free_rate:.2%}",
            "historical_volatility": f"{volatility:.2%}",
            "pricing": {
                "option_price": round(option_price, 4),
                "intrinsic_value": round(max(0, spot_price - strike) if option_type.lower() == "call" 
                                       else max(0, strike - spot_price), 4),
                "time_value": round(option_price - max(0, spot_price - strike) if option_type.lower() == "call" 
                                  else option_price - max(0, strike - spot_price), 4)
            },
            "greeks": {
                "delta": round(delta, 4),
                "gamma": round(gamma, 6),
                "theta": round(theta, 4),
                "vega": round(vega, 4),
                "rho": round(rho, 4)
            },
            "implied_volatility": f"{implied_vol:.2%}"
        }
        
    except Exception as e:
        print(f"Error in QuantLib options pricing: {e}")
        return {"error": str(e)}

@function_tool
def calculate_ml_price_prediction(symbol: str, model_type: str = "xgboost", forecast_days: int = 5, 
                                days_back: int = 252) -> dict | None:
    """
    Machine learning-based price prediction using XGBoost, LightGBM, or Random Forest.
    
    Args:
        symbol: Stock symbol
        model_type: 'xgboost', 'lightgbm', 'random_forest'
        forecast_days: Number of days to forecast
        days_back: Historical data period
    
    Returns:
        Dictionary containing ML model predictions and feature importance
    """
    try:
        # Get price data using centralized function
        df = get_fmp_price_data(symbol, "1d", days_back, return_format="dataframe")
        if df is None or df.empty:
            return {"error": f"Could not fetch price data for {symbol}"}
        
        # Feature engineering
        df['returns'] = df['Close'].pct_change()
        df['returns_lag1'] = df['returns'].shift(1)
        df['returns_lag2'] = df['returns'].shift(2)
        df['returns_lag3'] = df['returns'].shift(3)
        df['volatility'] = df['returns'].rolling(window=20).std()
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        df['rsi'] = 100 - (100 / (1 + (df['Close'].diff().clip(lower=0).rolling(14).mean() / 
                                       df['Close'].diff().clip(upper=0).abs().rolling(14).mean())))
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        df['price_volume'] = df['Close'] * df['Volume']
        df['high_low_ratio'] = df['High'] / df['Low']
        df['close_open_ratio'] = df['Close'] / df['Open']
        
        # Target variable (next day return)
        df['target'] = df['returns'].shift(-1)
        
        # Prepare features
        feature_cols = ['returns_lag1', 'returns_lag2', 'returns_lag3', 'volatility', 
                       'sma_20', 'sma_50', 'rsi', 'volume_sma', 'price_volume', 
                       'high_low_ratio', 'close_open_ratio']
        
        # Remove rows with NaN values
        df = df.dropna()
        
        if len(df) < 50:
            return {"error": "Insufficient data for ML model training"}
        
        X = df[feature_cols]
        y = df['target']
        
        # Split data
        train_size = int(len(df) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_type == "xgboost":
            model = xgb.XGBRegressor(n_estimators=100, max_depth=3, random_state=42)
            model.fit(X_train_scaled, y_train)
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            
        elif model_type == "lightgbm":
            model = lgb.LGBMRegressor(n_estimators=100, max_depth=3, random_state=42, verbose=-1)
            model.fit(X_train_scaled, y_train)
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            
        elif model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
            model.fit(X_train_scaled, y_train)
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Model performance
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Forecast future prices
        last_features = X.iloc[-1:].values
        last_features_scaled = scaler.transform(last_features)
        
        current_price = df['Close'].iloc[-1]
        forecasted_returns = []
        forecasted_prices = [current_price]
        
        for _ in range(forecast_days):
            pred_return = model.predict(last_features_scaled)[0]
            forecasted_returns.append(pred_return)
            next_price = forecasted_prices[-1] * (1 + pred_return)
            forecasted_prices.append(next_price)
        
        return {
            "symbol": symbol,
            "model_type": model_type,
            "current_price": round(current_price, 2),
            "forecast_days": forecast_days,
            "model_performance": {
                "mean_squared_error": round(mse, 6),
                "r2_score": round(r2, 4),
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            },
            "forecasted_prices": [round(p, 2) for p in forecasted_prices[1:]],
            "forecasted_returns": [f"{r:.2%}" for r in forecasted_returns],
            "feature_importance": {k: round(v, 4) for k, v in 
                                 sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)},
            "price_change_forecast": f"{((forecasted_prices[-1] / current_price) - 1):.2%}"
        }
        
    except Exception as e:
        print(f"Error in ML price prediction: {e}")
        return {"error": str(e)}

@function_tool
def calculate_volatility_metrics(symbol: str, timeframe: str = "1d", days_back: int = 252) -> dict | None:
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
        days_back: Number of days of historical data for analysis (default: 252 for 1 year)
    
    Returns:
        Dictionary containing comprehensive volatility and risk metrics
    """
    try:
        # Get historical data using centralized function
        df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
        if df is None or df.empty:
            return {"error": f"Could not fetch price data for {symbol}"}
        
        # Calculate returns
        returns = df['Close'].pct_change().dropna()
        
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
            "historical_volatility_annualized": float(returns.std() * np.sqrt(annual_factor) * 100),
            "daily_volatility": float(returns.std() * 100),
            "mean_return": float(returns.mean() * 100),
            "skewness": float(stats.skew(returns)),
            "kurtosis": float(stats.kurtosis(returns))
        }
        
        # Value at Risk (VaR) - 95% and 99% confidence levels
        metrics["risk_metrics"] = {
            "var_95": float(np.percentile(returns, 5) * 100),
            "var_99": float(np.percentile(returns, 1) * 100),
            "expected_shortfall_95": float(returns[returns <= np.percentile(returns, 5)].mean() * 100),
            "expected_shortfall_99": float(returns[returns <= np.percentile(returns, 1)].mean() * 100)
        }
        
        # Current price information
        current_price = df['Close'].iloc[-1]
        metrics["price_info"] = {
            "symbol": symbol,
            "current_price": float(current_price),
            "price_change_24h": float(((current_price / df['Close'].iloc[-2]) - 1) * 100) if len(df) > 1 else 0,
            "high_24h": float(df['High'].iloc[-1]),
            "low_24h": float(df['Low'].iloc[-1]),
            "volume_24h": float(df['Volume'].iloc[-1])
        }
        
        return metrics
        
    except Exception as e:
        print(f"Error calculating volatility metrics: {e}")
        return {"error": str(e)}

@function_tool
def calculate_correlation_analysis(symbols: List[str], timeframe: str = "1d", days_back: int = 252) -> dict | None:
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
        days_back: Number of days of historical data for analysis (default: 252 for 1 year)
    
    Returns:
        Dictionary containing correlation matrix and analysis insights
    """
    try:
        if len(symbols) < 2:
            return {"error": "Need at least 2 symbols for correlation analysis"}
        
        # Use the existing portfolio data function
        price_df = _get_price_data_for_portfolio(symbols, timeframe, days_back)
        
        if price_df is None or price_df.empty:
            return {"error": "Could not fetch sufficient data for correlation analysis"}
        
        # Calculate returns
        returns_df = price_df.pct_change().dropna()
        
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
        
        return results
        
    except Exception as e:
        print(f"Error in correlation analysis: {e}")
        return {"error": str(e)}

@function_tool
def calculate_riskfolio_portfolio_risk(symbols: List[str], risk_measure: str = "MV", days_back: int = 252) -> dict | None:
    """
    Advanced portfolio risk analysis (temporarily disabled due to dependency conflicts).
    """
    return {"error": "Riskfolio-lib temporarily disabled due to dependency conflicts. Use calculate_portfolio_optimization instead."}

@function_tool
def calculate_tsfresh_features(symbol: str, days_back: int = 252) -> dict | None:
    """
    Automated time series feature extraction (temporarily disabled due to dependency conflicts).
    """
    return {"error": "TSFresh temporarily disabled due to dependency conflicts. Use calculate_ml_price_prediction for feature-based analysis."}
