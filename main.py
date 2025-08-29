# main.py
# Pattern Detector V8.0 - Main Streamlit Application

import streamlit as st
import pandas as pd
from datetime import datetime

# Import our modules
from config import *
from data_handler import fetch_and_process_data, check_data_availability, get_timeframe_info
from pattern_detectors import detect_pattern
from market_timing import get_market_context, display_market_context, adjust_confidence_for_timing
from risk_calculator import calculate_levels
from chart_generator import create_chart

# Configure Streamlit
st.set_page_config(
    page_title=APP_TITLE,
    layout="wide"
)

def main():
    st.title(APP_TITLE)
    st.markdown(f"**{APP_SUBTITLE}** - {VERSION}")
    
    # Check data availability
    data_status = check_data_availability()
    if data_status['demo_mode']:
        st.warning(data_status['message'])
    
    # Disclaimer
    st.error(DISCLAIMER_TEXT)
    
    # Market Timing Context Display
    market_context = display_market_context()
    
    # Info about modular architecture
    with st.expander("What's New in v8.0 - Modular Architecture"):
        st.markdown("""
        ### Modular Design Benefits
        
        **Clean Code Organization**:
        - Separated into focused modules (config, data, patterns, charts, etc.)
        - Each file has a single, clear responsibility
        - Easy to maintain and enhance individual features
        
        **Enhanced Maintainability**:
        - All settings centralized in config.py
        - Pattern detection algorithms in dedicated module
        - Chart generation and risk calculations separated
        - Market timing logic isolated for easy updates
        
        **Developer-Friendly**:
        - No more 1000+ line files
        - Easy to test individual components
        - Simple to add new patterns or features
        - Clear imports and dependencies
        
        **All Previous Features Maintained**:
        - Inside Bar pattern with triple targets
        - Multi-timeframe support (Daily/Weekly)
        - Volume confirmation system
        - Market timing adjustments
        - Enhanced risk/reward calculations
        
        This architecture makes future enhancements much more manageable and maintainable.
        """)
    
    # Sidebar Configuration
    st.sidebar.header("Configuration")
    
    # Pattern Selection
    selected_patterns = st.sidebar.multiselect(
        "Select Patterns:", 
        PATTERNS, 
        default=DEFAULT_PATTERNS
    )
    
    # Ticker Input
    tickers = st.sidebar.text_input("Tickers:", "AAPL,MSFT,NVDA")
    
    # Period Selection
    period_display = st.sidebar.selectbox(
        "Period:", 
        PERIOD_OPTIONS, 
        index=PERIOD_OPTIONS.index(DEFAULT_PERIOD)
    )
    period = "1wk" if period_display == "1wk (Weekly)" else period_display
    
    # Confidence Threshold
    min_confidence = st.sidebar.slider(
        "Min Confidence:", 
        MIN_CONFIDENCE_RANGE[0], 
        MIN_CONFIDENCE_RANGE[1], 
        DEFAULT_MIN_CONFIDENCE
    )
    
    # Volume Filters
    st.sidebar.subheader("Volume Filters")
    require_volume = st.sidebar.checkbox("Require Volume Confirmation", value=False)
    volume_threshold = st.sidebar.selectbox(
        "Volume Threshold:", 
        ["1.3x (Good)", "1.5x (Strong)", "2.0x (Exceptional)"], 
        index=0
    )
    
    # Timing Filters
    st.sidebar.subheader("Timing Filters")
    show_timing_adjustments = st.sidebar.checkbox("Show Timing Adjustments", value=True)
    
    # Analysis Button
    if st.sidebar.button("Analyze", type="primary"):
        if tickers and selected_patterns:
            run_analysis(
                tickers, selected_patterns, period, period_display, min_confidence,
                require_volume, volume_threshold, show_timing_adjustments, market_context
            )
        else:
            st.error("Please enter tickers and select at least one pattern.")

