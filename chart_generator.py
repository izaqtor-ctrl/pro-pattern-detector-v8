# chart_generator.py
# Pattern Detector V8.0 - Chart Creation Functions

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from config import CHART_CONFIG

def create_chart(data, ticker, pattern_type, pattern_info, levels, market_context, timeframe):
    """Create enhanced chart with volume analysis and timing context"""
    timeframe_label = "Weekly" if timeframe == "1wk" else "Daily"
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            f'{ticker} - {pattern_type} ({timeframe_label}) | {levels["target_method"]} | {market_context["day"]}',
            'MACD Analysis', 
            'Volume Profile (20-Period Average)'
        ),
        vertical_spacing=0.05,
        row_heights=[0.6, 0.25, 0.15]
    )
    
    # Add candlestick chart
    add_candlestick_chart(fig, data)
    
    # Add moving average
    add_moving_averages(fig, data)
    
    # Add trading levels
    add_trading_levels(fig, levels)
    
    # Add pattern-specific annotations
    add_pattern_annotations(fig, data, pattern_type, pattern_info, levels)
    
    # Add market timing annotations
    add_timing_annotations(fig, data, market_context, levels)
    
    # Add volume status annotation
    add_volume_annotations(fig, data, pattern_info, levels)
    
    # Add MACD chart
    add_macd_chart(fig, data, pattern_info)
    
    # Add volume chart
    add_volume_chart(fig, data)
    
    # Configure layout
    configure_chart_layout(fig)
    
    return fig

def add_candlestick_chart(fig, data):
    """Add candlestick chart to figure"""
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price'
        ),
        row=1, col=1
    )

def add_moving_averages(fig, data):
    """Add moving averages to chart"""
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=data['SMA20'], 
            name='SMA 20', 
            line=dict(color=CHART_CONFIG['line_colors']['sma'], width=1)
        ),
        row=1, col=1
    )

def add_trading_levels(fig, levels):
    """Add trading levels to chart"""
    # Entry level
    fig.add_hline(
        y=levels['entry'], 
        line_color=CHART_CONFIG['line_colors']['entry'], 
        line_width=2,
        annotation_text=f"Entry: ${levels['entry']:.2f}", 
        row=1, col=1
    )
    
    # Stop level
    fig.add_hline(
        y=levels['stop'], 
        line_color=CHART_CONFIG['line_colors']['stop'], 
        line_width=2,
        annotation_text=f"Stop: ${levels['stop']:.2f}", 
        row=1, col=1
    )
    
    # Target levels
    fig.add_hline(
        y=levels['target1'], 
        line_color=CHART_CONFIG['line_colors']['target1'], 
        line_width=2,
        annotation_text=f"Target 1: ${levels['target1']:.2f} ({levels['rr_ratio1']:.1f}:1)", 
        row=1, col=1
    )
    
    fig.add_hline(
        y=levels['target2'], 
        line_color=CHART_CONFIG['line_colors']['target2'], 
        line_width=1,
        annotation_text=f"Target 2: ${levels['target2']:.2f} ({levels['rr_ratio2']:.1f}:1)", 
        row=1, col=1
    )
    
    # Add Target 3 for Inside Bar patterns
    if levels.get('has_target3'):
        fig.add_hline(
            y=levels['target3'], 
            line_color=CHART_CONFIG['line_colors']['target3'], 
            line_width=1,
            annotation_text=f"Target 3: ${levels['target3']:.2f} ({levels['rr_ratio3']:.1f}:1)", 
            row=1, col=1
        )

def add_pattern_annotations(fig, data, pattern_type, pattern_info, levels):
    """Add pattern-specific annotations to chart"""
    if pattern_type == "Inside Bar":
        add_inside_bar_annotations(fig, data, pattern_info, levels)
    elif pattern_type == "Bull Flag":
        add_bull_flag_annotations(fig, data, pattern_info, levels)
    elif pattern_type == "Cup Handle":
        add_cup_handle_annotations(fig, data, pattern_info, levels)
    elif pattern_type == "Flat Top Breakout":
        add_flat_top_annotations(fig, data, pattern_info, levels)

