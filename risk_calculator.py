# risk_calculator.py
# Pattern Detector V8.0 - Trading Level Calculations

from config import (
    RISK_MULTIPLIERS, MIN_RISK_REWARD_RATIOS, INSIDE_BAR_CONFIG
)

def calculate_levels(data, pattern_info, pattern_type):
    """Calculate entry, stop, targets using MEASURED MOVES"""
    current_price = data['Close'].iloc[-1]
    recent_range = data['High'].tail(20) - data['Low'].tail(20)
    avg_range = recent_range.mean()
    volatility_stop_distance = avg_range * RISK_MULTIPLIERS['volatility_stop']
    
    if pattern_type == "Inside Bar":
        return calculate_inside_bar_levels(pattern_info, current_price)
    elif pattern_type == "Flat Top Breakout":
        return calculate_flat_top_levels(data, pattern_info, current_price, volatility_stop_distance)
    elif pattern_type == "Bull Flag":
        return calculate_bull_flag_levels(data, pattern_info, current_price, volatility_stop_distance)
    elif pattern_type == "Cup Handle":
        return calculate_cup_handle_levels(data, pattern_info, current_price, volatility_stop_distance)
    else:
        return calculate_default_levels(current_price, volatility_stop_distance)

def calculate_inside_bar_levels(pattern_info, current_price):
    """Inside Bar specific calculations"""
    inside_bar_high = pattern_info.get('inside_bar_high', current_price)
    inside_bar_low = pattern_info.get('inside_bar_low', current_price * 0.95)
    mother_bar_high = pattern_info.get('mother_bar_high', current_price * 1.05)
    
    # Entry: 5% above inside bar high
    entry = inside_bar_high * INSIDE_BAR_CONFIG['entry_buffer']
    
    # Stop: 5% below inside bar low
    stop = inside_bar_low * INSIDE_BAR_CONFIG['stop_buffer']
    
    # Target 1: Mother bar high
    target1 = mother_bar_high
    
    # Target 2: 13% above mother bar high
    target2 = mother_bar_high * INSIDE_BAR_CONFIG['target2_multiplier']
    
    # Target 3: 21% above mother bar high
    target3 = mother_bar_high * INSIDE_BAR_CONFIG['target3_multiplier']
    
    target_method = "Inside Bar Fixed Targets"
    
    # Calculate risk/reward
    risk_amount = entry - stop
    reward1 = target1 - entry
    reward2 = target2 - entry
    reward3 = target3 - entry
    
    return {
        'entry': entry,
        'stop': stop,
        'target1': target1,
        'target2': target2,
        'target3': target3,
        'risk': risk_amount,
        'reward1': reward1,
        'reward2': reward2,
        'reward3': reward3,
        'rr_ratio1': reward1 / risk_amount if risk_amount > 0 else 0,
        'rr_ratio2': reward2 / risk_amount if risk_amount > 0 else 0,
        'rr_ratio3': reward3 / risk_amount if risk_amount > 0 else 0,
        'target_method': target_method,
        'measured_move': True,
        'volatility_adjusted': False,
        'has_target3': True
    }

def calculate_flat_top_levels(data, pattern_info, current_price, volatility_stop_distance):
    """Flat Top Breakout specific calculations"""
    entry = pattern_info.get('resistance_level', current_price * 1.01)
    recent_low = data['Low'].tail(15).min()
    volatility_stop = entry - volatility_stop_distance
    traditional_stop = recent_low * 0.98
    stop = max(volatility_stop, traditional_stop)
    
    min_stop_distance = entry * RISK_MULTIPLIERS['min_stop_distance']['Flat Top Breakout']
    if stop >= entry:
        stop = entry - min_stop_distance
    elif (entry - stop) < min_stop_distance:
        stop = entry - min_stop_distance
    
    if 'resistance_level' in pattern_info:
        support_level = data['Low'].tail(20).max()
        triangle_height = entry - support_level
        triangle_height = max(triangle_height, entry * 0.05)
        target1 = entry + triangle_height
        target2 = entry + (triangle_height * 1.618)
    else:
        risk = entry - stop
        target1 = entry + (risk * 2.0)
        target2 = entry + (risk * 3.5)
    
    target_method = "Triangle Height Projection"
    
    return create_standard_levels_dict(entry, stop, target1, target2, target_method)