def run_analysis(tickers, selected_patterns, period, period_display, min_confidence,
                require_volume, volume_threshold, show_timing_adjustments, market_context):
    """Run the pattern analysis"""
    
    ticker_list = [t.strip().upper() for t in tickers.split(',')]
    timeframe_info = get_timeframe_info(period)
    
    st.header("Pattern Analysis Results")
    results = []
    
    for ticker in ticker_list:
        st.subheader(f"{ticker}")
        
        # Fetch and process data
        data, summary, status_message = fetch_and_process_data(ticker, period)
        
        if data is None:
            st.error(f"⏸ {status_message}")
            continue
        
        # Analyze each selected pattern
        for pattern in selected_patterns:
            detected, confidence, info = detect_pattern(data, pattern, market_context, period)
            
            # Apply timing adjustments
            confidence, info = adjust_confidence_for_timing(confidence, info, market_context)
            
            # Apply volume filter
            skip_pattern = False
            if require_volume:
                volume_multiplier = info.get('volume_multiplier', 0)
                threshold_map = {"1.3x (Good)": 1.3, "1.5x (Strong)": 1.5, "2.0x (Exceptional)": 2.0}
                required_threshold = threshold_map[volume_threshold]
                
                if volume_multiplier < required_threshold:
                    skip_pattern = True
                    st.info(f"{pattern}: {confidence:.0f}% - Filtered by volume requirement")
                    continue
            
            if detected and confidence >= min_confidence:
                # Calculate trading levels
                levels = calculate_levels(data, info, pattern)
                
                # Display results
                display_pattern_results(
                    ticker, pattern, confidence, info, levels, data, 
                    market_context, period, show_timing_adjustments, timeframe_info
                )
                
                # Add to results
                result_dict = create_result_dict(
                    ticker, pattern, confidence, info, levels, timeframe_info
                )
                results.append(result_dict)
                
            else:
                if not skip_pattern:
                    st.info(f"⏸ {pattern}: {confidence:.0f}% (below threshold)")
    
    # Display summary
    if results:
        display_summary(results, market_context)
    else:
        st.info("📊 No patterns detected. Try lowering the confidence threshold or adjusting volume filters.")

def display_pattern_results(ticker, pattern, confidence, info, levels, data, 
                           market_context, period, show_timing_adjustments, timeframe_info):
    """Display individual pattern results"""
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Confidence display
        if confidence >= 80:
            st.success(f"{pattern} DETECTED")
        elif confidence >= 70:
            st.success(f"{pattern} DETECTED")
        else:
            st.info(f"{pattern} DETECTED")
        
        # Display timing-adjusted confidence
        if show_timing_adjustments and 'timing_adjusted_confidence' in info:
            original_conf = info['original_confidence']
            adjusted_conf = info['timing_adjusted_confidence']
            if abs(original_conf - adjusted_conf) > 0.5:
                st.metric("Confidence", f"{confidence:.0f}%", 
                         f"{adjusted_conf - original_conf:+.0f}% (timing)")
            else:
                st.metric("Confidence", f"{confidence:.0f}%")
        else:
            st.metric("Confidence", f"{confidence:.0f}%")
        
        # Volume status
        display_volume_status(info)
        
        # Show confidence capping and timing adjustments
        display_adjustments(info, show_timing_adjustments)
        
        # Trading levels
        display_trading_levels(levels)
        
    with col2:
        # Pattern and market information
        display_pattern_info(pattern, info, levels, market_context)
    
    # Create and display chart
    fig = create_chart(data, ticker, pattern, info, levels, market_context, period)
    st.plotly_chart(fig, use_container_width=True)

def display_volume_status(info):
    """Display volume status with appropriate styling"""
    volume_status = info.get('volume_status', 'Unknown')
    if info.get('exceptional_volume'):
        st.success(f"{volume_status}")
    elif info.get('strong_volume'):
        st.success(f"{volume_status}")
    elif info.get('good_volume'):
        st.info(f"{volume_status}")
    else:
        st.warning(f"{volume_status}")

def display_adjustments(info, show_timing_adjustments):
    """Display confidence adjustments"""
    if info.get('confidence_capped'):
        st.warning(f"Capped: {info['confidence_capped']}")
    
    if show_timing_adjustments and 'timing_adjustments' in info:
        with st.expander("Timing Details"):
            for adjustment in info['timing_adjustments']:
                st.write(f"• {adjustment}")
    
    # Special warnings
    if info.get('friday_risk'):
        st.warning(f"{info['friday_risk']}")
    if info.get('monday_gap_check'):
        st.info(f"{info['monday_gap_check']}")

def display_trading_levels(levels):
    """Display trading levels"""
    st.write("**Trading Levels:**")
    st.write(f"**Entry**: ${levels['entry']:.2f}")
    st.write(f"**Stop**: ${levels['stop']:.2f}")
    st.write(f"**Target 1**: ${levels['target1']:.2f}")
    st.write(f"**Target 2**: ${levels['target2']:.2f}")
    if levels.get('has_target3'):
        st.write(f"**Target 3**: ${levels['target3']:.2f}")
    
    st.write("**Risk/Reward:**")
    st.write(f"**T1 R/R**: {levels['rr_ratio1']:.1f}:1")
    st.write(f"**T2 R/R**: {levels['rr_ratio2']:.1f}:1")
    if levels.get('has_target3'):
        st.write(f"**T3 R/R**: {levels['rr_ratio3']:.1f}:1")
    
    st.info(f"**Method**: {levels['target_method']}")

def display_pattern_info(pattern, info, levels, market_context):
    """Display pattern-specific information"""
    # Market timing context
    st.write("**Market Context:**")
    st.write(f"• **Gap Risk**: {market_context['gap_risk']}")
    st.write(f"• **Entry Timing**: {market_context['entry_timing']}")
    
    # Pattern-specific information
    if pattern == "Inside Bar":
        display_inside_bar_info(info, levels)
    else:
        display_standard_pattern_info(info, levels)
    
    # Technical indicators
    display_technical_info(info)

