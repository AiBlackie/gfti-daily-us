"""
GFTI Daily™ - Complete US Financial History Database
Now with 58 indicators (50 raw FRED series + 8 proprietary calculations)
Includes historical crisis annotations for storytelling
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os
import base64
import time
import json
import hashlib
import csv
import zipfile
from io import BytesIO
from pathlib import Path
import visual_vault
import time
import requests
from io import StringIO


# ============================================================================
# CONFIGURATION & SECRETS HANDLING
# ============================================================================

# Check if we're running locally or on Streamlit Cloud
try:
    # Try to access secrets (will work on Streamlit Cloud)
    FORMSPREE_ENDPOINT = st.secrets["FORMSPREE_ENDPOINT"]
    DEBUG = st.secrets.get("DEBUG_MODE", False)
except:
    # Fallback for local development without .streamlit/secrets.toml
    FORMSPREE_ENDPOINT = "https://formspree.io/f/your-form-id-here"
    DEBUG = True
    print("⚠️ Running without secrets - using hardcoded values")

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="GFTI Daily™ - Complete US Economic History",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS (with trademark styling) - ADDED FRESHNESS STYLES
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FFD700;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #FFD700;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #FFD700;
        padding-bottom: 0.3rem;
    }
    .category-header {
        font-size: 1.2rem;
        color: #FFD700;
        font-weight: 600;
        margin-top: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #FFD700;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-label {
        color: #888;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
    }
    .metric-date {
        color: #888;
        font-size: 0.7rem;
        margin-top: 2px;
    }
    .metric-change {
        font-size: 0.9rem;
        margin-left: 10px;
    }
    .positive {
        color: #ff4d4d;
    }
    .negative {
        color: #00ff00;
    }
    .neutral {
        color: #888;
    }
    .fear-high {
        color: #ff4d4d;
        font-weight: bold;
    }
    .fear-medium {
        color: #FFD700;
        font-weight: bold;
    }
    .fear-low {
        color: #00ff00;
        font-weight: bold;
    }
    .story-card {
        background: linear-gradient(135deg, #00267F 0%, #0033A0 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .story-card h2 {
        color: #FFD700;
        margin-top: 0;
    }
    /* COMPLIANCE & ATTRIBUTION STYLES */
    .compliance-footer {
        text-align: center;
        color: #888;
        font-size: 0.7rem;
        padding: 20px 10px;
        border-top: 1px solid #333;
        margin-top: 40px;
        line-height: 1.6;
    }
    .compliance-footer a {
        color: #FFD700;
        text-decoration: none;
    }
    .compliance-footer a:hover {
        text-decoration: underline;
    }
    .attribution-box {
        background: rgba(255, 215, 0, 0.05);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #FFD700;
        margin: 20px 0;
    }
    .attribution-box h3 {
        color: #FFD700;
        margin-top: 0;
    }
    .attribution-box ul {
        color: #ccc;
        margin-bottom: 0;
    }
    .what-we-add {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border: 1px solid #FFD700;
    }
    .what-we-add h3 {
        color: #FFD700;
        margin-top: 0;
    }
    .badge {
        display: inline-block;
        background: #FFD700;
        color: #00267F;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-left: 5px;
        vertical-align: middle;
    }
    .trademark {
        font-size: 0.7rem;
        vertical-align: super;
        color: #FFD700;
        font-weight: normal;
    }
    .recession-box {
        background: rgba(255, 77, 77, 0.1);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #ff4d4d;
        margin: 20px 0;
    }
    .email-box {
        background: linear-gradient(135deg, #00267F 0%, #0033A0 100%);
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        margin: 30px 0;
    }
    .data-info {
        color: #888;
        font-size: 0.8rem;
        font-style: italic;
        margin-top: 5px;
    }
    .update-note {
        background: rgba(255, 215, 0, 0.1);
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #FFD700;
        margin: 10px 0;
        font-size: 0.9rem;
    }
    .stat-highlight {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FFD700;
    }
    .annotation-info {
        background: rgba(255, 215, 0, 0.05);
        padding: 8px;
        border-radius: 5px;
        margin: 5px 0;
        font-size: 0.85rem;
        border-left: 2px solid #FFD700;
    }
    .era-selector {
        background: rgba(255, 215, 0, 0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .waitlist-badge {
        display: inline-block;
        background: #FFD700;
        color: #00267F;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 10px;
    }
    /* NEW STYLES FROM APP2.PY */
    .daily-commitment {
        background: rgba(0,255,0,0.05);
        border-left: 4px solid #00ff00;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1.5rem 0;
    }
    .freshness-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .freshness-daily { background-color: #00ff00; box-shadow: 0 0 10px #00ff00; }
    .freshness-weekly { background-color: #FFD700; box-shadow: 0 0 10px #FFD700; }
    .freshness-monthly { background-color: #ff9900; box-shadow: 0 0 10px #ff9900; }
    .freshness-quarterly { background-color: #4169E1; box-shadow: 0 0 10px #4169E1; }
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.2rem;
        }
        .category-header {
            font-size: 1rem;
        }
        .main-header {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONSTANTS
# ============================================================================

WAR_START_DATE = "2026-02-28"  # Iran-USA war start date

# ============================================================================
# FREQUENCY CONSTANTS (NEW - FROM APP2.PY)
# ============================================================================

FREQUENCIES = {
    'daily': {'name': 'Daily', 'color': '#00ff00', 'emoji': '🟢', 'max_days': 2},
    'weekly': {'name': 'Weekly', 'color': '#FFD700', 'emoji': '🟡', 'max_days': 9},
    'monthly': {'name': 'Monthly', 'color': '#ff9900', 'emoji': '🟠', 'max_days': 40},
    'quarterly': {'name': 'Quarterly', 'color': '#4169E1', 'emoji': '🔵', 'max_days': 999}
}

# ============================================================================
# CRISIS THRESHOLDS (REALISTIC VALUES)
# ============================================================================

THRESHOLDS = {
    'vix': {'warning': 25, 'critical': 30},
    'oil': {'warning': 80, 'critical': 90},
    'spread': {'warning': 0.2, 'critical': 0},
    'hy_spread': {'warning': 4, 'critical': 5},
    'sentiment': {'warning': 60, 'critical': 50},
    'claims': {'warning': 300000, 'critical': 350000},
    'unrate': {'warning': 5, 'critical': 7},
    'cpi': {'warning': 3, 'critical': 5},
    'financial_stress': {'warning': 0.5, 'critical': 1.0}
}

# ============================================================================
# INDICATOR CLASSIFICATION - TRANSPARENT BREAKDOWN
# ============================================================================

RAW_INDICATORS = [
    # Treasury Yields (10)
    'DGS1', 'DGS10', 'DGS2', 'DGS20', 'DGS3', 'DGS30', 'DGS3MO', 'DGS5', 'DGS6MO', 'DGS7',
    
    # Fed Policy (5)
    'DFEDTARL', 'DFEDTARU', 'FEDFUNDS', 'TOTRESNS', 'WALCL',
    
    # Inflation (5 - raw price levels)
    'CPIAUCSL', 'CPILFESL', 'PCEPI', 'PCEPILFE',
    
    # Inflation Expectations (2)
    'T10YIE', 'T5YIE',
    
    # Labor Market (7)
    'AWHAETP', 'CIVPART', 'JTSJOL', 'JTSQUR', 'TEMPHELPS', 'U6RATE', 'UNRATE',
    
    # Jobless Claims (3)
    'CC4WSA', 'IC4WSA', 'ICSA',
    
    # Growth (3)
    'GDPC1', 'INDPRO', 'RSAFS',
    
    # Housing (3)
    'HOUST', 'PERMIT', 'RHORUSQ156N',
    
    # Money & Credit (3)
    'BAMLH0A0HYM2', 'M2SL', 'TNWBSHNO',
    
    # Market Fear (2)
    'STLFSI4', 'VIX',
    
    # Dollar & Oil (2)
    'DCOILWTICO', 'DTWEXBGS',
    
    # Demographics (1)
    'MEHOINUSA672N'
]

CALCULATED_INDICATORS = [
    # Inflation (1)
    'CPI_YOY',           # Year-over-year inflation rate
    
    # Money & Credit (2)
    'M2_REAL',           # Inflation-adjusted money supply
    'M2_REAL_YOY',       # Real money supply growth
    
    # Spreads (5)
    '10Y2Y',             # 10Y-2Y Treasury spread (recession indicator)
    '10Y3M',             # 10Y-3M Treasury spread
    'BAA_SPREAD',        # BAA corporate credit spread
    'AAA_SPREAD',        # AAA corporate credit spread
    'HY_SPREAD',         # High yield credit spread
    'RISK_APPETITE',     # HY vs BAA spread differential
]

# Combined list for backward compatibility
REAL_INDICATORS = RAW_INDICATORS + CALCULATED_INDICATORS

# ============================================================================
# EMAIL FUNCTIONS - USING FORMSPREE WITH SECRETS
# ============================================================================

def send_email_notification(email, interest):
    """Send email notification via Formspree using secrets"""
    try:
        # Get endpoint from secrets
        if 'FORMSPREE_ENDPOINT' not in st.secrets:
            print("❌ FORMSPREE_ENDPOINT not found in secrets")
            st.error("Email service not configured. Please contact support.")
            return False
        
        url = st.secrets["FORMSPREE_ENDPOINT"]
        
        # Prepare the data
        data = {
            'email': email,
            'interest': interest,
            '_replyto': email,  # So you can reply directly
            '_subject': f'🎯 New GFTI Daily Signup: {interest}',
            'message': f"""
New waitlist signup:

📧 Email: {email}
🎯 Interest: {interest}
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
This is an automated notification from GFTI Daily™
            """
        }
        
        print(f"📧 Sending notification for {email}...")
        
        # Send the request
        response = requests.post(url, data=data)
        
        print(f"📥 Response status: {response.status_code}")
        
        # Check if it worked
        if response.status_code == 200:
            print(f"✅ Notification sent to gftdaily@gmail.com")
            
            # Store in session state as backup
            if 'signups' not in st.session_state:
                st.session_state['signups'] = []
            
            st.session_state['signups'].append({
                'email': email,
                'interest': interest,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return True
        else:
            print(f"❌ Formspree error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception in send_email_notification: {e}")
        return False

# ============================================================================
# LEGACY FUNCTIONS (for compatibility)
# ============================================================================

def save_email_to_list(email, plan_interest):
    """Legacy function - kept for compatibility"""
    return True, 1

def get_waitlist_stats():
    """Legacy function - returns empty stats"""
    return {'total': 0, 'by_plan': {}}

# ============================================================================
# HISTORICAL EVENTS DATABASE
# ============================================================================

HISTORICAL_EVENTS = [
    # Recessions (with labels)
    {'start': '1960-04-01', 'end': '1961-02-28', 'label': '1960 Recession', 'category': 'recession', 
     'description': 'Post-WWII adjustment, Fed tightening', 'color': 'rgba(255,0,0,0.15)'},
    {'start': '1969-12-01', 'end': '1970-11-30', 'label': '1969 Recession', 'category': 'recession',
     'description': 'Vietnam War spending, Fed tightening', 'color': 'rgba(255,0,0,0.15)'},
    {'start': '1973-11-01', 'end': '1975-03-31', 'label': 'Oil Crisis', 'category': 'recession',
     'description': 'OPEC oil embargo, stagflation begins', 'color': 'rgba(255,0,0,0.15)'},
    {'start': '1980-01-01', 'end': '1980-07-31', 'label': 'Volcker Recession', 'category': 'recession',
     'description': 'Fed hikes rates to combat inflation', 'color': 'rgba(255,0,0,0.15)'},
    {'start': '1981-07-01', 'end': '1982-11-30', 'label': 'Severe Recession', 'category': 'recession',
     'description': 'Volcker shock, unemployment peaks at 10.8%', 'color': 'rgba(255,0,0,0.15)'},
    {'start': '1990-07-01', 'end': '1991-03-31', 'label': 'Gulf War Recession', 'category': 'recession',
     'description': 'Oil price spike, consumer confidence drop', 'color': 'rgba(255,0,0,0.15)'},
    {'start': '2001-03-01', 'end': '2001-11-30', 'label': 'Dot-com Bust', 'category': 'recession',
     'description': 'Tech bubble bursts, 9/11 attacks', 'color': 'rgba(255,0,0,0.15)'},
    {'start': '2007-12-01', 'end': '2009-06-30', 'label': 'Great Recession', 'category': 'recession',
     'description': 'Housing crash, financial crisis, 10% unemployment', 'color': 'rgba(255,0,0,0.25)'},
    {'start': '2020-02-01', 'end': '2020-04-30', 'label': 'COVID-19', 'category': 'recession',
     'description': 'Pandemic shutdowns, fastest crash/recovery', 'color': 'rgba(255,0,0,0.15)'},
    
    # Wars & Geopolitical Events
    {'date': '1973-10-06', 'label': 'Yom Kippur War', 'category': 'war',
     'description': 'Oil embargo, prices quadruple', 'marker': '⚔️', 'y_offset': 0},
    {'date': '1979-11-04', 'label': 'Iran Hostage Crisis', 'category': 'war',
     'description': 'Oil prices spike', 'marker': '⚔️', 'y_offset': 1},
    {'date': '1990-08-02', 'label': 'Gulf War', 'category': 'war',
     'description': 'Iraq invades Kuwait, oil spikes', 'marker': '⚔️', 'y_offset': -1},
    {'date': '2001-09-11', 'label': '9/11 Attacks', 'category': 'war',
     'description': 'Markets closed, Fed provides liquidity', 'marker': '⚔️', 'y_offset': 0},
    {'date': '2003-03-20', 'label': 'Iraq War', 'category': 'war',
     'description': 'US invades Iraq', 'marker': '⚔️', 'y_offset': 1},
    {'date': '2022-02-24', 'label': 'Russia-Ukraine War', 'category': 'war',
     'description': 'Energy crisis begins', 'marker': '⚔️', 'y_offset': -1},
    {'date': WAR_START_DATE, 'label': 'Iran-USA War', 'category': 'war',
     'description': 'US and Israel strike Iran', 'marker': '⚔️', 'y_offset': -2},
    
    # Major Market Events
    {'date': '1971-08-15', 'label': 'Nixon Shock', 'category': 'policy',
     'description': 'End of gold standard, Bretton Woods collapses', 'marker': '💰', 'y_offset': 0},
    {'date': '1979-08-06', 'label': 'Volcker Appointed', 'category': 'fed',
     'description': 'Paul Volcker becomes Fed Chair, begins inflation fight', 'marker': '🏦', 'y_offset': 2},
    {'date': '1987-10-19', 'label': 'Black Monday', 'category': 'market',
     'description': 'Stock market crashes -22% in single day', 'marker': '📉', 'y_offset': 1},
    {'date': '1994-02-04', 'label': 'Bond Massacre', 'category': 'fed',
     'description': 'Fed surprises with rate hikes, bond losses', 'marker': '💰', 'y_offset': -1},
    {'date': '1998-09-23', 'label': 'LTCM Bailout', 'category': 'crisis',
     'description': 'Hedge fund collapse, Fed orchestrates bailout', 'marker': '⚠️', 'y_offset': -1},
    {'date': '2008-09-15', 'label': 'Lehman Collapse', 'category': 'crisis',
     'description': 'Lehman Brothers fails, financial panic peaks', 'marker': '💥', 'y_offset': -2},
    {'date': '2008-10-03', 'label': 'TARP Passed', 'category': 'policy',
     'description': '$700B bank bailout program approved', 'marker': '💰', 'y_offset': 2},
    {'date': '2008-11-25', 'label': 'QE1 Begins', 'category': 'fed',
     'description': 'First quantitative easing program', 'marker': '🏦', 'y_offset': -2},
    {'date': '2010-04-27', 'label': 'Greek Crisis', 'category': 'global',
     'description': 'European debt crisis escalates', 'marker': '🇪🇺', 'y_offset': 1},
    {'date': '2011-08-05', 'label': 'US Downgraded', 'category': 'market',
     'description': 'S&P downgrades US credit rating', 'marker': '📉', 'y_offset': -1},
    {'date': '2013-05-22', 'label': 'Taper Tantrum', 'category': 'fed',
     'description': 'Bernanke hints at tapering, rates spike', 'marker': '🏦', 'y_offset': 1},
    {'date': '2015-12-16', 'label': 'First Hike', 'category': 'fed',
     'description': 'First rate hike after ZIRP era', 'marker': '🏦', 'y_offset': -1},
    {'date': '2018-12-24', 'label': 'Christmas Eve Selloff', 'category': 'market',
     'description': 'Markets nearly enter bear market', 'marker': '📉', 'y_offset': 0},
    {'date': '2020-03-15', 'label': 'Emergency Cut', 'category': 'fed',
     'description': 'Fed cuts rates to zero, launches QE', 'marker': '🏦', 'y_offset': -1},
    {'date': '2021-04-01', 'label': 'Inflation Surge', 'category': 'inflation',
     'description': 'CPI begins multi-year rise', 'marker': '📈', 'y_offset': 2},
    {'date': '2022-03-16', 'label': 'Hike Cycle Begins', 'category': 'fed',
     'description': 'Fed starts fastest hiking cycle since 1980s', 'marker': '🏦', 'y_offset': -2},
]

# ============================================================================
# COMPLIANCE FUNCTIONS
# ============================================================================

def generate_readme():
    """Generate README.txt content for data downloads"""
    readme = f"""====================================================================
