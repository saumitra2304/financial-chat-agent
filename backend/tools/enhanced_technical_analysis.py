"""
Enhanced Technical Analysis Tools with pandas_ta and Beautiful Charts
Uses Financial Modeling Prep API with intelligent symbol search.
"""

import os
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import warnings
import base64
from io import BytesIO
from dotenv import load_dotenv
from agents import function_tool
from python_helpers import get_fmp_price_data, search_symbol

warnings.filterwarnings('ignore')
load_dotenv()

# Set matplotlib style for beautiful charts
plt.style.use('dark_background')
sns.set_palette("husl")

def _resolve_symbol(symbol_or_name: str) -> str:
    """Internal helper to resolve company name to symbol using search_symbol."""
    # If it looks like a symbol (short and uppercase), use it directly
    if len(symbol_or_name) <= 6 and symbol_or_name.isupper():
        return symbol_or_name
    
    # Otherwise, search for the symbol
    resolved = search_symbol(symbol_or_name)
    if resolved:
        return resolved
    
    # Fallback to original input
    return symbol_or_name

def _get_price_data_for_charts(symbol: str, timeframe: str = "1d", days_back: int = 252) -> pd.DataFrame | None:
    """Internal helper to get price data as DataFrame for charting using FMP API."""
    try:
        # Use the centralized FMP function
        df = get_fmp_price_data(symbol, timeframe, days_back, return_format="dataframe")
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        return None

def _create_chart_base64(fig) -> str:
    """Convert matplotlib figure to base64 string for frontend display."""
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                facecolor='#1e1e1e', edgecolor='none')
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close(fig)
    return f"data:image/png;base64,{chart_base64}"