def calculate_bull_flag_levels(data, pattern_info, current_price, volatility_stop_distance):
    """Bull Flag specific calculations"""
    flag_high = data['High'].tail(15).max()
    entry = flag_high * 1.005
    flag_low = data['Low'].tail(12).min()
    volatility_stop = entry - volatility_stop_distance
    traditional_stop = flag_low * 0.98
    stop = max(volatility_stop, traditional_stop)
    
    min_stop_distance = entry * RISK_MULTIPLIERS['min_stop_distance']['Bull Flag']
    if stop >= entry:
        stop = entry - min_stop_distance
    elif (entry - stop) < min_stop_distance:
        stop = entry - min_stop_distance
    
    if 'flagpole_gain' in pattern_info:
        try:
            flagpole_pct_str = pattern_info['flagpole_gain'].replace('%', '')
            flagpole_pct = float(flagpole_pct_str) / 100
            flagpole_start_price = entry / (1 + flagpole_pct)
            flagpole_height = entry - flagpole_start_price
            flagpole_height = max(flagpole_height, entry * 0.08)
            target1 = entry + flagpole_height
            target2 = entry + (flagpole_height * 1.382)
        except (ValueError, KeyError):
            risk = entry - stop
            target1 = entry + (risk * 2.5)
            target2 = entry + (risk * 4.0)
    else:
        risk = entry - stop
        target1 = entry + (risk * 2.5)
        target2 = entry + (risk * 4.0)
    
    target_method = "Flagpole Height Projection"
    
    return create_standard_levels_dict(entry, stop, target1, target2, target_method)

def calculate_cup_handle_levels(data, pattern_info, current_price, volatility_stop_distance):
    """Cup Handle specific calculations"""
    if 'cup_depth' in pattern_info:
        try:
            cup_depth_str = pattern_info['cup_depth'].replace('%', '')
            cup_depth_pct = float(cup_depth_str) / 100
            estimated_rim = current_price / (1 - cup_depth_pct * 0.3)
            entry = estimated_rim * 1.005
        except (ValueError, KeyError):
            entry = current_price * 1.02
    else:
        entry = current_price * 1.02
    
    handle_low = data.tail(15)['Low'].min()
    volatility_stop = entry - volatility_stop_distance
    traditional_stop = handle_low * 0.97
    stop = max(volatility_stop, traditional_stop)
    
    min_stop_distance = entry * RISK_MULTIPLIERS['min_stop_distance']['Cup Handle']
    if stop >= entry:
        stop = entry - min_stop_distance
    elif (entry - stop) < min_stop_distance:
        stop = entry - min_stop_distance
    
    if 'cup_depth' in pattern_info:
        try:
            cup_depth_str = pattern_info['cup_depth'].replace('%', '')
            cup_depth_pct = float(cup_depth_str) / 100
            cup_depth_dollars = entry * cup_depth_pct
            cup_depth_dollars = max(cup_depth_dollars, entry * 0.10)
            target1 = entry + cup_depth_dollars
            target2 = entry + (cup_depth_dollars * 1.618)
        except (ValueError, KeyError):
            risk = entry - stop
            target1 = entry + (risk * 2.0)
            target2 = entry + (risk * 3.0)
    else:
        risk = entry - stop
        target1 = entry + (risk * 2.0)
        target2 = entry + (risk * 3.0)
    
    target_method = "Cup Depth Projection"
    
    return create_standard_levels_dict(entry, stop, target1, target2, target_method)

def calculate_default_levels(current_price, volatility_stop_distance):
    """Default calculation for unknown pattern types"""
    entry = current_price * 1.01
    stop = current_price * 0.95
    target1 = entry + (entry - stop) * 2.0
    target2 = entry + (entry - stop) * 3.0
    target_method = "Traditional 2:1 & 3:1"
    
    return create_standard_levels_dict(entry, stop, target1, target2, target_method)