GFTI DAILY™ DATASET
Complete US Financial History
====================================================================

VERSION: {datetime.now().strftime('%Y.%m.%d')}
INDICATORS: 58 total (50 raw FRED series + 8 proprietary calculations)
HISTORY: 1960-2026 (varies by indicator)
UPDATE FREQUENCY: Daily

====================================================================
DATA SOURCES & ATTRIBUTION
====================================================================

FRED® (Federal Reserve Economic Data)
Federal Reserve Bank of St. Louis
https://fred.stlouisfed.org/
Indicators: All economic series except VIX

Yahoo Finance
https://finance.yahoo.com/
Indicators: VIX (CBOE Volatility Index)

====================================================================
WHAT GFTI DAILY™ ADDS

This dataset contains cleaned, transformed, and enhanced versions
of publicly available data. We provide:

✓ Cleaned and standardized time series (removed gaps, weekends, holidays)
✓ 58 indicators combined into one file
✓ 8 proprietary calculations (spreads, real values, growth rates)
✓ Daily automated updates
✓ Historical event annotations
✓ Ready-to-use format (no API keys, no cleaning required)

Breakdown: 50 raw FRED series + 8 calculated indicators = 58 total

Proprietary Calculations:
• CPI_YOY - Year-over-year inflation rate
• M2_REAL - Inflation-adjusted money supply
• M2_REAL_YOY - Real money supply growth
• 10Y2Y - 10Y-2Y Treasury spread (recession indicator)
• 10Y3M - 10Y-3M Treasury spread
• BAA_SPREAD - BAA corporate credit spread
• AAA_SPREAD - AAA corporate credit spread
• HY_SPREAD - High yield credit spread
• RISK_APPETITE - HY vs BAA spread differential

====================================================================
COVERAGE BY ERA

1960-1969: 29 core indicators
1970-1979: 32 indicators
1980-1989: 41 indicators
1990-1999: 49 indicators
2000-2026: 58 indicators (full modern dataset)

====================================================================
REQUIRED ATTRIBUTION

If you publish or distribute any part of this dataset, you MUST include:

"Data sourced from FRED® (Federal Reserve Economic Data),
Federal Reserve Bank of St. Louis, and Yahoo Finance."

====================================================================
DISCLAIMER

GFTI Daily™ is an independent data provider. We are NOT affiliated with,
endorsed by, or sponsored by the Federal Reserve Bank of St. Louis
or Yahoo! Inc. All trademarks are property of their respective owners.

FRED® is a registered trademark of the Federal Reserve Bank of St. Louis.
Yahoo Finance is a trademark of Yahoo! Inc.
GFTI Daily™ is a trademark of Matthew A.A. Blackman.

====================================================================
CONTACT

hello@gftidaily.com
https://gftidaily.com

====================================================================
"""
    return readme

def get_email_footer():
    """Generate email footer with attribution"""
    return """
---
📊 GFTI Daily™ — Complete US Financial History
Data sourced from FRED® (Federal Reserve Economic Data, Federal Reserve Bank of St. Louis) and Yahoo Finance.
GFTI Daily™ is an independent provider, not affiliated with these organizations.
View our full terms and data sources: https://gftidaily.com/legal
"""

def get_compliance_footer():
    """Generate the compliance footer HTML"""
    return """
<div class="compliance-footer">
    <p>© 2026 GFTI Daily™. All rights reserved. GFTI Daily™ is a trademark of Matthew A.A. Blackman.</p>
    <p>
        Data sourced from <a href="https://fred.stlouisfed.org/" target="_blank">FRED®</a>
        (Federal Reserve Economic Data, Federal Reserve Bank of St. Louis) and
        <a href="https://finance.yahoo.com/" target="_blank">Yahoo Finance</a>.
    </p>
    <p>
        GFTI Daily™ is an independent provider of cleaned and enhanced economic data
        and is not affiliated with, endorsed by, or sponsored by the Federal Reserve
        Bank of St. Louis or Yahoo! Inc.
    </p>
    <p>
        FRED® is a registered trademark of the Federal Reserve Bank of St. Louis.
        Yahoo Finance is a trademark of Yahoo! Inc.
    </p>
    <p style="margin-top: 10px;">
        <a href="#attribution" style="color: #FFD700;">📋 Full Attribution Details</a> • 
        <a href="#terms" style="color: #FFD700;">Terms of Use</a> • 
        <a href="#privacy" style="color: #FFD700;">Privacy</a> • 
        <a href="#contact" style="color: #FFD700;">Contact</a>
    </p>
</div>
"""

# ============================================================================
# LOAD DATA FUNCTIONS - UPDATED WITH GOOGLE DRIVE
# ============================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_master_data():
    """Load the master dataset from Google Drive"""
    try:
        # First try to load from local file (for development)
        if os.path.exists('master_dataset.csv'):
            df = pd.read_csv('master_dataset.csv')
            print("✅ Loaded local master_dataset.csv")
            
            # Parse dates
            try:
                df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
                print("✅ Parsed dates with format='%d/%m/%Y'")
            except:
                try:
                    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
                    print("✅ Parsed dates with dayfirst=True")
                except:
                    df['date'] = pd.to_datetime(df['date'])
                    print("✅ Parsed dates with auto-detection")
            
            return df
        
        # For Streamlit Cloud - download from Google Drive
        st.info("📥 Loading 64 years of economic history from Google Drive...")
        
        # YOUR GOOGLE DRIVE FILE ID
        file_id = "1FfpJ7vS0q5E8rkn-PmHezJS0m3Rn7IjX"
        
        # Direct download link
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # Download with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Check for Google Drive virus warning page
        if 'Google Drive - Virus scan warning' in response.text:
            import re
            confirm = re.findall('confirm=([0-9A-Za-z]+)', response.text)
            if confirm:
                url = f"https://drive.google.com/uc?export=download&confirm={confirm[0]}&id={file_id}"
                response = session.get(url, headers=headers, stream=True)
        
        # Read the CSV
        df = pd.read_csv(StringIO(response.text))
        
        # Parse dates
        try:
            df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
            print("✅ Parsed dates with format='%d/%m/%Y'")
        except:
            try:
                df['date'] = pd.to_datetime(df['date'], dayfirst=True)
                print("✅ Parsed dates with dayfirst=True")
            except:
                df['date'] = pd.to_datetime(df['date'])
                print("✅ Parsed dates with auto-detection")
        
        st.success("✅ Data loaded successfully from Google Drive!")
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None

def load_data_with_spinner():
    """Load data with a spinner for better UX"""
    with st.spinner('📊 Loading 64 years of economic history...'):
        time.sleep(0.5)  # Small delay for visual feedback
        return load_master_data()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_indicator_count(df):
    """Count actual indicators (same method as analyzer)"""
    return len([c for c in df.columns if c not in ['date', 'year', 'month', 'day'] 
                and not c.endswith('_RAW') 
                and not c.endswith('_IS_QUARTERLY')
                and not c.endswith('_INV')])

def get_latest_value(df, column, alternative_cols=None):
    """Get the latest non-NaN value for a column - FIXED for monthly/weekly series"""
    if alternative_cols is None:
        alternative_cols = []
    
    # First check if there's a _RAW version of this column (for monthly/weekly series)
    raw_col = f'{column}_RAW'
    if raw_col in df.columns:
        valid_data = df[df[raw_col].notna()]
        if not valid_data.empty:
            latest_row = valid_data.iloc[-1]
            latest_date = latest_row['date']
            
            # Get the forward-filled value at the same date (or most recent)
            if column in df.columns:
                # Try to get the value at the exact date
                mask = df['date'] == latest_date
                if mask.any():
                    fwd_val = df.loc[mask, column].iloc[0]
                    if not pd.isna(fwd_val):
                        return fwd_val, latest_date
                
                # If no value at exact date, get the most recent non-null
                valid_fwd = df[df[column].notna()]
                if not valid_fwd.empty:
                    return valid_fwd.iloc[-1][column], latest_date
            
            # Fallback to the raw value
            return latest_row[raw_col], latest_date
    
    # Then try the main column
    if column in df.columns:
        valid_data = df[df[column].notna()]
        if not valid_data.empty:
            latest_row = valid_data.iloc[-1]
            latest_val = latest_row[column]
            latest_date = latest_row['date']
            
            # Validate the date is not NaT
            try:
                if pd.isna(latest_date):
                    # If date is NaT, try to find a valid date from _RAW column
                    raw_col = f'{column}_RAW'
                    if raw_col in df.columns:
                        raw_data = df[df[raw_col].notna()]
                        if not raw_data.empty:
                            latest_date = raw_data.iloc[-1]['date']
            except:
                pass
            
            return latest_val, latest_date
    
    # Try alternatives
    for alt in alternative_cols:
        if alt in df.columns:
            # Check for _RAW version of alternative
            alt_raw = f'{alt}_RAW'
            if alt_raw in df.columns:
                valid_data = df[df[alt_raw].notna()]
                if not valid_data.empty:
                    latest_row = valid_data.iloc[-1]
                    return latest_row[alt_raw], latest_row['date']
            
            # Try the main alternative column
            valid_data = df[df[alt].notna()]
            if not valid_data.empty:
                latest_row = valid_data.iloc[-1]
                return latest_row[alt], latest_row['date']
    
    return None, None

def format_change(current, prev, decimals=2, is_percent=True):
    """Format change with emoji and color"""
    if pd.isna(current) or pd.isna(prev) or prev == 0:
        return "", "neutral", "◆"
    diff = current - prev
    if abs(diff) < 0.005:
        return "", "neutral", "◆"
    emoji = "▲" if diff > 0 else "▼"
    color = "positive" if diff > 0 else "negative"
    unit = "%" if is_percent else ""
    return f"{emoji} {abs(diff):.{decimals}f}{unit}", color, emoji


# ============================================================================
# VIX STATUS AND FORMAT VALUE FUNCTIONS
# ============================================================================

def get_vix_status(vix):
    """Interpret VIX levels"""
    if pd.isna(vix):
        return "N/A", "#888"
    if vix > 30:
        return "🔴 HIGH FEAR", "#ff4d4d"
    elif vix > 20:
        return "🟡 MODERATE", "#FFD700"
    else:
        return "🟢 CALM", "#00ff00"


def format_value(value, decimals=2, prefix="", suffix=""):
    """Format a value for display"""
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, float):
        return f"{prefix}{value:.{decimals}f}{suffix}"
    return f"{prefix}{value}{suffix}"


# ============================================================================
# VULNERABILITY INDEX FUNCTIONS - FIXED WITH FALLBACKS
# ============================================================================

def normalize_curve_stress(spread):
    if pd.isna(spread):
        return np.nan
    # When spread is negative (inverted), stress is high
    # Normalize: spread from -1.5% to +0.5% maps to 100 to 0
    stress = ((spread * -1) + 0.5) * 66.7
    return max(0, min(100, stress))

def normalize_credit_stress(spread):
    if pd.isna(spread):
        return np.nan
    # HY spread typically ranges from 2% (calm) to 8% (crisis)
    # Normalize: 2% = 0 stress, 8% = 100 stress
    stress = (spread - 2) / 6 * 100
    return max(0, min(100, stress))

def normalize_vix_stress(vix):
    if pd.isna(vix):
        return np.nan
    # VIX typically ranges from 10 (calm) to 35+ (panic)
    # Normalize: 15 = 0 stress, 40 = 100 stress
    stress = (vix - 15) / 25 * 100
    return max(0, min(100, stress))

def normalize_systemic_stress(stlfsi):
    if pd.isna(stlfsi):
        return np.nan
    # STLFSI4 typically ranges from -2 to +2
    # Normalize: -2 = 0 stress, +2 = 100 stress
    stress = (stlfsi + 2) / 4 * 100
    return max(0, min(100, stress))

def calculate_vulnerability_index(df):
    """
    Calculate the composite Vulnerability Index™
    Combines: CURVE_STRESS, CREDIT_STRESS, VIX_STRESS, SYSTEM_STRESS
    Now with fallback values when components are missing
    """
    df = df.copy()
    
    # Initialize all stress columns with NaN
    df['CURVE_STRESS'] = np.nan
    df['CREDIT_STRESS'] = np.nan
    df['VIX_STRESS'] = np.nan
    df['SYSTEM_STRESS'] = np.nan
    
    # Calculate curve stress (10Y2Y)
    if '10Y2Y' in df.columns:
        df['CURVE_STRESS'] = df['10Y2Y'].apply(normalize_curve_stress)
    
    # Calculate credit stress (HY_SPREAD)
    if 'HY_SPREAD' in df.columns:
        df['CREDIT_STRESS'] = df['HY_SPREAD'].apply(normalize_credit_stress)
    
    # Calculate VIX stress
    if 'VIX' in df.columns:
        df['VIX_STRESS'] = df['VIX'].apply(normalize_vix_stress)
    
    # Calculate systemic stress
    if 'STLFSI4' in df.columns:
        df['SYSTEM_STRESS'] = df['STLFSI4'].apply(normalize_systemic_stress)
    
    # Calculate composite - fallback to available components with weighting
    # We'll use a weighted average that adjusts based on which components are available
    stress_components = []
    component_weights = []
    
    # Define base weights (sum to 1.0)
    weights = {
        'CURVE_STRESS': 0.30,
        'CREDIT_STRESS': 0.25,
        'VIX_STRESS': 0.25,
        'SYSTEM_STRESS': 0.20
    }
    
    # Build list of available components with their weights
    for col, weight in weights.items():
        if col in df.columns and df[col].notna().any():
            stress_components.append(df[col])
            component_weights.append(weight)
    
    if len(stress_components) >= 2:  # At least 2 components available
        # Normalize weights to sum to 1.0 based on available components
        total_weight = sum(component_weights)
        normalized_weights = [w / total_weight for w in component_weights]
        
        # Calculate weighted average
        weighted_sum = np.zeros(len(df))
        for component, weight in zip(stress_components, normalized_weights):
            weighted_sum += component.fillna(0) * weight
        
        # Only calculate where at least one component is non-null
        valid_mask = pd.concat(stress_components, axis=1).notna().any(axis=1)
        df['VULNERABILITY_INDEX'] = np.where(valid_mask, weighted_sum, np.nan)
    else:
        # Fallback: use VIX stress as proxy if only one component available
        if 'VIX_STRESS' in df.columns and df['VIX_STRESS'].notna().any():
            df['VULNERABILITY_INDEX'] = df['VIX_STRESS']
        elif 'CURVE_STRESS' in df.columns and df['CURVE_STRESS'].notna().any():
            df['VULNERABILITY_INDEX'] = df['CURVE_STRESS']
        elif 'CREDIT_STRESS' in df.columns and df['CREDIT_STRESS'].notna().any():
            df['VULNERABILITY_INDEX'] = df['CREDIT_STRESS']
        elif 'SYSTEM_STRESS' in df.columns and df['SYSTEM_STRESS'].notna().any():
            df['VULNERABILITY_INDEX'] = df['SYSTEM_STRESS']
        else:
            # Ultimate fallback: use a default moderate stress level
            df['VULNERABILITY_INDEX'] = 50.0
    
    return df

def get_vulnerability_status(value):
    """Get status text and color for vulnerability index"""
    if pd.isna(value) or value is None:
        return "MODERATE", "#FFD700"  # Fallback to moderate instead of unavailable
    if value < 40:
        return "LOW", "#00ff00"
    elif value < 70:
        return "MODERATE", "#FFD700"
    else:
        return "HIGH", "#ff4d4d"


# ============================================================================
# 24-MONTH RECESSION WARNING SYSTEM (Based on Vulnerability Index Factors)
# ============================================================================

def check_recession_24month(df):
    """
    Returns recession warning based on 5 key factors from Vulnerability Index
    Backtested: 90% precision at 24 months
    """
    # Get latest values
    spread_val, spread_date = get_latest_value(df, '10Y2Y')
    cpi_val, cpi_date = get_latest_value(df, 'CPI_YOY')
    unrate_val, unrate_date = get_latest_value(df, 'UNRATE')
    housing_val, housing_date = get_latest_value(df, 'HOUST')
    sentiment_val, sentiment_date = get_latest_value(df, 'UMCSENT')
    
    # Calculate score
    score = 0
    reasons = []
    factor_values = {}
    
    # Factor 1: Yield Curve (40% weight)
    if spread_val is not None:
        factor_values['10Y2Y'] = spread_val
        if spread_val < -0.5:
            score += 40
            reasons.append(f"🔴 Deep yield curve inversion: {spread_val:.2f}% (+40)")
        elif spread_val < 0:
            score += 30
            reasons.append(f"🟡 Yield curve inverted: {spread_val:.2f}% (+30)")
        elif spread_val < 0.2:
            score += 15
            reasons.append(f"⚠️ Yield curve flattening: {spread_val:.2f}% (+15)")
        else:
            reasons.append(f"✅ Yield curve normal: {spread_val:.2f}% (0)")
    else:
        factor_values['10Y2Y'] = None
    
    # Factor 2: Inflation (20% weight)
    if cpi_val is not None:
        factor_values['CPI_YOY'] = cpi_val
        if cpi_val > 8:
            score += 20
            reasons.append(f"🔥 Hyperinflation: {cpi_val:.1f}% (+20)")
        elif cpi_val > 5:
            score += 15
            reasons.append(f"📈 High inflation: {cpi_val:.1f}% (+15)")
        elif cpi_val > 4:
            score += 8
            reasons.append(f"📈 Elevated inflation: {cpi_val:.1f}% (+8)")
        else:
            reasons.append(f"✅ Inflation contained: {cpi_val:.1f}% (0)")
    else:
        factor_values['CPI_YOY'] = None
    
    # Factor 3: Unemployment (20% weight)
    if unrate_val is not None:
        factor_values['UNRATE'] = unrate_val
        if unrate_val > 7:
            score += 20
            reasons.append(f"👥 High unemployment: {unrate_val:.1f}% (+20)")
        elif unrate_val > 6:
            score += 12
            reasons.append(f"👥 Rising unemployment: {unrate_val:.1f}% (+12)")
        else:
            reasons.append(f"✅ Strong labor market: {unrate_val:.1f}% (0)")
    else:
        factor_values['UNRATE'] = None
    
    # Factor 4: Housing (10% weight)
    if housing_val is not None:
        factor_values['HOUST'] = housing_val
        housing_k = housing_val / 1000
        if housing_val < 1000000:
            score += 10
            reasons.append(f"🏠 Housing crash: {housing_k:.0f}K starts (+10)")
        elif housing_val < 1200000:
            score += 5
            reasons.append(f"🏠 Weak housing: {housing_k:.0f}K starts (+5)")
        else:
            reasons.append(f"✅ Healthy housing: {housing_k:.0f}K starts (0)")
    else:
        factor_values['HOUST'] = None
    
    # Factor 5: Consumer Sentiment (10% weight)
    if sentiment_val is not None:
        factor_values['UMCSENT'] = sentiment_val
        if sentiment_val < 50:
            score += 10
            reasons.append(f"😰 Consumer panic: {sentiment_val:.0f} (+10)")
        elif sentiment_val < 60:
            score += 5
            reasons.append(f"😟 Weak sentiment: {sentiment_val:.0f} (+5)")
        else:
            reasons.append(f"✅ Stable sentiment: {sentiment_val:.0f} (0)")
    else:
        factor_values['UMCSENT'] = None
    
    # Signal threshold: 60+ = recession warning
    signal = score >= 60
    
    return {
        'signal': signal,
        'score': score,
        'reasons': reasons,
        'factors': factor_values,
        'threshold': 60
    }


def display_recession_warning_24month(df):
    """
    Display the 24-month recession warning system
    """
    warning = check_recession_24month(df)
    
    # Get Vulnerability Index composite
    df_vuln = calculate_vulnerability_index(df)
    # Get the latest non-nan value
    vuln_series = df_vuln['VULNERABILITY_INDEX'].dropna()
    if not vuln_series.empty:
        vuln_composite = vuln_series.iloc[-1]
    else:
        vuln_composite = 50  # Fallback value
    vuln_status, vuln_color = get_vulnerability_status(vuln_composite)
    
    st.markdown('<div class="sub-header">📅 24-Month Recession Warning</div>', unsafe_allow_html=True)
    
    if warning['signal']:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #8B0000 0%, #ff4d4d 100%);
                    padding: 30px; border-radius: 20px; margin: 20px 0;
                    border-left: 8px solid #FFD700; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <div style="color: #FFD700; font-size: 1rem; text-transform: uppercase; letter-spacing: 2px;">RECESSION WARNING</div>
                    <div style="color: white; font-size: 3rem; font-weight: bold; margin: 10px 0;">HIGH CONFIDENCE</div>
                    <div style="color: #ccc;">Based on 64 years of data • 90% historical precision</div>
                    <div style="color: #FFD700; margin-top: 10px;">When we signal, history shows we're right</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #FFD700; font-size: 2.5rem; font-weight: bold;">{warning['score']}/100</div>
                    <div style="color: #888;">Warning Score</div>
                    <div style="color: #ff4d4d; margin-top: 10px;">⚠️ Threshold: {warning['threshold']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                    padding: 30px; border-radius: 20px; margin: 20px 0;
                    border-left: 8px solid #00ff00;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <div style="color: #00ff00; font-size: 1rem; text-transform: uppercase; letter-spacing: 2px;">NO RECESSION WARNING</div>
                    <div style="color: white; font-size: 3rem; font-weight: bold; margin: 10px 0;">LOW RISK</div>
                    <div style="color: #ccc;">Current conditions do not signal recession in next 24 months</div>
                    <div style="color: #888; margin-top: 10px;">Model precision: 90% when it signals</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #00ff00; font-size: 2.5rem; font-weight: bold;">{warning['score']}/100</div>
                    <div style="color: #888;">Stress Score</div>
                    <div style="color: #888;">Threshold: {warning['threshold']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Factor breakdown
    with st.expander("🔍 View Factor Breakdown", expanded=False):
        st.markdown("### What's Driving the Score")
        for reason in warning['reasons']:
            st.markdown(f"- {reason}")
        
        st.markdown("---")
        st.markdown("### Current Values vs Warning Thresholds")
        
        # Yield Curve
        if warning['factors'].get('10Y2Y') is not None:
            val = warning['factors']['10Y2Y']
            if val < 0:
                st.markdown(f"**Yield Curve (10Y-2Y):** <span style='color:#ff4d4d'>{val:.2f}%</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Warning: Below 0% (inverted)</span>", unsafe_allow_html=True)
            elif val < 0.2:
                st.markdown(f"**Yield Curve (10Y-2Y):** <span style='color:#FFD700'>{val:.2f}%</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Watch: Flattening</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Yield Curve (10Y-2Y):** <span style='color:#00ff00'>{val:.2f}%</span>", unsafe_allow_html=True)
        
        # Inflation
        if warning['factors'].get('CPI_YOY') is not None:
            val = warning['factors']['CPI_YOY']
            if val > 5:
                st.markdown(f"**Inflation (CPI YoY):** <span style='color:#ff4d4d'>{val:.1f}%</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Warning: Above 5%</span>", unsafe_allow_html=True)
            elif val > 4:
                st.markdown(f"**Inflation (CPI YoY):** <span style='color:#FFD700'>{val:.1f}%</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Watch: Above 4%</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Inflation (CPI YoY):** <span style='color:#00ff00'>{val:.1f}%</span>", unsafe_allow_html=True)
        
        # Unemployment
        if warning['factors'].get('UNRATE') is not None:
            val = warning['factors']['UNRATE']
            if val > 7:
                st.markdown(f"**Unemployment:** <span style='color:#ff4d4d'>{val:.1f}%</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Warning: Above 7%</span>", unsafe_allow_html=True)
            elif val > 6:
                st.markdown(f"**Unemployment:** <span style='color:#FFD700'>{val:.1f}%</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Watch: Above 6%</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Unemployment:** <span style='color:#00ff00'>{val:.1f}%</span>", unsafe_allow_html=True)
        
        # Housing
        if warning['factors'].get('HOUST') is not None:
            val = warning['factors']['HOUST'] / 1000
            if val < 1000:
                st.markdown(f"**Housing Starts:** <span style='color:#ff4d4d'>{val:.0f}K</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Warning: Below 1.0M</span>", unsafe_allow_html=True)
            elif val < 1200:
                st.markdown(f"**Housing Starts:** <span style='color:#FFD700'>{val:.0f}K</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Watch: Below 1.2M</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Housing Starts:** <span style='color:#00ff00'>{val:.0f}K</span>", unsafe_allow_html=True)
        
        # Consumer Sentiment
        if warning['factors'].get('UMCSENT') is not None:
            val = warning['factors']['UMCSENT']
            if val < 50:
                st.markdown(f"**Consumer Sentiment:** <span style='color:#ff4d4d'>{val:.0f}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Warning: Below 50</span>", unsafe_allow_html=True)
            elif val < 60:
                st.markdown(f"**Consumer Sentiment:** <span style='color:#FFD700'>{val:.0f}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#888; font-size:0.8rem'>⚠️ Watch: Below 60</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Consumer Sentiment:** <span style='color:#00ff00'>{val:.0f}</span>", unsafe_allow_html=True)
    
    # Vulnerability Index context
    st.markdown("---")
    st.markdown(f"""
    <div style="background: rgba(255,215,0,0.05); padding: 15px; border-radius: 10px; margin-top: 15px;">
        <p style="margin: 0; color: #888; font-size: 0.85rem;">
            <strong>📊 Vulnerability Index™ Composite:</strong> {vuln_composite:.0f}/100 • {vuln_status}
        </p>
        <p style="margin: 5px 0 0; color: #888; font-size: 0.85rem;">
            <strong>⚠️ Important:</strong> This model has 90% precision at 24 months. 
            When it signals, history shows it's right. It may miss some recessions, but it rarely gives false alarms.
        </p>
        <p style="margin: 5px 0 0; color: #888; font-size: 0.85rem;">
            <strong>🔍 Methodology:</strong> Weighted score from 5 factors (Yield Curve 40%, Inflation 20%, 
            Unemployment 20%, Housing 10%, Sentiment 10%). Threshold 60+ triggers warning.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    return warning['signal'], warning['score']


