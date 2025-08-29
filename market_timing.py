# market_timing.py
# Pattern Detector V8.0 - Market Context and Timing Analysis

import streamlit as st
from datetime import datetime
from config import MARKET_TIMING_ADJUSTMENTS

def get_market_context():
    """Get current market timing context and trading recommendations"""
    current_time = datetime.now()
    current_day = current_time.strftime('%A')
    current_hour = current_time.hour
    
    context = {
        'day': current_day,
        'hour': current_hour,
        'is_weekend': current_day in ['Saturday', 'Sunday'],
        'is_friday': current_day == 'Friday',
        'is_monday': current_day == 'Monday',
        'is_midweek': current_day in ['Tuesday', 'Wednesday', 'Thursday'],
        'market_hours': 9 <= current_hour <= 16,
        'pre_market': 4 <= current_hour < 9,
        'after_market': 16 < current_hour <= 20
    }
    
    # Generate timing recommendations
    if context['is_weekend']:
        context['warning'] = "Weekend Analysis: Patterns based on Friday's close. Monitor Monday gap risk."
        context['recommendation'] = "Action: Review patterns, prepare watchlist. Wait for Monday confirmation before entry."
        context['gap_risk'] = "HIGH - Weekend news can cause significant gaps"
        context['entry_timing'] = "Wait for Monday open confirmation"
        
    elif context['is_monday']:
        if context['pre_market']:
            context['warning'] = "Monday Pre-Market: Watch for gaps that might invalidate weekend patterns."
            context['recommendation'] = "Action: Check pre-market levels vs. pattern entry points."
            context['gap_risk'] = "ACTIVE - Monitor gap direction"
            context['entry_timing'] = "Wait for market open gap assessment"
        else:
            context['warning'] = "Monday Trading: Gap risk period. Validate patterns post-open."
            context['recommendation'] = "Action: Entry valid if patterns hold after gap settlement."
            context['gap_risk'] = "MEDIUM - Early session volatility"
            context['entry_timing'] = "Patterns valid if holding post-gap"
    
    elif context['is_friday']:
        if context['after_market']:
            context['warning'] = "Friday After-Hours: Consider weekend risk for new positions."
            context['recommendation'] = "Action: Avoid new breakouts. Weekend news risk."
            context['gap_risk'] = "MEDIUM - Weekend headline risk"
            context['entry_timing'] = "Avoid new positions into weekend"
        else:
            context['warning'] = "Friday Session: Strong volume required for weekend holds."
            context['recommendation'] = "Action: Require exceptional volume (2.0x+) for Friday entries."
            context['gap_risk'] = "MEDIUM - Weekend news risk"
            context['entry_timing'] = "High volume confirmation essential"
    
    elif context['is_midweek']:
        context['warning'] = None
        context['recommendation'] = f"{current_day} Trading: Optimal timing for pattern entries."
        context['gap_risk'] = "LOW - Standard trading conditions"
        context['entry_timing'] = "Patterns active for immediate consideration"
    
    else:
        context['warning'] = None
        context['recommendation'] = "Active Trading: Standard market conditions."
        context['gap_risk'] = "LOW - Normal conditions"
        context['entry_timing'] = "Patterns active for entry"
    
    return context

def display_market_context():
    """Display market timing context prominently in the UI"""
    market_context = get_market_context()
    
    st.markdown("### Market Timing Context")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Current Day**: {market_context['day']}")
        st.info(f"**Gap Risk**: {market_context['gap_risk']}")
    
    with col2:
        st.info(f"**Entry Timing**: {market_context['entry_timing']}")
    
    with col3:
        if market_context['is_weekend']:
            st.warning("Market Closed")
        elif market_context['market_hours']:
            st.success("Market Open")
        elif market_context['pre_market']:
            st.info("Pre-Market")
        elif market_context['after_market']:
            st.info("After-Hours")
        else:
            st.error("Market Closed")
    
    if market_context['warning']:
        st.warning(market_context['warning'])
    
    st.success(market_context['recommendation'])
    
    return market_context

