"""
GFTI Daily™ - Complete US Financial History Database
Now with 84 indicators covering all aspects of the US economy
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
    # You can hardcode temporarily for testing, but better to use secrets file
    FORMSPREE_ENDPOINT = "https://formspree.io/f/your-form-id-here"  # Replace with your actual endpoint
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
# CUSTOM CSS (with trademark styling)
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
# EMAIL FUNCTIONS - USING FORMSPREE WITH SECRETS
# ============================================================================

import requests
from datetime import datetime

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
    # This just returns success without doing anything
    return True, 1

def get_waitlist_stats():
    """Legacy function - returns empty stats"""
    return {'total': 0, 'by_plan': {}}

# ============================================================================
# LEGACY FUNCTIONS (for compatibility)
# ============================================================================

def save_email_to_list(email, plan_interest):
    """Legacy function - kept for compatibility"""
    # This just returns success without doing anything
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
    {'date': '2001-09-11', 'label': '9/11 Attacks', 'category': 'geopolitical',
     'description': 'Markets closed, Fed provides liquidity', 'marker': '🇺🇸', 'y_offset': 0},
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
INDICATORS: 50+
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
✓ 50+ indicators combined into one file
✓ Proprietary calculations (spreads, ratios, historical matches)
✓ Daily automated updates
✓ Historical event annotations
✓ Ready-to-use format (no API keys, no cleaning required)

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

import requests
from io import StringIO

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

def get_latest_value(df, column, alternative_cols=None):
    """Get the latest non-NaN value for a column"""
    if alternative_cols is None:
        alternative_cols = []
    
    # Try the main column first
    if column in df.columns:
        valid_data = df[df[column].notna()]
        if not valid_data.empty:
            latest_row = valid_data.iloc[-1]
            return latest_row[column], latest_row['date']
    
    # Try alternatives
    for alt in alternative_cols:
        if alt in df.columns:
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

def get_recession_probability(spread):
    """Calculate recession probability from yield spread"""
    if pd.isna(spread):
        return None, None, None
    
    if spread < -0.5:
        return 85, "CRITICAL", "#ff4d4d"
    elif spread < 0:
        return 70, "HIGH", "#ff9933"
    elif spread < 0.5:
        return 40, "ELEVATED", "#FFD700"
    else:
        return 15, "LOW", "#00ff00"

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
    if pd.isna(value):
        return "N/A"
    if isinstance(value, float):
        return f"{prefix}{value:.{decimals}f}{suffix}"
    return f"{prefix}{value}{suffix}"

def find_historical_matches(df, current_yield, current_date, n=5, era="All History"):
    """Find the closest historical matches for today's yield"""
    mask = (df['date'] < current_date - pd.Timedelta(days=30)) & (df['DGS10'].notna())
    
    # Apply era filter
    if era == "Pre-2000":
        mask &= (df['date'] < '2000-01-01')
    elif era == "Post-2000":
        mask &= (df['date'] >= '2000-01-01')
    
    candidates = df[mask].copy()
    
    if len(candidates) == 0:
        return pd.DataFrame()
    
    candidates['yield_diff'] = abs(candidates['DGS10'] - current_yield)
    candidates['similarity'] = 100 - (candidates['yield_diff'] * 50)
    candidates['similarity'] = candidates['similarity'].clip(0, 100)
    
    matches = candidates.nsmallest(n, 'yield_diff').copy()
    
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
# ============================================================================
# CRISIS MONITORING FUNCTIONS - Added March 2026
# ============================================================================