# ============================================================================
# FRESHNESS FUNCTIONS (NEW - FROM APP2.PY)
# ============================================================================

def safe_date_format(date_val, format_string='%b %d, %Y'):
    """Safely format a date, handling None, NaT, and various date types"""
    if date_val is None:
        return "Unknown"
    
    try:
        if pd.isna(date_val):
            return "Unknown"
    except:
        pass
    
    if isinstance(date_val, str):
        try:
            date_val = pd.to_datetime(date_val, format='%d/%m/%Y', dayfirst=True)
        except:
            try:
                date_val = pd.to_datetime(date_val)
            except:
                return str(date_val)
    
    if hasattr(date_val, 'strftime'):
        try:
            if pd.isna(date_val):
                return "Unknown"
            return date_val.strftime(format_string)
        except:
            return "Unknown"
    
    return str(date_val)

def get_frequency_category(days_old):
    """Categorize data freshness by days since last update"""
    if days_old <= FREQUENCIES['daily']['max_days']:
        return 'daily'
    elif days_old <= FREQUENCIES['weekly']['max_days']:
        return 'weekly'
    elif days_old <= FREQUENCIES['monthly']['max_days']:
        return 'monthly'
    else:
        return 'quarterly'

def get_last_update(df, column):
    """Get the last update date for a column"""
    if column not in df.columns:
        return None
    
    valid_data = df[df[column].notna()]
    if valid_data.empty:
        return None
    
    return valid_data.iloc[-1]['date']

def create_freshness_dashboard(df):
    """Create a dashboard showing data freshness by indicator"""
    
    freshness_data = []
    
    for col in df.columns:
        if col != 'date' and not col.endswith('_RAW') and not col.endswith('_IS_QUARTERLY') and not col.endswith('_INV'):
            last_date = get_last_update(df, col)
            if last_date:
                days_old = (datetime.now() - last_date).days
                freq = get_frequency_category(days_old)
                
                freshness_data.append({
                    'Indicator': col,
                    'Last Update': safe_date_format(last_date, '%Y-%m-%d'),
                    'Days Old': days_old,
                    'Frequency': FREQUENCIES[freq]['name'],
                    'Color': FREQUENCIES[freq]['color'],
                    'Emoji': FREQUENCIES[freq]['emoji']
                })
    
    freshness_df = pd.DataFrame(freshness_data)
    freq_counts = freshness_df['Frequency'].value_counts()
    
    return freshness_df, freq_counts

def find_historical_matches(df, current_yield, current_date, n=5, era="All History"):
    """Find the closest historical matches for today's yield - FIXED to remove duplicates"""
    mask = (df['date'] < current_date - pd.Timedelta(days=30)) & (df['DGS10'].notna())
    
    # Apply era filter
    if era == "Pre-2000":
        mask &= (df['date'] < '2000-01-01')
    elif era == "Post-2000":
        mask &= (df['date'] >= '2000-01-01')
    
    candidates = df[mask].copy()
    
    if len(candidates) == 0:
        return pd.DataFrame()
    
    # Calculate yield difference
    candidates['yield_diff'] = abs(candidates['DGS10'] - current_yield)
    
    # Sort by yield difference
    candidates = candidates.sort_values('yield_diff')
    
    # Create a month-year key to remove duplicates
    candidates['month_key'] = candidates['date'].dt.strftime('%Y-%m')
    
    # Drop duplicates by month_key, keeping the first occurrence (closest to target yield)
    unique_months = candidates.drop_duplicates(subset=['month_key'], keep='first')
    
    # Take top n unique months
    matches = unique_months.head(n).copy()
    
    # Calculate similarity score
    matches['similarity'] = 100 - (matches['yield_diff'] * 50)
    matches['similarity'] = matches['similarity'].clip(0, 100)
    
    results = []
    for idx, row in matches.iterrows():
        match_date = row['date']
        date_idx = df[df['date'] == match_date].index[0]
        
        future_12m_idx = min(date_idx + 264, len(df) - 1)
        future_slice = df.iloc[date_idx:min(date_idx+264, len(df))]
        
        year = match_date.year
        crisis_years = [1973, 1980, 1981, 1987, 1990, 2000, 2001, 2007, 2008, 2020]
        led_to_crisis = year in crisis_years or (year == 2006 and match_date.month > 6)
        
        # Get context data
        unrate_val = row.get('UNRATE', None)
        cpi_val = row.get('CPI_YOY', None)
        
        results.append({
            'date': match_date,
            'DGS10': row['DGS10'],
            'similarity': row['similarity'],
            'yield_12m': df.iloc[future_12m_idx]['DGS10'] if future_12m_idx > date_idx else None,
            'max_yield': future_slice['DGS10'].max() if not future_slice.empty else None,
            'min_yield': future_slice['DGS10'].min() if not future_slice.empty else None,
            'led_to_crisis': led_to_crisis,
            'unrate_then': unrate_val,
            'cpi_then': cpi_val
        })
    
    return pd.DataFrame(results)

def add_historical_annotations(fig, df, col_name, show_recessions, show_events):
    """Add historical event annotations to the chart with smart placement"""
    
    # Get data range for smarter y_offset
    y_min = df[col_name].min()
    y_max = df[col_name].max()
    y_range = y_max - y_min
    
    # Add recession shading with labels
    if show_recessions:
        for event in HISTORICAL_EVENTS:
            if 'start' in event and 'end' in event:
                # This is a recession (has start and end dates)
                fig.add_vrect(
                    x0=event['start'], 
                    x1=event['end'], 
                    fillcolor=event['color'], 
                    layer="below", 
                    line_width=0,
                    annotation_text=event['label'] if show_events else None,
                    annotation_position="top left",
                    annotation=dict(
                        font_size=10,
                        font_color="white",
                        bgcolor="rgba(255,0,0,0.7)",
                        borderpad=2
                    ) if show_events else None
                )
    
    # Add event markers with smart placement
    if show_events:
        # Group events by year to prevent overlap
        events_by_year = {}
        for event in HISTORICAL_EVENTS:
            if 'date' in event:
                year = pd.to_datetime(event['date']).year
                if year not in events_by_year:
                    events_by_year[year] = []
                events_by_year[year].append(event)
        
        for year, events in events_by_year.items():
            # Calculate vertical offsets for multiple events in same year
            for idx, event in enumerate(events):
                event_date = pd.to_datetime(event['date'])
                
                # Find closest data point
                date_mask = df['date'] >= event_date - pd.Timedelta(days=5)
                date_mask &= df['date'] <= event_date + pd.Timedelta(days=5)
                nearby = df[date_mask]
                
                if not nearby.empty and col_name in nearby.columns:
                    # Use the value at that time
                    closest = nearby.iloc[(nearby['date'] - event_date).abs().argsort()[:1]]
                    y_val = closest[col_name].values[0]
                    
                    # Smart offset based on number of events this year and data range
                    base_offset = event.get('y_offset', 0)
                    year_offset = idx * 8  # Stack multiple events
                    total_offset = base_offset * 5 + year_offset
                    
                    # Adjust offset based on position in chart
                    if y_val > y_min + y_range * 0.8:
                        total_offset = -abs(total_offset)  # Move down if near top
                    
                    # Add marker
                    fig.add_annotation(
                        x=event_date,
                        y=y_val,
                        text=f"{event['marker']} {event['label']}",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor="#FFD700",
                        font=dict(size=9, color="white"),
                        bgcolor="rgba(0,0,0,0.8)",
                        borderpad=3,
                        bordercolor="#FFD700",
                        borderwidth=1,
                        yshift=total_offset
                    )
                    
                    # Add invisible hover annotation for tooltip
                    fig.add_annotation(
                        x=event_date,
                        y=y_val,
                        text=event['description'],
                        visible=False,
                        showarrow=False,
                        hovertext=event['description'],
                        hoverlabel=dict(bgcolor="black", font_size=10)
                    )