@function_tool
def calculate_comprehensive_technical_analysis(symbol_or_name: str, timeframe: str = "1d", days_back: int = 252, 
                                             include_chart: bool = True) -> dict | None:
    """
    COMPREHENSIVE TECHNICAL ANALYSIS: Advanced technical analysis using pandas_ta with 50+ indicators and beautiful charts.
    
    This function provides professional-grade technical analysis including:
    - Automatic symbol resolution from company names (e.g., "Apple" -> "AAPL")
    - Momentum indicators (RSI, MACD, Stochastic, Williams %R, CCI, ROC, CMO, PPO)
    - Trend indicators (SMA, EMA, ADX, Aroon, PSAR, Supertrend)
    - Volatility indicators (Bollinger Bands, ATR, Keltner Channels, Donchian Channels)
    - Volume indicators (OBV, VWAP, A/D Line, Chaikin Money Flow, Ease of Movement)
    - Overlap studies (Ichimoku Cloud, Hull MA, Weighted MA, T3 MA)
    - Trading signals and pattern recognition
    - Beautiful 6-panel dashboard charts for frontend display
    
    Use this tool when users ask about:
    - Technical analysis, chart indicators, or trading signals
    - Company technical analysis using names (e.g., "Tesla technical analysis")
    - Moving averages, RSI, MACD, Bollinger Bands, or any technical indicators
    - Overbought/oversold conditions, momentum analysis, or trend analysis
    - Professional technical analysis with visual charts
    
    Args:
        symbol_or_name: Stock symbol (e.g., 'AAPL') or company name (e.g., 'Apple Inc')
        timeframe: Data interval - '1d' for daily, '1h' for hourly, '5min' for 5-minute
        days_back: Number of days of historical data (default: 252 for 1 year)
        include_chart: Whether to generate beautiful visualization charts (default: True)
    
    Returns:
        Dictionary containing all technical indicators, trading signals, and chart (if requested)
    """
    try:
        # Resolve symbol from company name if needed
        symbol = _resolve_symbol(symbol_or_name)
        
        # Get price data
        df = _get_price_data_for_charts(symbol, timeframe, days_back)
        if df is None or df.empty:
            return {"error": f"No price data available for {symbol_or_name} (resolved to: {symbol})"}
        
        # Limit data size for faster processing and smaller output
        if len(df) > 100:
            df = df.tail(100)  # Only use last 100 periods
        
        # Create a copy for indicator calculations
        data = df.copy()
        
        # === ESSENTIAL INDICATORS ONLY (focused selection) ===
        data.ta.rsi(length=14, append=True)  # RSI
        data.ta.macd(fast=12, slow=26, signal=9, append=True)  # MACD
        data.ta.sma(length=20, append=True)   # 20-day SMA
        data.ta.sma(length=50, append=True)   # 50-day SMA
        data.ta.ema(length=12, append=True)   # 12-day EMA
        data.ta.bbands(length=20, std=2, append=True)  # Bollinger Bands
        data.ta.atr(length=14, append=True)   # Average True Range
        data.ta.obv(append=True)              # On Balance Volume
        data.ta.adx(length=14, append=True)   # ADX
        data.ta.stoch(k=14, d=3, append=True)  # Stochastic
        
        # Get latest values for analysis
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest
        
        # === FOCUSED ANALYSIS (essential signals only) ===
        analysis = {
            "symbol": symbol,
            "symbol_resolved_from": symbol_or_name if symbol != symbol_or_name else None,
            "timeframe": timeframe,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_price": round(float(latest['Close']), 2),
            "price_change": round(float(latest['Close'] - previous['Close']), 2),
            "price_change_percent": round(float((latest['Close'] - previous['Close']) / previous['Close'] * 100), 2),
            
            # Key Technical Indicators
            "key_indicators": {
                "rsi": round(float(latest['RSI_14']), 2) if pd.notna(latest.get('RSI_14')) else None,
                "macd": round(float(latest['MACD_12_26_9']), 4) if pd.notna(latest.get('MACD_12_26_9')) else None,
                "macd_signal": round(float(latest['MACDs_12_26_9']), 4) if pd.notna(latest.get('MACDs_12_26_9')) else None,
                "sma_20": round(float(latest['SMA_20']), 2) if pd.notna(latest.get('SMA_20')) else None,
                "sma_50": round(float(latest['SMA_50']), 2) if pd.notna(latest.get('SMA_50')) else None,
                "ema_12": round(float(latest['EMA_12']), 2) if pd.notna(latest.get('EMA_12')) else None,
                "bb_upper": round(float(latest['BBU_20_2.0']), 2) if pd.notna(latest.get('BBU_20_2.0')) else None,
                "bb_middle": round(float(latest['BBM_20_2.0']), 2) if pd.notna(latest.get('BBM_20_2.0')) else None,
                "bb_lower": round(float(latest['BBL_20_2.0']), 2) if pd.notna(latest.get('BBL_20_2.0')) else None,
                "atr": round(float(latest['ATR_14']), 2) if pd.notna(latest.get('ATR_14')) else None,
                "adx": round(float(latest['ADX_14']), 2) if pd.notna(latest.get('ADX_14')) else None,
                "stoch_k": round(float(latest['STOCHk_14_3_3']), 2) if pd.notna(latest.get('STOCHk_14_3_3')) else None,
            },
            
            # Simple Trading Signals (focused analysis)
            "trading_signals": []
        }
        
        # Generate focused trading signals
        signals = []
        
        # RSI Signals
        if analysis["key_indicators"]["rsi"]:
            rsi = analysis["key_indicators"]["rsi"]
            if rsi > 70:
                signals.append(f"RSI overbought at {rsi} - Consider selling")
            elif rsi < 30:
                signals.append(f"RSI oversold at {rsi} - Consider buying")
            elif 40 <= rsi <= 60:
                signals.append(f"RSI neutral at {rsi} - Wait for clear signal")
        
        # Moving Average Signals
        price = analysis["current_price"]
        sma_20 = analysis["key_indicators"]["sma_20"]
        sma_50 = analysis["key_indicators"]["sma_50"]
        
        if sma_20 and sma_50:
            if sma_20 > sma_50 and price > sma_20:
                signals.append("Price above rising 20-day SMA - Bullish trend")
            elif sma_20 < sma_50 and price < sma_20:
                signals.append("Price below falling 20-day SMA - Bearish trend")
        
        # Bollinger Bands Signals
        bb_upper = analysis["key_indicators"]["bb_upper"]
        bb_lower = analysis["key_indicators"]["bb_lower"]
        
        if bb_upper and bb_lower:
            if price >= bb_upper:
                signals.append("Price at upper Bollinger Band - Overbought")
            elif price <= bb_lower:
                signals.append("Price at lower Bollinger Band - Oversold")
        
        # MACD Signals
        macd = analysis["key_indicators"]["macd"]
        macd_signal = analysis["key_indicators"]["macd_signal"]
        
        if macd and macd_signal:
            if macd > macd_signal:
                signals.append("MACD above signal line - Bullish momentum")
            else:
                signals.append("MACD below signal line - Bearish momentum")
        
        analysis["trading_signals"] = signals[:5]  # Limit to top 5 signals
        
        # Skip chart generation to reduce output size (can be re-enabled if needed)
        if include_chart:
            analysis["chart_note"] = "Chart generation temporarily disabled to reduce data size"
        
        return analysis
        
    except Exception as e:
        return {"error": str(e)}