def display_inside_bar_info(info, levels):
    """Display Inside Bar specific information"""
    if info.get('single_inside_bar'):
        st.write("Single inside bar (preferred)")
    elif info.get('double_inside_bar'):
        st.write("Double inside bar")
    if info.get('size_ratio'):
        st.write(f"Consolidation: {info['size_ratio']}")
    if info.get('tight_consolidation'):
        st.success("Tight consolidation")
    if info.get('color_validated'):
        st.success("Mother Bar: Green | Inside Bar: Red")
    st.success("**Triple Targets**: T1 Mother Bar, T2 +13%, T3 +21%")

def display_standard_pattern_info(info, levels):
    """Display information for standard patterns"""
    if info.get('initial_ascension'):
        st.write(f"🚀 Initial rise: {info['initial_ascension']}")
    if info.get('flagpole_gain'):
        st.write(f"🚀 Flagpole: {info['flagpole_gain']}")
        st.success(f"🎯 **Measured Move**: ${levels['reward1']:.2f}")
    if info.get('cup_depth'):
        st.write(f"☕ Cup depth: {info['cup_depth']}")
        st.success(f"🎯 **Measured Move**: ${levels['reward1']:.2f}")

def display_technical_info(info):
    """Display technical indicator information"""
    if info.get('macd_bullish'):
        st.write("📈 MACD bullish")
    if info.get('momentum_recovering'):
        st.write("📈 Momentum recovering")
    if info.get('near_breakout'):
        st.write("🎯 Near breakout")

def create_result_dict(ticker, pattern, confidence, info, levels, timeframe_info):
    """Create result dictionary for summary table"""
    timing_status = f"{info.get('day', 'Unknown')} ({info.get('gap_risk', 'Unknown')} Gap Risk)"
    
    result_dict = {
        'Ticker': ticker,
        'Pattern': pattern,
        'Timeframe': timeframe_info['display_name'],
        'Confidence': f"{confidence:.0f}%",
        'Volume': info.get('volume_status', 'Unknown'),
        'Entry': f"${levels['entry']:.2f}",
        'Stop': f"${levels['stop']:.2f}",
        'Target 1': f"${levels['target1']:.2f}",
        'Target 2': f"${levels['target2']:.2f}",
        'R/R 1': f"{levels['rr_ratio1']:.1f}:1",
        'R/R 2': f"{levels['rr_ratio2']:.1f}:1",
        'Risk': f"${levels['risk']:.2f}",
        'Method': levels['target_method']
    }
    
    # Add Target 3 for Inside Bar patterns
    if levels.get('has_target3'):
        result_dict['Target 3'] = f"${levels['target3']:.2f}"
        result_dict['R/R 3'] = f"{levels['rr_ratio3']:.1f}:1"
    
    return result_dict

def display_summary(results, market_context):
    """Display analysis summary"""
    st.header("📋 Summary")
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Patterns", len(results))
    with col2:
        scores = [int(r['Confidence'].replace('%', '')) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        st.metric("Avg Confidence", f"{avg_score:.0f}%")
    with col3:
        if results:
            ratios = [float(r['R/R 1'].split(':')[0]) for r in results]
            avg_rr = sum(ratios) / len(ratios) if ratios else 0
            st.metric("Avg R/R T1", f"{avg_rr:.1f}:1")
    with col4:
        high_vol_count = sum(1 for r in results if 'Strong' in r['Volume'] or 'Exceptional' in r['Volume'])
        vol_quality = (high_vol_count / len(results)) * 100 if results else 0
        st.metric("High Volume %", f"{vol_quality:.0f}%")
    with col5:
        # This would need market timing info passed through
        st.metric("Patterns Found", len(results))
    
    # Pattern distribution
    if len(results) > 1:
        display_pattern_distribution(results)
    
    # Download results
    csv = df.to_csv(index=False)
    filename = EXPORT_FILENAME_FORMAT.format(timestamp=datetime.now().strftime('%Y%m%d_%H%M'))
    st.download_button(
        "📥 Download Results",
        csv,
        filename,
        "text/csv"
    )

def display_pattern_distribution(results):
    """Display pattern distribution statistics"""
    st.subheader("📊 Pattern Distribution")
    pattern_counts = {}
    timeframe_counts = {}
    
    for result in results:
        pattern = result['Pattern']
        timeframe = result['Timeframe']
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        timeframe_counts[timeframe] = timeframe_counts.get(timeframe, 0) + 1
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**By Pattern:**")
        for pattern, count in pattern_counts.items():
            pct = (count / len(results)) * 100
            st.write(f"• {pattern}: {count} ({pct:.0f}%)")
    
    with col2:
        st.write("**By Timeframe:**")
        for timeframe, count in timeframe_counts.items():
            pct = (count / len(results)) * 100
            st.write(f"• {timeframe}: {count} ({pct:.0f}%)")

if __name__ == "__main__":
    main()