def check_crisis_signals(df, war_start_date="2026-02-23"):
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
        if vix_val > 30:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'VIX',
                'message': f'VIX at {vix_val:.1f} - Market PANIC',
                'value': vix_val,
                'threshold': 30,
                'date': vix_date,
                'color': '#ff4d4d'
            })
        elif vix_val > 25:
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
        if oil_val > 90:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'OIL',
                'message': f'Oil at ${oil_val:.2f} - Inflation shock',
                'value': oil_val,
                'threshold': 90,
                'date': oil_date,
                'color': '#ff4d4d'
            })
        elif oil_val > 80:
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
        if spread_val < 0:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'YIELD CURVE',
                'message': f'Curve inverted at {spread_val:.2f}% - RECESSION SIGNAL',
                'value': spread_val,
                'threshold': 0,
                'date': spread_date,
                'color': '#ff4d4d'
            })
        elif spread_val < 0.2:
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
        if hy_val > 5:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'CREDIT',
                'message': f'High yield spreads at {hy_val:.2f}% - Credit crunch',
                'value': hy_val,
                'threshold': 5,
                'date': hy_date,
                'color': '#ff4d4d'
            })
        elif hy_val > 4:
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
        if sent_val < 50:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'SENTIMENT',
                'message': f'Consumer sentiment at {sent_val:.1f} - PANIC',
                'value': sent_val,
                'threshold': 50,
                'date': sent_date,
                'color': '#ff4d4d'
            })
        elif sent_val < 60:
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
        if claims_val > 350000:
            alerts.append({
                'level': '🔴 CRITICAL',
                'indicator': 'CLAIMS',
                'message': f'Jobless claims at {claims_val/1000:.0f}K - Mass layoffs',
                'value': claims_val,
                'threshold': 350000,
                'date': claims_date,
                'color': '#ff4d4d'
            })
        elif claims_val > 300000:
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
    st.markdown(f"*Monitoring since Feb 23, 2026 - Day {(datetime.now() - pd.to_datetime('2026-02-23')).days} of conflict*")
    
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
            <div style="color: #888;">as of {vix_date.strftime('%b %d, %Y') if vix_date else 'N/A'}</div>
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
            <div style="color: #888;">as of {oil_date.strftime('%b %d, %Y') if oil_date else 'N/A'}</div>
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
            <div style="color: #888;">as of {spread_date.strftime('%b %d, %Y') if spread_date else 'N/A'}</div>
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
            <div style="color: #888;">as of {hy_date.strftime('%b %d, %Y') if hy_date else 'N/A'}</div>
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
            <div style="color: #888;">as of {sent_date.strftime('%b %d, %Y') if sent_date else 'N/A'}</div>
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
            <div style="color: #888;">as of {claims_date.strftime('%b %d, %Y') if claims_date else 'N/A'}</div>
        </div>
        """, unsafe_allow_html=True)


def display_war_timeline(df, before_values):
    """
    Display the War Impact Timeline showing changes since Feb 23, 2026
    """
    
    st.markdown('<div class="sub-header">📅 War Impact Timeline</div>', unsafe_allow_html=True)
    
    # Get current values
    vix_val, vix_date = get_latest_value(df, 'VIX')
    oil_val, oil_date = get_latest_value(df, 'DCOILWTICO')
    spread_val, spread_date = get_latest_value(df, '10Y2Y')
    hy_val, hy_date = get_latest_value(df, 'HY_SPREAD')
    sent_val, sent_date = get_latest_value(df, 'UMCSENT')
    claims_val, claims_date = get_latest_value(df, 'IC4WSA')
    
    # Calculate days since war started
    war_start = before_values['war_start']
    days_since = (datetime.now() - war_start).days
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="color: #FFD700; font-size: 1.2rem; font-weight: bold;">⚔️ Conflict Day {days_since}</span>
                <span style="color: #888; margin-left: 10px;">(Feb 23 - {datetime.now().strftime('%b %d, %Y')})</span>
            </div>
            <div style="color: #ff4d4d;">{len([a for a in st.session_state.get('crisis_alerts', []) if '🔴' in a['level']])} Critical • {len([a for a in st.session_state.get('crisis_alerts', []) if '🟡' in a['level']])} Warning</div>
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
    if vix_val is not None and before_values['vix'] is not None:
        vix_change = ((vix_val - before_values['vix']) / before_values['vix']) * 100
        vix_color = "#ff4d4d" if vix_change > 0 else "#00ff00"
        vix_status = "🔴 WARNING" if vix_val > 25 else "🟢 OK" if vix_val < 20 else "🟡 ELEVATED"
        
        col1.markdown("😨 VIX")
        col2.markdown(f"{before_values['vix']:.1f}")
        col3.markdown(f"{vix_val:.1f}")
        col4.markdown(f"<span style='color: {vix_color};'>▲ {vix_change:.0f}%</span>", unsafe_allow_html=True)
        col5.markdown(vix_status)
    
    # Oil Row
    if oil_val is not None and before_values['oil'] is not None:
        oil_change = ((oil_val - before_values['oil']) / before_values['oil']) * 100
        oil_color = "#ff4d4d" if oil_change > 0 else "#00ff00"
        oil_status = "🟢 OK" if oil_val < 80 else "🟡 ELEVATED" if oil_val < 90 else "🔴 CRITICAL"
        
        col1.markdown("🛢️ Oil")
        col2.markdown(f"${before_values['oil']:.2f}")
        col3.markdown(f"${oil_val:.2f}")
        col4.markdown(f"<span style='color: {oil_color};'>▲ {oil_change:.0f}%</span>", unsafe_allow_html=True)
        col5.markdown(oil_status)
    
    # Yield Curve Row
    if spread_val is not None and before_values['spread'] is not None:
        spread_change = spread_val - before_values['spread']
        spread_color = "#ff4d4d" if spread_change < 0 else "#00ff00"
        spread_status = "🟢 OK" if spread_val > 0.5 else "🟡 FLATTENING" if spread_val > 0 else "🔴 INVERTED"
        
        col1.markdown("📉 Yield Curve")
        col2.markdown(f"{before_values['spread']:.2f}%")
        col3.markdown(f"{spread_val:.2f}%")
        col4.markdown(f"<span style='color: {spread_color};'>{spread_change:+.2f}%</span>", unsafe_allow_html=True)
        col5.markdown(spread_status)
    
    # Credit Spreads Row
    if hy_val is not None and before_values['hy'] is not None:
        hy_change = hy_val - before_values['hy']
        hy_color = "#ff4d4d" if hy_change > 0 else "#00ff00"
        hy_status = "🟢 OK" if hy_val < 4 else "🟡 STRESS" if hy_val < 5 else "🔴 CRUNCH"
        
        col1.markdown("💰 Credit Spreads")
        col2.markdown(f"{before_values['hy']:.2f}%")
        col3.markdown(f"{hy_val:.2f}%")
        col4.markdown(f"<span style='color: {hy_color};'>{hy_change:+.2f}%</span>", unsafe_allow_html=True)
        col5.markdown(hy_status)
    
    # Consumer Sentiment Row
    if sent_val is not None and before_values['sent'] is not None:
        sent_change = sent_val - before_values['sent']
        sent_color = "#ff4d4d" if sent_change < 0 else "#00ff00"
        sent_status = "🟢 OK" if sent_val > 60 else "🟡 WEAK" if sent_val > 50 else "🔴 PANIC"
        
        col1.markdown("💬 Sentiment")
        col2.markdown(f"{before_values['sent']:.1f}")
        col3.markdown(f"{sent_val:.1f}")
        col4.markdown(f"<span style='color: {sent_color};'>{sent_change:+.1f}</span>", unsafe_allow_html=True)
        col5.markdown(sent_status)
    
    # Jobless Claims Row
    if claims_val is not None and before_values['claims'] is not None:
        claims_change = claims_val - before_values['claims']
        claims_color = "#ff4d4d" if claims_change > 0 else "#00ff00"
        claims_status = "🟢 OK" if claims_val < 300000 else "🟡 SOFTENING" if claims_val < 350000 else "🔴 LAYOFFS"
        
        col1.markdown("📋 Jobless Claims")
        col2.markdown(f"{before_values['claims']/1000:.0f}K")
        col3.markdown(f"{claims_val/1000:.0f}K")
        col4.markdown(f"<span style='color: {claims_color};'>{claims_change/1000:+.0f}K</span>", unsafe_allow_html=True)
        col5.markdown(claims_status)


def display_alert_system(alerts):
    """
    Display the notification bell with alert count and expandable alert list
    """
    
    critical_count = len([a for a in alerts if '🔴' in a['level']])
    warning_count = len([a for a in alerts if '🟡' in a['level']])
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
                    st.markdown(f"""
                    <div style="background: {alert['color']}10; padding: 8px; border-radius: 5px; margin: 5px 0; border-left: 3px solid {alert['color']};">
                        <span style="color: {alert['color']};">{alert['level']}</span><br>
                        <span style="color: white;">{alert['message']}</span><br>
                        <span style="color: #888; font-size: 0.8rem;">{alert['date'].strftime('%b %d, %Y') if alert['date'] else 'N/A'}</span>
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
    st.markdown("""
    **84 indicators** covering:
    
    **💰 Rates & Fed** (15)
    - Complete yield curve
    - Fed policy & balance sheet
    
    **👥 Labor Market** (10)
    - Unemployment, JOLTS, claims
    - Hours worked, temp help
    
    **📊 Growth** (8)
    - GDP, IP, retail sales
    - Consumer sentiment
    
    **🏠 Housing** (5)
    - Starts, permits, homeownership
    
    **📉 Market Fear** (3)
    - VIX, financial stress
    - Credit spreads
    
    **🌎 Demographics** (3)
    - Income, inequality, ownership
    """)
    
    st.markdown("---")
    
    # Quick stats
    df = load_data_with_spinner()
    if df is not None:
        st.markdown("### 📊 Dataset Stats")
        col1, col2 = st.columns(2)
        with col1:
            numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
            st.metric("Indicators", f"{numeric_cols}")
        with col2:
            st.metric("Days", f"{len(df):,}")
        
        st.markdown(f"**Date range:** {df['date'].min().year} - {df['date'].max().year}")
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
st.markdown("*Complete US Financial History Database - 84 Indicators*")

