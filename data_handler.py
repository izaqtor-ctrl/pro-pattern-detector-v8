# data_handler.py
# Pattern Detector V8.0 - Data Fetching and Processing

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from config import DEMO_DATA_CONFIG, ERROR_MESSAGES, WARNING_MESSAGES

warnings.filterwarnings('ignore')

# Try to import yfinance with error handling
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

def create_demo_data(ticker, period):
    """Create realistic demo data when yfinance is not available"""
    if period == "1wk":
        days_map = {"1y": 52, "6mo": 26, "3mo": 13, "1mo": 4}
        freq = 'W'
    else:
        days_map = {"1y": 252, "6mo": 126, "3mo": 63, "1mo": 22}
        freq = 'D'
    
    days = days_map.get(period.replace("1wk", "1y"), 63)
    dates = pd.date_range(end=datetime.now(), periods=days, freq=freq)
    
    # Create reproducible but varied data per ticker
    np.random.seed(hash(ticker) % 2147483647)
    base_price = np.random.randint(
        DEMO_DATA_CONFIG["base_price_range"][0], 
        DEMO_DATA_CONFIG["base_price_range"][1]
    )
    
    # Generate realistic price movements
    returns = np.random.normal(0.001, DEMO_DATA_CONFIG["volatility"], days)
    returns[0] = 0
    
    close_prices = base_price * np.cumprod(1 + returns)
    
    # Generate OHLC data with realistic relationships
    high_mult = 1 + np.abs(np.random.normal(0, 0.01, days))
    low_mult = 1 - np.abs(np.random.normal(0, 0.01, days))
    open_mult = 1 + np.random.normal(0, 0.005, days)
    
    data = pd.DataFrame({
        'Open': close_prices * open_mult,
        'High': close_prices * high_mult,
        'Low': close_prices * low_mult,
        'Close': close_prices,
        'Volume': np.random.randint(
            DEMO_DATA_CONFIG["volume_range"][0], 
            DEMO_DATA_CONFIG["volume_range"][1], 
            days
        )
    }, index=dates)
    
    # Ensure OHLC relationships are correct
    data['High'] = np.maximum.reduce([data['Open'], data['High'], data['Low'], data['Close']])
    data['Low'] = np.minimum.reduce([data['Open'], data['High'], data['Low'], data['Close']])
    
    return data

def get_stock_data(ticker, period):
    """Fetch stock data with fallback to demo data"""
    if not YFINANCE_AVAILABLE:
        return create_demo_data(ticker, period), "demo"
    
    try:
        stock = yf.Ticker(ticker)
        
        # Handle weekly data
        if period == "1wk":
            data = stock.history(period="1y", interval="1wk")
        else:
            data = stock.history(period=period)
            
        if len(data) == 0:
            return create_demo_data(ticker, period), "demo"
        
        return data, "real"
        
    except Exception as e:
        return create_demo_data(ticker, period), "demo"

def calculate_rsi(data, period=14):
    """Calculate RSI (Relative Strength Index)"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    ema_fast = data['Close'].ewm(span=fast).mean()
    ema_slow = data['Close'].ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def add_technical_indicators(data):
    """Add all technical indicators to the dataset"""
    # RSI
    data['RSI'] = calculate_rsi(data)
    
    # MACD
    macd_line, signal_line, histogram = calculate_macd(data)
    data['MACD'] = macd_line
    data['MACD_Signal'] = signal_line
    data['MACD_Histogram'] = histogram
    
    # Moving averages
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    
    # Volume indicators
    data['Volume_SMA20'] = data['Volume'].rolling(window=20).mean()
    data['Volume_Ratio'] = data['Volume'] / data['Volume_SMA20']
    
    return data

def validate_data_quality(data, ticker):
    """Validate data quality and return status"""
    if data is None or len(data) == 0:
        return False, f"No data available for {ticker}"
    
    if len(data) < 10:
        return False, f"Insufficient data for {ticker} (only {len(data)} periods)"
    
    # Check for required columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        return False, f"Missing required columns for {ticker}: {missing_columns}"
    
    # Check for null values in recent data
    recent_data = data.tail(20)
    if recent_data[required_columns].isnull().any().any():
        return False, f"Missing values in recent data for {ticker}"
    
    # Check for unrealistic values
    if (recent_data['High'] < recent_data['Low']).any():
        return False, f"Data integrity error for {ticker}: High < Low"
    
    if (recent_data['Volume'] <= 0).any():
        return False, f"Invalid volume data for {ticker}"
    
    return True, "Data quality OK"

def get_data_summary(data, ticker, data_source):
    """Generate data summary for display"""
    if data is None or len(data) == 0:
        return None
    
    summary = {
        'ticker': ticker,
        'source': data_source,
        'periods': len(data),
        'date_range': f"{data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}",
        'current_price': data['Close'].iloc[-1],
        'price_change': data['Close'].iloc[-1] - data['Close'].iloc[-2] if len(data) > 1 else 0,
        'avg_volume': data['Volume'].tail(20).mean(),
        'current_volume': data['Volume'].iloc[-1]
    }
    
    return summary

def fetch_and_process_data(ticker, period):
    """Main function to fetch and process data for a ticker"""
    # Fetch raw data
    data, source = get_stock_data(ticker, period)
    
    # Validate data quality
    is_valid, status_message = validate_data_quality(data, ticker)
    
    if not is_valid:
        return None, None, status_message
    
    # Add technical indicators
    data = add_technical_indicators(data)
    
    # Generate summary
    summary = get_data_summary(data, ticker, source)
    
    return data, summary, status_message

def get_timeframe_info(period):
    """Get timeframe information for display and processing"""
    if period == "1wk":
        return {
            'display_name': 'Weekly',
            'frequency': 'weekly',
            'lookback_multiplier': 1.5,  # Weekly patterns need longer lookback
            'aging_threshold_multiplier': 1.3
        }
    else:
        return {
            'display_name': 'Daily',
            'frequency': 'daily', 
            'lookback_multiplier': 1.0,
            'aging_threshold_multiplier': 1.0
        }

def check_data_availability():
    """Check if yfinance is available and return status"""
    return {
        'yfinance_available': YFINANCE_AVAILABLE,
        'demo_mode': not YFINANCE_AVAILABLE,
        'message': WARNING_MESSAGES["demo_mode"] if not YFINANCE_AVAILABLE else "Real-time data available"
    }
