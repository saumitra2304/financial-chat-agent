"""
Professional Quantitative Finance Analysis Tools (Hygiene-Upgraded Version)
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
from pypfopt import CLA, HRPOpt
from arch import arch_model

# Scientific Computing
from scipy import stats

warnings.filterwarnings('ignore')
load_dotenv()

# -----------------------------------------------------------------------------
# Internal helpers
# -----------------------------------------------------------------------------

def _align_and_clip_returns(df: pd.DataFrame, lookback_days: Optional[int] = None,
                            winsorise: bool = False) -> pd.Series:
    """
    Align prices to common index, apply optional lookback truncation and winsorisation.
    """
    series = df['Close']

    # Lookback truncation
    if lookback_days is not None and lookback_days < len(series):
        series = series.tail(lookback_days)

    # Convert to returns
    returns = series.pct_change().dropna()

    if winsorise:
        lower = np.percentile(returns, 1)  # 1% tail
        upper = np.percentile(returns, 99)
        returns = np.clip(returns, lower, upper)

    return returns


# -----------------------------------------------------------------------------
# CORE TOOLS (UPGRADED)
# -----------------------------------------------------------------------------

@function_tool
def get_historical_price_data(symbol: str, timeframe: str = "5min",
                              days_back: int = 30) -> dict | None:
    result = get_fmp_price_data(symbol, timeframe, days_back, return_format="dict")
    if result and "data" in result:
        result["data"] = result["data"][:50]  # truncate for context safety
        return result
    return result


@function_tool
def calculate_volatility_metrics(symbol: str, timeframe: str = "1d", days_back: int = 252,
                                 winsorise: bool = False) -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch price data for {symbol}"}

    returns = _align_and_clip_returns(df, lookback_days=None, winsorise=winsorise)
    if len(returns) < 20:
        return {"error": "Insufficient data for volatility calculation"}

    annual_factor = {"1min": 525600, "5min": 105120, "15min": 35040,
                     "30min": 17520, "1hour": 8760, "4hour": 2190,
                     "1day": 252}.get(timeframe, 252)

    return {
        "symbol": symbol,
        "volatility_metrics": {
            "daily_volatility": float(returns.std() * 100),
            "annual_volatility": float(returns.std() * np.sqrt(annual_factor) * 100),
            "mean_return": float(returns.mean() * 100),
            "skewness": float(stats.skew(returns)),
            "kurtosis": float(stats.kurtosis(returns))
        }
    }


@function_tool
def calculate_correlation_analysis(symbols: List[str], timeframe: str = "1d", days_back: int = 252,
                                   winsorise: bool = False) -> dict | None:
    price_df = pd.DataFrame()
    for sym in symbols:
        df = get_fmp_price_data(sym, timeframe, days_back, return_format="dataframe")
        if df is not None and not df.empty:
            price_df[sym] = df["Close"]

    if price_df.empty:
        return {"error": "Could not fetch data"}

    # Align by dropping rows where all are NaN
    price_df = price_df.dropna(how="all").dropna()

    returns = price_df.pct_change().dropna()
    if winsorise:
        lower, upper = np.percentile(returns.values, 1), np.percentile(returns.values, 99)
        returns = returns.clip(lower, upper)

    corr = returns.corr()
    highest, lowest = None, None
    high_val, low_val = -1, 1
    for i, s1 in enumerate(symbols):
        for s2 in symbols[i+1:]:
            cval = corr.loc[s1, s2]
            if abs(cval) > abs(high_val):
                high_val, highest = cval, f"{s1}-{s2}"
            if abs(cval) < abs(low_val):
                low_val, lowest = cval, f"{s1}-{s2}"

    return {
        "symbols": symbols,
        "correlation_matrix": corr.round(4).to_dict(),
        "highest_correlation": {"pair": highest, "correlation": round(float(high_val), 4)},
        "lowest_correlation": {"pair": lowest, "correlation": round(float(low_val), 4)}
    }


@function_tool
def calculate_advanced_statistics(symbol: str, timeframe: str = "1d", days_back: int = 252,
                                  winsorise: bool = False) -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch price data for {symbol}"}

    returns = _align_and_clip_returns(df, lookback_days=None, winsorise=winsorise)
    if len(returns) < 30:
        return {"error": "Insufficient data for statistical analysis"}

    jb = stats.jarque_bera(returns)
    from statsmodels.tsa.stattools import acf
    auto = acf(returns, nlags=5, fft=True)

    return {
        "symbol": symbol,
        "descriptive_stats": {
            "mean_return": float(returns.mean()),
            "std_deviation": float(returns.std()),
            "skewness": float(stats.skew(returns)),
            "kurtosis": float(stats.kurtosis(returns))
        },
        "normality_tests": {
            "jarque_bera_statistic": float(jb.statistic),
            "p_value": float(jb.pvalue),
            "is_normal": jb.pvalue > 0.05
        },
        "autocorrelation": {f"lag_{i}": float(auto[i]) for i in range(1, 5)}
    }


@function_tool
def calculate_monte_carlo_simulation(symbol: str, forecast_days: int = 10, simulations: int = 100,
                                     confidence_level: float = 0.95, winsorise: bool = False) -> dict | None:
    df = get_fmp_price_data(symbol, "1d", 252, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch price data for {symbol}"}

    returns = _align_and_clip_returns(df, winsorise=winsorise)
    current_price = df["Close"].iloc[-1]
    mean_ret, vol = returns.mean(), returns.std()

    results = []
    for _ in range(simulations):
        p = current_price
        for _ in range(forecast_days):
            p *= (1 + np.random.normal(mean_ret, vol))
        results.append(p)

    lower = np.percentile(results, (1-confidence_level)*100)
    upper = np.percentile(results, confidence_level*100)
    return {
        "symbol": symbol,
        "expected_price": float(np.mean(results)),
        "confidence_interval_lower": float(lower),
        "confidence_interval_upper": float(upper)
    }


@function_tool
def calculate_portfolio_optimization(symbols: List[str], optimization_method: str = "efficient_frontier",
                                     risk_model: str = "sample_cov", days_back: int = 1260,
                                     lookback_days: Optional[int] = None,
                                     risk_free_rate: float = 0.0,
                                     winsorise: bool = False) -> dict | None:
    price_df = pd.DataFrame()
    for sym in symbols:
        df = get_fmp_price_data(sym, "1d", days_back, return_format="dataframe")
        if df is not None and not df.empty:
            price_df[sym] = df["Close"]

    if price_df.empty:
        return {"error": "Could not fetch price data"}

    if lookback_days is not None:
        price_df = price_df.tail(lookback_days)

    price_df = price_df.dropna(how="all").dropna()
    returns = price_df.pct_change().dropna()
    if winsorise:
        lower, upper = np.percentile(returns.values, 1), np.percentile(returns.values, 99)
        returns = returns.clip(lower, upper)

    mu = expected_returns.mean_historical_return(price_df, frequency=252) - risk_free_rate
    cov = getattr(risk_models, risk_model)(price_df, frequency=252)

    if optimization_method == "efficient_frontier":
        ef = EfficientFrontier(mu, cov)
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
        perf = ef.portfolio_performance(risk_free_rate=risk_free_rate)
        clean_w = ef.clean_weights()
    elif optimization_method == "cla":
        cla = CLA(mu, cov)
        weights = cla.max_sharpe()
        clean_w = cla.clean_weights()
        perf = cla.portfolio_performance()
    else:
        hrp = HRPOpt(returns)
        clean_w = hrp.optimize()
        port_ret = (returns * pd.Series(clean_w)).sum(axis=1)
        perf = (port_ret.mean() * 252, port_ret.std() * np.sqrt(252),
                (port_ret.mean() * 252) / (port_ret.std() * np.sqrt(252)))

    return {
        "symbols": symbols,
        "weights": clean_w,
        "expected_annual_return": f"{perf[0]:.2%}",
        "annual_volatility": f"{perf[1]:.2%}",
        "sharpe_ratio": round(perf[2], 4)
    }


@function_tool
def calculate_garch_volatility_models(symbol: str, model_type: str = "GARCH",
                                      days_back: int = 252,
                                      lookback_days: Optional[int] = None,
                                      winsorise: bool = False) -> dict | None:
    df = get_fmp_price_data(symbol, "1d", days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch price data for {symbol}"}

    if lookback_days is not None and lookback_days < len(df):
        df = df.tail(lookback_days)

    returns = df['Close'].pct_change().dropna() * 100
    if winsorise:
        lower = np.percentile(returns, 1)
        upper = np.percentile(returns, 99)
        returns = np.clip(returns, lower, upper)

    if model_type == "EGARCH":
        model = arch_model(returns, vol="EGARCH", p=1, q=1)
    elif model_type == "GJR-GARCH":
        model = arch_model(returns, vol="GARCH", p=1, o=1, q=1)
    else:
        model = arch_model(returns, vol="GARCH", p=1, q=1)

    fitted = model.fit(disp="off")
    return {
        "symbol": symbol,
        "model_type": model_type,
        "log_likelihood": float(fitted.loglikelihood),
        "aic": float(fitted.aic),
        "bic": float(fitted.bic),
        "current_volatility": f"{fitted.conditional_volatility.iloc[-1]:.2f}%"
    }


# -----------------------------------------------------------------------------
# EXPLORATORY / REGIME / FACTOR TOOLS (UPGRADED)
# -----------------------------------------------------------------------------

@function_tool
def calculate_pca_decomposition(symbols: List[str], timeframe: str = "1d", days_back: int = 252,
                                lookback_days: Optional[int] = None,
                                excess_returns: bool = False,
                                winsorise: bool = False) -> dict | None:
    price_df = pd.DataFrame()
    for sym in symbols:
        d = get_fmp_price_data(sym, timeframe, days_back, return_format="dataframe")
        if d is not None and not d.empty:
            price_df[sym] = d["Close"]

    if price_df.empty:
        return {"error": "Could not fetch data"}

    if lookback_days is not None:
        price_df = price_df.tail(lookback_days)

    price_df = price_df.dropna(how="all").dropna()
    returns = price_df.pct_change().dropna()

    if excess_returns:
        returns = returns.sub(returns.mean(axis=1), axis=0)

    if winsorise:
        lower, upper = np.percentile(returns.values, 1), np.percentile(returns.values, 99)
        returns = returns.clip(lower, upper)

    cov_matrix = returns.cov()
    eig_vals, eig_vecs = np.linalg.eig(cov_matrix)
    total_var = float(np.sum(eig_vals))
    explained_variance = {f"PC{i+1}": float(v / total_var) for i, v in enumerate(eig_vals)}

    top_loadings = {}
    for i, vec in enumerate(eig_vecs.T[:3]):  # top 3 PCs
        top_loadings[f"PC{i+1}"] = {sym: float(val) for sym, val in zip(price_df.columns, vec)}

    return {
        "symbols": symbols,
        "explained_variance": explained_variance,
        "top_factor_loadings": top_loadings
    }


@function_tool
def calculate_rolling_beta(symbol: str, benchmark_symbol: str, window: int = 60,
                           timeframe: str = "1d", days_back: int = 252,
                           lookback_days: Optional[int] = None,
                           winsorise: bool = False) -> dict | None:
    s_df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    b_df = get_fmp_price_data(benchmark_symbol, timeframe, days_back, return_format="dataframe")
    if s_df is None or b_df is None or s_df.empty or b_df.empty:
        return {"error": "Could not fetch data"}

    if lookback_days is not None:
        s_df, b_df = s_df.tail(lookback_days), b_df.tail(lookback_days)

    r_s = s_df["Close"].pct_change().dropna()
    r_b = b_df["Close"].pct_change().dropna()
    common_index = r_s.index.intersection(r_b.index)
    r_s, r_b = r_s.loc[common_index], r_b.loc[common_index]

    if winsorise:
        lower, upper = np.percentile(r_s.values, 1), np.percentile(r_s.values, 99)
        r_s = np.clip(r_s, lower, upper)
        r_b = np.clip(r_b, lower, upper)

    betas = []
    for i in range(window, len(r_s)):
        cov = np.cov(r_s[i-window:i], r_b[i-window:i])[0][1]
        var = np.var(r_b[i-window:i])
        betas.append(cov / var if var != 0 else 0.0)

    return {
        "symbol": symbol,
        "benchmark": benchmark_symbol,
        "rolling_beta_last": float(betas[-1]) if betas else None
    }


@function_tool
def calculate_autocorrelation_analysis(symbol: str, timeframe: str = "1d", days_back: int = 252,
                                       lookback_days: Optional[int] = None,
                                       winsorise: bool = False) -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    returns = df['Close'].pct_change().dropna()
    if winsorise:
        lower = np.percentile(returns, 1)
        upper = np.percentile(returns, 99)
        returns = np.clip(returns, lower, upper)

    from statsmodels.tsa.stattools import acf
    ac_vals = acf(returns, nlags=5, fft=True)
    return {f"lag_{i}": float(ac_vals[i]) for i in range(1, 6)}


@function_tool
def calculate_cointegration_test(symbol1: str, symbol2: str, timeframe: str = "1d", days_back: int = 252,
                                 lookback_days: Optional[int] = None,
                                 use_returns: bool = False,
                                 winsorise: bool = False) -> dict | None:
    df1 = get_fmp_price_data(symbol1, timeframe, days_back, return_format="dataframe")
    df2 = get_fmp_price_data(symbol2, timeframe, days_back, return_format="dataframe")
    if df1 is None or df2 is None or df1.empty or df2.empty:
        return {"error": "Could not fetch data"}

    if lookback_days is not None:
        df1, df2 = df1.tail(lookback_days), df2.tail(lookback_days)

    series1, series2 = df1["Close"], df2["Close"]
    if use_returns:
        series1, series2 = series1.pct_change().dropna(), series2.pct_change().dropna()

    common_index = series1.index.intersection(series2.index)
    series1, series2 = series1.loc[common_index], series2.loc[common_index]

    if winsorise:
        lower1 = np.percentile(series1, 1); upper1 = np.percentile(series1, 99)
        lower2 = np.percentile(series2, 1); upper2 = np.percentile(series2, 99)
        series1, series2 = np.clip(series1, lower1, upper1), np.clip(series2, lower2, upper2)

    from statsmodels.tsa.stattools import coint
    score, pvalue, _ = coint(series1, series2)
    return {
        "pair": f"{symbol1}-{symbol2}",
        "coint_score": float(score),
        "p_value": float(pvalue),
        "cointegrated": bool(pvalue < 0.05)
    }


@function_tool
def calculate_kalman_spread(symbol1: str, symbol2: str, timeframe: str = "1d", days_back: int = 252,
                            lookback_days: Optional[int] = None,
                            winsorise: bool = False) -> dict | None:
    try:
        import pykalman
    except ImportError:
        return {"error": "pykalman library not available"}
    
    df1 = get_fmp_price_data(symbol1, timeframe, days_back, return_format="dataframe")
    df2 = get_fmp_price_data(symbol2, timeframe, days_back, return_format="dataframe")
    if df1 is None or df2 is None or df1.empty or df2.empty:
        return {"error": "Could not fetch data"}

    if lookback_days is not None:
        df1, df2 = df1.tail(lookback_days), df2.tail(lookback_days)

    y, x = df1["Close"].values, df2["Close"].values
    if winsorise:
        lower1, upper1 = np.percentile(y, 1), np.percentile(y, 99)
        lower2, upper2 = np.percentile(x, 1), np.percentile(x, 99)
        y, x = np.clip(y, lower1, upper1), np.clip(x, lower2, upper2)

    delta = 1e-5
    trans_cov = delta / (1 - delta) * np.eye(2)
    obs_mat = np.vstack([x, np.ones(len(x))]).T[:, np.newaxis, :]

    kf = pykalman.KalmanFilter(
        transition_matrices=np.eye(2),
        observation_matrices=obs_mat,
        transition_covariance=trans_cov,
        observation_covariance=1.0,
        initial_state_mean=np.zeros(2),
        initial_state_covariance=np.ones((2, 2))
    )
    state_means, _ = kf.filter(y)
    return {
        "pair": f"{symbol1}-{symbol2}",
        "last_hedge_ratio": float(state_means[:, 0][-1])
    }


@function_tool
def calculate_rolling_volatility(symbol: str, window: int = 30, timeframe: str = "1d",
                                 days_back: int = 252, lookback_days: Optional[int] = None,
                                 winsorise: bool = False) -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    returns = df["Close"].pct_change().dropna()
    if winsorise:
        lower, upper = np.percentile(returns, 1), np.percentile(returns, 99)
        returns = np.clip(returns, lower, upper)

    roll_vol = returns.rolling(window).std().dropna()
    return {
        "symbol": symbol,
        "rolling_volatility_last": float(roll_vol.iloc[-1])
    }


@function_tool
def calculate_drawdown_series(symbol: str, timeframe: str = "1d", days_back: int = 252,
                              lookback_days: Optional[int] = None) -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    prices = df["Close"]
    peak = prices.expanding(min_periods=1).max()
    dd = (prices - peak) / peak
    return {
        "symbol": symbol,
        "max_drawdown": float(dd.min()),
        "last_drawdown": float(dd.iloc[-1])
    }


@function_tool
def calculate_var_cvar_analysis(symbol: str, confidence: float = 0.95,
                                timeframe: str = "1d", days_back: int = 252,
                                lookback_days: Optional[int] = None,
                                winsorise: bool = False) -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    returns = df["Close"].pct_change().dropna()
    if winsorise:
        lower, upper = np.percentile(returns, 1), np.percentile(returns, 99)
        returns = np.clip(returns, lower, upper)

    var = np.percentile(returns, (1 - confidence) * 100)
    cvar = returns[returns <= var].mean()
    return {
        "symbol": symbol,
        "historical_VaR": float(var),
        "historical_CVaR": float(cvar)
    }


@function_tool
def calculate_markov_regime_detection(symbol: str, timeframe: str = "1d", days_back: int = 252,
                                      lookback_days: Optional[int] = None) -> dict | None:
    try:
        from hmmlearn.hmm import GaussianHMM
    except ImportError:
        return {"error": "hmmlearn library not available"}
        
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    returns = df["Close"].pct_change().dropna().values.reshape(-1, 1)
    model = GaussianHMM(n_components=2, covariance_type="diag", n_iter=100)
    model.fit(returns)
    state = int(model.predict(returns)[-1])
    return {
        "symbol": symbol,
        "current_regime_state": state
    }


@function_tool
def calculate_factor_exposure_ols(symbol: str, factor_symbols: List[str],
                                  timeframe: str = "1d", days_back: int = 252,
                                  lookback_days: Optional[int] = None,
                                  excess_returns: bool = False,
                                  risk_free_rate: float = 0.0,
                                  winsorise: bool = False) -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    y = df["Close"].pct_change().dropna()
    if excess_returns:
        y = y - risk_free_rate / 252.0

    X = pd.DataFrame()
    for fac in factor_symbols:
        fdf = get_fmp_price_data(fac, timeframe, days_back, return_format="dataframe")
        if fdf is not None and not fdf.empty:
            X[fac] = fdf["Close"].pct_change()
    X = X.dropna()
    y = y.loc[X.index]

    if winsorise:
        threshold_low, threshold_high = np.percentile(y, 1), np.percentile(y, 99)
        y = np.clip(y, threshold_low, threshold_high)

    try:
        import statsmodels.api as sm
    except ImportError:
        return {"error": "statsmodels library not available"}
    
    X_const = sm.add_constant(X.values)
    model = sm.OLS(y.values, X_const).fit()

    coeffs = {"Intercept": float(model.params[0])}
    for i, fac in enumerate(X.columns):
        coeffs[fac] = float(model.params[i + 1])

    return {
        "symbol": symbol,
        "factors": factor_symbols,
        "ols_coefficients": coeffs
    }


@function_tool
def calculate_factor_exposure_pca(symbol: str, factor_symbols: List[str],
                                  timeframe: str = "1d", days_back: int = 252,
                                  lookback_days: Optional[int] = None,
                                  excess_returns: bool = False,
                                  winsorise: bool = False) -> dict | None:
    df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
    if df is None or df.empty:
        return {"error": f"Could not fetch data for {symbol}"}

    if lookback_days is not None:
        df = df.tail(lookback_days)

    data = {symbol: df["Close"].pct_change()}
    for fac in factor_symbols:
        fdf = get_fmp_price_data(fac, timeframe, days_back, return_format="dataframe")
        if fdf is not None and not fdf.empty:
            data[fac] = fdf["Close"].pct_change()

    df_returns = pd.DataFrame(data).dropna()
    if excess_returns:
        df_returns = df_returns.sub(df_returns.mean(axis=1), axis=0)

    if winsorise:
        lower, upper = np.percentile(df_returns.values, 1), np.percentile(df_returns.values, 99)
        df_returns = df_returns.clip(lower, upper)

    cov_matrix = df_returns.cov()
    eig_vals, _ = np.linalg.eig(cov_matrix)
    total_var = float(np.sum(eig_vals))
    explained_variance = {f"PC{i+1}": float(v / total_var) for i, v in enumerate(eig_vals)}

    return {
        "symbol_and_factors": [symbol] + factor_symbols,
        "explained_variance": explained_variance
    }