# Load data with spinner
df = load_data_with_spinner()
if df is None:
    st.stop()

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

# Create tabs - ADDED ATTRIBUTION TAB
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Today's Story", 
    "📈 History Explorer", 
    "🔍 Historical Matches",
    "📦 Data Shop",
    "📋 Attribution & Legal",
    "🎨 Visual Vault"  # New tab!
])

# ============================================================================
# TAB 1: TODAY'S STORY
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
    claims_val, claims_date = get_latest_value(df, 'IC4WSA', ['IC4WSA', 'ICSA'])
    civpart_val, civpart_date = get_latest_value(df, 'CIVPART', ['CIVPART'])
    cpi_val, cpi_date = get_latest_value(df, 'CPI_YOY', ['CPI_YOY'])
    pce_val, pce_date = get_latest_value(df, 'PCEPILFE', ['PCEPILFE'])
    tie_val, tie_date = get_latest_value(df, 'T10YIE', ['T10YIE'])
    sent_val, sent_date = get_latest_value(df, 'UMCSENT', ['UMCSENT'])
    retail_val, retail_date = get_latest_value(df, 'RSAFS', ['RSAFS'])
    hous_val, hous_date = get_latest_value(df, 'HOUST', ['HOUST'])
    permit_val, permit_date = get_latest_value(df, 'PERMIT', ['PERMIT'])
    vix_val, vix_date = get_latest_value(df, 'VIX', ['VIX'])
    hy_val, hy_date = get_latest_value(df, 'HY_SPREAD', ['HY_SPREAD', 'BAMLH0A0HYM2'])
    oil_val, oil_date = get_latest_value(df, 'DCOILWTICO', ['DCOILWTICO'])
    
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
    alerts, before_values = check_crisis_signals(df, war_start_date="2026-02-23")
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
        # Recession probability
        prob, label, color = get_recession_probability(spread_val)
        if prob:
            st.markdown(f"""
            <div style="background: {color}20; padding: 20px; border-radius: 10px; border-left: 4px solid {color};">
                <div style="text-align: center;">
                    <div style="color: #888;">RECESSION PROBABILITY</div>
                    <div style="font-size: 48px; font-weight: bold; color: {color};">{prob}%</div>
                    <div style="color: {color};">{label}</div>
                    <div style="color: #888; font-size: 0.8rem;">Next 12 months</div>
                </div>
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
        date_str = f" ({dgs10_date.strftime('%m/%d/%y')})" if dgs10_date else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">10Y YIELD{date_str}</div>
            <div><span class="metric-value">{format_value(dgs10_val, 2, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        date_str = f" ({dgs2_date.strftime('%m/%d/%y')})" if dgs2_date else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">2Y YIELD{date_str}</div>
            <div><span class="metric-value">{format_value(dgs2_val, 2, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        date_str = f" ({fed_date.strftime('%m/%d/%y')})" if fed_date else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">FED FUNDS{date_str}</div>
            <div><span class="metric-value">{format_value(fed_val, 2, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if spread_val is not None:
            spread_color = "#ff4d4d" if spread_val < 0 else "#00ff00"
            date_str = f" ({spread_date.strftime('%m/%d/%y')})" if spread_date else ""
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
        date_str = f" ({real_fed_date.strftime('%m/%d/%y')})" if real_fed_date else ""
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
            date_str = f" ({unrate_date.strftime('%m/%d/%y')})" if unrate_date else ""
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
        date_str = f" ({u6_date.strftime('%m/%d/%y')})" if u6_date else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">U-6 UNEMPLOYMENT{date_str}</div>
            <div><span class="metric-value">{format_value(u6_val, 1, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        date_str = f" ({jolts_date.strftime('%m/%d/%y')})" if jolts_date else ""
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
            date_str = f" ({claims_date.strftime('%m/%d/%y')})" if claims_date else ""
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
        date_str = f" ({civpart_date.strftime('%m/%d/%y')})" if civpart_date else ""
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
            date_str = f" ({cpi_date.strftime('%m/%d/%y')})" if cpi_date else ""
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
        date_str = f" ({pce_date.strftime('%m/%d/%y')})" if pce_date else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CORE PCE{date_str}</div>
            <div><span class="metric-value">{format_value(pce_val, 1, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        date_str = f" ({tie_date.strftime('%m/%d/%y')})" if tie_date else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">10Y INFLATION EXPECTATION{date_str}</div>
            <div><span class="metric-value">{format_value(tie_val, 2, '', '%')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if sent_val is not None:
            color = "#00ff00" if sent_val > 80 else "#ff4d4d" if sent_val < 60 else "#FFD700"
            date_str = f" ({sent_date.strftime('%m/%d/%y')})" if sent_date else ""
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
        date_str = f" ({retail_date.strftime('%m/%d/%y')})" if retail_date else ""
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
        date_str = f" ({hous_date.strftime('%m/%d/%y')})" if hous_date else ""
        hous_display = f"{hous_val/1000:.1f}M" if hous_val is not None else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">HOUSING STARTS{date_str}</div>
            <div><span class="metric-value">{hous_display}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        date_str = f" ({permit_date.strftime('%m/%d/%y')})" if permit_date else ""
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
            date_str = f" ({vix_date.strftime('%m/%d/%y')})" if vix_date else ""
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
            date_str = f" ({hy_date.strftime('%m/%d/%y')})" if hy_date else ""
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
        date_str = f" ({oil_date.strftime('%m/%d/%y')})" if oil_date else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">WTI OIL{date_str}</div>
            <div><span class="metric-value">{format_value(oil_val, 2, '$')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================
    # THE FULL STORY SUMMARY
    # =========================================
    
    st.markdown('<div class="sub-header">📝 The Complete Story</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🔴 Risks")
        risks = []
        
        if spread_val is not None and spread_val < 0:
            risks.append("• **Inverted yield curve** - Historically predicts recession")
        if unrate_val is not None and unrate_val < 3.5:
            risks.append("• **Ultra-low unemployment** - Could overheat economy")
        if cpi_val is not None and cpi_val > 4:
            risks.append("• **High inflation** - Erodes purchasing power")
        if hy_val is not None and hy_val > 5:
            risks.append("• **Wide high yield spreads** - Corporate stress")
        if vix_val is not None and vix_val > 30:
            risks.append("• **Elevated VIX** - Market fear/stress")
        
        if risks:
            for risk in risks:
                st.markdown(risk)
        else:
            st.markdown("• No major risks detected")
    
    with col2:
        st.markdown("##### 🟢 Strengths")
        strengths = []
        
        if spread_val is not None and spread_val > 0.5:
            strengths.append("• **Steep yield curve** - Growth expectations")
        if unrate_val is not None and 3.5 <= unrate_val <= 5:
            strengths.append("• **Goldilocks unemployment** - Healthy labor market")
        if cpi_val is not None and 2 <= cpi_val <= 3:
            strengths.append("• **Inflation near target** - Price stability")
        if hous_val is not None and hous_val > 1500:
            strengths.append("• **Robust housing starts** - Construction strength")
        if vix_val is not None and vix_val < 20:
            strengths.append("• **Low market fear** - Calm markets")
        
        if strengths:
            for strength in strengths:
                st.markdown(strength)
        else:
            st.markdown("• Economy showing mixed signals")
    
    # Data freshness note
    st.markdown("""
    <div class="data-info">
        *Dates in parentheses show when each value was last updated. Different indicators update at different frequencies.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB 2: HISTORY EXPLORER (ALL INDICATORS WITH ANNOTATIONS)
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
    
    # Comprehensive indicator dictionary organized by category
    indicators = {
        # Rates & Yields
        '💰 Rates: 10Y Treasury': 'DGS10',
        '💰 Rates: 2Y Treasury': 'DGS2',
        '💰 Rates: 30Y Treasury': 'DGS30',
        '💰 Rates: 3M Treasury': 'DGS3MO',
        '💰 Rates: 1Y Treasury': 'DGS1',
        '💰 Rates: 3Y Treasury': 'DGS3',
        '💰 Rates: 5Y Treasury': 'DGS5',
        '💰 Rates: 7Y Treasury': 'DGS7',
        '💰 Rates: 20Y Treasury': 'DGS20',
        
        # Fed Policy
        '🏦 Fed: Fed Funds Rate': 'FEDFUNDS',
        '🏦 Fed: Target Rate Upper': 'DFEDTARU',
        '🏦 Fed: Target Rate Lower': 'DFEDTARL',
        '🏦 Fed: Balance Sheet': 'WALCL',
        '🏦 Fed: Real Fed Funds': 'REAL_FEDFUNDS',
        
        # Spreads
        '📐 Spread: 10Y-2Y': '10Y2Y',
        '📐 Spread: 10Y-3M': '10Y3M',
        '📐 Spread: BAA-10Y Credit': 'BAA_SPREAD',
        '📐 Spread: AAA-10Y Credit': 'AAA_SPREAD',
        '📐 Spread: High Yield': 'HY_SPREAD',
        '📐 Spread: Risk Appetite (HY-BAA)': 'RISK_APPETITE',
        
        # Corporate Yields
        '🏢 Corporate: BAA Yield': 'BAA10Y',
        '🏢 Corporate: AAA Yield': 'AAA10Y',
        
        # Inflation
        '📈 Inflation: CPI All Items': 'CPIAUCSL',
        '📈 Inflation: Core CPI': 'CPILFESL',
        '📈 Inflation: PCE': 'PCEPI',
        '📈 Inflation: Core PCE': 'PCEPILFE',
        '📈 Inflation: CPI YoY': 'CPI_YOY',
        '📈 Inflation: 10Y Expectation': 'T10YIE',
        '📈 Inflation: 5Y Expectation': 'T5YIE',
        
        # Labor Market
        '👥 Labor: Unemployment Rate': 'UNRATE',
        '👥 Labor: U-6 Unemployment': 'U6RATE',
        '👥 Labor: Participation Rate': 'CIVPART',
        '👥 Labor: Job Openings (JOLTS)': 'JTSJOL',
        '👥 Labor: Quits Rate': 'JTSQUR',
        '👥 Labor: Initial Claims': 'IC4WSA',
        '👥 Labor: Continued Claims': 'CC4WSA',
        '👥 Labor: 4-Week Avg Claims': 'ICSA',
        '👥 Labor: Avg Weekly Hours': 'AWHAETP',
        '👥 Labor: Temporary Help': 'TEMPHELPS',
        
        # Growth & Output
        '📊 Growth: Real GDP': 'GDPC1',
        '📊 Growth: Industrial Production': 'INDPRO',
        '📊 Growth: Retail Sales': 'RSAFS',
        
        # Housing
        '🏠 Housing: Starts': 'HOUST',
        '🏠 Housing: Permits': 'PERMIT',
        '🏠 Housing: Homeownership Rate': 'RHORUSQ156N',
        
        # Consumer
        '💳 Consumer: Sentiment': 'UMCSENT',
        '💳 Consumer: Median Income': 'MEHOINUSA672N',
        
        # Money & Credit
        '💰 Money: M2 Supply': 'M2SL',
        '💰 Money: M2 Real': 'M2_REAL',
        '💰 Money: M2 Real Growth': 'M2_REAL_YOY',
        '💰 Money: Household Net Worth': 'TNWBSHNO',
        '💰 Money: Total Reserves': 'TOTRESNS',
        
        # Market Indicators
        '😨 Market: VIX Fear Gauge': 'VIX',
        '🛢️ Market: Oil Price (WTI)': 'DCOILWTICO',
        '💵 Market: Dollar Index': 'DTWEXBGS',
        '📉 Market: Financial Stress': 'STLFSI4',
        
        # Demographics
        '🌎 Demographics: Gini Coefficient': 'GINIALL',
        
        # Recession Probability
        '⚠️ Recession Probability': 'RECPROUSM156N'
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
# TAB 3: HISTORICAL MATCHES (ENHANCED)
# ============================================================================

with tab3:
    st.markdown('<div class="sub-header">🔍 Historical Matches: Where Have We Seen This Before?</div>', unsafe_allow_html=True)
    
    if 'DGS10' in df.columns:
        latest_yield = df[df['DGS10'].notna()].iloc[-1]['DGS10'] if not df[df['DGS10'].notna()].empty else None
        latest_date = df[df['DGS10'].notna()].iloc[-1]['date'] if not df[df['DGS10'].notna()].empty else None
        
        if latest_yield is not None:
            # Get current context
            current_unrate = df[df['UNRATE'].notna()].iloc[-1]['UNRATE'] if 'UNRATE' in df.columns else None
            current_cpi = df[df['CPI_YOY'].notna()].iloc[-1]['CPI_YOY'] if 'CPI_YOY' in df.columns else None
            
            # Current environment card
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                        padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="color: #FFD700; margin: 0;">Current Economic Environment</h4>
                <p style="color: white; margin: 5px 0;">
                    10Y Yield: {latest_yield:.2f}% • 
                    Unemployment: {current_unrate:.1f}% • 
                    Inflation: {current_cpi:.1f}%
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Era selector
            col1, col2 = st.columns([3, 1])
            with col1:
                era = st.radio(
                    "Focus on:", 
                    ["All History", "Pre-2000", "Post-2000"], 
                    horizontal=True,
                    help="Compare current yields with different historical periods"
                )
            
            matches = find_historical_matches(df, latest_yield, latest_date, n=5, era=era)
            
            if not matches.empty:
                # Summary stats
                crisis_count = matches['led_to_crisis'].sum()
                st.markdown(f"""
                <div class="era-selector">
                    <strong>{crisis_count} of 5</strong> similar periods led to crisis within 12 months
                </div>
                """, unsafe_allow_html=True)
                
                for i, (_, match) in enumerate(matches.iterrows(), 1):
                    with st.expander(f"Match #{i}: {match['date'].strftime('%B %Y')} (Similarity: {match['similarity']:.0f}%)", expanded=(i==1)):
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Yield then:** {match['DGS10']:.2f}%")
                            if pd.notna(match['unrate_then']):
                                st.markdown(f"**Unemployment then:** {match['unrate_then']:.1f}%")
                            if pd.notna(match['cpi_then']):
                                st.markdown(f"**Inflation then:** {match['cpi_then']:.1f}%")
                        
                        with col2:
                            outcome = "🔴 LED TO CRISIS" if match['led_to_crisis'] else "🟢 NO CRISIS"
                            st.markdown(f"**Outcome:** {outcome}")
                            if pd.notna(match['yield_12m']):
                                change = match['yield_12m'] - match['DGS10']
                                direction = "▲" if change > 0 else "▼"
                                st.markdown(f"**12 months later:** {match['yield_12m']:.2f}% ({direction} {abs(change):.2f}%)")
                        
                        if pd.notna(match['max_yield']) and pd.notna(match['min_yield']):
                            st.markdown(f"**Range next 12 months:** {match['min_yield']:.2f}% - {match['max_yield']:.2f}%")
            else:
                st.info("No close historical matches found for current yield level in selected era.")
        else:
            st.warning("No recent DGS10 data available for historical matching")
    else:
        st.warning("DGS10 data not available for historical matching")

# ============================================================================
# TAB 4: DATA SHOP (WITH EMAIL CAPTURE AND ATTRIBUTION)
# ============================================================================

with tab4:
    st.markdown('<div class="sub-header">📦 Complete US Economic Dataset</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                padding: 20px; border-radius: 8px; margin-bottom: 30px;">
        <h2 style="color: #FFD700; margin: 0;">84 Indicators • 64 Years • Daily Updates</h2>
        <p style="color: #ccc; margin: 10px 0 0;">The complete story of the American economy, cleaned and ready to use.</p>
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
            <div>✓ 50+ indicators in one file</div>
            <div>✓ Proprietary spreads & ratios</div>
            <div>✓ Daily automated updates</div>
            <div>✓ No gaps, weekends, or holidays</div>
            <div>✓ Historical event annotations</div>
            <div>✓ Historical match analysis</div>
            <div>✓ One-click download, no API keys</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
        
        **📈 Inflation** (8)
        - CPI, Core CPI, PCE, Core PCE
        - Breakeven expectations
        - Real-time inflation
        
        **🏠 Housing** (5)
        - Starts, permits, homeownership
        - Housing market health
        """)
    
    with col2:
        st.markdown("""
        **📊 Growth** (5)
        - GDP, Industrial Production
        - Retail sales, sentiment
        
        **📉 Market Stress** (5)
        - VIX fear gauge
        - Financial stress index
        - High yield spreads
        
        **💵 Money & Credit** (8)
        - M2 money supply
        - Household net worth
        - Credit spreads (BAA, AAA, HY)
        
        **🌎 Demographics** (3)
        - Income, inequality, ownership
        """)
    
    # Stats
    st.markdown("### 📈 Dataset Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
        st.metric("Total Indicators", f"{numeric_cols}")
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
        <p style="color: white; opacity: 0.9;">We're preparing the complete 84-indicator dataset for download. Join the waitlist and we'll email you when it's available.</p>
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
                <li><strong>The raw dataset</strong> - 84 indicators in CSV format</li>
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
    | Combine 50+ indicators into one file | One download, one source |
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

# In tab6:
with tab6:
    visual_vault.create_vault_tab(df, HISTORICAL_EVENTS)

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