def adjust_confidence_for_timing(confidence, pattern_info, market_context):
    """Adjust pattern confidence based on market timing"""
    original_confidence = confidence
    timing_adjustments = []
    
    if market_context['is_weekend']:
        confidence *= MARKET_TIMING_ADJUSTMENTS['weekend_penalty']
        timing_adjustments.append("Weekend analysis (-5%)")
    
    elif market_context['is_friday']:
        volume_status = pattern_info.get('volume_status', '')
        
        if 'Exceptional' not in volume_status:
            confidence *= MARKET_TIMING_ADJUSTMENTS['friday_penalty']
            timing_adjustments.append("Friday without exceptional volume (-15%)")
            pattern_info['friday_risk'] = "High volume required for weekend hold"
        else:
            timing_adjustments.append("Friday with exceptional volume (✓)")
    
    elif market_context['is_monday']:
        timing_adjustments.append("Monday gap risk - validate post-open")
        pattern_info['monday_gap_check'] = "Verify patterns hold after gap"
    
    elif market_context['is_midweek']:
        confidence *= MARKET_TIMING_ADJUSTMENTS['midweek_bonus']
        timing_adjustments.append("Mid-week optimal timing (+2%)")
    
    pattern_info['timing_adjustments'] = timing_adjustments
    pattern_info['original_confidence'] = original_confidence
    pattern_info['timing_adjusted_confidence'] = confidence
    pattern_info['day'] = market_context['day']
    pattern_info['gap_risk'] = market_context['gap_risk']
    
    return confidence, pattern_info

def get_timing_recommendation(pattern_info, market_context):
    """Get specific timing recommendation for a detected pattern"""
    recommendations = []
    
    if market_context['is_weekend']:
        recommendations.append("Wait for Monday confirmation before entry")
        recommendations.append("Monitor pre-market for gap risk")
    
    elif market_context['is_friday']:
        volume_status = pattern_info.get('volume_status', '')
        if 'Exceptional' not in volume_status:
            recommendations.append("Consider waiting until next week")
            recommendations.append("Weekend news risk without strong volume")
        else:
            recommendations.append("Entry acceptable with exceptional volume")
    
    elif market_context['is_monday']:
        recommendations.append("Validate pattern holds after gap settlement")
        recommendations.append("Wait for first hour to confirm levels")
    
    else:
        recommendations.append("Pattern active for immediate consideration")
        recommendations.append("Standard market conditions apply")
    
    return recommendations

def assess_gap_risk(market_context, pattern_info):
    """Assess gap risk level and provide guidance"""
    gap_assessment = {
        'risk_level': market_context['gap_risk'],
        'factors': [],
        'mitigation': []
    }
    
    if market_context['is_weekend']:
        gap_assessment['factors'].append("Weekend news cycle")
        gap_assessment['factors'].append("Extended market closure")
        gap_assessment['mitigation'].append("Review pre-market levels Monday")
        gap_assessment['mitigation'].append("Confirm pattern validity post-gap")
    
    elif market_context['is_friday']:
        gap_assessment['factors'].append("Weekend headline risk")
        gap_assessment['factors'].append("Position carries over weekend")
        gap_assessment['mitigation'].append("Require exceptional volume")
        gap_assessment['mitigation'].append("Consider smaller position size")
    
    elif market_context['is_monday']:
        gap_assessment['factors'].append("Overnight news accumulation")
        gap_assessment['factors'].append("Weekly market reset")
        gap_assessment['mitigation'].append("Wait for gap fill assessment")
        gap_assessment['mitigation'].append("Validate support/resistance post-gap")
    
    return gap_assessment

def get_optimal_entry_timing(pattern_type, market_context):
    """Get optimal entry timing based on pattern type and market context"""
    timing_guidance = {
        'immediate': False,
        'wait_for': [],
        'conditions': [],
        'risk_factors': []
    }
    
    if market_context['is_midweek']:
        timing_guidance['immediate'] = True
        timing_guidance['conditions'].append("Optimal market timing")
        timing_guidance['conditions'].append("Standard gap risk")
    
    elif market_context['is_monday']:
        timing_guidance['wait_for'].append("Gap settlement (first 30-60 minutes)")
        timing_guidance['conditions'].append("Pattern levels hold post-gap")
        timing_guidance['risk_factors'].append("Gap volatility")
    
    elif market_context['is_friday']:
        timing_guidance['conditions'].append("Exceptional volume required (2.0x+)")
        timing_guidance['risk_factors'].append("Weekend news risk")
        timing_guidance['risk_factors'].append("Extended holding period")
    
    elif market_context['is_weekend']:
        timing_guidance['wait_for'].append("Monday market open")
        timing_guidance['wait_for'].append("Pre-market assessment")
        timing_guidance['risk_factors'].append("Gap risk HIGH")
    
    # Pattern-specific timing considerations
    if pattern_type == "Inside Bar":
        timing_guidance['conditions'].append("Breakout above consolidation range")
        timing_guidance['conditions'].append("Volume expansion on breakout")
    elif pattern_type == "Bull Flag":
        timing_guidance['conditions'].append("Break above flag high")
        timing_guidance['conditions'].append("Volume confirmation")
    elif pattern_type == "Flat Top Breakout":
        timing_guidance['conditions'].append("Clear break above resistance")
        timing_guidance['conditions'].append("Volume surge preferred")
    elif pattern_type == "Cup Handle":
        timing_guidance['conditions'].append("Break above rim level")
        timing_guidance['conditions'].append("Volume expansion")
    
    return timing_guidance