def add_inside_bar_annotations(fig, data, pattern_info, levels):
    """Add Inside Bar specific annotations"""
    mother_bar_high = pattern_info.get('mother_bar_high')
    mother_bar_low = pattern_info.get('mother_bar_low')
    inside_bar_high = pattern_info.get('inside_bar_high')
    inside_bar_low = pattern_info.get('inside_bar_low')
    
    if mother_bar_high and mother_bar_low:
        fig.add_hline(
            y=mother_bar_high, 
            line_color="blue", 
            line_width=1, 
            line_dash="dash",
            annotation_text=f"Mother Bar High: ${mother_bar_high:.2f}", 
            row=1, col=1
        )
        fig.add_hline(
            y=mother_bar_low, 
            line_color="blue", 
            line_width=1, 
            line_dash="dash",
            annotation_text=f"Mother Bar Low: ${mother_bar_low:.2f}", 
            row=1, col=1
        )
    
    if inside_bar_high and inside_bar_low:
        fig.add_hline(
            y=inside_bar_high, 
            line_color="yellow", 
            line_width=1, 
            line_dash="dot",
            annotation_text=f"Inside Bar High: ${inside_bar_high:.2f}", 
            row=1, col=1
        )
    
    # Consolidation annotation
    consolidation_info = f"Consolidation: {pattern_info.get('size_ratio', 'N/A')}"
    if pattern_info.get('inside_bars_count', 0) > 1:
        consolidation_info += f" | {pattern_info['inside_bars_count']} Inside Bars"
    
    fig.add_annotation(
        x=data.index[-5], 
        y=levels['target1'],
        text=consolidation_info,
        showarrow=True, 
        arrowhead=2, 
        arrowcolor="blue",
        bgcolor="rgba(0,0,255,0.1)", 
        bordercolor="blue"
    )

def add_bull_flag_annotations(fig, data, pattern_info, levels):
    """Add Bull Flag specific annotations"""
    if 'flagpole_gain' in pattern_info:
        flagpole_height = levels['reward1']
        fig.add_annotation(
            x=data.index[-5], 
            y=levels['target1'],
            text=f"Measured Move: ${flagpole_height:.2f}",
            showarrow=True, 
            arrowhead=2, 
            arrowcolor="lime",
            bgcolor="rgba(0,255,0,0.1)", 
            bordercolor="lime"
        )

def add_cup_handle_annotations(fig, data, pattern_info, levels):
    """Add Cup Handle specific annotations"""
    if 'cup_depth' in pattern_info:
        cup_move = levels['reward1']
        fig.add_annotation(
            x=data.index[-5], 
            y=levels['target1'],
            text=f"Cup Depth Move: ${cup_move:.2f}",
            showarrow=True, 
            arrowhead=2, 
            arrowcolor="lime",
            bgcolor="rgba(0,255,0,0.1)", 
            bordercolor="lime"
        )

def add_flat_top_annotations(fig, data, pattern_info, levels):
    """Add Flat Top specific annotations"""
    triangle_height = levels['reward1']
    fig.add_annotation(
        x=data.index[-5], 
        y=levels['target1'],
        text=f"Triangle Height: ${triangle_height:.2f}",
        showarrow=True, 
        arrowhead=2, 
        arrowcolor="lime",
        bgcolor="rgba(0,255,0,0.1)", 
        bordercolor="lime"
    )

def add_timing_annotations(fig, data, market_context, levels):
    """Add market timing context annotations"""
    timing_color = get_timing_color(market_context)
    
    fig.add_annotation(
        x=data.index[-15], 
        y=levels['entry'] * 0.98,
        text=f"{market_context['entry_timing']}",
        showarrow=True, 
        arrowhead=2, 
        arrowcolor=timing_color,
        bgcolor="rgba(255,255,255,0.8)", 
        bordercolor=timing_color,
        font=dict(color=timing_color, size=10)
    )

def get_timing_color(market_context):
    """Get color based on market timing context"""
    if market_context['is_weekend']:
        return 'red'
    elif market_context['is_friday']:
        return 'orange'
    elif market_context['is_monday']:
        return 'yellow'
    else:
        return 'lightgreen'

def add_volume_annotations(fig, data, pattern_info, levels):
    """Add volume status annotations"""
    volume_status = pattern_info.get('volume_status', 'Unknown Volume')
    volume_color = get_volume_color(pattern_info)
    
    fig.add_annotation(
        x=data.index[-10], 
        y=levels['entry'] * 1.02,
        text=f"{volume_status}",
        showarrow=True, 
        arrowhead=2, 
        arrowcolor=volume_color,
        bgcolor="rgba(255,255,255,0.8)", 
        bordercolor=volume_color,
        font=dict(color=volume_color, size=12)
    )

