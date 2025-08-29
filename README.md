# Pattern Detector V8.0

**Professional Stock Pattern Recognition System**

A modular Streamlit application for detecting high-probability swing trading patterns with institutional-grade analysis.

## Quick Start

```bash
pip install streamlit pandas numpy plotly yfinance
streamlit run main.py
```

## What It Does

Detects 4 professional trading patterns:
- **Inside Bar**: Consolidation breakouts with triple targets
- **Bull Flag**: Trend continuation with flagpole projection
- **Flat Top Breakout**: Resistance breakouts with triangle targets  
- **Cup Handle**: Base breakouts with cup depth projection

## Key Features

**Smart Pattern Detection**
- Volume confirmation system (1.3x to 2.0x+ thresholds)
- Market timing intelligence (weekend/Friday/Monday adjustments)
- Measured move targets (not fixed ratios)
- Age validation and pattern invalidation

**Professional Risk Management**
- Volatility-based stop losses
- Multiple target system (2:1 to 4:1 R/R typical)
- Position sizing calculations
- Inside Bar triple targets (Mother bar, +13%, +21%)

**Market Timing Intelligence**
- Day-of-week analysis with confidence adjustments
- Gap risk assessment (HIGH/MEDIUM/LOW)
- Entry timing recommendations
- Weekend/Friday risk warnings

**Enhanced Visualization**
- Multi-panel charts (Price/MACD/Volume)
- **Pattern structure annotations** (shows formation points)
- **Educational markers** (cup start/bottom, flagpole peaks, etc.)
- Volume confirmation indicators
- Market timing context display
- **Invalidation warnings** (prominent alerts for broken patterns)

## Modular Architecture

```
pattern-detector-v8/
├── main.py                 # Streamlit interface
├── config.py              # All settings/constants
├── data_handler.py        # Data fetching/processing
├── pattern_detectors.py   # Pattern algorithms
├── market_timing.py       # Timing analysis
├── risk_calculator.py     # Level calculations
└── chart_generator.py     # Visualization
```

**Benefits of Modular Design:**
- Each file under 300 lines
- Easy to modify individual features
- Clear separation of concerns
- Simple testing and debugging

## Usage Example

```python
# Configure in Streamlit sidebar:
# - Select patterns: Bull Flag, Inside Bar
# - Tickers: AAPL,MSFT,NVDA  
# - Period: 3mo
# - Min confidence: 55%
# - Volume confirmation: Enabled

# Results show:
# - Pattern confidence scores
# - Volume status (Good/Strong/Exceptional)
# - Entry/Stop/Target levels
# - Risk/reward ratios
# - Market timing context
```

## Enhanced Learning Features

**Pattern Structure Education:**
- **Inside Bar**: Mother bar range, consolidation zone markers
- **Bull Flag**: Flagpole start/peak, flag formation points  
- **Flat Top**: Pattern start, peaks, pullbacks, resistance lines
- **Cup Handle**: Cup rims/bottom, handle formation points

**Smart Invalidation System:**
- Prominent warnings for broken patterns
- Specific reasons: "Below support", "Pattern aging", etc.
- User choice: See compromised patterns with clear alerts
- Educational value: Learn why patterns fail

**Inside Bar Detection:**
- Green mother bar + Red inside bar(s)
- Entry: 5% above inside bar high
- Stop: 5% below inside bar low
- Targets: Mother bar high, +13%, +21%

**Bull Flag Detection:**
- Flagpole gain 8%+ → Controlled pullback
- Entry: Flag high + 0.5%
- Target: Flagpole height projection
- Volume: Flagpole vs flag analysis

## Volume Analysis

**Scoring System:**
- Exceptional (2.0x+): 25 points
- Strong (1.5x): 20 points  
- Good (1.3x): 15 points
- Weak (<1.3x): 0 points

**Confidence Capping:**
- Without volume confirmation: Max 70%
- With volume confirmation: Up to 100%

## Market Timing

**Day-of-Week Adjustments:**
- Weekend: -5% confidence (gap risk)
- Friday: -15% without exceptional volume
- Monday: Gap validation required
- Mid-week: +2% bonus (optimal timing)

## Installation

**Method 1: Download Files**
1. Download all 7 Python files from this repository
2. Place in same directory
3. Install requirements: `pip install streamlit pandas numpy plotly yfinance`
4. Run: `streamlit run main.py`

**Method 2: Git Clone**
```bash
git clone https://github.com/[username]/pattern-detector-v8.git
cd pattern-detector-v8
pip install -r requirements.txt  # (create this file with dependencies)
streamlit run main.py
```

## Configuration

**Sidebar Options:**
- Pattern selection (multi-select from 4 patterns)
- Tickers (comma-separated)
- Timeframe (1mo to 1y, plus Weekly)
- Confidence threshold (45-85%)
- Volume filters (optional)
- Timing adjustments (show/hide)

**Default Settings:**
- Patterns: Flat Top, Bull Flag, Inside Bar
- Period: 3 months
- Min confidence: 55%
- Volume confirmation: Optional

## Results Export

CSV export includes:
- Ticker and pattern type
- Confidence scores
- Volume status
- Entry/stop/target levels
- Risk/reward ratios
- Target calculation methods
- Timeframe information

## Example Output

```
Ticker  Pattern     Confidence  Volume          Entry    Target1   R/R1
AAPL    Bull Flag   78%        Strong (1.6x)   $185.50  $195.20   2.1:1
MSFT    Inside Bar  85%        Good (1.4x)     $415.25  $425.00   2.8:1
NVDA    Flat Top    72%        Exceptional     $875.30  $920.15   1.9:1
```

## Disclaimer

**Educational purposes only. Not financial advice.**
Trading involves substantial risk. Consult professionals before trading.

## Development History

- **V8.0**: Modular architecture redesign
- **V7.0**: Inside Bar pattern + multi-timeframe
- **V6.0**: Market timing intelligence  
- **V5.0**: Enhanced volume analysis
- **V4.0**: Measured move targets
- **V1.0-V3.0**: Basic pattern detection

## Contributing

This modular architecture makes contributions easy:
- Add patterns: Modify `pattern_detectors.py`
- Improve charts: Edit `chart_generator.py`
- Adjust settings: Update `config.py`
- Enhance timing: Modify `market_timing.py`

Each module is focused and manageable (<300 lines).

## License

[Specify your license here]

## Contact

[Your contact information]

---

**Ready to detect professional trading patterns with institutional-grade analysis.**