@function_tool
def analyze_candlestick_patterns(symbol_or_name: str, timeframe: str = "1d", days_back: int = 30) -> dict | None:
    """
    CANDLESTICK PATTERN ANALYSIS: Focused candlestick pattern recognition with key trading signals.
    
    Identifies key candlestick patterns with automatic symbol resolution including:
    - Automatic symbol resolution from company names (e.g., "Microsoft" -> "MSFT")
    - Major reversal patterns (Doji, Hammer, Engulfing patterns)
    - Pattern strength and trading implications
    - Focused analysis to avoid data overload
    
    Use this tool when users ask about:
    - Candlestick patterns, price patterns, or pattern recognition
    - Company candlestick analysis using names (e.g., "Amazon candlestick patterns")
    - Reversal patterns and pattern-based trading signals
    
    Args:
        symbol_or_name: Stock symbol (e.g., 'MSFT') or company name (e.g., 'Microsoft Corporation')
        timeframe: Data interval - '1d', '1h', '4h'
        days_back: Number of days of historical data (default: 30, reduced for efficiency)
        
    Returns:
        Dictionary containing key patterns and focused trading signals
    """
    try:
        # Resolve symbol from company name if needed
        symbol = _resolve_symbol(symbol_or_name)
        
        # Get price data (limited size)
        df = _get_price_data_for_charts(symbol, timeframe, days_back)
        if df is None or df.empty:
            return {"error": f"No price data available for {symbol_or_name} (resolved to: {symbol})"}
        
        # Limit to last 20 periods for analysis
        if len(df) > 20:
            df = df.tail(20)
            
        # Add only key candlestick patterns
        data = df.copy()
        
        # Essential patterns only
        data.ta.cdl_doji(append=True)
        data.ta.cdl_hammer(append=True)
        data.ta.cdl_engulfing(append=True)
        data.ta.cdl_morningstar(append=True)
        data.ta.cdl_eveningstar(append=True)
        
        # Find recent patterns (last 10 periods)
        recent_data = data.tail(10)
        patterns_found = []
        
        pattern_columns = ['CDL_DOJI', 'CDL_HAMMER', 'CDL_ENGULFING', 'CDL_MORNINGSTAR', 'CDL_EVENINGSTAR']
        
        for col in pattern_columns:
            if col in recent_data.columns:
                pattern_signals = recent_data[recent_data[col] != 0]
                for date, row in pattern_signals.iterrows():
                    pattern_name = col.replace('CDL_', '').replace('_', ' ').title()
                    signal_strength = "BULLISH" if row[col] > 0 else "BEARISH"
                    patterns_found.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "pattern": pattern_name,
                        "signal": signal_strength,
                        "price": round(row['Close'], 2)
                    })
        
        # Sort by date (most recent first) and limit to top 5
        patterns_found = sorted(patterns_found, key=lambda x: x["date"], reverse=True)[:5]
        
        return {
            "symbol": symbol,
            "symbol_resolved_from": symbol_or_name if symbol != symbol_or_name else None,
            "timeframe": timeframe,
            "analysis_period": f"Last {days_back} days",
            "patterns_found": patterns_found,
            "pattern_count": len(patterns_found),
            "latest_price": round(float(data['Close'].iloc[-1]), 2),
            "analysis_summary": f"Found {len(patterns_found)} key candlestick patterns in recent trading sessions"
        }
        
    except Exception as e:
        return {"error": str(e)}