def get_volume_color(pattern_info):
    """Get color based on volume status"""
    if pattern_info.get('exceptional_volume'):
        return 'lime'
    elif pattern_info.get('strong_volume'):
        return 'orange'
    elif pattern_info.get('good_volume'):
        return 'yellow'
    else:
        return 'red'

def add_macd_chart(fig, data, pattern_info):
    """Add MACD chart to figure"""
    macd_line = pattern_info['macd_line']
    signal_line = pattern_info['signal_line']
    histogram = pattern_info['histogram']
    
    # MACD and Signal lines
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=macd_line, 
            name='MACD', 
            line=dict(color='blue')
        ), 
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=signal_line, 
            name='Signal', 
            line=dict(color='red')
        ), 
        row=2, col=1
    )
    
    # MACD Histogram
    colors = ['green' if h >= 0 else 'red' for h in histogram]
    fig.add_trace(
        go.Bar(
            x=data.index, 
            y=histogram, 
            name='Histogram', 
            marker_color=colors, 
            opacity=0.6
        ), 
        row=2, col=1
    )
    
    # Zero line
    fig.add_hline(y=0, line_color="black", row=2, col=1)

def add_volume_chart(fig, data):
    """Add volume chart with color coding"""
    volume_colors = get_volume_colors(data)
    
    # Volume bars
    fig.add_trace(
        go.Bar(
            x=data.index, 
            y=data['Volume'], 
            name='Volume', 
            marker_color=volume_colors, 
            opacity=CHART_CONFIG['volume_opacity']
        ), 
        row=3, col=1
    )
    
    # Volume moving average
    avg_volume = data['Volume'].rolling(window=20).mean()
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=avg_volume, 
            name='20-Period Avg', 
            line=dict(color='black', width=2, dash='dash')
        ), 
        row=3, col=1
    )

def get_volume_colors(data):
    """Generate volume colors based on average volume comparison"""
    volume_colors = []
    avg_volume = data['Volume'].rolling(window=20).mean()
    
    for i, vol in enumerate(data['Volume']):
        if i >= 19:  # Only color after we have 20-period average
            avg_vol = avg_volume.iloc[i]
            if vol >= avg_vol * 2.0:
                volume_colors.append(CHART_CONFIG['volume_colors']['exceptional'])
            elif vol >= avg_vol * 1.5:
                volume_colors.append(CHART_CONFIG['volume_colors']['strong'])
            elif vol >= avg_vol * 1.3:
                volume_colors.append(CHART_CONFIG['volume_colors']['good'])
            else:
                volume_colors.append(CHART_CONFIG['volume_colors']['weak'])
        else:
            volume_colors.append(CHART_CONFIG['volume_colors']['default'])
    
    return volume_colors

def configure_chart_layout(fig):
    """Configure chart layout and styling"""
    fig.update_layout(
        height=CHART_CONFIG['height'], 
        showlegend=True, 
        xaxis_rangeslider_visible=False
    )
    
    # Update y-axis titles
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="Volume", row=3, col=1)

def create_simple_price_chart(data, ticker, levels):
    """Create simple price chart without patterns (for testing)"""
    fig = go.Figure()
    
    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=ticker
        )
    )
    
    # Add basic levels
    if levels:
        fig.add_hline(y=levels['entry'], line_color="green", annotation_text=f"Entry: ${levels['entry']:.2f}")
        fig.add_hline(y=levels['stop'], line_color="red", annotation_text=f"Stop: ${levels['stop']:.2f}")
        fig.add_hline(y=levels['target1'], line_color="lime", annotation_text=f"Target: ${levels['target1']:.2f}")
    
    fig.update_layout(
        title=f"{ticker} - Price Chart",
        height=600,
        showlegend=False,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def add_support_resistance_lines(fig, data, levels=None):
    """Add basic support and resistance lines"""
    # Recent highs and lows
    recent_high = data['High'].tail(20).max()
    recent_low = data['Low'].tail(20).min()
    
    fig.add_hline(
        y=recent_high, 
        line_color="orange", 
        line_dash="dot", 
        opacity=0.5,
        annotation_text=f"Recent High: ${recent_high:.2f}"
    )
    
    fig.add_hline(
        y=recent_low, 
        line_color="purple", 
        line_dash="dot", 
        opacity=0.5,
        annotation_text=f"Recent Low: ${recent_low:.2f}"
    )
    
    return fig