def create_standard_levels_dict(entry, stop, target1, target2, target_method):
    """Create standard levels dictionary for non-Inside Bar patterns"""
    risk_amount = entry - stop
    reward1 = target1 - entry
    reward2 = target2 - entry
    
    if risk_amount > 0:
        rr1 = reward1 / risk_amount
        rr2 = reward2 / risk_amount
        
        # Ensure minimum risk/reward ratios
        if rr1 < MIN_RISK_REWARD_RATIOS['target1']:
            target1 = entry + (risk_amount * MIN_RISK_REWARD_RATIOS['target1'])
            reward1 = target1 - entry
            rr1 = MIN_RISK_REWARD_RATIOS['target1']
        
        if rr2 < MIN_RISK_REWARD_RATIOS['target2']:
            target2 = entry + (risk_amount * MIN_RISK_REWARD_RATIOS['target2'])
            reward2 = target2 - entry
            rr2 = MIN_RISK_REWARD_RATIOS['target2']
    else:
        # Emergency fallback if risk calculation fails
        risk_amount = entry * 0.05
        stop = entry - risk_amount
        target1 = entry + (risk_amount * 2.0)
        target2 = entry + (risk_amount * 3.0)
        reward1 = target1 - entry
        reward2 = target2 - entry
        rr1 = 2.0
        rr2 = 3.0
    
    return {
        'entry': entry,
        'stop': stop,
        'target1': target1,
        'target2': target2,
        'risk': risk_amount,
        'reward1': reward1,
        'reward2': reward2,
        'rr_ratio1': reward1 / risk_amount if risk_amount > 0 else 0,
        'rr_ratio2': reward2 / risk_amount if risk_amount > 0 else 0,
        'target_method': target_method,
        'measured_move': True,
        'volatility_adjusted': True,
        'has_target3': False
    }

def validate_levels(levels):
    """Validate trading levels for consistency"""
    issues = []
    
    # Basic validation
    if levels['entry'] <= levels['stop']:
        issues.append("Entry price must be above stop loss")
    
    if levels['target1'] <= levels['entry']:
        issues.append("Target 1 must be above entry price")
    
    if levels['target2'] <= levels['target1']:
        issues.append("Target 2 must be above Target 1")
    
    # Risk/Reward validation
    if levels['rr_ratio1'] < 1.0:
        issues.append("Target 1 risk/reward ratio below 1:1")
    
    if levels['rr_ratio2'] < 2.0:
        issues.append("Target 2 risk/reward ratio below 2:1")
    
    # Inside Bar specific validation
    if levels.get('has_target3'):
        if levels['target3'] <= levels['target2']:
            issues.append("Target 3 must be above Target 2")
        if levels['rr_ratio3'] < 2.5:
            issues.append("Target 3 risk/reward ratio below 2.5:1")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues
    }

def calculate_position_size(levels, account_size, risk_percentage=2.0):
    """Calculate position size based on risk management"""
    risk_amount = levels['risk']
    max_loss = account_size * (risk_percentage / 100)
    
    if risk_amount > 0:
        shares = int(max_loss / risk_amount)
        position_value = shares * levels['entry']
        
        return {
            'shares': shares,
            'position_value': position_value,
            'risk_amount': risk_amount * shares,
            'risk_percentage_actual': (risk_amount * shares / account_size) * 100,
            'max_loss': max_loss
        }
    
    return None

def get_level_summary(levels):
    """Generate a summary of trading levels"""
    summary = {
        'entry_price': f"${levels['entry']:.2f}",
        'stop_loss': f"${levels['stop']:.2f}",
        'risk_amount': f"${levels['risk']:.2f}",
        'risk_percentage': f"{(levels['risk'] / levels['entry']) * 100:.1f}%",
        'target1': {
            'price': f"${levels['target1']:.2f}",
            'reward': f"${levels['reward1']:.2f}",
            'rr_ratio': f"{levels['rr_ratio1']:.1f}:1"
        },
        'target2': {
            'price': f"${levels['target2']:.2f}",
            'reward': f"${levels['reward2']:.2f}",
            'rr_ratio': f"{levels['rr_ratio2']:.1f}:1"
        },
        'method': levels['target_method']
    }
    
    if levels.get('has_target3'):
        summary['target3'] = {
            'price': f"${levels['target3']:.2f}",
            'reward': f"${levels['reward3']:.2f}",
            'rr_ratio': f"{levels['rr_ratio3']:.1f}:1"
        }
    
    return summary