def _create_comprehensive_chart(data: pd.DataFrame, symbol: str, analysis: dict) -> str:
    """Create a beautiful comprehensive technical analysis chart."""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12), facecolor='#1e1e1e')
    
    # Create grid layout
    gs = fig.add_gridspec(4, 2, height_ratios=[3, 1, 1, 1], hspace=0.3, wspace=0.2)
    
    # Main price chart with moving averages and Bollinger Bands
    ax1 = fig.add_subplot(gs[0, :])
    
    # Plot candlestick-style price chart
    dates = data.index
    opens = data['Open'].values
    highs = data['High'].values
    lows = data['Low'].values
    closes = data['Close'].values
    
    # Candlestick colors
    up = closes >= opens
    down = ~up
    
    # Plot candlesticks
    ax1.bar(dates[up], closes[up] - opens[up], bottom=opens[up], color='#00ff88', alpha=0.8, width=0.8)
    ax1.bar(dates[down], opens[down] - closes[down], bottom=closes[down], color='#ff4444', alpha=0.8, width=0.8)
    ax1.vlines(dates[up], lows[up], highs[up], color='#00ff88', alpha=0.8, linewidth=1)
    ax1.vlines(dates[down], lows[down], highs[down], color='#ff4444', alpha=0.8, linewidth=1)
    
    # Add moving averages
    if 'SMA_20' in data.columns:
        ax1.plot(dates, data['SMA_20'], color='#ffaa00', linewidth=2, label='SMA 20', alpha=0.8)
    if 'SMA_50' in data.columns:
        ax1.plot(dates, data['SMA_50'], color='#00aaff', linewidth=2, label='SMA 50', alpha=0.8)
    if 'EMA_12' in data.columns:
        ax1.plot(dates, data['EMA_12'], color='#ff00ff', linewidth=1.5, label='EMA 12', alpha=0.7)
    
    # Add Bollinger Bands
    if all(col in data.columns for col in ['BBU_20_2.0', 'BBM_20_2.0', 'BBL_20_2.0']):
        ax1.plot(dates, data['BBU_20_2.0'], color='#888888', linewidth=1, alpha=0.6)
        ax1.plot(dates, data['BBM_20_2.0'], color='#888888', linewidth=1, alpha=0.6)
        ax1.plot(dates, data['BBL_20_2.0'], color='#888888', linewidth=1, alpha=0.6)
        ax1.fill_between(dates, data['BBU_20_2.0'], data['BBL_20_2.0'], alpha=0.1, color='#888888', label='Bollinger Bands')
    
    ax1.set_title(f'{symbol} - Comprehensive Technical Analysis', fontsize=16, color='white', pad=20)
    ax1.set_ylabel('Price ($)', fontsize=12, color='white')
    ax1.legend(loc='upper left', fancybox=True, framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(colors='white')
    
    # Volume chart
    ax2 = fig.add_subplot(gs[1, :])
    volume_colors = ['#00ff88' if close >= open else '#ff4444' for close, open in zip(closes, opens)]
    ax2.bar(dates, data['Volume'], color=volume_colors, alpha=0.7)
    if 'VWAP_D' in data.columns:
        ax2_twin = ax2.twinx()
        ax2_twin.plot(dates, data['VWAP_D'], color='#ffff00', linewidth=2, label='VWAP', alpha=0.8)
        ax2_twin.legend(loc='upper right')
        ax2_twin.tick_params(colors='white')
    
    ax2.set_ylabel('Volume', fontsize=12, color='white')
    ax2.tick_params(colors='white')
    ax2.grid(True, alpha=0.3)
    
    # RSI chart
    ax3 = fig.add_subplot(gs[2, 0])
    if 'RSI_14' in data.columns:
        ax3.plot(dates, data['RSI_14'], color='#ff8800', linewidth=2, label='RSI 14')
        ax3.axhline(y=70, color='#ff4444', linestyle='--', alpha=0.7, label='Overbought (70)')
        ax3.axhline(y=30, color='#00ff88', linestyle='--', alpha=0.7, label='Oversold (30)')
        ax3.fill_between(dates, 30, 70, alpha=0.1, color='#888888')
        ax3.set_ylim(0, 100)
    
    ax3.set_title('RSI (14)', fontsize=12, color='white')
    ax3.set_ylabel('RSI', fontsize=10, color='white')
    ax3.legend(fontsize=8)
    ax3.tick_params(colors='white')
    ax3.grid(True, alpha=0.3)
    
    # MACD chart
    ax4 = fig.add_subplot(gs[2, 1])
    if all(col in data.columns for col in ['MACD_12_26_9', 'MACDs_12_26_9', 'MACDh_12_26_9']):
        ax4.plot(dates, data['MACD_12_26_9'], color='#00aaff', linewidth=2, label='MACD')
        ax4.plot(dates, data['MACDs_12_26_9'], color='#ff8800', linewidth=2, label='Signal')
        
        # MACD histogram
        macd_hist = data['MACDh_12_26_9']
        colors = ['#00ff88' if x >= 0 else '#ff4444' for x in macd_hist]
        ax4.bar(dates, macd_hist, color=colors, alpha=0.6, label='Histogram')
        ax4.axhline(y=0, color='white', linewidth=0.5)
    
    ax4.set_title('MACD', fontsize=12, color='white')
    ax4.set_ylabel('MACD', fontsize=10, color='white')
    ax4.legend(fontsize=8)
    ax4.tick_params(colors='white')
    ax4.grid(True, alpha=0.3)
    
    # ADX and Aroon chart
    ax5 = fig.add_subplot(gs[3, 0])
    if 'ADX_14' in data.columns:
        ax5.plot(dates, data['ADX_14'], color='#ffffff', linewidth=2, label='ADX')
        ax5.axhline(y=25, color='#ffaa00', linestyle='--', alpha=0.7, label='Strong Trend (25)')
    if all(col in data.columns for col in ['AROONU_14', 'AROOND_14']):
        ax5.plot(dates, data['AROONU_14'], color='#00ff88', linewidth=1.5, label='Aroon Up', alpha=0.8)
        ax5.plot(dates, data['AROOND_14'], color='#ff4444', linewidth=1.5, label='Aroon Down', alpha=0.8)
    
    ax5.set_title('ADX & Aroon', fontsize=12, color='white')
    ax5.set_ylabel('Value', fontsize=10, color='white')
    ax5.legend(fontsize=8)
    ax5.tick_params(colors='white')
    ax5.grid(True, alpha=0.3)
    ax5.set_ylim(0, 100)
    
    # Stochastic chart
    ax6 = fig.add_subplot(gs[3, 1])
    if all(col in data.columns for col in ['STOCHk_14_3_3', 'STOCHd_14_3_3']):
        ax6.plot(dates, data['STOCHk_14_3_3'], color='#00aaff', linewidth=2, label='%K')
        ax6.plot(dates, data['STOCHd_14_3_3'], color='#ff8800', linewidth=2, label='%D')
        ax6.axhline(y=80, color='#ff4444', linestyle='--', alpha=0.7)
        ax6.axhline(y=20, color='#00ff88', linestyle='--', alpha=0.7)
        ax6.fill_between(dates, 20, 80, alpha=0.1, color='#888888')
        ax6.set_ylim(0, 100)
    
    ax6.set_title('Stochastic', fontsize=12, color='white')
    ax6.set_ylabel('Value', fontsize=10, color='white')
    ax6.set_xlabel('Date', fontsize=10, color='white')
    ax6.legend(fontsize=8)
    ax6.tick_params(colors='white')
    ax6.grid(True, alpha=0.3)
    
    # Format x-axis for all subplots
    for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        if ax != ax6:  # Don't show x-axis labels except on bottom
            ax.set_xticklabels([])
        ax.set_facecolor('#2e2e2e')
        
        # Add subtle border
        for spine in ax.spines.values():
            spine.set_color('#555555')
            spine.set_linewidth(1)
    
    plt.suptitle(f'{symbol} Technical Analysis Dashboard', fontsize=18, color='white', y=0.98)
    
    # Add current price and change info
    current_price = analysis["current_price"]
    price_change = analysis["price_change"]
    price_change_pct = analysis["price_change_percent"]
    color = '#00ff88' if price_change >= 0 else '#ff4444'
    
    fig.text(0.02, 0.95, f'Current: ${current_price}', fontsize=14, color='white', weight='bold')
    fig.text(0.02, 0.92, f'Change: ${price_change:+.2f} ({price_change_pct:+.2f}%)', 
             fontsize=12, color=color, weight='bold')
    
    plt.tight_layout()
    return _create_chart_base64(fig)

def _create_pattern_chart(data: pd.DataFrame, symbol: str, patterns_found: list) -> str:
    """Create a beautiful candlestick pattern chart."""
    
    fig = plt.figure(figsize=(16, 10), facecolor='#1e1e1e')
    ax = plt.subplot(111)
    
    # Plot candlestick chart
    dates = data.index
    opens = data['Open'].values
    highs = data['High'].values
    lows = data['Low'].values
    closes = data['Close'].values
    
    up = closes >= opens
    down = ~up
    
    # Candlesticks
    ax.bar(dates[up], closes[up] - opens[up], bottom=opens[up], 
           color='#00ff88', alpha=0.8, width=0.8, label='Bullish')
    ax.bar(dates[down], opens[down] - closes[down], bottom=closes[down], 
           color='#ff4444', alpha=0.8, width=0.8, label='Bearish')
    ax.vlines(dates[up], lows[up], highs[up], color='#00ff88', alpha=0.8, linewidth=1)
    ax.vlines(dates[down], lows[down], highs[down], color='#ff4444', alpha=0.8, linewidth=1)
    
    # Mark patterns
    for pattern in patterns_found[-10:]:  # Show last 10 patterns
        pattern_date = pd.to_datetime(pattern["date"])
        if pattern_date in dates:
            pattern_price = pattern["price"]
            color = '#00ff88' if pattern["signal"] == "BULLISH" else '#ff4444'
            ax.annotate(pattern["pattern"], 
                       xy=(pattern_date, pattern_price), 
                       xytext=(10, 20), 
                       textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color=color),
                       fontsize=8, color='white', weight='bold')
    
    ax.set_title(f'{symbol} - Candlestick Patterns Analysis', fontsize=16, color='white', pad=20)
    ax.set_ylabel('Price ($)', fontsize=12, color='white')
    ax.set_xlabel('Date', fontsize=12, color='white')
    ax.grid(True, alpha=0.3)
    ax.tick_params(colors='white')
    ax.set_facecolor('#2e2e2e')
    
    for spine in ax.spines.values():
        spine.set_color('#555555')
    
    plt.tight_layout()
    return _create_chart_base64(fig)