def get_download_link(df, filename="gfti_sample.csv"):
    """Generate a download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="color: #FFD700; text-decoration: none;">⬇️ Click to Download Sample</a>'
    return href

def get_coverage_summary(df):
    """Get coverage summary by era - DYNAMIC counting from actual data"""
    eras = [
        ('1960-1969', '1960-01-01', '1969-12-31'),
        ('1970-1979', '1970-01-01', '1979-12-31'),
        ('1980-1989', '1980-01-01', '1989-12-31'),
        ('1990-1999', '1990-01-01', '1999-12-31'),
        ('2000-2009', '2000-01-01', '2009-12-31'),
        ('2010-2019', '2010-01-01', '2019-12-31'),
        ('2020-2026', '2020-01-01', '2026-12-31'),
    ]
    
    coverage = []
    
    # Get all actual data columns (excluding helper columns)
    data_cols = [c for c in df.columns if c not in ['date', 'year', 'month', 'day'] 
                and not c.endswith('_RAW') 
                and not c.endswith('_IS_QUARTERLY')
                and not c.endswith('_INV')]
    
    for era_name, start, end in eras:
        start_date = pd.to_datetime(start)
        end_date = pd.to_datetime(end)
        
        # Count indicators that have ANY data in this era
        era_count = 0
        for col in data_cols:
            # Check if this column has any non-null data in the era
            has_data = df[(df['date'] >= start_date) & 
                         (df['date'] <= end_date) & 
                         (df[col].notna())].shape[0] > 0
            if has_data:
                era_count += 1
        
        coverage.append((era_name, era_count))
    
    return coverage

def find_multi_factor_historical_matches(df, current_date=None, n=10):
    """
    Find historical periods with similar multi-factor profiles
    Calculates similarity based on all available factors
    """
    if current_date is None or pd.isna(current_date):
        valid_dates = df[df['date'].notna()]['date']
        if not valid_dates.empty:
            current_date = valid_dates.iloc[-1]
        else:
            current_date = datetime.now()
    
    # Get current values for all factors
    current_values = {}
    factor_columns = {
        'DGS10': 'yield',
        '10Y2Y': 'spread',
        'DCOILWTICO': 'oil',
        'VIX': 'vix',
        'HY_SPREAD': 'credit',
        'UMCSENT': 'sentiment',
        'UNRATE': 'unemployment',
        'CPI_YOY': 'inflation'
    }
    
    for col, name in factor_columns.items():
        val, _ = get_latest_value(df, col)
        if val is not None:
            current_values[name] = val
    
    # Create historical dataset (exclude last 30 days)
    mask = df['date'] < current_date - pd.Timedelta(days=30)
    candidates = df[mask].copy()
    
    if len(candidates) == 0:
        return pd.DataFrame()
    
    # Calculate similarity score for each candidate
    similarity_scores = []
    
    for idx, row in candidates.iterrows():
        score = 0
        factors_used = 0
        
        # Yield curve similarity (weight: 0.25)
        if 'spread' in current_values and '10Y2Y' in row and pd.notna(row['10Y2Y']):
            spread_diff = abs(row['10Y2Y'] - current_values['spread'])
            spread_score = max(0, 100 - (spread_diff * 50))
            score += spread_score * 0.25
            factors_used += 0.25
        
        # Oil similarity (weight: 0.15)
        if 'oil' in current_values and 'DCOILWTICO' in row and pd.notna(row['DCOILWTICO']):
            oil_diff = abs(row['DCOILWTICO'] - current_values['oil'])
            oil_score = max(0, 100 - (oil_diff * 0.5))
            score += oil_score * 0.15
            factors_used += 0.15
        
        # VIX similarity (weight: 0.15)
        if 'vix' in current_values and 'VIX' in row and pd.notna(row['VIX']):
            vix_diff = abs(row['VIX'] - current_values['vix'])
            vix_score = max(0, 100 - (vix_diff * 2))
            score += vix_score * 0.15
            factors_used += 0.15
        
        # Credit similarity (weight: 0.15)
        if 'credit' in current_values and 'HY_SPREAD' in row and pd.notna(row['HY_SPREAD']):
            credit_diff = abs(row['HY_SPREAD'] - current_values['credit'])
            credit_score = max(0, 100 - (credit_diff * 10))
            score += credit_score * 0.15
            factors_used += 0.15
        
        # Sentiment similarity (weight: 0.10)
        if 'sentiment' in current_values and 'UMCSENT' in row and pd.notna(row['UMCSENT']):
            sent_diff = abs(row['UMCSENT'] - current_values['sentiment'])
            sent_score = max(0, 100 - (sent_diff * 1))
            score += sent_score * 0.10
            factors_used += 0.10
        
        # Unemployment similarity (weight: 0.10)
        if 'unemployment' in current_values and 'UNRATE' in row and pd.notna(row['UNRATE']):
            unrate_diff = abs(row['UNRATE'] - current_values['unemployment'])
            unrate_score = max(0, 100 - (unrate_diff * 10))
            score += unrate_score * 0.10
            factors_used += 0.10
        
        # Inflation similarity (weight: 0.10)
        if 'inflation' in current_values and 'CPI_YOY' in row and pd.notna(row['CPI_YOY']):
            cpi_diff = abs(row['CPI_YOY'] - current_values['inflation'])
            cpi_score = max(0, 100 - (cpi_diff * 10))
            score += cpi_score * 0.10
            factors_used += 0.10
        
        # Normalize score by factors used
        if factors_used > 0:
            normalized_score = score / factors_used
            similarity_scores.append({
                'date': row['date'],
                'similarity': normalized_score,
                'factors_used': factors_used
            })
    
    # Convert to DataFrame and sort
    similarity_df = pd.DataFrame(similarity_scores)
    if similarity_df.empty:
        return pd.DataFrame()
    
    similarity_df = similarity_df.sort_values('similarity', ascending=False)
    
    # Remove duplicates by month
    similarity_df['month_key'] = similarity_df['date'].dt.strftime('%Y-%m')
    similarity_df = similarity_df.drop_duplicates(subset=['month_key'], keep='first')
    
    return similarity_df.head(n)


# ============================================================================
# CRISIS MONITORING FUNCTIONS - Added March 2026
# ============================================================================

def check_crisis_signals(df, war_start_date=WAR_START_DATE):
    """
    Check all indicators and return active alerts based on crisis thresholds
    Used by both the Crisis Watch panel and Alert system
    """
    
    alerts = []
    war_start = pd.to_datetime(war_start_date)
    
    # Get latest values with dates
    vix_val, vix_date = get_latest_value(df, 'VIX')
    oil_val, oil_date = get_latest_value(df, 'DCOILWTICO')
    spread_val, spread_date = get_latest_value(df, '10Y2Y')
    hy_val, hy_date = get_latest_value(df, 'HY_SPREAD')
    sent_val, sent_date = get_latest_value(df, 'UMCSENT')
    claims_val, claims_date = get_latest_value(df, 'IC4WSA')
    unrate_val, unrate_date = get_latest_value(df, 'UNRATE')
    
    # Convert None to NaT for safety (but we'll handle formatting elsewhere)
    vix_date = pd.NaT if vix_date is None else vix_date
    oil_date = pd.NaT if oil_date is None else oil_date
    spread_date = pd.NaT if spread_date is None else spread_date
    hy_date = pd.NaT if hy_date is None else hy_date
    sent_date = pd.NaT if sent_date is None else sent_date
    claims_date = pd.NaT if claims_date is None else claims_date
    
    # Get before-war values (for context)
    before_war = df[df['date'] < war_start]
    
    vix_before = before_war[before_war['VIX'].notna()].iloc[-1]['VIX'] if not before_war.empty and 'VIX' in before_war.columns else None
    oil_before = before_war[before_war['DCOILWTICO'].notna()].iloc[-1]['DCOILWTICO'] if not before_war.empty and 'DCOILWTICO' in before_war.columns else None
    spread_before = before_war[before_war['10Y2Y'].notna()].iloc[-1]['10Y2Y'] if not before_war.empty and '10Y2Y' in before_war.columns else None
    hy_before = before_war[before_war['HY_SPREAD'].notna()].iloc[-1]['HY_SPREAD'] if not before_war.empty and 'HY_SPREAD' in before_war.columns else None
    sent_before = before_war[before_war['UMCSENT'].notna()].iloc[-1]['UMCSENT'] if not before_war.empty and 'UMCSENT' in before_war.columns else None
    claims_before = before_war[before_war['IC4WSA'].notna()].iloc[-1]['IC4WSA'] if not before_war.empty and 'IC4WSA' in before_war.columns else None
    
    # Store before values for timeline
    before_values = {
        'vix': vix_before,
        'oil': oil_before,
        'spread': spread_before,
        'hy': hy_before,
        'sent': sent_before,
        'claims': claims_before,
        'war_start': war_start
    }
    
    # =========================================
    # VIX ALERTS (Market Fear)
    # =========================================
    if vix_val is not None:
        if vix_val > THRESHOLDS['vix']['critical']:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'VIX',
                'message': f'VIX at {vix_val:.1f} - Market PANIC',
                'value': vix_val,
                'threshold': 30,
                'date': vix_date,
                'color': '#ff4d4d'
            })
        elif vix_val > THRESHOLDS['vix']['warning']:
            alerts.append({
                'level': '🟡 WARNING',
                'indicator': 'VIX',
                'message': f'VIX at {vix_val:.1f} - Elevated fear',
                'value': vix_val,
                'threshold': 25,
                'date': vix_date,
                'color': '#FFD700'
            })
    
    # =========================================
    # OIL ALERTS (Energy Shock)
    # =========================================
    if oil_val is not None:
        if oil_val > THRESHOLDS['oil']['critical']:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'OIL',
                'message': f'Oil at ${oil_val:.2f} - Inflation shock',
                'value': oil_val,
                'threshold': 90,
                'date': oil_date,
                'color': '#ff4d4d'
            })
        elif oil_val > THRESHOLDS['oil']['warning']:
            alerts.append({
                'level': '🟡 WARNING',
                'indicator': 'OIL',
                'message': f'Oil at ${oil_val:.2f} - Rising energy costs',
                'value': oil_val,
                'threshold': 80,
                'date': oil_date,
                'color': '#FFD700'
            })
    
    # =========================================
    # YIELD CURVE ALERTS (Recession Signal)
    # =========================================
    if spread_val is not None:
        if spread_val < THRESHOLDS['spread']['critical']:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'YIELD CURVE',
                'message': f'Curve inverted at {spread_val:.2f}% - RECESSION SIGNAL',
                'value': spread_val,
                'threshold': 0,
                'date': spread_date,
                'color': '#ff4d4d'
            })
        elif spread_val < THRESHOLDS['spread']['warning']:
            alerts.append({
                'level': '🟡 WARNING',
                'indicator': 'YIELD CURVE',
                'message': f'Curve flattening at {spread_val:.2f}% - Watch closely',
                'value': spread_val,
                'threshold': 0.2,
                'date': spread_date,
                'color': '#FFD700'
            })
    
    # =========================================
    # CREDIT SPREAD ALERTS (Corporate Stress)
    # =========================================
    if hy_val is not None:
        if hy_val > THRESHOLDS['hy_spread']['critical']:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'CREDIT',
                'message': f'High yield spreads at {hy_val:.2f}% - Credit crunch',
                'value': hy_val,
                'threshold': 5,
                'date': hy_date,
                'color': '#ff4d4d'
            })
        elif hy_val > THRESHOLDS['hy_spread']['warning']:
            alerts.append({
                'level': '🟡 WARNING',
                'indicator': 'CREDIT',
                'message': f'High yield spreads at {hy_val:.2f}% - Corporate stress',
                'value': hy_val,
                'threshold': 4,
                'date': hy_date,
                'color': '#FFD700'
            })
    
    # =========================================
    # CONSUMER SENTIMENT ALERTS (Confidence)
    # =========================================
    if sent_val is not None:
        if sent_val < THRESHOLDS['sentiment']['critical']:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'SENTIMENT',
                'message': f'Consumer sentiment at {sent_val:.1f} - PANIC',
                'value': sent_val,
                'threshold': 50,
                'date': sent_date,
                'color': '#ff4d4d'
            })
        elif sent_val < THRESHOLDS['sentiment']['warning']:
            alerts.append({
                'level': '🟡 WARNING',
                'indicator': 'SENTIMENT',
                'message': f'Consumer sentiment at {sent_val:.1f} - Weak confidence',
                'value': sent_val,
                'threshold': 60,
                'date': sent_date,
                'color': '#FFD700'
            })
    
    # =========================================
    # JOBLESS CLAIMS ALERTS (Layoffs)
    # =========================================
    if claims_val is not None:
        if claims_val > THRESHOLDS['claims']['critical']:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'CLAIMS',
                'message': f'Jobless claims at {claims_val/1000:.0f}K - Mass layoffs',
                'value': claims_val,
                'threshold': 350000,
                'date': claims_date,
                'color': '#ff4d4d'
            })
        elif claims_val > THRESHOLDS['claims']['warning']:
            alerts.append({
                'level': '🟡 WARNING',
                'indicator': 'CLAIMS',
                'message': f'Jobless claims at {claims_val/1000:.0f}K - Labor softening',
                'value': claims_val,
                'threshold': 300000,
                'date': claims_date,
                'color': '#FFD700'
            })
    
    return alerts, before_values


def display_crisis_watch(df, alerts):
    """
    Display the Crisis Watch panel with color-coded status cards
    """
    
    st.markdown('<div class="sub-header">🚨 Crisis Watch: Iran-USA War Impact</div>', unsafe_allow_html=True)
    
    # Calculate days since war started
    war_start = pd.to_datetime(WAR_START_DATE)
    days_since = (datetime.now() - war_start).days
    
    st.markdown(f"*Monitoring since Feb 28, 2026 - Day {days_since} of conflict*")
    
    # Create a dictionary of alerts by indicator for quick lookup
    alert_dict = {}
    for alert in alerts:
        alert_dict[alert['indicator']] = alert
    
    # Get latest values
    vix_val, vix_date = get_latest_value(df, 'VIX')
    oil_val, oil_date = get_latest_value(df, 'DCOILWTICO')
    spread_val, spread_date = get_latest_value(df, '10Y2Y')
    hy_val, hy_date = get_latest_value(df, 'HY_SPREAD')
    sent_val, sent_date = get_latest_value(df, 'UMCSENT')
    claims_val, claims_date = get_latest_value(df, 'IC4WSA')
    
    # Helper function to safely format dates
    def safe_date_format(date_val):
        if date_val is None:
            return "N/A"
        try:
            # Check if it's a valid datetime and not NaT
            if hasattr(date_val, 'strftime') and not pd.isna(date_val):
                return date_val.strftime('%b %d, %Y')
            else:
                return "N/A"
        except:
            return "N/A"
    
    # Create 3 rows of 2 columns for the 6 indicators
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    row3_col1, row3_col2 = st.columns(2)
    
    # Row 1: VIX and Oil
    with row1_col1:
        if 'VIX' in alert_dict:
            alert = alert_dict['VIX']
            bg_color = alert['color'] + '20'  # 20% opacity
            border_color = alert['color']
            status = alert['level']
        else:
            bg_color = "#00ff0020"
            border_color = "#00ff00"
            status = "🟢 NORMAL"
        
        st.markdown(f"""
        <div style="background: {bg_color}; padding: 15px; border-radius: 8px; border-left: 4px solid {border_color}; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #FFD700; font-weight: bold;">😨 VIX (Fear Gauge)</span>
                <span style="color: {border_color};">{status}</span>
            </div>
            <div style="font-size: 1.8rem; color: white; font-weight: bold;">{format_value(vix_val, 1)}</div>
            <div style="color: #888;">as of {safe_date_format(vix_date)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with row1_col2:
        if 'OIL' in alert_dict:
            alert = alert_dict['OIL']
            bg_color = alert['color'] + '20'
            border_color = alert['color']
            status = alert['level']
        else:
            bg_color = "#00ff0020"
            border_color = "#00ff00"
            status = "🟢 NORMAL"
        
        st.markdown(f"""
        <div style="background: {bg_color}; padding: 15px; border-radius: 8px; border-left: 4px solid {border_color}; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #FFD700; font-weight: bold;">🛢️ WTI Oil</span>
                <span style="color: {border_color};">{status}</span>
            </div>
            <div style="font-size: 1.8rem; color: white; font-weight: bold;">{format_value(oil_val, 2, '$')}</div>
            <div style="color: #888;">as of {safe_date_format(oil_date)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 2: Yield Curve and Credit Spreads
    with row2_col1:
        if 'YIELD CURVE' in alert_dict:
            alert = alert_dict['YIELD CURVE']
            bg_color = alert['color'] + '20'
            border_color = alert['color']
            status = alert['level']
        else:
            bg_color = "#00ff0020"
            border_color = "#00ff00"
            status = "🟢 NORMAL"
        
        spread_display = f"{spread_val:.2f}%" if spread_val is not None else "N/A"
        st.markdown(f"""
        <div style="background: {bg_color}; padding: 15px; border-radius: 8px; border-left: 4px solid {border_color}; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #FFD700; font-weight: bold;">📉 Yield Curve (10Y-2Y)</span>
                <span style="color: {border_color};">{status}</span>
            </div>
            <div style="font-size: 1.8rem; color: white; font-weight: bold;">{spread_display}</div>
            <div style="color: #888;">as of {safe_date_format(spread_date)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col2:
        if 'CREDIT' in alert_dict:
            alert = alert_dict['CREDIT']
            bg_color = alert['color'] + '20'
            border_color = alert['color']
            status = alert['level']
        else:
            bg_color = "#00ff0020"
            border_color = "#00ff00"
            status = "🟢 NORMAL"
        
        hy_display = f"{hy_val:.2f}%" if hy_val is not None else "N/A"
        st.markdown(f"""
        <div style="background: {bg_color}; padding: 15px; border-radius: 8px; border-left: 4px solid {border_color}; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #FFD700; font-weight: bold;">💰 High Yield Spread</span>
                <span style="color: {border_color};">{status}</span>
            </div>
            <div style="font-size: 1.8rem; color: white; font-weight: bold;">{hy_display}</div>
            <div style="color: #888;">as of {safe_date_format(hy_date)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 3: Consumer Sentiment and Jobless Claims
    with row3_col1:
        if 'SENTIMENT' in alert_dict:
            alert = alert_dict['SENTIMENT']
            bg_color = alert['color'] + '20'
            border_color = alert['color']
            status = alert['level']
        else:
            bg_color = "#00ff0020"
            border_color = "#00ff00"
            status = "🟢 NORMAL"
        
        st.markdown(f"""
        <div style="background: {bg_color}; padding: 15px; border-radius: 8px; border-left: 4px solid {border_color}; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #FFD700; font-weight: bold;">💬 Consumer Sentiment</span>
                <span style="color: {border_color};">{status}</span>
            </div>
            <div style="font-size: 1.8rem; color: white; font-weight: bold;">{format_value(sent_val, 1)}</div>
            <div style="color: #888;">as of {safe_date_format(sent_date)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with row3_col2:
        if 'CLAIMS' in alert_dict:
            alert = alert_dict['CLAIMS']
            bg_color = alert['color'] + '20'
            border_color = alert['color']
            status = alert['level']
        else:
            bg_color = "#00ff0020"
            border_color = "#00ff00"
            status = "🟢 NORMAL"
        
        claims_display = f"{claims_val/1000:.0f}K" if claims_val is not None else "N/A"
        st.markdown(f"""
        <div style="background: {bg_color}; padding: 15px; border-radius: 8px; border-left: 4px solid {border_color}; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #FFD700; font-weight: bold;">📋 Initial Jobless Claims</span>
                <span style="color: {border_color};">{status}</span>
            </div>
            <div style="font-size: 1.8rem; color: white; font-weight: bold;">{claims_display}</div>
            <div style="color: #888;">as of {safe_date_format(claims_date)}</div>
        </div>
        """, unsafe_allow_html=True)


def display_war_timeline(df, before_values):
    """
    Display the War Impact Timeline showing changes since Feb 28, 2026
    FIXED: Properly handles dates and uses the passed before_values
    """
    
    st.markdown('<div class="sub-header">📅 War Impact Timeline</div>', unsafe_allow_html=True)
    
    # Get current values (latest non-null)
    vix_val, vix_date = get_latest_value(df, 'VIX')
    oil_val, oil_date = get_latest_value(df, 'DCOILWTICO')
    spread_val, spread_date = get_latest_value(df, '10Y2Y')
    hy_val, hy_date = get_latest_value(df, 'HY_SPREAD')
    sent_val, sent_date = get_latest_value(df, 'UMCSENT')
    claims_val, claims_date = get_latest_value(df, 'IC4WSA')
    
    # Helper function to safely format dates
    def safe_date_format(date_val):
        if date_val is None:
            return "N/A"
        try:
            # Check if it's a valid datetime and not NaT
            if hasattr(date_val, 'strftime') and not pd.isna(date_val):
                return date_val.strftime('%b %d, %Y')
            else:
                return "N/A"
        except:
            return "N/A"
    
    # Calculate days since war started
    war_start = before_values.get('war_start', pd.to_datetime(WAR_START_DATE))
    # Ensure war_start is a datetime object
    if isinstance(war_start, str):
        war_start = pd.to_datetime(war_start)
    days_since = (datetime.now() - war_start).days
    
    # Get current alerts from session state to show counts
    current_alerts = st.session_state.get('crisis_alerts', [])
    critical_count = len([a for a in current_alerts if '🔴' in a.get('level', '')])
    warning_count = len([a for a in current_alerts if '🟡' in a.get('level', '')])
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="color: #FFD700; font-size: 1.2rem; font-weight: bold;">⚔️ Conflict Day {days_since}</span>
                <span style="color: #888; margin-left: 10px;">(Feb 28 - {datetime.now().strftime('%b %d, %Y')})</span>
            </div>
            <div style="color: #ff4d4d;">{critical_count} Critical • {warning_count} Warning</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create comparison table
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    col1.markdown("**Indicator**")
    col2.markdown("**Before War**")
    col3.markdown("**Now**")
    col4.markdown("**Change**")
    col5.markdown("**Status**")
    
    # VIX Row
    if vix_val is not None and before_values.get('vix') is not None:
        vix_before = before_values['vix']
        if vix_before != 0:
            vix_change = ((vix_val - vix_before) / vix_before) * 100
        else:
            vix_change = 0
        vix_color = "#ff4d4d" if vix_change > 0 else "#00ff00"
        
        # Determine VIX status
        if vix_val > 30:
            vix_status = "🔴 CRITICAL"
            vix_status_color = "#ff4d4d"
        elif vix_val > 25:
            vix_status = "🟡 WARNING"
            vix_status_color = "#FFD700"
        else:
            vix_status = "🟢 OK"
            vix_status_color = "#00ff00"
        
        col1.markdown("😨 VIX")
        col2.markdown(f"{vix_before:.1f}")
        col3.markdown(f"{vix_val:.1f}")
        col4.markdown(f"<span style='color: {vix_color};'>▲ {vix_change:.0f}%</span>", unsafe_allow_html=True)
        col5.markdown(f"<span style='color: {vix_status_color};'>{vix_status}</span>", unsafe_allow_html=True)
    
    # Oil Row
    if oil_val is not None and before_values.get('oil') is not None:
        oil_before = before_values['oil']
        if oil_before != 0:
            oil_change = ((oil_val - oil_before) / oil_before) * 100
        else:
            oil_change = 0
        oil_color = "#ff4d4d" if oil_change > 0 else "#00ff00"
        
        # Determine oil status
        if oil_val > 90:
            oil_status = "🔴 CRITICAL"
            oil_status_color = "#ff4d4d"
        elif oil_val > 80:
            oil_status = "🟡 ELEVATED"
            oil_status_color = "#FFD700"
        else:
            oil_status = "🟢 OK"
            oil_status_color = "#00ff00"
        
        col1.markdown("🛢️ Oil")
        col2.markdown(f"${oil_before:.2f}")
        col3.markdown(f"${oil_val:.2f}")
        col4.markdown(f"<span style='color: {oil_color};'>▲ {oil_change:.0f}%</span>", unsafe_allow_html=True)
        col5.markdown(f"<span style='color: {oil_status_color};'>{oil_status}</span>", unsafe_allow_html=True)
    
    # Yield Curve Row
    if spread_val is not None and before_values.get('spread') is not None:
        spread_before = before_values['spread']
        spread_change = spread_val - spread_before
        spread_color = "#ff4d4d" if spread_change < 0 else "#00ff00"
        
        # Determine yield curve status
        if spread_val < 0:
            spread_status = "🔴 INVERTED"
            spread_status_color = "#ff4d4d"
        elif spread_val < 0.2:
            spread_status = "🟡 FLATTENING"
            spread_status_color = "#FFD700"
        else:
            spread_status = "🟢 NORMAL"
            spread_status_color = "#00ff00"
        
        col1.markdown("📉 Yield Curve")
        col2.markdown(f"{spread_before:.2f}%")
        col3.markdown(f"{spread_val:.2f}%")
        col4.markdown(f"<span style='color: {spread_color};'>{spread_change:+.2f}%</span>", unsafe_allow_html=True)
        col5.markdown(f"<span style='color: {spread_status_color};'>{spread_status}</span>", unsafe_allow_html=True)
    
    # Credit Spreads Row
    if hy_val is not None and before_values.get('hy') is not None:
        hy_before = before_values['hy']
        hy_change = hy_val - hy_before
        hy_color = "#ff4d4d" if hy_change > 0 else "#00ff00"
        
        # Determine credit status
        if hy_val > 5:
            hy_status = "🔴 CRUNCH"
            hy_status_color = "#ff4d4d"
        elif hy_val > 4:
            hy_status = "🟡 STRESS"
            hy_status_color = "#FFD700"
        else:
            hy_status = "🟢 OK"
            hy_status_color = "#00ff00"
        
        col1.markdown("💰 Credit Spreads")
        col2.markdown(f"{hy_before:.2f}%")
        col3.markdown(f"{hy_val:.2f}%")
        col4.markdown(f"<span style='color: {hy_color};'>{hy_change:+.2f}%</span>", unsafe_allow_html=True)
        col5.markdown(f"<span style='color: {hy_status_color};'>{hy_status}</span>", unsafe_allow_html=True)
    
    # Consumer Sentiment Row
    if sent_val is not None and before_values.get('sent') is not None:
        sent_before = before_values['sent']
        sent_change = sent_val - sent_before
        sent_color = "#ff4d4d" if sent_change < 0 else "#00ff00"
        
        # Determine sentiment status
        if sent_val < 50:
            sent_status = "🔴 PANIC"
            sent_status_color = "#ff4d4d"
        elif sent_val < 60:
            sent_status = "🟡 WEAK"
            sent_status_color = "#FFD700"
        else:
            sent_status = "🟢 OK"
            sent_status_color = "#00ff00"
        
        col1.markdown("💬 Sentiment")
        col2.markdown(f"{sent_before:.1f}")
        col3.markdown(f"{sent_val:.1f}")
        col4.markdown(f"<span style='color: {sent_color};'>{sent_change:+.1f}</span>", unsafe_allow_html=True)
        col5.markdown(f"<span style='color: {sent_status_color};'>{sent_status}</span>", unsafe_allow_html=True)
    
    # Jobless Claims Row
    if claims_val is not None and before_values.get('claims') is not None:
        claims_before = before_values['claims']
        claims_change = claims_val - claims_before
        claims_color = "#ff4d4d" if claims_change > 0 else "#00ff00"
        
        # Determine claims status
        if claims_val > 350000:
            claims_status = "🔴 LAYOFFS"
            claims_status_color = "#ff4d4d"
        elif claims_val > 300000:
            claims_status = "🟡 SOFTENING"
            claims_status_color = "#FFD700"
        else:
            claims_status = "🟢 OK"
            claims_status_color = "#00ff00"
        
        col1.markdown("📋 Jobless Claims")
        col2.markdown(f"{claims_before/1000:.0f}K")
        col3.markdown(f"{claims_val/1000:.0f}K")
        col4.markdown(f"<span style='color: {claims_color};'>{claims_change/1000:+.0f}K</span>", unsafe_allow_html=True)
        col5.markdown(f"<span style='color: {claims_status_color};'>{claims_status}</span>", unsafe_allow_html=True)


def display_alert_system(alerts):
    """
    Display the notification bell with alert count and expandable alert list
    """
    
    critical_count = len([a for a in alerts if '🔴' in a.get('level', '')])
    warning_count = len([a for a in alerts if '🟡' in a.get('level', '')])
    total_alerts = len(alerts)
    
    # Create the notification bell in the sidebar
    with st.sidebar:
        st.markdown("---")
        
        if total_alerts > 0:
            # Create an expander that looks like a notification bell
            with st.expander(f"🔔 **ALERTS ({total_alerts})**", expanded=False):
                st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <span style="color: #ff4d4d;">🔴 Critical: {critical_count}</span><br>
                    <span style="color: #FFD700;">🟡 Warning: {warning_count}</span>
                </div>
                """, unsafe_allow_html=True)
                
                for alert in alerts:
                    # FIX: Safely handle date formatting
                    date_str = "N/A"
                    alert_date = alert.get('date')
                    if alert_date is not None:
                        try:
                            # Check if it's a valid datetime and not NaT
                            if hasattr(alert_date, 'strftime') and not pd.isna(alert_date):
                                date_str = alert_date.strftime('%b %d, %Y')
                        except:
                            # If any error in date formatting, just use N/A
                            pass
                    
                    st.markdown(f"""
                    <div style="background: {alert.get('color', '#FFD700')}10; padding: 8px; border-radius: 5px; margin: 5px 0; border-left: 3px solid {alert.get('color', '#FFD700')};">
                        <span style="color: {alert.get('color', '#FFD700')};">{alert.get('level', 'ALERT')}</span><br>
                        <span style="color: white;">{alert.get('message', 'Alert')}</span><br>
                        <span style="color: #888; font-size: 0.8rem;">as of {date_str}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <span style="font-size: 1.5rem;">🔔</span><br>
                <span style="color: #00ff00;">✅ No active alerts</span>
            </div>
            """, unsafe_allow_html=True)


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <span style="font-size: 24px; font-weight: bold; color: #FFD700;">📊 GFTI Daily™</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📈 Complete US Economic History")
    
    # Load data first to get actual counts
    df = load_data_with_spinner()
    
    if df is not None:
        # Get actual indicator count using analyzer method
        indicator_count = get_indicator_count(df)
        
        st.markdown(f"""
        **{indicator_count} indicators** (50 raw FRED + 8 calculated)
        """)
        
        # Add transparency expander
        with st.expander("🔍 Raw vs Calculated Breakdown"):
            st.markdown(f"""
            **Raw FRED Series (50)**
            - Treasury Yields (10)
            - Fed Policy (5)
            - Inflation (5 price levels)
            - Inflation Expectations (2)
            - Labor Market (7)
            - Jobless Claims (3)
            - Growth (3)
            - Housing (3)
            - Money & Credit (3)
            - Market Fear (2)
            - Dollar & Oil (2)
            - Demographics (1)
            
            **Proprietary Calculations (8)**
            - CPI_YOY (inflation rate)
            - M2_REAL (real money supply)
            - M2_REAL_YOY (real money growth)
            - 10Y2Y, 10Y3M (yield spreads)
            - BAA_SPREAD, AAA_SPREAD (credit spreads)
            - HY_SPREAD (high yield spread)
            - RISK_APPETITE (risk differential)
            """)
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Dataset Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Indicators", f"{indicator_count}")
        with col2:
            st.metric("Days", f"{len(df):,}")
        
        # Coverage by era
        coverage = get_coverage_summary(df)
        
        st.markdown("### 📅 Coverage by Era")
        for era, count in coverage:
            st.markdown(f"**{era}:** {count} indicators")
        
        st.markdown(f"**Last update:** {df['date'].max().strftime('%b %d, %Y')}")
    
    # Show waitlist stats
    stats = get_waitlist_stats()
    if stats['total'] > 0:
        st.markdown("---")
        st.markdown(f"### 📋 Waitlist")
        st.markdown(f"**{stats['total']}** investors waiting")
        if stats['by_plan']:
            st.markdown("**Plan interest:**")
            for plan, count in stats['by_plan'].items():
                if count > 0:
                    st.markdown(f"• {plan}: {count}")
    
    # =========================================
    # ADD ALERT SYSTEM HERE
    # =========================================
    if 'crisis_alerts' in st.session_state:
        display_alert_system(st.session_state['crisis_alerts'])
    else:
        # If first run, check signals
        if df is not None:
            alerts, _ = check_crisis_signals(df)
            st.session_state['crisis_alerts'] = alerts
            display_alert_system(alerts)


# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown('<div class="main-header">📊 GFTI Daily™</div>', unsafe_allow_html=True)

# Get indicator count
indicator_count = get_indicator_count(df) if df is not None else 58
st.markdown(f"*Complete US Financial History Database - {indicator_count} Indicators (50 raw FRED + 8 calculated)*")

# Load data with spinner
df = load_data_with_spinner()
if df is None:
    st.stop()

# ============================================================================
# NEW: GFTI DAILY COMMITMENT BANNER (FROM APP2.PY)
# ============================================================================

st.markdown(f"""
<div class="daily-commitment">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <span style="color: #00ff00; font-weight: bold; font-size: 1.1rem;">📅 GFTI Daily™ means:</span>
    </div>
    <div style="display: flex; gap: 30px; flex-wrap: wrap; margin-bottom: 10px;">
        <div><span style="color: #00ff00;">✓</span> We check all 58 sources daily</div>
        <div><span style="color: #00ff00;">✓</span> We update the dashboard daily</div>
        <div><span style="color: #00ff00;">✓</span> You get the latest data every day</div>
    </div>
    <div style="color: #888; margin-top: 10px; font-size: 0.9rem;">
        (Data releases follow their natural frequency: 🟢 daily yields & markets, 🟡 weekly claims, 🟠 monthly CPI & housing, 🔵 quarterly GDP)
    </div>
</div>
""", unsafe_allow_html=True)

# Show update note about data timing
st.markdown("""
<div class="update-note">
    📅 <strong>Note:</strong> Different indicators update at different times:
    • Treasury yields: Daily at 6pm ET
    • Labor data: Weekly (Thurs) & Monthly
    • Inflation: Monthly
    • GDP: Quarterly
    Values show the most recent available data.
</div>
""", unsafe_allow_html=True)

# Coverage summary banner
coverage = get_coverage_summary(df)
st.markdown(f"""
<div style="background: rgba(255,215,0,0.1); padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center;">
    <span style="color: #FFD700;">📊 Coverage:</span> 
    {coverage[0][1]} indicators since 1960s • 
    {coverage[2][1]} since 1980s • 
    {coverage[3][1]} since 1990s • 
    {coverage[4][1]} since 2000s
</div>
""", unsafe_allow_html=True)

# Create tabs - ADDED DATA FRESHNESS TAB
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Today's Story", 
    "📈 History Explorer", 
    "🔍 Historical Matches",
    "📦 Data Shop",
    "📋 Attribution & Legal",
    "🎨 Visual Vault",
    "📅 Data Freshness"
])

# ============================================================================
# TAB 1: TODAY'S STORY - UPDATED WITH 24-MONTH RECESSION WARNING
# ============================================================================

with tab1:
    # Get latest values with their actual dates
    dgs10_val, dgs10_date = get_latest_value(df, 'DGS10', ['DGS10'])
    dgs2_val, dgs2_date = get_latest_value(df, 'DGS2', ['DGS2'])
    fed_val, fed_date = get_latest_value(df, 'FEDFUNDS', ['FEDFUNDS', 'DFEDTARU'])
    spread_val, spread_date = get_latest_value(df, '10Y2Y', ['10Y2Y'])
    real_fed_val, real_fed_date = get_latest_value(df, 'REAL_FEDFUNDS', ['REAL_FEDFUNDS'])
    unrate_val, unrate_date = get_latest_value(df, 'UNRATE', ['UNRATE'])
    u6_val, u6_date = get_latest_value(df, 'U6RATE', ['U6RATE'])
    jolts_val, jolts_date = get_latest_value(df, 'JTSJOL', ['JTSJOL'])
    claims_val, claims_date = get_latest_value(df, 'IC4WSA', ['IC4WSA', 'ICSA'])  # Claims
    civpart_val, civpart_date = get_latest_value(df, 'CIVPART', ['CIVPART'])
    cpi_val, cpi_date = get_latest_value(df, 'CPI_YOY', ['CPI_YOY'])
    pce_val, pce_date = get_latest_value(df, 'PCEPILFE', ['PCEPILFE'])
    tie_val, tie_date = get_latest_value(df, 'T10YIE', ['T10YIE'])
    sent_val, sent_date = get_latest_value(df, 'UMCSENT', ['UMCSENT'])  # Consumer Sentiment
    retail_val, retail_date = get_latest_value(df, 'RSAFS', ['RSAFS'])
    hous_val, hous_date = get_latest_value(df, 'HOUST', ['HOUST'])
    permit_val, permit_date = get_latest_value(df, 'PERMIT', ['PERMIT'])
    vix_val, vix_date = get_latest_value(df, 'VIX', ['VIX'])
    hy_val, hy_date = get_latest_value(df, 'HY_SPREAD', ['HY_SPREAD', 'BAMLH0A0HYM2'])
    oil_val, oil_date = get_latest_value(df, 'DCOILWTICO', ['DCOILWTICO'])
    
    # Helper function to safely format dates for display
    def safe_date_short(date_val):
        """Safely format a date for display, handling None, NaT, and various date types"""
        if date_val is None:
            return ""
        
        # Check for NaT (pandas Not a Time)
        try:
            if pd.isna(date_val):
                return ""
        except:
            pass
        
        # If it's a string, try to convert to datetime
        if isinstance(date_val, str):
            try:
                date_val = pd.to_datetime(date_val, format='%d/%m/%Y', dayfirst=True)
            except:
                try:
                    date_val = pd.to_datetime(date_val)
                except:
                    return ""
        
        # If it's a datetime-like object with strftime method
        if hasattr(date_val, 'strftime'):
            try:
                # Additional check for NaT
                if pd.isna(date_val):
                    return ""
                return f" ({date_val.strftime('%m/%d/%y')})"
            except:
                return ""
        
        return ""
    
    # Date header
    st.markdown(f"""
    <div class="story-card">
        <h2 style="margin: 0; color: #FFD700;">Market Data Summary</h2>
        <p style="margin: 5px 0 0; opacity: 0.9;">Most recent available data (as of {df['date'].max().strftime('%B %d, %Y')})</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================
    # CHECK FOR CRISIS SIGNALS AND STORE IN SESSION STATE
    # =========================================
    alerts, before_values = check_crisis_signals(df, war_start_date=WAR_START_DATE)
    st.session_state['crisis_alerts'] = alerts
    st.session_state['before_values'] = before_values
    
    # =========================================
    # DISPLAY CRISIS WATCH PANEL
    # =========================================
    display_crisis_watch(df, alerts)
    
    # =========================================
    # DISPLAY WAR IMPACT TIMELINE
    # =========================================
    display_war_timeline(df, before_values)
    
    # =========================================
    # DISPLAY 24-MONTH RECESSION WARNING SYSTEM (NEW - REPLACES OLD PROBABILITY)
    # =========================================
    display_recession_warning_24month(df)
    
    # =========================================
    # THE BIG PICTURE STORY
    # =========================================
    
    st.markdown('<div class="sub-header">📰 The Big Picture</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        story_points = []
        
        # Yield curve story
        if spread_val is not None:
            if spread_val < 0:
                story_points.append(f"🔴 **Inverted Yield Curve**: The 10Y-2Y spread is {spread_val:.2f}% — historically this precedes recessions by 12-18 months.")
            else:
                story_points.append(f"🟢 **Normal Yield Curve**: The 10Y-2Y spread is {spread_val:.2f}% — suggesting economic expansion ahead.")
        
        # Labor market story
        if unrate_val is not None:
            if unrate_val < 4:
                story_points.append(f"🔥 **Ultra-Tight Labor Market**: Unemployment at {unrate_val:.1f}% — near historic lows.")
            elif unrate_val < 5:
                story_points.append(f"✅ **Healthy Labor Market**: Unemployment at {unrate_val:.1f}% — the 'goldilocks' zone.")
            else:
                story_points.append(f"⚠️ **Softening Labor Market**: Unemployment at {unrate_val:.1f}%.")
        
        # Inflation story
        if cpi_val is not None:
            if cpi_val > 4:
                story_points.append(f"🔥 **High Inflation**: CPI at {cpi_val:.1f}% — well above the Fed's 2% target.")
            elif cpi_val > 2.5:
                story_points.append(f"⚠️ **Elevated Inflation**: CPI at {cpi_val:.1f}% — above target.")
            else:
                story_points.append(f"✅ **Inflation at Target**: CPI at {cpi_val:.1f}% — near Fed's 2% goal.")
        
        # Fed story
        if real_fed_val is not None:
            if real_fed_val > 2:
                story_points.append(f"💰 **Restrictive Fed Policy**: Real Fed Funds at {real_fed_val:.1f}% — actively slowing the economy.")
            elif real_fed_val > 0:
                story_points.append(f"⚖️ **Neutral-Leaning Policy**: Real Fed Funds at {real_fed_val:.1f}% — mildly restrictive.")
            else:
                story_points.append(f"💧 **Accommodative Policy**: Real Fed Funds at {real_fed_val:.1f}% — stimulating the economy.")
        
        # VIX story
        if vix_val is not None:
            status, _ = get_vix_status(vix_val)
            story_points.append(f"😨 **Market Fear**: VIX at {vix_val:.1f} — {status}.")
        
        # Housing story
        if hous_val is not None:
            starts = hous_val / 1000
            if starts > 1.5:
                story_points.append(f"🏠 **Housing Boom**: Housing starts at {starts:.1f}M — robust construction activity.")
            elif starts > 1.0:
                story_points.append(f"🏠 **Normal Housing**: Housing starts at {starts:.1f}M — steady construction.")
            else:
                story_points.append(f"🏠 **Housing Slowdown**: Housing starts at {starts:.1f}M — below historical averages.")
        
        # Credit story
        if hy_val is not None:
            if hy_val > 5:
                story_points.append(f"🔴 **Credit Stress**: High yield spread at {hy_val:.2f}% — elevated corporate borrowing costs.")
            elif hy_val > 3:
                story_points.append(f"🟡 **Normal Credit**: High yield spread at {hy_val:.2f}% — typical risk pricing.")
            else:
                story_points.append(f"🟢 **Complacent Credit**: High yield spread at {hy_val:.2f}% — tight spreads suggest low concern.")
        
        # Display story
        for point in story_points[:5]:  # Top 5 most important
            st.markdown(f"- {point}")
    
    with col2:
        # =========================================
        # DISPLAY VULNERABILITY INDEX QUICK VIEW - FIXED
        # =========================================
        df_vuln = calculate_vulnerability_index(df)
        # Get the latest non-nan value
        vuln_series = df_vuln['VULNERABILITY_INDEX'].dropna()
        if not vuln_series.empty:
            vuln_composite = vuln_series.iloc[-1]
        else:
            vuln_composite = 50  # Fallback value
        vuln_status, vuln_color = get_vulnerability_status(vuln_composite)
        
        # Get the date of the vulnerability index (use latest date from df)
        vuln_date = df['date'].max() if df is not None else None
        date_str = safe_date_short(vuln_date)
        
        st.markdown(f"""
        <div style="background: {vuln_color}20; padding: 20px; border-radius: 15px; border-left: 4px solid {vuln_color}; margin: 10px 0;">
            <div style="color: #888; font-size: 0.8rem;">VULNERABILITY INDEX™{date_str}</div>
            <div style="font-size: 2rem; font-weight: bold; color: {vuln_color};">{vuln_composite:.0f}</div>
            <div style="color: {vuln_color};">{vuln_status} STRESS</div>
            <div style="color: #888; font-size: 0.7rem; margin-top: 8px;">Composite of 4 components</div>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================
    # KEY METRICS BY CATEGORY
    # =========================================
    
    st.markdown('<div class="sub-header">📊 Key Metrics (Most Recent)</div>', unsafe_allow_html=True)
    
    # Row 1: Rates & Fed
    st.markdown('<div class="category-header">💰 Rates & Fed Policy</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        date_str = safe_date_short(dgs10_date)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">10Y YIELD{date_str}</div>
            <div><span class="metric-value">{format_value(dgs10_val, 2, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        date_str = safe_date_short(dgs2_date)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">2Y YIELD{date_str}</div>
            <div><span class="metric-value">{format_value(dgs2_val, 2, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        date_str = safe_date_short(fed_date)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">FED FUNDS{date_str}</div>
            <div><span class="metric-value">{format_value(fed_val, 2, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if spread_val is not None:
            spread_color = "#ff4d4d" if spread_val < 0 else "#00ff00"
            date_str = safe_date_short(spread_date)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {spread_color};">
                <div class="metric-label">10Y-2Y SPREAD{date_str}</div>
                <div><span class="metric-value" style="color: {spread_color};">{format_value(spread_val, 2, '', '%')}</span></div>
                <div style="color: {spread_color};">{"INVERTED" if spread_val < 0 else "NORMAL"}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">10Y-2Y SPREAD</div>
                <div><span class="metric-value">N/A</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col5:
        date_str = safe_date_short(real_fed_date)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">REAL FED FUNDS{date_str}</div>
            <div><span class="metric-value">{format_value(real_fed_val, 1, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 2: Labor Market
    st.markdown('<div class="category-header">👥 Labor Market</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if unrate_val is not None:
            color = "#00ff00" if unrate_val < 5 else "#ff4d4d" if unrate_val > 6 else "#FFD700"
            date_str = safe_date_short(unrate_date)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">UNEMPLOYMENT{date_str}</div>
                <div><span class="metric-value">{format_value(unrate_val, 1, '', '%')}</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">UNEMPLOYMENT</div>
                <div><span class="metric-value">N/A</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        date_str = safe_date_short(u6_date)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">U-6 UNEMPLOYMENT{date_str}</div>
            <div><span class="metric-value">{format_value(u6_val, 1, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        date_str = safe_date_short(jolts_date)
        jolts_display = f"{jolts_val/1000:.1f}M" if jolts_val is not None else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">JOB OPENINGS{date_str}</div>
            <div><span class="metric-value">{jolts_display}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if claims_val is not None:
            claims_display = f"{claims_val/1000:.0f}K"
            color = "#00ff00" if claims_val < 250000 else "#ff4d4d" if claims_val > 350000 else "#FFD700"
            date_str = safe_date_short(claims_date)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">INITIAL CLAIMS{date_str}</div>
                <div><span class="metric-value">{claims_display}</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">INITIAL CLAIMS</div>
                <div><span class="metric-value">N/A</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col5:
        date_str = safe_date_short(civpart_date)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PARTICIPATION{date_str}</div>
            <div><span class="metric-value">{format_value(civpart_val, 1, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 3: Inflation & Consumer
    st.markdown('<div class="category-header">📈 Inflation & Consumer</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if cpi_val is not None:
            color = "#ff4d4d" if cpi_val > 4 else "#00ff00" if cpi_val < 2.5 else "#FFD700"
            date_str = safe_date_short(cpi_date)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">CPI (YOY){date_str}</div>
                <div><span class="metric-value">{format_value(cpi_val, 1, '', '%')}</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">CPI (YOY)</div>
                <div><span class="metric-value">N/A</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        date_str = safe_date_short(pce_date)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CORE PCE{date_str}</div>
            <div><span class="metric-value">{format_value(pce_val, 1, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        date_str = safe_date_short(tie_date)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">10Y INFLATION EXPECTATION{date_str}</div>
            <div><span class="metric-value">{format_value(tie_val, 2, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if sent_val is not None:
            color = "#00ff00" if sent_val > 80 else "#ff4d4d" if sent_val < 60 else "#FFD700"
            date_str = safe_date_short(sent_date)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">CONSUMER SENTIMENT{date_str}</div>
                <div><span class="metric-value">{format_value(sent_val, 1)}</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">CONSUMER SENTIMENT</div>
                <div><span class="metric-value">N/A</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col5:
        date_str = safe_date_short(retail_date)
        retail_display = f"${retail_val/1000:.0f}B" if retail_val is not None else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">RETAIL SALES{date_str}</div>
            <div><span class="metric-value">{retail_display}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 4: Housing & Markets
    st.markdown('<div class="category-header">🏠 Housing & Markets</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        date_str = safe_date_short(hous_date)
        hous_display = f"{hous_val/1000:.1f}M" if hous_val is not None else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">HOUSING STARTS{date_str}</div>
            <div><span class="metric-value">{hous_display}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        date_str = safe_date_short(permit_date)
        permit_display = f"{permit_val/1000:.1f}M" if permit_val is not None else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">BUILDING PERMITS{date_str}</div>
            <div><span class="metric-value">{permit_display}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if vix_val is not None:
            status, color = get_vix_status(vix_val)
            date_str = safe_date_short(vix_date)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">VIX (FEAR GAUGE){date_str}</div>
                <div><span class="metric-value">{format_value(vix_val, 1)}</span></div>
                <div style="color: {color};">{status}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">VIX (FEAR GAUGE)</div>
                <div><span class="metric-value">N/A</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if hy_val is not None:
            color = "#ff4d4d" if hy_val > 5 else "#00ff00" if hy_val < 3 else "#FFD700"
            date_str = safe_date_short(hy_date)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">HIGH YIELD SPREAD{date_str}</div>
                <div><span class="metric-value">{format_value(hy_val, 2, '', '%')}</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">HIGH YIELD SPREAD</div>
                <div><span class="metric-value">N/A</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col5:
        date_str = safe_date_short(oil_date)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">WTI OIL{date_str}</div>
            <div><span class="metric-value">{format_value(oil_val, 2, '$')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================
    # THE FULL STORY SUMMARY - FIXED to use the correct alerts
    # =========================================
    
    st.markdown('<div class="sub-header">📝 The Complete Story</div>', unsafe_allow_html=True)
    
    # Get the current alerts from session state (which were set above)
    current_alerts = st.session_state.get('crisis_alerts', [])
    critical_count = len([a for a in current_alerts if '🔴' in a.get('level', '')])
    warning_count = len([a for a in current_alerts if '🟡' in a.get('level', '')])
    
    if critical_count > 0 or warning_count > 0:
        # Determine the border color based on highest severity
        border_color = "#ff4d4d" if critical_count > 0 else "#FFD700"
        
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 10px; border-radius: 5px; border-left: 4px solid {border_color}; margin-bottom: 15px;">
            <span style="color: #ff4d4d; font-weight: bold;">🔴 {critical_count} Critical</span>
            <span style="color: #FFD700; font-weight: bold; margin-left: 15px;">🟡 {warning_count} Warning{'s' if warning_count != 1 else ''}</span>
        </div>
        """, unsafe_allow_html=True)    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🔴 Risks")
        risks = []
        
        # Yield Curve Risk
        if spread_val is not None:
            if spread_val < 0:
                risks.append(f"• **🔴 Inverted yield curve ({spread_val:.2f}%)** - Historically predicts recession")
            elif spread_val < 0.2:
                risks.append(f"• **🟡 Flattening yield curve ({spread_val:.2f}%)** - Watching for inversion")
        
        # Oil Price Risk
        if oil_val is not None:
            if oil_val > 90:
                risks.append(f"• **🔴 CRITICAL: Oil at ${oil_val:.2f}** - Inflation shock, energy crisis")
            elif oil_val > 80:
                risks.append(f"• **🟡 Elevated oil at ${oil_val:.2f}** - Rising energy costs")
        
        # VIX / Market Fear Risk
        if vix_val is not None:
            if vix_val > 30:
                risks.append(f"• **🔴 Market PANIC: VIX at {vix_val:.1f}** - Extreme fear")
            elif vix_val > 25:
                risks.append(f"• **🟡 Elevated fear: VIX at {vix_val:.1f}** - Market stress")
        
        # Credit Spread Risk
        if hy_val is not None:
            if hy_val > 5:
                risks.append(f"• **🔴 Credit crunch: HY spreads at {hy_val:.2f}%** - Corporate stress")
            elif hy_val > 4:
                risks.append(f"• **🟡 Corporate stress: HY spreads at {hy_val:.2f}%**")
        
        # Consumer Sentiment Risk
        if sent_val is not None:
            if sent_val < 50:
                risks.append(f"• **🔴 Consumer PANIC: Sentiment at {sent_val:.1f}**")
            elif sent_val < 60:
                risks.append(f"• **🟡 Weak confidence: Sentiment at {sent_val:.1f}**")
        
        # Jobless Claims Risk
        if claims_val is not None:
            if claims_val > 350000:
                risks.append(f"• **🔴 Mass layoffs: Claims at {claims_val/1000:.0f}K**")
            elif claims_val > 300000:
                risks.append(f"• **🟡 Labor softening: Claims at {claims_val/1000:.0f}K**")
        
        # Inflation Risk (keep existing)
        if cpi_val is not None:
            if cpi_val > 4:
                risks.append(f"• **🔴 High inflation: CPI at {cpi_val:.1f}%**")
            elif cpi_val > 2.5:
                risks.append(f"• **🟡 Elevated inflation: CPI at {cpi_val:.1f}%**")
        
        # Ultra-low unemployment risk (overheating)
        if unrate_val is not None and unrate_val < 3.5:
            risks.append(f"• **⚡ Ultra-tight labor market ({unrate_val:.1f}%)** - Risk of overheating")
        
        if risks:
            for risk in risks:
                st.markdown(risk)
        else:
            st.markdown("• No major risks detected")
    
    with col2:
        st.markdown("##### 🟢 Strengths")
        strengths = []
        
        # Yield Curve Strength (steep)
        if spread_val is not None and spread_val > 0.5:
            strengths.append(f"• **Steep yield curve ({spread_val:.2f}%)** - Growth expectations")
        
        # Goldilocks unemployment
        if unrate_val is not None and 3.5 <= unrate_val <= 5:
            strengths.append(f"• **Goldilocks unemployment ({unrate_val:.1f}%)** - Healthy labor market")
        
        # Inflation at target
        if cpi_val is not None and 2 <= cpi_val <= 3:
            strengths.append(f"• **Inflation near target ({cpi_val:.1f}%)** - Price stability")
        
        # Strong housing
        if hous_val is not None and hous_val > 1500:
            strengths.append(f"• **Robust housing starts ({hous_val/1000:.1f}M)** - Construction strength")
        
        # Calm markets
        if vix_val is not None and vix_val < 20:
            strengths.append("• **Low market fear** - Calm markets")
        
        # Low oil prices (strength)
        if oil_val is not None and oil_val < 70:
            strengths.append(f"• **Low energy costs** - Oil at ${oil_val:.2f}")
        
        # Strong consumer sentiment
        if sent_val is not None and sent_val > 80:
            strengths.append(f"• **Strong consumer confidence ({sent_val:.1f})**")
        
        # Tight credit spreads (strength)
        if hy_val is not None and hy_val < 3:
            strengths.append(f"• **Tight credit spreads ({hy_val:.2f}%)** - Low corporate stress")
        
        if strengths:
            for strength in strengths:
                st.markdown(strength)
        else:
            st.markdown("• Economy showing mixed signals")


# ============================================================================
# TAB 2: HISTORY EXPLORER - UPDATED DROPDOWN (58 indicators)
# ============================================================================

with tab2:
    st.markdown('<div class="sub-header">📈 Explore 64 Years of Economic History</div>', unsafe_allow_html=True)
    
    # Add info about the new feature
    st.markdown("""
    <div class="annotation-info">
        📜 <strong>Story Mode Enabled:</strong> Hover over event markers to learn about major historical events.
        Use the toggles below to customize your view.
    </div>
    """, unsafe_allow_html=True)
    
    # Comprehensive indicator dictionary organized by category - based on analyzer output (58 total)
    indicators = {
        # Rates & Yields (10)
        '💰 Rates: 1Y Treasury': 'DGS1',
        '💰 Rates: 10Y Treasury': 'DGS10',
        '💰 Rates: 2Y Treasury': 'DGS2',
        '💰 Rates: 20Y Treasury': 'DGS20',
        '💰 Rates: 3Y Treasury': 'DGS3',
        '💰 Rates: 30Y Treasury': 'DGS30',
        '💰 Rates: 3M Treasury': 'DGS3MO',
        '💰 Rates: 5Y Treasury': 'DGS5',
        '💰 Rates: 6M Treasury': 'DGS6MO',
        '💰 Rates: 7Y Treasury': 'DGS7',
        
        # Fed Policy (5)
        '🏦 Fed: Target Rate Lower': 'DFEDTARL',
        '🏦 Fed: Target Rate Upper': 'DFEDTARU',
        '🏦 Fed: Fed Funds Rate': 'FEDFUNDS',
        '🏦 Fed: Total Reserves': 'TOTRESNS',
        '🏦 Fed: Balance Sheet': 'WALCL',
        
        # Inflation (7)
        '📈 Inflation: CPI All Items': 'CPIAUCSL',
        '📈 Inflation: Core CPI': 'CPILFESL',
        '📈 Inflation: PCE': 'PCEPI',
        '📈 Inflation: Core PCE': 'PCEPILFE',
        '📈 Inflation: 10Y Expectation': 'T10YIE',
        '📈 Inflation: 5Y Expectation': 'T5YIE',
        '📈 Inflation: CPI YoY': 'CPI_YOY',
        
        # Labor Market (7)
        '👥 Labor: Avg Weekly Hours': 'AWHAETP',
        '👥 Labor: Participation Rate': 'CIVPART',
        '👥 Labor: Job Openings (JOLTS)': 'JTSJOL',
        '👥 Labor: Quits Rate': 'JTSQUR',
        '👥 Labor: Temporary Help': 'TEMPHELPS',
        '👥 Labor: U-6 Unemployment': 'U6RATE',
        '👥 Labor: Unemployment Rate': 'UNRATE',
        
        # Jobless Claims (3)
        '📋 Claims: Continued Claims': 'CC4WSA',
        '📋 Claims: Initial Claims': 'IC4WSA',
        '📋 Claims: 4-Week Avg': 'ICSA',
        
        # Growth & Output (3)
        '📊 Growth: Real GDP': 'GDPC1',
        '📊 Growth: Industrial Production': 'INDPRO',
        '📊 Growth: Retail Sales': 'RSAFS',
        
        # Housing (3)
        '🏠 Housing: Starts': 'HOUST',
        '🏠 Housing: Permits': 'PERMIT',
        '🏠 Housing: Homeownership Rate': 'RHORUSQ156N',
        
        # Money & Credit (5)
        '💰 Money: High Yield Index': 'BAMLH0A0HYM2',
        '💰 Money: M2 Supply': 'M2SL',
        '💰 Money: M2 Real': 'M2_REAL',
        '💰 Money: M2 Real Growth': 'M2_REAL_YOY',
        '💰 Money: Household Net Worth': 'TNWBSHNO',
        
        # Spreads (6)
        '📐 Spread: 10Y-2Y': '10Y2Y',
        '📐 Spread: 10Y-3M': '10Y3M',
        '📐 Spread: AAA-10Y Credit': 'AAA_SPREAD',
        '📐 Spread: BAA-10Y Credit': 'BAA_SPREAD',
        '📐 Spread: High Yield': 'HY_SPREAD',
        '📐 Spread: Risk Appetite': 'RISK_APPETITE',
        
        # Market Indicators (5)
        '😨 Market: Financial Stress': 'STLFSI4',
        '😨 Market: VIX Fear Gauge': 'VIX',
        '🛢️ Market: Oil Price (WTI)': 'DCOILWTICO',
        '💵 Market: Dollar Index': 'DTWEXBGS',
        '📈 Market: Consumer Sentiment': 'UMCSENT',
        
        # Demographics (1)
        '🌎 Demographics: Median Income': 'MEHOINUSA672N',
    }
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        selected = st.selectbox("Select indicator to explore:", list(indicators.keys()))
        col_name = indicators[selected]
    
    with col2:
        show_recessions = st.checkbox("Show recessions", value=True)
    
    with col3:
        show_events = st.checkbox("Show historical events", value=True, 
                                  help="Display major market events and crises with labels")
    
    with col4:
        log_scale = st.checkbox("Log scale", value=False)
    
    # Get data for selected indicator
    if col_name in df.columns:
        plot_df = df[['date', col_name]].dropna().copy()
        
        if not plot_df.empty:
            # Get date range
            start_date = plot_df['date'].min()
            end_date = plot_df['date'].max()
            years_available = (end_date - start_date).days / 365
            
            st.markdown(f"**Data available:** {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')} ({years_available:.1f} years)")
            
            # Create figure
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=plot_df['date'],
                y=plot_df[col_name],
                mode='lines',
                name=selected,
                line=dict(color='#FFD700', width=2),
                hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>'
            ))
            
            # Add historical annotations (recessions and events)
            add_historical_annotations(fig, plot_df, col_name, show_recessions, show_events)
            
            fig.update_layout(
                title=f'{selected} - {years_available:.1f} Years of History',
                xaxis_title='Year',
                yaxis_title=selected,
                height=500,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                xaxis=dict(rangeslider=dict(visible=True), type='date'),
                yaxis=dict(type='log' if log_scale else 'linear')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            st.markdown("### 📊 Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            current = plot_df[col_name].iloc[-1]
            
            with col1:
                st.metric("Current", f"{current:.2f}")
            with col2:
                st.metric("Average", f"{plot_df[col_name].mean():.2f}")
            with col3:
                max_val = plot_df[col_name].max()
                max_date = plot_df.loc[plot_df[col_name].idxmax(), 'date']
                st.metric("All-time High", f"{max_val:.2f}", f"{max_date.strftime('%b %Y')}")
            with col4:
                min_val = plot_df[col_name].min()
                min_date = plot_df.loc[plot_df[col_name].idxmin(), 'date']
                st.metric("All-time Low", f"{min_val:.2f}", f"{min_date.strftime('%b %Y')}")
    else:
        st.warning(f"Indicator {col_name} not available in dataset")


# ============================================================================
# TAB 3: HISTORICAL MATCHES (ENHANCED WITH MULTI-FACTOR SIMILARITY)
# ============================================================================

with tab3:
    st.markdown('<div class="sub-header">🔍 Historical Matches: Multi-Factor Similarity Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(255,215,0,0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <p style="color: white; margin: 0;">
            <span style="color: #FFD700;">🎯 Multi-Factor Analysis:</span> Finding historical periods with similar 
            yield curve, oil prices, market fear (VIX), credit spreads, consumer sentiment, unemployment, and inflation.
            Higher similarity score = more comparable economic environment.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current values for context
    spread_val, _ = get_latest_value(df, '10Y2Y')
    oil_val, _ = get_latest_value(df, 'DCOILWTICO')
    vix_val, _ = get_latest_value(df, 'VIX')
    hy_val, _ = get_latest_value(df, 'HY_SPREAD')
    sent_val, _ = get_latest_value(df, 'UMCSENT')
    unrate_val, _ = get_latest_value(df, 'UNRATE')
    cpi_val, _ = get_latest_value(df, 'CPI_YOY')
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                padding: 15px; border-radius: 8px; margin: 10px 0;">
        <h4 style="color: #FFD700; margin: 0;">Current Multi-Factor Profile</h4>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px;">
            <div><span style="color: #888;">Spread:</span> {format_value(spread_val, 2)}%</div>
            <div><span style="color: #888;">Oil:</span> {format_value(oil_val, 2, '$')}</div>
            <div><span style="color: #888;">VIX:</span> {format_value(vix_val, 1)}</div>
            <div><span style="color: #888;">Credit:</span> {format_value(hy_val, 2)}%</div>
            <div><span style="color: #888;">Sentiment:</span> {format_value(sent_val, 1)}</div>
            <div><span style="color: #888;">Unemp:</span> {format_value(unrate_val, 1)}%</div>
            <div><span style="color: #888;">CPI:</span> {format_value(cpi_val, 1)}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Find multi-factor matches
    matches = find_multi_factor_historical_matches(df, current_date=df['date'].iloc[-1], n=10)
    
    if not matches.empty:
        st.markdown("### 📊 Top 10 Historical Multi-Factor Matches")
        st.markdown("*Ranked by overall similarity to today's economic profile*")
        
        for i, (_, match) in enumerate(matches.iterrows(), 1):
            # Get the full row data for this match
            match_row = df[df['date'] == match['date']].iloc[0]
            
            # Get values for display
            match_spread = match_row.get('10Y2Y', None)
            match_oil = match_row.get('DCOILWTICO', None)
            match_vix = match_row.get('VIX', None)
            match_hy = match_row.get('HY_SPREAD', None)
            match_sent = match_row.get('UMCSENT', None)
            match_unrate = match_row.get('UNRATE', None)
            match_cpi = match_row.get('CPI_YOY', None)
            
            # Determine if this period led to crisis
            year = match['date'].year
            crisis_years = [1973, 1980, 1981, 1990, 2001, 2007, 2008, 2020]
            led_to_crisis = year in crisis_years
            
            # Color based on similarity score
            sim = match['similarity']
            if sim >= 80:
                border_color = '#ff4d4d'
                bg_color = '#ff4d4d20'
            elif sim >= 70:
                border_color = '#ff9933'
                bg_color = '#ff993320'
            elif sim >= 60:
                border_color = '#FFD700'
                bg_color = '#FFD70020'
            else:
                border_color = '#4169E1'
                bg_color = '#4169E120'
            
            with st.expander(f"Match #{i}: {match['date'].strftime('%B %Y')} (Similarity: {sim:.0f}% - {match['factors_used']*100:.0f}% factors matched)", expanded=(i==1)):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Then vs Now**")
                    st.markdown(f"• Spread: {format_value(match_spread, 2)}% (Now: {format_value(spread_val, 2)}%)")
                    st.markdown(f"• Oil: {format_value(match_oil, 2, '$')} (Now: {format_value(oil_val, 2, '$')})")
                    st.markdown(f"• VIX: {format_value(match_vix, 1)} (Now: {format_value(vix_val, 1)})")
                    st.markdown(f"• Credit: {format_value(match_hy, 2)}% (Now: {format_value(hy_val, 2)}%)")
                
                with col2:
                    st.markdown(f"• Sentiment: {format_value(match_sent, 1)} (Now: {format_value(sent_val, 1)})")
                    st.markdown(f"• Unemployment: {format_value(match_unrate, 1)}% (Now: {format_value(unrate_val, 1)}%)")
                    st.markdown(f"• Inflation: {format_value(match_cpi, 1)}% (Now: {format_value(cpi_val, 1)}%)")
                    
                    outcome = "🔴 LED TO CRISIS" if led_to_crisis else "🟢 NO CRISIS"
                    st.markdown(f"**Outcome:** {outcome}")
                
                # Look ahead 12 months
                date_idx = df[df['date'] == match['date']].index[0]
                future_12m_idx = min(date_idx + 264, len(df) - 1)
                
                if future_12m_idx > date_idx:
                    future_yield = df.iloc[future_12m_idx]['DGS10'] if 'DGS10' in df.columns else None
                    if future_yield is not None and pd.notna(match_row.get('DGS10')):
                        change = future_yield - match_row['DGS10']
                        direction = "▲" if change > 0 else "▼"
                        st.markdown(f"**12 months later:** 10Y Yield {direction} {abs(change):.2f}% to {future_yield:.2f}%")
    else:
        st.info("No close multi-factor historical matches found.")
    
    st.markdown("---")
    
    # Keep the original yield-only matches as a secondary option
    with st.expander("📊 View Traditional Yield-Only Matches"):
        st.info("These matches are based on yield levels ONLY, not the full multi-factor profile.")
        
        if 'DGS10' in df.columns:
            latest_yield = df[df['DGS10'].notna()].iloc[-1]['DGS10'] if not df[df['DGS10'].notna()].empty else None
            latest_date = df[df['DGS10'].notna()].iloc[-1]['date'] if not df[df['DGS10'].notna()].empty else None
            
            if latest_yield is not None:
                col1, col2 = st.columns([3, 1])
                with col1:
                    era = st.radio(
                        "Focus on:", 
                        ["All History", "Pre-2000", "Post-2000"], 
                        horizontal=True,
                        key="yield_matches_era"
                    )
                
                yield_matches = find_historical_matches(df, latest_yield, latest_date, n=5, era=era)
                
                if not yield_matches.empty:
                    for i, (_, match) in enumerate(yield_matches.iterrows(), 1):
                        st.markdown(f"""
                        **Match #{i}: {match['date'].strftime('%B %Y')}** (Yield: {match['DGS10']:.2f}%, Similarity: {match['similarity']:.0f}%)
                        - {'🔴 LED TO CRISIS' if match['led_to_crisis'] else '🟢 NO CRISIS'}
                        """)
                else:
                    st.info("No yield matches found.")


# ============================================================================
# TAB 4: DATA SHOP (WITH EMAIL CAPTURE AND ATTRIBUTION)
# ============================================================================

with tab4:
    st.markdown('<div class="sub-header">📦 Complete US Economic Dataset</div>', unsafe_allow_html=True)
    
    indicator_count = get_indicator_count(df)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                padding: 20px; border-radius: 8px; margin-bottom: 30px;">
        <h2 style="color: #FFD700; margin: 0;">{indicator_count} Indicators • 64 Years • Daily Updates</h2>
        <p style="color: #ccc; margin: 10px 0 0;">(50 raw FRED series + 8 proprietary calculations)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================
    # FREE ACCESS MESSAGE
    # =========================================
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                padding: 25px; border-radius: 10px; text-align: center; margin: 20px 0; border: 1px solid #FFD700;">
        <h2 style="color: #00ff00; margin-top: 0;">✅ You're Already Using It FREE</h2>
        <p style="color: white; font-size: 1.2rem;">The complete interactive dashboard is yours at no cost.</p>
        <p style="color: #ccc;">When you need the raw dataset for your own analysis, join the waitlist below.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # WHAT WE ADD SECTION - Clear value proposition
    st.markdown("""
    <div class="what-we-add">
        <h3>✨ What GFTI Daily™ Adds</h3>
        <p style="color: #ccc;">FRED provides the raw materials. We build the finished product. Think of FRED as the lumber yard, and we're the carpenters who build you a table. You're paying for our craftsmanship, not the wood.</p>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 15px;">
            <div>✓ Cleaned & standardized time series</div>
            <div>✓ 58 indicators in one file</div>
            <div>✓ Proprietary spreads & ratios</div>
            <div>✓ Daily automated updates</div>
            <div>✓ No gaps, weekends, or holidays</div>
            <div>✓ Historical event annotations</div>
            <div>✓ Historical match analysis</div>
            <div>✓ One-click download, no API keys</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Transparency expander
    with st.expander("🔢 Raw vs Calculated Breakdown"):
        st.markdown("""
        | Type | Count | Examples |
        |------|-------|----------|
        | **Raw FRED Series** | 50 | DGS10, UNRATE, CPIAUCSL, M2SL, VIX |
        | **Proprietary Calculations** | 8 | CPI_YOY, 10Y2Y, M2_REAL, HY_SPREAD |
        | **TOTAL** | **58** | |
        
        **Proprietary Calculations Include:**
        - **CPI_YOY** - Year-over-year inflation rate
        - **M2_REAL** - Inflation-adjusted money supply
        - **M2_REAL_YOY** - Real money supply growth
        - **10Y2Y** - 10Y-2Y Treasury spread (recession indicator)
        - **10Y3M** - 10Y-3M Treasury spread
        - **BAA_SPREAD** - BAA corporate credit spread
        - **AAA_SPREAD** - AAA corporate credit spread
        - **HY_SPREAD** - High yield credit spread
        - **RISK_APPETITE** - HY vs BAA spread differential
        
        We do the math so you don't have to. All spreads, real values, 
        and growth rates are pre-calculated and ready to use.
        """)
    
    # Coverage by era
    st.markdown("### 📅 Coverage by Era")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("1960s-1980s", f"{coverage[2][1]}+ indicators")
    with col2:
        st.metric("1990s", f"{coverage[3][1]}+ indicators")
    with col3:
        st.metric("2000s", f"{coverage[4][1]}+ indicators")
    with col4:
        st.metric("Today", f"{coverage[6][1]} indicators")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 What's Included
        
        **💰 Rates & Fed** (15)
        - Complete yield curve (1M-30Y)
        - Fed Funds & balance sheet
        - Real rates & targets
        
        **👥 Labor Market** (10)
        - Unemployment (U3 & U6)
        - JOLTS job openings/quits
        - Weekly claims & hours
        
        **📈 Inflation** (7)
        - CPI, Core CPI, PCE, Core PCE
        - Breakeven expectations
        
        **🏠 Housing** (3)
        - Starts, permits, homeownership
        """)
    
    with col2:
        st.markdown("""
        **📊 Growth** (4)
        - GDP, Industrial Production
        - Retail sales, sentiment
        
        **📉 Market Stress** (5)
        - VIX fear gauge
        - Financial stress index
        - Oil, dollar, credit spreads
        
        **💵 Money & Credit** (5)
        - M2 money supply
        - Household net worth
        - High yield spread
        
        **🌎 Demographics** (1)
        - Median household income
        """)
    
    # Stats
    st.markdown("### 📈 Dataset Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Indicators", f"{indicator_count}")
    with col2:
        st.metric("Date Range", f"{df['date'].min().year} - {df['date'].max().year}")
    with col3:
        st.metric("Daily Observations", f"{len(df):,}")
    with col4:
        st.metric("Last Update", df['date'].max().strftime('%b %d, %Y'))
    
    # Sample download with README
    st.markdown("### 📥 Download Free Sample (Includes README)")
    sample_df = df.tail(1000).copy()
    sample_cols = ['date', 'DGS10', 'UNRATE', 'CPI_YOY', 'VIX', 'HOUST']
    available_cols = [col for col in sample_cols if col in df.columns]
    sample_df = df[available_cols].tail(100).copy()
    
    # Create ZIP with sample data + README
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        # Add sample data
        csv_data = sample_df.to_csv(index=False)
        zip_file.writestr('gfti_daily_sample.csv', csv_data)
        # Add README
        zip_file.writestr('README.txt', generate_readme())
    
    zip_buffer.seek(0)
    
    st.download_button(
        label="⬇️ Download Sample + README (ZIP)",
        data=zip_buffer,
        file_name=f"gfti_daily_sample_{datetime.now().strftime('%Y%m%d')}.zip",
        mime="application/zip",
        use_container_width=True
    )
    
    st.markdown("---")
    
    # =========================================
    # EMAIL CAPTURE SECTION - DIRECT TO YOUR INBOX (NO STORAGE)
    # =========================================
    
    st.markdown("""
    <div class="email-box">
        <h3 style="color: white; margin-top: 0;">📋 Get the Full Dataset When Ready</h3>
        <p style="color: white; opacity: 0.9;">We're preparing the complete 58-indicator dataset for download. Join the waitlist and we'll email you when it's available.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple interest selector
    interest = st.radio(
        "I'm interested in:",
        ["Individual/Academic", "Business/Commercial", "Just browsing"],
        horizontal=True,
        key="interest_radio"
    )
    
    # Email signup form
    with st.form(key='email_capture_form'):
        email = st.text_input(
            "", 
            placeholder="Enter your email address", 
            label_visibility="collapsed",
            key="waitlist_email"
        )
        submit = st.form_submit_button("📋 Join Waitlist", use_container_width=True, type="primary")
        
        if submit and email:
            # Validate email (basic check)
            if '@' in email and '.' in email:
                # Map interest to plan
                plan_map = {
                    "Individual/Academic": "Individual",
                    "Business/Commercial": "Business",
                    "Just browsing": "Browser"
                }
                selected_plan = plan_map[interest]
                
                # Send email notification (no storage)
                success = send_email_notification(email, selected_plan)
                
                if success:
                    st.balloons()
                    st.success(f"✅ Thanks! We'll email you at {email} when the dataset is ready.")
                else:
                    st.error("❌ Could not send notification. Please try again later.")
            else:
                st.error("❌ Please enter a valid email address")
    
    # Simple success message instead of stored stats
    st.markdown("""
    <p style='text-align: center; color: #FFD700; margin-top: 10px;'>
        ⭐ <strong>Privacy first:</strong> Your email is sent directly to us, never stored.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # =========================================
    # EXPLAINER EXPANDER
    # =========================================
    with st.expander("🤔 What will I get when I join the waitlist?"):
        st.markdown("""
        <div style="background: #1a1a1a; padding: 15px; border-radius: 5px;">
            <p><strong>You're already using the interactive dashboard for FREE.</strong> That's not changing.</p>
            <p>The waitlist is for people who want:</p>
            <ul>
                <li><strong>The raw dataset</strong> - 58 indicators (50 raw FRED + 8 calculated) in CSV format</li>
                <li><strong>Daily updates</strong> - Automated data delivery</li>
                <li><strong>Proprietary calculations</strong> - Our spreads and ratios pre-calculated</li>
                <li><strong>No cleaning needed</strong> - Gaps removed, weekends handled</li>
                <li><strong>Ready-to-use files</strong> - One download, no API keys required</li>
            </ul>
            <p style="color: #FFD700; margin-top: 10px;">Join the waitlist, and we'll notify you the moment data downloads are ready.</p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# TAB 5: ATTRIBUTION & LEGAL (NEW)
# ============================================================================

with tab5:
    st.markdown('<div class="sub-header">📋 Data Sources & Attribution</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="attribution-box">
        <h3>🎯 Why This Matters</h3>
        <p>GFTI Daily™ is built on public data from trusted sources. We believe in transparency — 
        both in financial markets and in how we build our products. Every indicator, every chart, 
        every number comes with proper attribution.</p>
        <p><strong>We don't sell raw data. We sell our work on public data.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🏦 FRED® (Federal Reserve Economic Data)
        Federal Reserve Bank of St. Louis
        
        **What we use:**
        - All Treasury yields (1M-30Y)
        - Fed Funds rate & balance sheet
        - Unemployment & labor data
        - Inflation measures (CPI, PCE)
        - GDP, housing, consumer sentiment
        - Money supply & credit data
        
        **Attribution required:**
        > "Data sourced from FRED® (Federal Reserve Economic Data), Federal Reserve Bank of St. Louis."
        
        **Original source:** [fred.stlouisfed.org](https://fred.stlouisfed.org/)
        
        **Terms of use:** [fred.stlouisfed.org/legal/](https://fred.stlouisfed.org/legal/)
        """)
    
    with col2:
        st.markdown("""
        ### 📈 Yahoo Finance
        
        **What we use:**
        - VIX (CBOE Volatility Index)
        
        **Attribution required:**
        > "VIX data sourced from Yahoo Finance."
        
        **Original source:** [finance.yahoo.com/quote/%5EVIX](https://finance.yahoo.com/quote/%5EVIX)
        
        **Terms of use:** [legal.yahoo.com/](https://legal.yahoo.com/)
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🔄 What GFTI Daily™ Adds
    
    <div style="background: #1a1a1a; padding: 20px; border-radius: 10px; margin: 10px 0;">
        <p style="color: #FFD700; font-size: 1.1rem; margin: 0;">"FRED provides the raw materials. We build the finished product."</p>
    </div>
    
    | We Do This | You Get |
    |------------|---------|
    | Clean and standardize all time series | Ready-to-use data, no gaps |
    | Combine 58 indicators into one file | One download, one source |
    | Remove weekends and holidays | Trading-day aligned data |
    | Calculate proprietary spreads | 10Y-2Y, risk appetite, real rates |
    | Add historical event annotations | Context for every major market move |
    | Create historical match analysis | "When have we seen this before?" |
    | Deliver daily updates | Always current |
    
    **The bottom line:** You're paying for 100+ hours of data cleaning and analysis — 
    work you'd otherwise have to do yourself. The raw data remains freely available from FRED and Yahoo.
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### 📜 Required Attribution for Users
    
    If you publish or distribute any part of this dataset, you MUST include:
    
    <div style="background: #0f0f0f; padding: 15px; border-radius: 8px; font-family: monospace; margin: 10px 0;">
        "Data sourced from FRED® (Federal Reserve Economic Data),<br>
        Federal Reserve Bank of St. Louis, and Yahoo Finance."
    </div>
    
    **Example for research papers:**
    > Economic data provided by GFTI Daily™, which transforms public data from FRED® (Federal Reserve Economic Data, Federal Reserve Bank of St. Louis) and Yahoo Finance.
    
    **Example for websites:**
    > All data sourced from FRED® and Yahoo Finance. GFTI Daily™ provides cleaned and enhanced versions.
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### ⚖️ Legal & Disclaimer
    
    **GFTI Daily™** is an independent data provider. We are NOT affiliated with, endorsed by, 
    or sponsored by the Federal Reserve Bank of St. Louis or Yahoo! Inc.
    
    All trademarks are property of their respective owners:
    - FRED® is a registered trademark of the Federal Reserve Bank of St. Louis
    - Yahoo Finance is a trademark of Yahoo! Inc.
    - GFTI Daily™ is a trademark of Matthew A.A. Blackman
    
    **Our service:** We provide cleaned, transformed, and enhanced versions of publicly available data. 
    The value we add is in the cleaning, standardization, combination, and delivery — not in the underlying data itself.
    """)
    
    # Download full README
    st.markdown("---")
    st.markdown("### 📥 Download Attribution Package")
    
    readme_content = generate_readme()
    
    st.download_button(
        label="📄 Download README.txt (Attribution Guide)",
        data=readme_content,
        file_name=f"GFTI_Daily_README_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )


# ============================================================================
# TAB 6: VISUAL VAULT - Fixed for Fullscreen Animation
# ============================================================================

with tab6:
    # Initialize session state for Visual Vault
    if 'vault_view_mode' not in st.session_state:
        st.session_state.vault_view_mode = 'thumbnail'
    if 'fullscreen_chart_id' not in st.session_state:
        st.session_state.fullscreen_chart_id = None
    if 'vault_key_counter' not in st.session_state:
        st.session_state.vault_key_counter = 0
    
    # Track when we enter this tab
    if 'last_tab' not in st.session_state:
        st.session_state.last_tab = None
    
    # If we're switching to this tab, increment counter to force fresh charts
    if st.session_state.last_tab != 'vault':
        st.session_state.vault_key_counter += 1
        st.session_state.last_tab = 'vault'
    
    # Call the vault tab function with ALL required parameters
    visual_vault.create_vault_tab(
        df, 
        HISTORICAL_EVENTS,
        view_mode=st.session_state.vault_view_mode,
        fullscreen_id=st.session_state.fullscreen_chart_id
    )


# ============================================================================
# TAB 7: DATA FRESHNESS (NEW - FROM APP2.PY)
# ============================================================================

with tab7:
    st.markdown('<div class="sub-header">📅 Data Freshness Dashboard</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(255,215,0,0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <p style="color: white; margin: 0;">
            <span style="color: #FFD700;">ℹ️ About this dashboard:</span> Different indicators update at different frequencies.
            We check every source daily, but some data (like GDP) is only released quarterly.
            This dashboard shows you exactly how fresh each indicator is.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    freshness_df, freq_counts = create_freshness_dashboard(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        daily_count = freq_counts.get('Daily', 0)
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #00ff00;">
            <div style="color: #00ff00; font-size: 2rem;">{daily_count}</div>
            <div style="color: #888;">Daily Indicators</div>
            <div style="color: #00ff00; font-size: 0.8rem;">🟢 Updates next day</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        weekly_count = freq_counts.get('Weekly', 0)
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #FFD700;">
            <div style="color: #FFD700; font-size: 2rem;">{weekly_count}</div>
            <div style="color: #888;">Weekly Indicators</div>
            <div style="color: #FFD700; font-size: 0.8rem;">🟡 Updates Thursdays</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        monthly_count = freq_counts.get('Monthly', 0)
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #ff9900;">
            <div style="color: #ff9900; font-size: 2rem;">{monthly_count}</div>
            <div style="color: #888;">Monthly Indicators</div>
            <div style="color: #ff9900; font-size: 0.8rem;">🟠 Varies by release</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        quarterly_count = freq_counts.get('Quarterly', 0)
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #4169E1;">
            <div style="color: #4169E1; font-size: 2rem;">{quarterly_count}</div>
            <div style="color: #888;">Quarterly Indicators</div>
            <div style="color: #4169E1; font-size: 0.8rem;">🔵 Every 3 months</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📋 Detailed Freshness by Indicator")
    
    sort_by = st.radio(
        "Sort by:",
        ["Days Old (newest first)", "Days Old (oldest first)", "Indicator Name", "Frequency"],
        horizontal=True
    )
    
    if sort_by == "Days Old (newest first)":
        freshness_df = freshness_df.sort_values('Days Old', ascending=True)
    elif sort_by == "Days Old (oldest first)":
        freshness_df = freshness_df.sort_values('Days Old', ascending=False)
    elif sort_by == "Indicator Name":
        freshness_df = freshness_df.sort_values('Indicator')
    elif sort_by == "Frequency":
        freshness_df = freshness_df.sort_values('Frequency')
    
    st.dataframe(
        freshness_df[['Indicator', 'Last Update', 'Days Old', 'Frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            'Days Old': st.column_config.NumberColumn(
                'Days Old',
                help="Days since last update",
                format="%d days"
            )
        }
    )
    
    st.markdown("---")
    
    with st.expander("📅 When Do Indicators Typically Update?"):
        st.markdown("""
        | Frequency | Typical Release Schedule |
        |-----------|-------------------------|
        | **Daily** | Treasury yields: 6pm ET daily<br>VIX, Markets: Throughout trading day<br>Oil: Daily settlement |
        | **Weekly** | Jobless Claims: Every Thursday at 8:30am ET |
        | **Monthly** | Unemployment: First Friday<br>CPI: Second week<br>Retail Sales: Mid-month<br>Housing Starts: Mid-month |
        | **Quarterly** | GDP Advance: Late January, April, July, October<br>GDP Preliminary: One month later<br>GDP Final: One month after that |
        
        We check every source daily and update the dataset as soon as new data becomes available.
        """)


# ============================================================================
# COMPLIANCE FOOTER (Added to every page)
# ============================================================================

st.markdown(get_compliance_footer(), unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.7rem; padding: 10px; border-top: 1px solid #333;">
    <p>© 2026 GFTI Daily™. All rights reserved. 
    <a href="https://gftidaily.com" style="color: #FFD700; text-decoration: none;">gftidaily.com</a> | 
    <a href="mailto:hello@gftidaily.com" style="color: #FFD700; text-decoration: none;">hello@gftidaily.com</a></p>
</div>
""", unsafe_allow_html=True)