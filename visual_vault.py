# visual_vault.py - Complete version with all fixes
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

# ============================================================================
# IMPORTANT: VULNERABILITY INDEX™ vs VIX - PLEASE READ
# ============================================================================
"""
🔴 THE VULNERABILITY INDEX™ IS NOT THE VIX!

Many users ask: "Is this just the VIX?" The answer is NO.

The VIX (CBOE Volatility Index) measures ONLY stock market fear - 
it's just one small piece of the puzzle.

The Vulnerability Index™ is a COMPOSITE measure of SYSTEMIC US MARKET STRESS:

┌─────────────────┬──────────────────────────────────────────────┐
│ COMPONENT       │ WHAT IT MEASURES                             │
├─────────────────┼──────────────────────────────────────────────┤
│ CURVE STRESS    │ Yield curve inversion (10Y-2Y spread)        │
│ CREDIT STRESS   │ High yield corporate borrowing costs         │
│ VIX STRESS      │ Stock market fear/volatility (this is the VIX)│
│ SYSTEMIC STRESS │ Overall financial conditions index           │
└─────────────────┴──────────────────────────────────────────────┘

Think of it this way:
- VIX = Your heart rate during a scary movie
- Vulnerability Index™ = Your doctor's full check-up (blood pressure, cholesterol, etc.)

The VIX is just ONE of FOUR components that make up your proprietary index.
"""

# ============================================================================
# CONFIGURATION - REPLACE THE EXISTING COLORS DICTIONARY WITH THIS
# ============================================================================

# Unified color scheme for both light and dark modes
COLORS = {
    # Primary - works in both modes
    'gold': '#D4AF37',  # Softer gold (less harsh in light mode)
    'gold_light': '#F0E68C',  # Khaki for light backgrounds
    'gold_dark': '#996515',  # Darker gold for dark backgrounds
    
    # Status colors - adjusted for both modes
    'green': '#2E7D32',  # Forest green (works on light & dark)
    'green_light': '#81C784',  # Lighter green for dark mode
    'green_dark': '#1B5E20',  # Darker green for light mode
    
    'red': '#C62828',  # Deep red (not too bright)
    'red_light': '#EF5350',  # Lighter red for dark mode
    'red_dark': '#8B0000',  # Dark red for light mode
    
    'yellow': '#FFB300',  # Amber (better than pure gold for light mode)
    
    # Era colors - adjusted for both modes
    'era_1960s': '#64B5F6',  # Medium blue (not too light, not too dark)
    'era_1970s': '#FF7043',  # Coral (works in both)
    'era_1980s': '#42A5F5',  # Bright blue (pops in both)
    'era_1990s': '#FFD54F',  # Soft gold (less harsh than pure gold)
    'era_2000s': '#B71C1C',  # Deep red (works in both)
    'era_2010s': '#AB47BC',  # Medium purple (visible in both)
    'era_2020s': '#FF8A65',  # Soft orange (works in both)
    
    # Chart-specific palettes - updated to use era colors
    'american_century': '#D4AF37',
    'vulnerability': '#FF6B6B',
    'yield_curve': ['#FFD700', '#FFA500', '#FF8C00', '#FF4500', '#DC143C'],
    'regime_map': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    'fed_footprint': ['#D4AF37', '#42A5F5'],  # Updated gold and blue
    'unemployment': ['#D4AF37', '#FF7043', '#AB47BC'],  # Updated colors
    'inflation': ['#D4AF37', '#81C784', '#42A5F5'],  # Updated colors
    'vulnerability_clock': ['#FF6B6B', '#64B5F6', '#AB47BC', '#81C784', '#FFD54F', '#FF8A65', '#B71C1C', '#42A5F5'],
    'era_comparison': ['#D4AF37', '#42A5F5', '#FF7043'],  # Updated colors
    'fear_timeline': ['#D4AF37', '#FF7043', '#C62828', '#8B0000'],
    'housing_cycle': ['#D4AF37', '#64B5F6', '#81C784'],
    'dashboard': ['#D4AF37', '#2E7D32', '#C62828', '#FFB300', '#AB47BC', '#FF8A65', '#64B5F6', '#FF7043'],
    
    # Utility colors - adaptive
    'white': '#FFFFFF',
    'gray': '#9E9E9E',
    'gray_light': '#E0E0E0',
    'gray_dark': '#616161',
    'dark_bg': '#1a1a1a',
    'light_bg': '#f5f5f5'
}



CHART_METADATA = [
    {'id': 1, 'title': 'The American Yield', 'description': '64 years of boom, bust, and everything in between', 'icon': '📜'},
    {'id': 2, 'title': 'The Vulnerability Index', 'description': 'Your proprietary crisis warning system', 'icon': '🔴'},
    {'id': 3, 'title': 'The Economic Carousel', 'description': '10Y yield by decade - like a Ferris wheel of history', 'icon': '🎪'},
    {'id': 4, 'title': 'The Economic Compass', 'description': 'Navigate the inflation-unemployment trade-off through history', 'icon': '🧭'},
    {'id': 5, 'title': 'The Fed Footprint', 'description': 'Two tools of the Fed', 'icon': '🏦'},
    {'id': 6, 'title': 'The Real Unemployment Gap', 'description': 'Official numbers lie', 'icon': '👥'},
    {'id': 7, 'title': 'The Inflation Story', 'description': "What's actually getting expensive", 'icon': '📊'},
    {'id': 8, 'title': 'The Vulnerability Clock', 'description': '8 dimensions of stress in one glance', 'icon': '⏰'},
    {'id': 9, 'title': 'Era Comparison', 'description': 'This happened before...', 'icon': '🔄'},
    {'id': 10, 'title': 'The Fear Timeline', 'description': 'Every crisis, measured in fear', 'icon': '😨'},
    {'id': 11, 'title': 'The Housing Cycle', 'description': 'Housing leads everything', 'icon': '🏠'},
    {'id': 12, 'title': 'The Complete Dashboard', 'description': 'Economy in 3 seconds', 'icon': '📋'}
]

# ============================================================================
# SAFE DATE HANDLING FUNCTION
# ============================================================================

def safe_strftime(date_obj, format_string):
    """Safely format a date, handling both string and datetime objects"""
    if date_obj is None:
        return "Unknown"
    if isinstance(date_obj, str):
        try:
            date_obj = pd.to_datetime(date_obj, format='%d/%m/%Y', dayfirst=True)
        except:
            try:
                date_obj = pd.to_datetime(date_obj)
            except:
                return str(date_obj)
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime(format_string)
    return str(date_obj)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_curve_stress(spread):
    if pd.isna(spread):
        return np.nan
    stress = ((spread * -1) + 0.5) * 66.7
    return max(0, min(100, stress))

def normalize_credit_stress(spread):
    if pd.isna(spread):
        return np.nan
    stress = (spread - 2) / 6 * 100
    return max(0, min(100, stress))

def normalize_vix_stress(vix):
    if pd.isna(vix):
        return np.nan
    stress = (vix - 15) / 25 * 100
    return max(0, min(100, stress))

def normalize_systemic_stress(stlfsi):
    if pd.isna(stlfsi):
        return np.nan
    stress = stlfsi / 2 * 100
    return max(0, min(100, stress))

def normalize_labor_stress(unrate):
    if pd.isna(unrate):
        return np.nan
    stress = (unrate - 3) / 7 * 100
    return max(0, min(100, stress))

def normalize_inflation_stress(cpi):
    if pd.isna(cpi):
        return np.nan
    stress = (cpi - 2) / 6 * 100
    return max(0, min(100, stress))

def normalize_housing_stress(starts):
    if pd.isna(starts):
        return np.nan
    stress = (2000 - starts) / 1500 * 100
    return max(0, min(100, stress))

def normalize_dollar_stress(dollar):
    if pd.isna(dollar):
        return np.nan
    stress = (dollar - 90) / 40 * 100
    return max(0, min(100, stress))

def normalize_sentiment_stress(sentiment):
    if pd.isna(sentiment):
        return np.nan
    stress = (100 - sentiment) / 60 * 100
    return max(0, min(100, stress))

def calculate_vulnerability_index(df):
    """
    Calculate the composite Vulnerability Index™
    
    ⚠️ NOTE: This is NOT the VIX! The VIX is only ONE component.
    
    The Vulnerability Index™ combines:
    - CURVE_STRESS: Yield curve inversion (10Y2Y) - signals recession risk
    - CREDIT_STRESS: High yield spreads - corporate borrowing stress
    - VIX_STRESS: Market fear/volatility - stock market panic
    - SYSTEM_STRESS: Financial conditions index - broad market stress
    
    Range: 0-100
    - <40: LOW stress - Normal conditions
    - 40-70: ELEVATED stress - Caution warranted
    - >70: HIGH stress - Crisis conditions
    
    Returns DataFrame with added VULNERABILITY_INDEX column
    """
    df = df.copy()
    
    # Initialize all stress columns with NaN
    df['CURVE_STRESS'] = np.nan
    df['CREDIT_STRESS'] = np.nan
    df['VIX_STRESS'] = np.nan
    df['SYSTEM_STRESS'] = np.nan
    
    # Calculate curve stress (10Y2Y) - most reliable
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
    
    # Calculate composite - only where at least 2 components are available
    stress_components = [df['CURVE_STRESS'], df['CREDIT_STRESS'], 
                         df['VIX_STRESS'], df['SYSTEM_STRESS']]
    
    # Count non-null components for each row
    non_null_count = pd.concat(stress_components, axis=1).notna().sum(axis=1)
    
    # Calculate mean of available components (minimum 2 components required)
    df['VULNERABILITY_INDEX'] = np.where(
        non_null_count >= 2,
        pd.concat(stress_components, axis=1).mean(axis=1, skipna=True),
        np.nan
    )
    
    return df

def get_vulnerability_status(value):
    """Get status text and color for vulnerability index"""
    if pd.isna(value) or value is None:
        return "UNAVAILABLE", COLORS['gray']
    if value < 40:
        return "LOW", COLORS['green']
    elif value < 70:
        return "ELEVATED", COLORS['yellow']
    else:
        return "HIGH", COLORS['red']

# ============================================================================
# IMPROVED HISTORICAL MATCHES FUNCTION - REPLACE WITH THIS
# ============================================================================

def find_historical_matches(df, current_date):
    """Find closest historical matches for era comparison with better data quality"""
    
    current_yield = df['DGS10'].iloc[-1]
    current_unrate = df['UNRATE'].iloc[-1]
    current_cpi = df['CPI_YOY'].iloc[-1]
    current_spread = df['10Y2Y'].iloc[-1]
    
    # Create historical dataset (exclude last 30 days)
    historical = df[df['date'] < current_date - pd.Timedelta(days=30)].copy()
    
    if historical.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # Filter to rows that have at least 3 of 4 indicators available
    historical['data_quality'] = (
        historical['DGS10'].notna().astype(int) +
        historical['UNRATE'].notna().astype(int) +
        historical['CPI_YOY'].notna().astype(int) +
        historical['10Y2Y'].notna().astype(int)
    )
    
    # Only consider rows with good data quality
    quality_df = historical[historical['data_quality'] >= 3].copy()
    
    if quality_df.empty:
        # Fallback to any data if quality filter is too strict
        quality_df = historical.copy()
    
    # Calculate weighted difference
    quality_df['score'] = (
        abs(quality_df['DGS10'].fillna(current_yield) - current_yield) * 0.3 +
        abs(quality_df['UNRATE'].fillna(current_unrate) - current_unrate) * 0.3 +
        abs(quality_df['CPI_YOY'].fillna(current_cpi) - current_cpi) * 0.2 +
        abs(quality_df['10Y2Y'].fillna(current_spread) - current_spread) * 0.2
    )
    
    # Split into pre-2000 and post-2000
    pre_2000 = quality_df[quality_df['date'] < '2000-01-01']
    post_2000 = quality_df[quality_df['date'] >= '2000-01-01']
    
    # Get best matches
    pre_match = pre_2000.nsmallest(1, 'score') if not pre_2000.empty else pd.DataFrame()
    post_match = post_2000.nsmallest(1, 'score') if not post_2000.empty else pd.DataFrame()
    
    return pre_match, post_match

# ============================================================================
# HELPER FUNCTION TO GET LATEST NON-NULL VALUE
# ============================================================================

def get_latest_value(df, column, default="N/A", format_func=None):
    """Get the most recent non-null value for a column"""
    if column not in df.columns:
        return default, COLORS['gray'], None
    
    # Get all non-null values
    valid_data = df[df[column].notna()]
    if valid_data.empty:
        return default, COLORS['gray'], None
    
    # Get the most recent value
    latest_row = valid_data.iloc[-1]
    latest_val = latest_row[column]
    latest_date = latest_row['date']
    
    # Format the value
    if format_func:
        formatted_val = format_func(latest_val)
    else:
        formatted_val = f"{latest_val:.2f}" if isinstance(latest_val, (int, float)) else str(latest_val)
    
    # Determine color based on value and column
    color = determine_color(column, latest_val)
    
    return formatted_val, color, latest_date

def determine_color(column, value):
    """Determine the color for a value based on its column and value"""
    if pd.isna(value):
        return COLORS['gray']
    
    if column == 'DGS10':
        return COLORS['green'] if value < 4 else COLORS['red'] if value > 6 else COLORS['yellow']
    elif column == 'UNRATE':
        return COLORS['green'] if value < 4 else COLORS['red'] if value > 6 else COLORS['yellow']
    elif column == 'CPI_YOY':
        return COLORS['green'] if value < 3 else COLORS['red'] if value > 5 else COLORS['yellow']
    elif column == '10Y2Y':
        return COLORS['red'] if value < 0 else COLORS['green']
    elif column == 'VIX':
        status, color = get_vulnerability_status(normalize_vix_stress(value))
        return color
    elif column == 'DCOILWTICO':
        return COLORS['dashboard'][5]
    elif column == 'HOUST':
        return COLORS['green'] if value > 1500 else COLORS['red'] if value < 1000 else COLORS['yellow']
    elif column == 'UMCSENT':
        return COLORS['green'] if value > 80 else COLORS['red'] if value < 60 else COLORS['yellow']
    else:
        return COLORS['gold']

# ============================================================================
# ANIMATION HELPERS
# ============================================================================

def create_animation_buttons():
    """Create play/pause buttons for animations"""
    return [dict(
        type="buttons",
        buttons=[dict(
            label="▶️ Play",
            method="animate",
            args=[None, {"frame": {"duration": 200, "redraw": True}, "fromcurrent": True}]
        ), dict(
            label="⏸️ Pause",
            method="animate",
            args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]
        )],
        direction="left",
        pad={"r": 10, "t": 10},
        showactive=False,
        x=0.1,
        y=0,
        xanchor="right",
        yanchor="top"
    )]

# ============================================================================
# HELPER FUNCTIONS FOR VULNERABILITY CLOCK
# ============================================================================

def get_value_with_fallback(df, column, target_date):
    """
    Get value for a specific date, falling back to most recent non-null value
    """
    if column not in df.columns:
        return None
    
    # Try to get value at exact date
    mask = df['date'] == target_date
    if mask.any():
        val = df.loc[mask, column].iloc[0]
        if not pd.isna(val):
            return val
    
    # Fall back to most recent value before target_date
    mask = df['date'] <= target_date
    valid_data = df[mask & df[column].notna()]
    if not valid_data.empty:
        return valid_data.iloc[-1][column]
    
    return None

def normalize_by_column(column, value):
    """Normalize a raw value to 0-100 stress scale based on column type"""
    if column == '10Y2Y':
        return normalize_curve_stress(value)
    elif column == 'HY_SPREAD':
        return normalize_credit_stress(value)
    elif column == 'UNRATE':
        return normalize_labor_stress(value)
    elif column == 'CPI_YOY':
        return normalize_inflation_stress(value)
    elif column == 'VIX':
        return normalize_vix_stress(value)
    elif column == 'HOUST':
        return normalize_housing_stress(value)
    elif column == 'DTWEXBGS':
        return normalize_dollar_stress(value)
    elif column == 'UMCSENT':
        return normalize_sentiment_stress(value)
    else:
        return 50

# ============================================================================
# CHART 1: THE AMERICAN YIELD - MINARD-INSPIRED ERA VISUALIZATION
# ============================================================================

def create_american_yield_eras(df):
    """
    Chart 1: The American Yield - 64 Years of Boom, Bust, and Everything in Between
    Inspired by Minard's Napoleon map - showing multiple dimensions in one view
    """
    
    # Define eras with their characteristics
    eras = [
        {
            'name': '1960s',
            'start': '1960-01-01',
            'end': '1969-12-31',
            'icon': '🌅',
            'description': 'Calm Before the Storm',
            'yield_trend': 'Stable 4-5%',
            'inflation': 'Low (1-2%)',
            'recessions': '2 (1960, 1969)',
            'market': 'Mixed',
            'color': '#87CEEB',  # Sky blue
            'story': 'Post-war prosperity, but inflation begins to stir'
        },
        {
            'name': '1970s',
            'start': '1970-01-01',
            'end': '1979-12-31',
            'icon': '🔥',
            'description': 'Stagflation',
            'yield_trend': '6% → 12%',
            'inflation': 'HIGH (6-14%)',
            'recessions': '2 (1973, 1979)',
            'market': 'FLAT (Dow 800→800)',
            'color': '#FF4500',  # Orange-red
            'story': 'Oil shocks, wage-price spiral, "misery index" soars'
        },
        {
            'name': '1980s',
            'start': '1980-01-01',
            'end': '1989-12-31',
            'icon': '❄️',
            'description': 'Volcker Disinflation',
            'yield_trend': '12% → 8%',
            'inflation': 'FALLING (14%→4%)',
            'recessions': '2 (1980, 1981)',
            'market': 'BOOMING (+220%)',
            'color': '#00BFFF',  # Deep sky blue
            'story': 'Volcker breaks inflation, economy rebounds, stocks soar'
        },
        {
            'name': '1990s',
            'start': '1990-01-01',
            'end': '1999-12-31',
            'icon': '✨',
            'description': 'Goldilocks',
            'yield_trend': '8% → 5%',
            'inflation': 'LOW (2-3%)',
            'recessions': '1 (1990)',
            'market': 'BOOMING (+320%)',
            'color': '#FFD700',  # Gold
            'story': 'Perfect economy: growth + low inflation + tech boom'
        },
        {
            'name': '2000s',
            'start': '2000-01-01',
            'end': '2009-12-31',
            'icon': '💥',
            'description': 'Bubble & Bust',
            'yield_trend': '5% → 2%',
            'inflation': 'MODERATE (2-4%)',
            'recessions': '1 (2008 BIG)',
            'market': 'CRASH (-40% peak to trough)',
            'color': '#8B0000',  # Dark red
            'story': 'Dot-com crash, housing bubble, financial crisis'
        },
        {
            'name': '2010s',
            'start': '2010-01-01',
            'end': '2019-12-31',
            'icon': '💊',
            'description': 'ZIRP Era',
            'yield_trend': '2% → 1%',
            'inflation': 'LOW (1-2%)',
            'recessions': '0',
            'market': 'BOOMING (+190%)',
            'color': '#9370DB',  # Medium purple
            'story': 'Zero interest rates, quantitative easing, slow growth'
        },
        {
            'name': '2020s',
            'start': '2020-01-01',
            'end': df['date'].max().strftime('%Y-%m-%d'),
            'icon': '🔥',
            'description': 'Inflation Return',
            'yield_trend': '1% → 4%',
            'inflation': 'SURGING (2→9%)',
            'recessions': '1 (COVID)',
            'market': 'VOLATILE',
            'color': '#FF6346',  # Tomato
            'story': 'Pandemic, stimulus, inflation spike, Fed hiking'
        }
    ]
    
    # Create figure
    fig = go.Figure()
    
    # Add yield line as background
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['DGS10'],
        mode='lines',
        name='10Y Treasury Yield',
        line=dict(color=COLORS['gold'], width=2),
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Yield: %{y:.2f}%<extra></extra>'
    ))
    
    # Add era shading and annotations
    for i, era in enumerate(eras):
        start_date = pd.to_datetime(era['start'])
        end_date = pd.to_datetime(era['end'])
        
        # Add colored background
        fig.add_vrect(
            x0=start_date,
            x1=end_date,
            fillcolor=era['color'],
            opacity=0.15,
            layer='below',
            line_width=0,
        )
        
        # Calculate middle of era for annotation
        mid_date = start_date + (end_date - start_date) / 2
        
        # Get average yield during era for vertical positioning
        era_data = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        avg_yield = era_data['DGS10'].mean() if not era_data.empty else 5
        
        # Era icon and name at top
        fig.add_annotation(
            x=mid_date,
            y=15,
            text=f"{era['icon']} {era['name']}",
            showarrow=False,
            font=dict(size=12, color='white', family='Arial Black'),
            bgcolor=era['color'],
            bordercolor='white',
            borderwidth=1,
            borderpad=4,
            yshift=0
        )
        
        # Era details in hover
        hover_text = (
            f"<b>{era['icon']} {era['name']}: {era['description']}</b><br><br>"
            f"📈 Yield Trend: {era['yield_trend']}<br>"
            f"📊 Inflation: {era['inflation']}<br>"
            f"📉 Recessions: {era['recessions']}<br>"
            f"💹 Market: {era['market']}<br><br>"
            f"📖 {era['story']}"
        )
        
        # Add invisible marker for hover
        fig.add_trace(go.Scatter(
            x=[mid_date],
            y=[avg_yield],
            mode='markers',
            marker=dict(size=20, color='rgba(0,0,0,0)'),
            name=era['name'],
            text=hover_text,
            hoverinfo='text',
            showlegend=False
        ))
        
        # Add era-specific icons along the yield line
        if era['icon'] == '🔥' and era['name'] == '1970s':
            # Add fire icons for each year of high inflation
            years = [1973, 1974, 1975, 1979]
            for year in years:
                year_date = pd.to_datetime(f'{year}-06-30')
                year_data = df[df['date'] == year_date]
                if not year_data.empty:
                    y_val = year_data['DGS10'].iloc[0]
                    fig.add_annotation(
                        x=year_date,
                        y=y_val,
                        text='🔥',
                        showarrow=False,
                        font=dict(size=16)
                    )
        
        elif era['icon'] == '❄️' and era['name'] == '1980s':
            # Add snowflake at Volcker peak
            volcker_date = pd.to_datetime('1981-10-01')
            volcker_data = df[df['date'] == volcker_date]
            if not volcker_data.empty:
                y_val = volcker_data['DGS10'].iloc[0]
                fig.add_annotation(
                    x=volcker_date,
                    y=y_val,
                    text='❄️ Volcker Peak',
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor='white',
                    font=dict(size=10, color='white'),
                    bgcolor='rgba(0,0,0,0.7)',
                    bordercolor='white',
                    borderwidth=1,
                    yshift=20
                )
        
        elif era['icon'] == '✨' and era['name'] == '1990s':
            # Add sparkle at tech boom
            tech_date = pd.to_datetime('1999-12-31')
            tech_data = df[df['date'] == tech_date]
            if not tech_data.empty:
                y_val = tech_data['DGS10'].iloc[0]
                fig.add_annotation(
                    x=tech_date,
                    y=y_val,
                    text='✨ Tech Boom',
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor='white',
                    font=dict(size=10, color='white'),
                    bgcolor='rgba(0,0,0,0.7)',
                    bordercolor='white',
                    borderwidth=1,
                    yshift=-20
                )
        
        elif era['icon'] == '💥' and era['name'] == '2000s':
            # Add explosion at Lehman
            lehman_date = pd.to_datetime('2008-09-15')
            lehman_data = df[df['date'] == lehman_date]
            if not lehman_data.empty:
                y_val = lehman_data['DGS10'].iloc[0]
                fig.add_annotation(
                    x=lehman_date,
                    y=y_val,
                    text='💥 Lehman',
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor='red',
                    font=dict(size=10, color='white'),
                    bgcolor='rgba(0,0,0,0.7)',
                    bordercolor='red',
                    borderwidth=2,
                    yshift=20
                )
    
    # Add "YOU ARE HERE" marker
    today = df['date'].iloc[-1]
    today_yield = df['DGS10'].iloc[-1]
    
    fig.add_annotation(
        x=today,
        y=today_yield,
        text='📍 YOU ARE HERE',
        showarrow=True,
        arrowhead=2,
        arrowsize=2,
        arrowwidth=3,
        arrowcolor=COLORS['gold'],
        font=dict(size=14, color='white', family='Arial Black'),
        bgcolor='rgba(0,0,0,0.8)',
        bordercolor=COLORS['gold'],
        borderwidth=3,
        yshift=30
    )
    
    # Add legend for icons
    legend_text = (
        "🔥 Stagflation | ❄️ Disinflation | ✨ Goldilocks | 💥 Crisis | 💊 ZIRP"
    )
    
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=1.05,
        text=legend_text,
        showarrow=False,
        font=dict(size=12, color='white'),
        align="center"
    )
    
    fig.update_layout(
        title=dict(
            text="📜 The American Yield: 64 Years of Boom, Bust, and Everything in Between",
            font=dict(color=COLORS['gold'], size=20, family='Arial Black')
        ),
        xaxis=dict(
            title="Year",
            gridcolor='rgba(255,255,255,0.1)',
            range=[df['date'].min(), df['date'].max()]
        ),
        yaxis=dict(
            title="10Y Treasury Yield (%)",
            gridcolor='rgba(255,255,255,0.1)',
            range=[0, 16]
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=600,
        showlegend=False,
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    return fig

# ============================================================================
# CHART 2: THE VULNERABILITY INDEX
# ============================================================================

def create_vulnerability_index(df, historical_events):
    """Chart 2: The Vulnerability Index™ - Your proprietary crisis warning system"""
    
    # Add this at the beginning of the function
    st.caption("""
    ⚠️ **Note:** The Vulnerability Index™ is NOT the VIX. 
    It combines 4 components: Curve Stress (yield curve), Credit Stress (spreads), 
    VIX Stress (market fear), and Systemic Stress (financial conditions).
    The VIX is just one of four inputs.
    """)
    
    df_vuln = calculate_vulnerability_index(df)
    df_vuln = df_vuln.dropna(subset=['VULNERABILITY_INDEX'])
    
    fig = go.Figure()
    
    # Add background zones
    fig.add_hrect(y0=0, y1=40, line_width=0, fillcolor="rgba(0,255,0,0.15)",
                  annotation_text="LOW", annotation_position="top left",
                  annotation_font=dict(color=COLORS['green'], family='Arial Black'))
    fig.add_hrect(y0=40, y1=70, line_width=0, fillcolor="rgba(255,215,0,0.15)",
                  annotation_text="ELEVATED", annotation_position="top left",
                  annotation_font=dict(color=COLORS['yellow'], family='Arial Black'))
    fig.add_hrect(y0=70, y1=100, line_width=0, fillcolor="rgba(255,68,68,0.15)",
                  annotation_text="HIGH", annotation_position="top left",
                  annotation_font=dict(color=COLORS['red'], family='Arial Black'))
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=df_vuln['date'],
        y=df_vuln['VULNERABILITY_INDEX'],
        mode='lines',
        name='Vulnerability Index',
        line=dict(color=COLORS['vulnerability'], width=3),
        fill='tozeroy',
        fillcolor='rgba(255,107,107,0.2)'
    ))
    
    # Add crisis markers
    crisis_dates = [
        ('2001-09-11', '9/11', COLORS['red_dark']),
        ('2008-09-15', 'Lehman', COLORS['red']),
        ('2020-03-15', 'COVID', COLORS['red_light'])
    ]
    
    for date, label, color in crisis_dates:
        event_date = pd.to_datetime(date)
        mask = abs(df_vuln['date'] - event_date) < pd.Timedelta(days=30)
        if mask.any():
            y_val = df_vuln.loc[mask, 'VULNERABILITY_INDEX'].iloc[0]
            fig.add_annotation(
                x=event_date,
                y=y_val,
                text=f"🔴 {label}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=color,
                font=dict(size=11, color='white', family='Arial Black'),
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor=color,
                borderwidth=2
            )
    
    fig.update_layout(
        title=dict(
            text="🔴 The Vulnerability Index™ - Crisis Warning System",
            font=dict(color=COLORS['vulnerability'], size=20, family='Arial Black')
        ),
        xaxis=dict(
            title=dict(text="", font=dict(color='white')),
            rangeslider=dict(visible=True),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text="Stress Level (0-100)", font=dict(color=COLORS['vulnerability'])),
            tickfont=dict(color=COLORS['vulnerability']),
            range=[0, 100],
            gridcolor='rgba(255,255,255,0.1)'
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    
    return fig

# ============================================================================
# CHART 3: The Economic Carousel - With Streamlit State Management
# ============================================================================

def create_economic_carousel(df, chart_key="carousel"):
    """
    Chart 3: Circular Bar Chart - Uses session state to preserve animation
    """
    
    # Initialize session state for this chart
    if f'{chart_key}_rotation' not in st.session_state:
        st.session_state[f'{chart_key}_rotation'] = 345  # Start at 345°
    if f'{chart_key}_playing' not in st.session_state:
        st.session_state[f'{chart_key}_playing'] = False
    
    # Calculate decade averages
    df['decade'] = (df['date'].dt.year // 10) * 10
    decade_avg = df.groupby('decade')['DGS10'].mean().reset_index()
    
    # Format for chart
    decades = [f"{int(d)}s" for d in decade_avg['decade']]
    yields = decade_avg['DGS10'].round(2).tolist()
    
    # Unified era colors
    era_colors = {
        1960: '#64B5F6',  # Medium blue
        1970: '#FF7043',  # Coral
        1980: '#42A5F5',  # Bright blue
        1990: '#FFD54F',  # Soft gold
        2000: '#B71C1C',  # Deep red
        2010: '#AB47BC',  # Medium purple
        2020: '#FF8A65'   # Soft orange
    }
    
    colors = [era_colors.get(d, '#9E9E9E') for d in decade_avg['decade']]
    
    # Get today's yield
    today_data = df[df['DGS10'].notna()]
    if not today_data.empty:
        today_row = today_data.iloc[-1]
        today_yield = today_row['DGS10']
        today_date = today_row['date']
        today_str = today_date.strftime('%b %d, %Y')
        today_display = f"{today_yield:.2f}%"
    else:
        today_yield = 4.5
        today_date = datetime.now()
        today_str = today_date.strftime('%b %d, %Y')
        today_display = f"{today_yield:.2f}%"
    
    # Create circular bar chart
    fig = go.Figure()
    
    # Add the original trace
    fig.add_trace(go.Barpolar(
        r=yields,
        theta=decades,
        width=[30] * len(decades),
        marker=dict(
            color=colors,
            line=dict(color='white', width=2)
        ),
        opacity=1.0,
        text=[f"{y}%" for y in yields],
        hoverinfo='text+theta+r',
        name='10Y Yield by Decade',
        hovertemplate='<b>%{theta}</b><br>Avg Yield: %{r:.2f}%<extra></extra>'
    ))
    
    # Adaptive text colors
    title_color = '#D4AF37'
    axis_color = '#D4AF37'
    
    # Create frames for rotation
    frames = []
    for rotation in range(0, 360, 3):
        
        # Calculate which decade line is aligned
        base_angles = [i * (360 / len(decades)) for i in range(len(decades))]
        aligned_text = ""
        aligned_decade = None
        aligned_yield = None
        aligned_idx = None
        
        for i, base_angle in enumerate(base_angles):
            effective_angle = (base_angle - rotation) % 360
            if effective_angle < 10 or effective_angle > 350:
                aligned_text = f"<b>{decades[i]}<br>{yields[i]}%</b>"
                aligned_decade = decades[i]
                aligned_yield = yields[i]
                aligned_idx = i
                break
        
        # Create frame with yield display
        frame_layout = go.Layout(
            polar=dict(
                angularaxis=dict(rotation=rotation)
            ),
            annotations=[
                dict(
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    text=aligned_text,
                    showarrow=False,
                    font=dict(size=28, color='white', family='Arial Black'),
                    bgcolor='rgba(0,0,0,0.9)',
                    bordercolor='#D4AF37',
                    borderwidth=4,
                    borderpad=12,
                    visible=True if aligned_text else False
                ),
                dict(
                    x=0.5, y=-0.1,
                    xref="paper", yref="paper",
                    text=f"📍 Today: {today_display} ({today_str})",
                    showarrow=False,
                    font=dict(size=12, color=axis_color),
                    align="center"
                )
            ]
        )
        
        # If aligned, highlight the bar
        if aligned_decade:
            frame_data = [
                go.Barpolar(
                    r=yields,
                    theta=decades,
                    width=[30] * len(decades),
                    marker=dict(
                        color=colors,
                        line=dict(color='white', width=2),
                        opacity=0.4
                    ),
                    opacity=0.4,
                    text=[f"{y}%" for y in yields],
                    hoverinfo='text+theta+r'
                ),
                go.Barpolar(
                    r=[aligned_yield],
                    theta=[aligned_decade],
                    width=[35],
                    marker=dict(
                        color=era_colors.get(decade_avg['decade'].iloc[aligned_idx], '#FFFFFF'),
                        line=dict(color='gold', width=4),
                        opacity=1.0
                    ),
                    opacity=1.0,
                    text=[f"<b>{aligned_yield}%</b>"],
                    hoverinfo='text'
                )
            ]
        else:
            frame_data = [go.Barpolar(
                r=yields,
                theta=decades,
                width=[30] * len(decades),
                marker=dict(
                    color=colors,
                    line=dict(color='white', width=2)
                ),
                opacity=0.4,
                text=[f"{y}%" for y in yields],
                hoverinfo='text+theta+r'
            )]
        
        frame = go.Frame(
            data=frame_data,
            name=f'rotate_{rotation}',
            layout=frame_layout
        )
        frames.append(frame)
    
    # Add reset frame
    reset_frame = go.Frame(
        data=[go.Barpolar(
            r=yields,
            theta=decades,
            width=[30] * len(decades),
            marker=dict(
                color=colors,
                line=dict(color='white', width=2),
                opacity=1.0
            ),
            opacity=1.0,
            text=[f"{y}%" for y in yields],
            hoverinfo='text+theta+r'
        )],
        name='reset_state',
        layout=go.Layout(
            polar=dict(
                angularaxis=dict(rotation=345)
            ),
            annotations=[],
        )
    )
    
    frames.insert(0, reset_frame)
    fig.frames = frames
    
    # Base layout
    fig.update_layout(
        title=dict(
            text="🎪 The Economic Carousel: 10Y Yield by Decade",
            font=dict(color=title_color, size=20, family='Arial Black'),
            x=0.5
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 16],
                tickfont=dict(color='#9E9E9E', size=10),
                gridcolor='rgba(158,158,158,0.2)',
                gridwidth=1,
                title=dict(text="Yield (%)", font=dict(color=axis_color))
            ),
            angularaxis=dict(
                tickfont=dict(color=axis_color, size=12, family='Arial Black'),
                gridcolor='#D4AF37',
                gridwidth=3,
                linewidth=3,
                showline=True,
                direction='clockwise'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9E9E9E'),
        height=600,
        width=600,
        showlegend=False,
        
        annotations=[
            dict(
                x=0.5, y=-0.1,
                xref="paper", yref="paper",
                text=f"📍 Today: {today_display} ({today_str})",
                showarrow=False,
                font=dict(size=12, color=axis_color),
                align="center"
            )
        ],
        
        # Slider for manual rotation
        sliders=[{
            'active': 0,
            'currentvalue': {'prefix': 'Rotation: '},
            'pad': {'t': 50},
            'steps': [
                {'args': [[f'rotate_{r}'], {'frame': {'duration': 0, 'redraw': True},
                                           'mode': 'immediate'}],
                 'label': f'{r}°',
                 'method': 'animate'}
                for r in range(0, 360, 15)
            ]
        }],
        
        # Buttons with JavaScript callbacks to update session state
        updatemenus=[
            {
                'type': 'buttons',
                'buttons': [
                    {'args': [None, {'frame': {'duration': 150, 'redraw': True},
                                    'fromcurrent': True, 'mode': 'immediate'}],
                     'label': '▶️ Play',
                     'method': 'animate'}
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 10},
                'showactive': False,
                'x': 0.0,
                'y': 0,
                'xanchor': 'left'
            },
            {
                'type': 'buttons',
                'buttons': [
                    {'args': [[None], {'frame': {'duration': 0, 'redraw': False},
                                      'mode': 'immediate'}],
                     'label': '⏸️ Pause',
                     'method': 'animate'}
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 10},
                'showactive': False,
                'x': 0.1,
                'y': 0,
                'xanchor': 'left'
            },
            {
                'type': 'buttons',
                'buttons': [
                    {'args': [['reset_state'],
                             {'frame': {'duration': 0, 'redraw': True},
                              'mode': 'immediate',
                              'fromcurrent': False}],
                     'label': '🔄 Reset',
                     'method': 'animate'}
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 10},
                'showactive': False,
                'x': 0.2,
                'y': 0,
                'xanchor': 'left'
            }
        ],
        
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    return fig
# ============================================================================
# CHART 4: THE ECONOMIC COMPASS - SIMPLE BUT POWERFUL
# ============================================================================

def create_economic_compass(df):
    """
    Chart 4: The Economic Compass
    A 2D scatter plot with Inflation on X, Unemployment on Y, 
    colored by decade, sized by VIX
    """
    
    # Prepare data
    required_cols = ['UNRATE', 'CPI_YOY', 'VIX', 'date']
    plot_df = df[required_cols].copy().dropna()
    
    if plot_df.empty:
        st.warning("No data for Economic Compass")
        return go.Figure()
    
    # Add decade
    plot_df['decade'] = (plot_df['date'].dt.year // 10) * 10
    plot_df['decade_label'] = plot_df['decade'].astype(str) + 's'
    
    # Scale VIX for point sizes
    vix_min = plot_df['VIX'].min()
    vix_max = plot_df['VIX'].max()
    plot_df['size'] = ((plot_df['VIX'] - vix_min) / (vix_max - vix_min) * 30) + 10
    
    # Colors by decade
    decade_colors = {
        1960: '#4169E1',  # Royal Blue
        1970: '#FF4500',  # Orange Red
        1980: '#1E90FF',  # Dodger Blue
        1990: '#FFD700',  # Gold
        2000: '#8B0000',  # Dark Red
        2010: '#9370DB',  # Medium Purple
        2020: '#FF6346'   # Tomato
    }
    
    # Create figure
    fig = go.Figure()
    
    # Add each decade
    for decade in sorted(plot_df['decade'].unique()):
        decade_data = plot_df[plot_df['decade'] == decade]
        color = decade_colors.get(decade, '#808080')
        
        fig.add_trace(go.Scatter(
            x=decade_data['CPI_YOY'],
            y=decade_data['UNRATE'],
            mode='markers',
            marker=dict(
                size=decade_data['size'],
                color=color,
                opacity=0.7,
                line=dict(color='white', width=1)
            ),
            name=f"{int(decade)}s",
            text=[f"<b>{row['date'].strftime('%b %Y')}</b><br>"
                  f"Unemp: {row['UNRATE']:.1f}%<br>"
                  f"Inflation: {row['CPI_YOY']:.1f}%<br>"
                  f"VIX: {row['VIX']:.1f}" 
                  for _, row in decade_data.iterrows()],
            hoverinfo='text',
            showlegend=True
        ))
    
    # Add today
    today = plot_df.iloc[-1]
    fig.add_trace(go.Scatter(
        x=[today['CPI_YOY']],
        y=[today['UNRATE']],
        mode='markers',
        marker=dict(
            size=35,
            color='#FFD700',
            symbol='star',
            line=dict(color='white', width=3)
        ),
        name='📍 TODAY',
        text=[f"<b>TODAY</b><br>Unemp: {today['UNRATE']:.1f}%<br>"
              f"Inflation: {today['CPI_YOY']:.1f}%<br>"
              f"VIX: {today['VIX']:.1f}"],
        hoverinfo='text',
        showlegend=True
    ))
    
    # Add quadrant lines
    fig.add_hline(y=5, line_dash="dash", line_color="rgba(255,255,255,0.3)",
                  annotation_text="Natural Rate")
    fig.add_vline(x=2, line_dash="dash", line_color="rgba(255,255,255,0.3)",
                  annotation_text="Fed Target")
    
    fig.update_layout(
        title=dict(
            text="🧭 THE ECONOMIC COMPASS",
            font=dict(color='#FFD700', size=32, family='Arial Black'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text="<b>INFLATION (CPI %)</b>", font=dict(color='#FFD700', size=16)),
            range=[-2, 15],
            gridcolor='rgba(255,255,255,0.2)',
            tickfont=dict(color='white', size=12),
            tickvals=[-2, 0, 2, 4, 6, 8, 10, 12, 14],
            ticktext=['-2%', '0%', '2%', '4%', '6%', '8%', '10%', '12%', '14%']
        ),
        yaxis=dict(
            title=dict(text="<b>UNEMPLOYMENT (%)</b>", font=dict(color='#FFD700', size=16)),
            range=[0, 12],
            gridcolor='rgba(255,255,255,0.2)',
            tickfont=dict(color='white', size=12),
            tickvals=[0, 2, 4, 6, 8, 10, 12],
            ticktext=['0%', '2%', '4%', '6%', '8%', '10%', '12%']
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=800,
        width=1000,
        legend=dict(
            title=dict(text="<b>DECADES</b>", font=dict(color='#FFD700')),
            font=dict(color='white'),
            bgcolor='rgba(0,0,0,0.8)',
            bordercolor='#FFD700',
            borderwidth=2
        ),
        annotations=[
            dict(
                xref="paper", yref="paper",
                x=0.98, y=0.98,
                text="<b>⭐ STAR SIZE = FEAR (VIX)</b>",
                showarrow=False,
                font=dict(size=12, color='#FFD700'),
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='#FFD700',
                borderwidth=2,
                borderpad=6
            ),
            dict(
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                text=f"<b>{plot_df['date'].min().year} - {plot_df['date'].max().year}</b>",
                showarrow=False,
                font=dict(size=12, color='white'),
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='#FFD700',
                borderwidth=2,
                borderpad=6
            )
        ]
    )
    
    return fig

# ============================================================================
# CHART 5: THE FED FOOTPRINT
# ============================================================================

def create_fed_footprint(df):
    """Chart 5: Dual-axis chart of Fed Funds Rate and Balance Sheet"""
    
    # Prepare data (post-2000 for focus)
    fed_df = df[df['date'] >= '2000-01-01'].copy()
    
    # Convert balance sheet to trillions
    fed_df['WALCL_TRILLIONS'] = fed_df['WALCL'] / 1_000_000
    
    fig = go.Figure()
    
    # Add Fed Funds Rate (left axis)
    fig.add_trace(go.Scatter(
        x=fed_df['date'],
        y=fed_df['FEDFUNDS'],
        name='Fed Funds Rate',
        line=dict(color=COLORS['fed_footprint'][0], width=3),
        yaxis='y'
    ))
    
    # Add Balance Sheet (right axis)
    fig.add_trace(go.Scatter(
        x=fed_df['date'],
        y=fed_df['WALCL_TRILLIONS'],
        name='Balance Sheet (Trillions $)',
        line=dict(color=COLORS['fed_footprint'][1], width=3),
        fill='tozeroy',
        fillcolor='rgba(0,191,255,0.1)',
        yaxis='y2'
    ))
    
    # Add annotations for major events
    events = [
        ('2008-11-25', 'QE1', COLORS['fed_footprint'][1]),
        ('2010-11-03', 'QE2', COLORS['fed_footprint'][1]),
        ('2012-09-13', 'QE3', COLORS['fed_footprint'][1]),
        ('2020-03-15', 'COVID QE', COLORS['red'])
    ]
    
    for date, label, color in events:
        event_date = pd.to_datetime(date)
        mask = abs(fed_df['date'] - event_date) < pd.Timedelta(days=30)
        if mask.any():
            y_val = fed_df.loc[mask, 'WALCL_TRILLIONS'].iloc[0]
            fig.add_annotation(
                x=event_date,
                y=y_val,
                text=label,
                showarrow=True,
                arrowhead=2,
                arrowcolor=color,
                font=dict(color='white', size=11, family='Arial Black'),
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor=color,
                borderwidth=2,
                yshift=20
            )
    
    fig.update_layout(
        title=dict(
            text="🏦 The Fed Footprint: Rates vs Balance Sheet",
            font=dict(color=COLORS['gold'], size=20, family='Arial Black')
        ),
        xaxis=dict(
            title=dict(text="", font=dict(color='white')),
            rangeslider=dict(visible=True),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text="Fed Funds Rate (%)", font=dict(color=COLORS['fed_footprint'][0])),
            tickfont=dict(color=COLORS['fed_footprint'][0]),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis2=dict(
            title=dict(text="Balance Sheet ($ Trillions)", font=dict(color=COLORS['fed_footprint'][1])),
            tickfont=dict(color=COLORS['fed_footprint'][1]),
            anchor='x',
            overlaying='y',
            side='right',
            gridcolor='rgba(255,255,255,0.1)'
        ),
        height=400,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        )
    )
    
    return fig

# ============================================================================
# CHART 6: THE REAL UNEMPLOYMENT GAP
# ============================================================================

def create_real_unemployment_gap(df):
    """Chart 6: U3 vs U6 with hidden unemployment gap"""
    
    # Filter to where U6 is available (1994+)
    unemp_df = df[df['date'] >= '1994-01-01'].copy()
    unemp_df = unemp_df.dropna(subset=['UNRATE', 'U6RATE'])
    
    fig = go.Figure()
    
    # Add U3 (official)
    fig.add_trace(go.Scatter(
        x=unemp_df['date'],
        y=unemp_df['UNRATE'],
        name='Official Unemployment (U-3)',
        line=dict(color=COLORS['unemployment'][0], width=3),
        fill=None
    ))
    
    # Add U6 (real)
    fig.add_trace(go.Scatter(
        x=unemp_df['date'],
        y=unemp_df['U6RATE'],
        name='Real Unemployment (U-6)',
        line=dict(color=COLORS['unemployment'][1], width=3),
        fill='tonexty',
        fillcolor='rgba(255,105,180,0.2)'
    ))
    
    # Calculate and show current gap
    latest = unemp_df.iloc[-1]
    gap = latest['U6RATE'] - latest['UNRATE']
    
    fig.update_layout(
        title=dict(
            text="👥 The Real Unemployment Gap: Official vs Reality",
            font=dict(color=COLORS['gold'], size=20, family='Arial Black')
        ),
        xaxis=dict(
            title=dict(text="", font=dict(color='white')),
            rangeslider=dict(visible=True),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text="Unemployment Rate (%)", font=dict(color='white')),
            tickfont=dict(color='white'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        ),
        annotations=[
            dict(
                x=latest['date'],
                y=latest['U6RATE'],
                text=f"Hidden: {gap:.1f}%",
                showarrow=True,
                arrowhead=2,
                arrowcolor=COLORS['unemployment'][1],
                font=dict(color='white', size=12, family='Arial Black'),
                bgcolor='rgba(255,105,180,0.8)',
                bordercolor=COLORS['unemployment'][1],
                borderwidth=2,
                yshift=20
            )
        ]
    )
    
    return fig

# ============================================================================
# CHART 7: THE INFLATION STORY
# ============================================================================

def create_inflation_story(df):
    """Chart 7: Inflation decomposition and expectations"""
    
    # Prepare data
    inflation_df = df[df['date'] >= '2000-01-01'].copy()
    
    fig = go.Figure()
    
    # Headline CPI
    fig.add_trace(go.Scatter(
        x=inflation_df['date'],
        y=inflation_df['CPI_YOY'],
        name='Headline CPI',
        line=dict(color=COLORS['inflation'][0], width=3)
    ))
    
    # Core CPI (calculated from CPILFESL)
    inflation_df['CORE_YOY'] = inflation_df['CPILFESL'].pct_change(12) * 100
    fig.add_trace(go.Scatter(
        x=inflation_df['date'],
        y=inflation_df['CORE_YOY'],
        name='Core CPI',
        line=dict(color=COLORS['inflation'][1], width=3)
    ))
    
    # Add Fed target line
    fig.add_hline(y=2, line_width=2, line_dash="dash", line_color=COLORS['green'],
                  annotation_text="Fed Target", annotation_position="bottom right",
                  annotation_font=dict(color=COLORS['green']))
    
    # Add upper and lower bounds
    fig.add_hrect(y0=1.5, y1=2.5, line_width=0, fillcolor="rgba(0,255,0,0.1)")
    
    # Add inflation expectations if available
    if 'T10YIE' in inflation_df.columns:
        fig.add_trace(go.Scatter(
            x=inflation_df['date'],
            y=inflation_df['T10YIE'],
            name='10Y Expectation',
            line=dict(color=COLORS['inflation'][2], width=2, dash='dot')
        ))
    
    fig.update_layout(
        title=dict(
            text="📊 The Inflation Story: Headline vs Core vs Expectations",
            font=dict(color=COLORS['gold'], size=20, family='Arial Black')
        ),
        xaxis=dict(
            title=dict(text="", font=dict(color='white')),
            rangeslider=dict(visible=True),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text="Inflation Rate (%)", font=dict(color='white')),
            tickfont=dict(color='white'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        )
    )
    
    return fig

# ============================================================================
# CHART 8: THE VULNERABILITY CLOCK
# ============================================================================

def create_vulnerability_clock(df):
    """
    Chart 8: Radar chart showing 8 dimensions of stress
    
    ⚠️ NOTE: "Market Fear" in this chart IS the VIX. 
    The overall Vulnerability Index™ (Chart 2) combines 4 components,
    while this clock shows 8 separate dimensions including the VIX.
    """
    
    # Get today's date and date 6 months ago
    today_date = df['date'].iloc[-1]
    six_months_ago_date = today_date - pd.Timedelta(days=180)
    
    # Define the 8 dimensions and their columns - FIXED: No f-strings in lambda
    dimensions = [
        {'name': 'Curve', 'column': '10Y2Y', 'format': lambda x: "{:.2f}%".format(x)},
        {'name': 'Credit', 'column': 'HY_SPREAD', 'format': lambda x: "{:.2f}%".format(x)},
        {'name': 'Labor', 'column': 'UNRATE', 'format': lambda x: "{:.1f}%".format(x)},
        {'name': 'Inflation', 'column': 'CPI_YOY', 'format': lambda x: "{:.1f}%".format(x)},
        {'name': 'Market Fear', 'column': 'VIX', 'format': lambda x: "{:.1f}".format(x)},
        {'name': 'Housing', 'column': 'HOUST', 'format': lambda x: "{:.2f}M".format(x/1000)},
        {'name': 'Dollar', 'column': 'DTWEXBGS', 'format': lambda x: "{:.1f}".format(x)},
        {'name': 'Sentiment', 'column': 'UMCSENT', 'format': lambda x: "{:.1f}".format(x)}
    ]
    
    # Get current values with fallback
    current_values = []
    current_displays = []
    fallback_notes = []
    
    for dim in dimensions:
        val = get_value_with_fallback(df, dim['column'], today_date)
        if val is not None:
            current_values.append(normalize_by_column(dim['column'], val))
            current_displays.append(dim['format'](val))
            
            # Check if this was a fallback
            exact_mask = df['date'] == today_date
            if dim['column'] in df.columns and exact_mask.any():
                exact_val = df.loc[exact_mask, dim['column']].iloc[0] if exact_mask.any() else None
                if pd.isna(exact_val):
                    fallback_notes.append(f"• {dim['name']}: using most recent value")
        else:
            # If no data at all, use historical average as last resort
            if dim['column'] in df.columns:
                avg_val = df[dim['column']].mean()
                if not pd.isna(avg_val):
                    current_values.append(normalize_by_column(dim['column'], avg_val))
                    current_displays.append(dim['format'](avg_val) + "*")
                    fallback_notes.append(f"• {dim['name']}: using historical average")
                else:
                    current_values.append(50)
                    current_displays.append("N/A")
                    fallback_notes.append(f"• {dim['name']}: NO DATA")
            else:
                current_values.append(50)
                current_displays.append("N/A")
                fallback_notes.append(f"• {dim['name']}: column missing")
    
    # Get values from 6 months ago with fallback
    past_values = []
    for dim in dimensions:
        val = get_value_with_fallback(df, dim['column'], six_months_ago_date)
        if val is not None:
            past_values.append(normalize_by_column(dim['column'], val))
        else:
            past_values.append(50)  # Default if no data
    
    # Get status emoji for each dimension
    def get_status_emoji(value):
        if pd.isna(value):
            return "⚪"
        if value < 40:
            return "🟢"
        elif value < 70:
            return "🟡"
        else:
            return "🔴"
    
    status_emojis = [get_status_emoji(val) for val in current_values]
    
    # Define categories and their angular positions
    categories = [dim['name'] for dim in dimensions]
    angles = [
        np.pi/2,           # Curve - Top
        np.pi/2 - np.pi/4, # Credit - Top-right
        0,                  # Labor - Right
        -np.pi/4,           # Inflation - Bottom-right
        -np.pi/2,           # Market Fear - Bottom
        -3*np.pi/4,         # Housing - Bottom-left
        np.pi,              # Dollar - Left
        3*np.pi/4           # Sentiment - Top-left
    ]
    
    # Create figure
    fig = go.Figure()
    
    # Add colored background rings
    fig.add_trace(go.Scatterpolar(
        r=[40, 40, 40, 40, 40, 40, 40, 40, 40],
        theta=categories + [categories[0]],
        mode='lines',
        line=dict(color=COLORS['green'], width=1, dash='dot'),
        name='Low Stress (0-40)',
        fill='toself',
        fillcolor='rgba(0,255,0,0.05)',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[70, 70, 70, 70, 70, 70, 70, 70, 70],
        theta=categories + [categories[0]],
        mode='lines',
        line=dict(color=COLORS['yellow'], width=1, dash='dot'),
        name='Elevated (40-70)',
        fill='toself',
        fillcolor='rgba(255,215,0,0.05)',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[100, 100, 100, 100, 100, 100, 100, 100, 100],
        theta=categories + [categories[0]],
        mode='lines',
        line=dict(color=COLORS['red'], width=1, dash='dot'),
        name='High Stress (70-100)',
        fill='toself',
        fillcolor='rgba(255,68,68,0.05)',
        showlegend=True
    ))
    
    # Add current period line
    fig.add_trace(go.Scatterpolar(
        r=current_values + [current_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Today',
        line=dict(color=COLORS['gold'], width=3),
        fillcolor='rgba(255,215,0,0.2)'
    ))
    
    # Add 6 months ago line
    fig.add_trace(go.Scatterpolar(
        r=past_values + [past_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='6 Months Ago',
        line=dict(color='white', width=2, dash='dash'),
        fillcolor='rgba(255,255,255,0.1)'
    ))
    
    # Add axis labels
    annotations = []
    for i, (cat, val, display, emoji, angle) in enumerate(zip(
        categories, current_values, current_displays, status_emojis, angles)):
        
        label_distance = 1.25
        x_pos = label_distance * np.cos(angle)
        y_pos = label_distance * np.sin(angle)
        
        if abs(x_pos) < 0.1:
            xanchor = 'center'
        elif x_pos > 0:
            xanchor = 'left'
        else:
            xanchor = 'right'
            
        if abs(y_pos) < 0.1:
            yanchor = 'middle'
        elif y_pos > 0:
            yanchor = 'bottom'
        else:
            yanchor = 'top'
        
        if pd.isna(val):
            color = COLORS['gray']
        elif val < 40:
            color = COLORS['green']
        elif val < 70:
            color = COLORS['yellow']
        else:
            color = COLORS['red']
        
        label_text = f"<b>{cat}</b><br>{emoji} {display}"
        
        annotations.append(dict(
            xref="paper", yref="paper",
            x=0.5 + x_pos*0.25,
            y=0.5 + y_pos*0.25,
            text=label_text,
            showarrow=False,
            font=dict(size=11, color=color, family='Arial Black'),
            align='center',
            xanchor=xanchor,
            yanchor=yanchor,
            bordercolor=color,
            borderwidth=1,
            borderpad=4,
            bgcolor='rgba(0,0,0,0.8)'
        ))
    
    # Add fallback notes if any
    if fallback_notes:
        notes_text = "📌 " + " • ".join(fallback_notes[:3])
        if len(fallback_notes) > 3:
            notes_text += f" • +{len(fallback_notes)-3} more"
        
        annotations.append(dict(
            xref="paper", yref="paper",
            x=0.5, y=0.08,
            text=notes_text,
            showarrow=False,
            font=dict(size=9, color=COLORS['gray']),
            align="center",
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor=COLORS['gold'],
            borderwidth=1,
            borderpad=4
        ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=9, color='white'),
                gridcolor='rgba(255,255,255,0.2)',
                tickmode='array',
                tickvals=[0, 20, 40, 60, 80, 100],
                ticktext=['0', '20', '40', '60', '80', '100']
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=COLORS['gold'], family='Arial Black'),
                gridcolor='rgba(255,255,255,0.2)',
                rotation=90,
                direction='clockwise'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        title=dict(
            text="⏰ The Vulnerability Clock™ - 8 Dimensions of Stress",
            font=dict(color=COLORS['gold'], size=20, family='Arial Black'),
            y=0.98
        ),
        height=700,
        width=700,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color='white', size=10),
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor=COLORS['gold'],
            borderwidth=1
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=80, r=80, t=120, b=100),
        annotations=annotations + [
            dict(
                xref="paper", yref="paper",
                x=0.5, y=0.02,
                text="🟢 Low (0-40)  🟡 Elevated (40-70)  🔴 High (70-100)  * = historical avg",
                showarrow=False,
                font=dict(size=10, color='white'),
                align="center",
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor=COLORS['gold'],
                borderwidth=1,
                borderpad=6
            )
        ]
    )
    
    return fig

# ============================================================================
# CHART 9: ERA COMPARISON - IMPROVED VERSION WITH BETTER MATCHES
# ============================================================================

def create_era_comparison(df):
    """Chart 9: Compare today with pre-2000 and post-2000 matches (improved)"""
    
    pre_2000_match, post_2000_match = find_historical_matches(df, df['date'].iloc[-1])
    
    # Get today's values
    today_yield, _, today_date = get_latest_value(df, 'DGS10')
    today_unrate, _, _ = get_latest_value(df, 'UNRATE')
    today_cpi, _, _ = get_latest_value(df, 'CPI_YOY')
    today_spread, _, _ = get_latest_value(df, '10Y2Y')
    
    # Create three columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['dark_bg']} 0%, {COLORS['light_bg']} 100%);
                    padding: 20px; border-radius: 10px; border-left: 6px solid {COLORS['era_comparison'][0]};
                    margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h4 style="color: {COLORS['era_comparison'][0]}; margin-top: 0; font-family: Arial Black;">🔴 TODAY</h4>
            <p style="color: white; font-size: 1.2rem; margin: 5px 0;"><strong>{safe_strftime(today_date, '%B %Y') if today_date else 'N/A'}</strong></p>
            <hr style="border-color: {COLORS['gray_dark']};">
            <p style="color: white; margin: 10px 0;"><span style="color: {COLORS['era_comparison'][0]};">10Y Yield:</span> {today_yield}</p>
            <p style="color: white; margin: 5px 0;"><span style="color: {COLORS['era_comparison'][0]};">Unemployment:</span> {today_unrate}</p>
            <p style="color: white; margin: 5px 0;"><span style="color: {COLORS['era_comparison'][0]};">Inflation:</span> {today_cpi}</p>
            <p style="color: white; margin: 5px 0;"><span style="color: {COLORS['era_comparison'][0]};">Spread:</span> {today_spread}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if not pre_2000_match.empty:
            match = pre_2000_match.iloc[0]
            match_date = match['date']
            
            # Get values for the match date
            match_yield, _, _ = get_latest_value(df[df['date'] <= match_date + pd.Timedelta(days=30)], 'DGS10')
            match_unrate, _, _ = get_latest_value(df[df['date'] <= match_date + pd.Timedelta(days=30)], 'UNRATE')
            match_cpi, _, _ = get_latest_value(df[df['date'] <= match_date + pd.Timedelta(days=30)], 'CPI_YOY')
            match_spread, _, _ = get_latest_value(df[df['date'] <= match_date + pd.Timedelta(days=30)], '10Y2Y')
            
            # Look ahead 12 months
            future_date = match_date + pd.Timedelta(days=365)
            future_df = df[df['date'] <= future_date + pd.Timedelta(days=30)]
            future_yield, _, future_date_actual = get_latest_value(future_df, 'DGS10')
            
            # Calculate change
            change_text = "N/A"
            change_color = COLORS['gray']
            if match_yield != "N/A" and future_yield != "N/A":
                try:
                    match_num = float(match_yield.replace('%', ''))
                    future_num = float(future_yield.replace('%', ''))
                    change = future_num - match_num
                    change_color = COLORS['green'] if change < 0 else COLORS['red']
                    change_text = f"{change:+.2f}%"
                except:
                    pass
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {COLORS['dark_bg']} 0%, {COLORS['light_bg']} 100%);
                        padding: 20px; border-radius: 10px; border-left: 6px solid {COLORS['era_comparison'][1]};
                        margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <h4 style="color: {COLORS['era_comparison'][1]}; margin-top: 0; font-family: Arial Black;">📜 PRE-2000 MATCH</h4>
                <p style="color: white; font-size: 1.2rem; margin: 5px 0;"><strong>{safe_strftime(match_date, '%B %Y')}</strong></p>
                <hr style="border-color: {COLORS['gray_dark']};">
                <p style="color: white; margin: 10px 0;"><span style="color: {COLORS['era_comparison'][1]};">10Y Yield:</span> {match_yield}</p>
                <p style="color: white; margin: 5px 0;"><span style="color: {COLORS['era_comparison'][1]};">Unemployment:</span> {match_unrate}</p>
                <p style="color: white; margin: 5px 0;"><span style="color: {COLORS['era_comparison'][1]};">Inflation:</span> {match_cpi}</p>
                <p style="color: white; margin: 5px 0;"><span style="color: {COLORS['era_comparison'][1]};">Spread:</span> {match_spread}</p>
                <hr style="border-color: {COLORS['gray_dark']};">
                <p style="color: white; margin: 5px 0;"><strong>12 Months Later:</strong> {safe_strftime(future_date_actual if future_date_actual else future_date, '%b %Y')}</p>
                <p style="color: white; margin: 5px 0;">Yield: {future_yield} 
                    <span style="color: {change_color};">({change_text})</span></p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if not post_2000_match.empty:
            match = post_2000_match.iloc[0]
            match_date = match['date']
            
            # Get values for the match date
            match_yield, _, _ = get_latest_value(df[df['date'] <= match_date + pd.Timedelta(days=30)], 'DGS10')
            match_unrate, _, _ = get_latest_value(df[df['date'] <= match_date + pd.Timedelta(days=30)], 'UNRATE')
            match_cpi, _, _ = get_latest_value(df[df['date'] <= match_date + pd.Timedelta(days=30)], 'CPI_YOY')
            match_spread, _, _ = get_latest_value(df[df['date'] <= match_date + pd.Timedelta(days=30)], '10Y2Y')
            
            # Look ahead 12 months
            future_date = match_date + pd.Timedelta(days=365)
            future_df = df[df['date'] <= future_date + pd.Timedelta(days=30)]
            future_yield, _, future_date_actual = get_latest_value(future_df, 'DGS10')
            
            # Calculate change
            change_text = "N/A"
            change_color = COLORS['gray']
            if match_yield != "N/A" and future_yield != "N/A":
                try:
                    match_num = float(match_yield.replace('%', ''))
                    future_num = float(future_yield.replace('%', ''))
                    change = future_num - match_num
                    change_color = COLORS['green'] if change < 0 else COLORS['red']
                    change_text = f"{change:+.2f}%"
                except:
                    pass
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {COLORS['dark_bg']} 0%, {COLORS['light_bg']} 100%);
                        padding: 20px; border-radius: 10px; border-left: 6px solid {COLORS['era_comparison'][2]};
                        margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <h4 style="color: {COLORS['era_comparison'][2]}; margin-top: 0; font-family: Arial Black;">📜 POST-2000 MATCH</h4>
                <p style="color: white; font-size: 1.2rem; margin: 5px 0;"><strong>{safe_strftime(match_date, '%B %Y')}</strong></p>
                <hr style="border-color: {COLORS['gray_dark']};">
                <p style="color: white; margin: 10px 0;"><span style="color: {COLORS['era_comparison'][2]};">10Y Yield:</span> {match_yield}</p>
                <p style="color: white; margin: 5px 0;"><span style="color: {COLORS['era_comparison'][2]};">Unemployment:</span> {match_unrate}</p>
                <p style="color: white; margin: 5px 0;"><span style="color: {COLORS['era_comparison'][2]};">Inflation:</span> {match_cpi}</p>
                <p style="color: white; margin: 5px 0;"><span style="color: {COLORS['era_comparison'][2]};">Spread:</span> {match_spread}</p>
                <hr style="border-color: {COLORS['gray_dark']};">
                <p style="color: white; margin: 5px 0;"><strong>12 Months Later:</strong> {safe_strftime(future_date_actual if future_date_actual else future_date, '%b %Y')}</p>
                <p style="color: white; margin: 5px 0;">Yield: {future_yield} 
                    <span style="color: {change_color};">({change_text})</span></p>
            </div>
            """, unsafe_allow_html=True)
    
    return None

# ============================================================================
# CHART 9: ERA COMPARISON - FIGURE VERSION FOR FULL SCREEN (FIXED)
# ============================================================================

def create_era_comparison_figure(df):
    """Create a figure version of Era Comparison for full screen display"""
    
    pre_2000_match, post_2000_match = find_historical_matches(df, df['date'].iloc[-1])
    
    # Get today's values
    today_yield, _, today_date = get_latest_value(df, 'DGS10')
    today_unrate, _, _ = get_latest_value(df, 'UNRATE')
    today_cpi, _, _ = get_latest_value(df, 'CPI_YOY')
    today_spread, _, _ = get_latest_value(df, '10Y2Y')
    
    # Create a figure with 3 columns
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('TODAY', 'PRE-2000 MATCH', 'POST-2000 MATCH'),
        horizontal_spacing=0.1
    )
    
    # Helper function to get value near a date
    def get_value_near_date_fig(col, target_date):
        mask = (df['date'] >= target_date - pd.Timedelta(days=60)) & (df['date'] <= target_date + pd.Timedelta(days=60))
        valid = df[mask & df[col].notna()]
        if not valid.empty:
            closest_idx = (valid['date'] - target_date).abs().argsort()[:1]
            val = valid.iloc[closest_idx][col].iloc[0]
            if col == 'DGS10':
                return f"{val:.2f}%", val
            elif col == 'UNRATE':
                return f"{val:.1f}%", val
            elif col == 'CPI_YOY':
                return f"{val:.1f}%", val
            elif col == '10Y2Y':
                return f"{val:.2f}%", val
        return "N/A", None
    
    # Today's data
    today_text = (
        f"<b>{safe_strftime(today_date, '%B %Y') if today_date else 'N/A'}</b><br><br>"
        f"10Y Yield: {today_yield}<br>"
        f"Unemployment: {today_unrate}<br>"
        f"Inflation: {today_cpi}<br>"
        f"Spread: {today_spread}"
    )
    
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.17, y=0.5,
        text=today_text,
        showarrow=False,
        font=dict(size=14, color=COLORS['era_comparison'][0]),
        align="center",
        bordercolor=COLORS['era_comparison'][0],
        borderwidth=2,
        borderpad=10,
        bgcolor=COLORS['dark_bg']
    )
    
    # Pre-2000 match
    if not pre_2000_match.empty:
        match = pre_2000_match.iloc[0]
        match_date = match['date']
        
        match_yield, match_yield_num = get_value_near_date_fig('DGS10', match_date)
        match_unrate, _ = get_value_near_date_fig('UNRATE', match_date)
        match_cpi, _ = get_value_near_date_fig('CPI_YOY', match_date)
        match_spread, _ = get_value_near_date_fig('10Y2Y', match_date)
        
        # Look ahead 12 months
        future_date = match_date + pd.Timedelta(days=365)
        future_yield, future_yield_num = get_value_near_date_fig('DGS10', future_date)
        
        # Calculate change
        change_text = ""
        change_color = COLORS['gray']
        if match_yield_num is not None and future_yield_num is not None:
            change = future_yield_num - match_yield_num
            change_color = COLORS['green'] if change < 0 else COLORS['red']
            change_text = f"{change:+.2f}%"
        else:
            change_text = "N/A"
        
        pre_text = (
            f"<b>{safe_strftime(match_date, '%B %Y')}</b><br><br>"
            f"10Y Yield: {match_yield}<br>"
            f"Unemployment: {match_unrate}<br>"
            f"Inflation: {match_cpi}<br>"
            f"Spread: {match_spread}<br><br>"
            f"<b>12 Months Later:</b><br>"
            f"{safe_strftime(future_date, '%b %Y')}: {future_yield}<br>"
            f"Change: <span style='color:{change_color};'>{change_text}</span>"
        )
        
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            text=pre_text,
            showarrow=False,
            font=dict(size=14, color=COLORS['era_comparison'][1]),
            align="center",
            bordercolor=COLORS['era_comparison'][1],
            borderwidth=2,
            borderpad=10,
            bgcolor=COLORS['dark_bg']
        )
    
    # Post-2000 match
    if not post_2000_match.empty:
        match = post_2000_match.iloc[0]
        match_date = match['date']
        
        match_yield, match_yield_num = get_value_near_date_fig('DGS10', match_date)
        match_unrate, _ = get_value_near_date_fig('UNRATE', match_date)
        match_cpi, _ = get_value_near_date_fig('CPI_YOY', match_date)
        match_spread, _ = get_value_near_date_fig('10Y2Y', match_date)
        
        # Look ahead 12 months
        future_date = match_date + pd.Timedelta(days=365)
        future_yield, future_yield_num = get_value_near_date_fig('DGS10', future_date)
        
        # Calculate change
        change_text = ""
        change_color = COLORS['gray']
        if match_yield_num is not None and future_yield_num is not None:
            change = future_yield_num - match_yield_num
            change_color = COLORS['green'] if change < 0 else COLORS['red']
            change_text = f"{change:+.2f}%"
        else:
            change_text = "N/A"
        
        post_text = (
            f"<b>{safe_strftime(match_date, '%B %Y')}</b><br><br>"
            f"10Y Yield: {match_yield}<br>"
            f"Unemployment: {match_unrate}<br>"
            f"Inflation: {match_cpi}<br>"
            f"Spread: {match_spread}<br><br>"
            f"<b>12 Months Later:</b><br>"
            f"{safe_strftime(future_date, '%b %Y')}: {future_yield}<br>"
            f"Change: <span style='color:{change_color};'>{change_text}</span>"
        )
        
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.83, y=0.5,
            text=post_text,
            showarrow=False,
            font=dict(size=14, color=COLORS['era_comparison'][2]),
            align="center",
            bordercolor=COLORS['era_comparison'][2],
            borderwidth=2,
            borderpad=10,
            bgcolor=COLORS['dark_bg']
        )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="🔄 Era Comparison - Today vs Historical Matches",
            font=dict(color=COLORS['gold'], size=24, family='Arial Black'),
            x=0.5,
            xanchor='center'
        ),
        height=700,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    # Hide axes
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    
    return fig

# ============================================================================
# CHART 10: THE FEAR TIMELINE
# ============================================================================

def create_fear_timeline(df, historical_events):
    """Chart 10: VIX timeline with crisis markers"""
    
    vix_df = df[df['date'] >= '1990-01-01'].dropna(subset=['VIX']).copy()
    
    fig = go.Figure()
    
    # Add VIX line
    fig.add_trace(go.Scatter(
        x=vix_df['date'],
        y=vix_df['VIX'],
        mode='lines',
        name='VIX (Fear Gauge)',
        line=dict(color=COLORS['fear_timeline'][0], width=3),
        fill='tozeroy',
        fillcolor='rgba(255,215,0,0.15)'
    ))
    
    # Add threshold lines
    fig.add_hline(y=20, line_width=2, line_dash="dash", line_color=COLORS['green'],
                  annotation_text="Normal", annotation_position="bottom right",
                  annotation_font=dict(color=COLORS['green']))
    fig.add_hline(y=30, line_width=2, line_dash="dash", line_color=COLORS['yellow'],
                  annotation_text="Elevated", annotation_position="bottom right",
                  annotation_font=dict(color=COLORS['yellow']))
    fig.add_hline(y=40, line_width=2, line_dash="dash", line_color=COLORS['red'],
                  annotation_text="Panic", annotation_position="bottom right",
                  annotation_font=dict(color=COLORS['red']))
    
    # Add crisis markers
    crisis_events = [
        ('1990-08-02', 'Gulf War', 25),
        ('1997-10-27', 'Asian Crisis', 35),
        ('1998-09-23', 'LTCM', 45),
        ('2000-03-10', 'Dot-com', 30),
        ('2001-09-11', '9/11', 45),
        ('2008-09-15', 'Lehman', 80),
        ('2010-05-06', 'Flash Crash', 40),
        ('2011-08-08', 'US Downgrade', 48),
        ('2020-03-16', 'COVID', 85),
        ('2022-06-13', 'Inflation', 35)
    ]
    
    for date, label, vix_level in crisis_events:
        event_date = pd.to_datetime(date)
        
        fig.add_annotation(
            x=event_date,
            y=vix_level,
            text=label,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='white',
            font=dict(size=10, color='white', family='Arial Black'),
            bgcolor='rgba(0,0,0,0.8)',
            bordercolor='white',
            borderwidth=2,
            yshift=10
        )
    
    fig.update_layout(
        title=dict(
            text="😨 The Fear Timeline - Every Crisis Measured in VIX",
            font=dict(color=COLORS['gold'], size=20, family='Arial Black')
        ),
        xaxis=dict(
            title=dict(text="", font=dict(color='white')),
            rangeslider=dict(visible=True),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text="VIX (Volatility Index)", font=dict(color=COLORS['fear_timeline'][0])),
            tickfont=dict(color=COLORS['fear_timeline'][0]),
            range=[0, 90],
            gridcolor='rgba(255,255,255,0.1)'
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    
    return fig

# ============================================================================
# CHART 11: THE HOUSING CYCLE
# ============================================================================

def create_housing_cycle(df):
    """Chart 11: Housing starts, permits, and homeownership rate"""
    
    housing_df = df.copy()
    
    fig = go.Figure()
    
    # Housing Starts (left axis)
    fig.add_trace(go.Scatter(
        x=housing_df['date'],
        y=housing_df['HOUST'],
        name='Housing Starts (000s)',
        line=dict(color=COLORS['housing_cycle'][0], width=3),
        yaxis='y'
    ))
    
    # Building Permits (left axis)
    fig.add_trace(go.Scatter(
        x=housing_df['date'],
        y=housing_df['PERMIT'],
        name='Building Permits (000s)',
        line=dict(color=COLORS['housing_cycle'][1], width=3),
        yaxis='y'
    ))
    
    # Homeownership Rate (right axis)
    if 'RHORUSQ156N' in housing_df.columns:
        fig.add_trace(go.Scatter(
            x=housing_df['date'],
            y=housing_df['RHORUSQ156N'],
            name='Homeownership Rate (%)',
            line=dict(color=COLORS['housing_cycle'][2], width=3, dash='dot'),
            yaxis='y2'
        ))
    
    fig.update_layout(
        title=dict(
            text="🏠 The Housing Cycle: Starts, Permits, and Homeownership",
            font=dict(color=COLORS['gold'], size=20, family='Arial Black')
        ),
        xaxis=dict(
            title=dict(text="", font=dict(color='white')),
            rangeslider=dict(visible=True),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text="Housing Units (000s)", font=dict(color=COLORS['housing_cycle'][0])),
            tickfont=dict(color=COLORS['housing_cycle'][0]),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis2=dict(
            title=dict(text="Homeownership Rate (%)", font=dict(color=COLORS['housing_cycle'][2])),
            tickfont=dict(color=COLORS['housing_cycle'][2]),
            anchor='x',
            overlaying='y',
            side='right',
            range=[60, 70],
            gridcolor='rgba(255,255,255,0.1)'
        ),
        height=400,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        )
    )
    
    return fig

# ============================================================================
# CHART 12: THE COMPLETE DASHBOARD - REGULAR VERSION (COMPLETELY FIXED)
# ============================================================================

def create_sparkline_card(title, column, df, card_id=None):
    """Helper function to create a sparkline card with latest value"""
    
    # Get the latest non-null value
    valid_data = df[df[column].notna()]
    if not valid_data.empty:
        latest_row = valid_data.iloc[-1]
        latest_val = latest_row[column]
        latest_date = latest_row['date']
        
        # Format based on column
        if column == 'DGS10':
            value = f"{latest_val:.2f}%"
            color = COLORS['green'] if latest_val < 4 else COLORS['red'] if latest_val > 6 else COLORS['yellow']
            status = ""
        elif column == 'UNRATE':
            value = f"{latest_val:.1f}%"
            color = COLORS['green'] if latest_val < 4 else COLORS['red'] if latest_val > 6 else COLORS['yellow']
            status = ""
        elif column == 'CPI_YOY':
            value = f"{latest_val:.1f}%"
            color = COLORS['green'] if latest_val < 3 else COLORS['red'] if latest_val > 5 else COLORS['yellow']
            status = ""
        elif column == '10Y2Y':
            value = f"{latest_val:.2f}%"
            color = COLORS['red'] if latest_val < 0 else COLORS['green']
            status = "INVERTED" if latest_val < 0 else "NORMAL"
        elif column == 'VIX':
            value = f"{latest_val:.1f}"
            status, color = get_vulnerability_status(normalize_vix_stress(latest_val))
        elif column == 'DCOILWTICO':
            value = f"${latest_val:.2f}"
            color = COLORS['dashboard'][5]
            status = ""
        elif column == 'HOUST':
            value = f"{latest_val/1000:.1f}M"
            status = "Strong" if latest_val > 1500 else "Weak" if latest_val < 1000 else "Normal"
            color = COLORS['green'] if latest_val > 1500 else COLORS['red'] if latest_val < 1000 else COLORS['yellow']
        elif column == 'UMCSENT':
            value = f"{latest_val:.1f}"
            status = "High" if latest_val > 80 else "Low" if latest_val < 60 else "Medium"
            color = COLORS['green'] if latest_val > 80 else COLORS['red'] if latest_val < 60 else COLORS['yellow']
        else:
            value = str(latest_val)
            color = COLORS['gold']
            status = ""
        
        # Create date string
        date_str = safe_strftime(latest_date, '%b %d, %Y')
        
    else:
        value = "No data"
        color = COLORS['gray']
        date_str = ""
        status = ""
    
    # Get last 3 years of data for sparkline
    three_years = df[df['date'] >= df['date'].max() - pd.Timedelta(days=3*365)]
    
    # Create mini sparkline
    fig = go.Figure()
    
    # Check if we have data in the last 3 years
    col_data = three_years[three_years[column].notna()]
    if not col_data.empty:
        fig.add_trace(go.Scatter(
            x=col_data['date'],
            y=col_data[column],
            mode='lines',
            line=dict(color=color, width=2),
            showlegend=False
        ))
    
    fig.update_layout(
        height=70,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False)
    )
    
    # Display card
    if status:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['dark_bg']} 0%, {COLORS['light_bg']} 100%);
                    padding: 15px; border-radius: 10px; border-left: 6px solid {color};
                    margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <div style="color: {COLORS['gray']}; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">{title}</div>
            <div style="color: white; font-size: 1.8rem; font-weight: bold; margin: 5px 0;">{value}</div>
            <div style="color: {color}; font-size: 0.8rem;">{status} • as of {date_str}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['dark_bg']} 0%, {COLORS['light_bg']} 100%);
                    padding: 15px; border-radius: 10px; border-left: 6px solid {color};
                    margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <div style="color: {COLORS['gray']}; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">{title}</div>
            <div style="color: white; font-size: 1.8rem; font-weight: bold; margin: 5px 0;">{value}</div>
            <div style="color: {color}; font-size: 0.8rem;">as of {date_str}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Use a unique key for each chart
    unique_key = f"sparkline_{card_id}_{column}_{int(np.random.random()*10000)}"
    st.plotly_chart(fig, use_container_width=True, key=unique_key)


def create_complete_dashboard(df):
    """Chart 12: 2x4 grid of sparkline cards showing latest available values"""
    
    # Create container
    dashboard_container = st.container()
    
    with dashboard_container:
        # Create 2 rows, 4 columns
        row1 = st.columns(4)
        row2 = st.columns(4)
        
        # Row 1
        with row1[0]:
            create_sparkline_card(
                "10Y Yield",
                'DGS10',
                df,
                card_id="yield"
            )
        
        with row1[1]:
            create_sparkline_card(
                "Unemployment",
                'UNRATE',
                df,
                card_id="unemployment"
            )
        
        with row1[2]:
            create_sparkline_card(
                "Inflation (CPI)",
                'CPI_YOY',
                df,
                card_id="inflation"
            )
        
        with row1[3]:
            create_sparkline_card(
                "10Y-2Y Spread",
                '10Y2Y',
                df,
                card_id="spread"
            )
        
        # Row 2
        with row2[0]:
            create_sparkline_card(
                "VIX (Fear)",
                'VIX',
                df,
                card_id="vix"
            )
        
        with row2[1]:
            create_sparkline_card(
                "Oil (WTI)",
                'DCOILWTICO',
                df,
                card_id="oil"
            )
        
        with row2[2]:
            create_sparkline_card(
                "Housing Starts",
                'HOUST',
                df,
                card_id="housing"
            )
        
        with row2[3]:
            create_sparkline_card(
                "Consumer Sentiment",
                'UMCSENT',
                df,
                card_id="sentiment"
            )
    
    return None


# ============================================================================
# CHART 12: THE COMPLETE DASHBOARD - FIGURE VERSION FOR FULL SCREEN (FIXED)
# ============================================================================

def create_dashboard_figure(df):
    """Create a figure version of the Complete Dashboard for full screen display"""
    
    # Create a 2x4 grid of subplots
    fig = make_subplots(
        rows=2, cols=4,
        subplot_titles=('10Y Yield', 'Unemployment', 'Inflation (CPI)', '10Y-2Y Spread',
                       'VIX (Fear)', 'Oil (WTI)', 'Housing Starts', 'Consumer Sentiment'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Get last 3 years of data for sparklines
    three_years = df[df['date'] >= df['date'].max() - pd.Timedelta(days=3*365)]
    
    # Define columns to display
    columns = ['DGS10', 'UNRATE', 'CPI_YOY', '10Y2Y', 'VIX', 'DCOILWTICO', 'HOUST', 'UMCSENT']
    
    # Add sparklines to each subplot
    for i, col in enumerate(columns):
        row = i // 4 + 1
        col_pos = i % 4 + 1
        
        # Get the latest value
        valid_data = df[df[col].notna()]
        if not valid_data.empty:
            latest_row = valid_data.iloc[-1]
            latest_val = latest_row[col]
            latest_date = latest_row['date']
            
            # Format based on column
            if col == 'DGS10':
                value = f"{latest_val:.2f}%"
                color = COLORS['green'] if latest_val < 4 else COLORS['red'] if latest_val > 6 else COLORS['yellow']
            elif col == 'UNRATE':
                value = f"{latest_val:.1f}%"
                color = COLORS['green'] if latest_val < 4 else COLORS['red'] if latest_val > 6 else COLORS['yellow']
            elif col == 'CPI_YOY':
                value = f"{latest_val:.1f}%"
                color = COLORS['green'] if latest_val < 3 else COLORS['red'] if latest_val > 5 else COLORS['yellow']
            elif col == '10Y2Y':
                value = f"{latest_val:.2f}%"
                color = COLORS['red'] if latest_val < 0 else COLORS['green']
            elif col == 'VIX':
                value = f"{latest_val:.1f}"
                _, color = get_vulnerability_status(normalize_vix_stress(latest_val))
            elif col == 'DCOILWTICO':
                value = f"${latest_val:.2f}"
                color = COLORS['dashboard'][5]
            elif col == 'HOUST':
                value = f"{latest_val/1000:.1f}M"
                color = COLORS['green'] if latest_val > 1500 else COLORS['red'] if latest_val < 1000 else COLORS['yellow']
            elif col == 'UMCSENT':
                value = f"{latest_val:.1f}"
                color = COLORS['green'] if latest_val > 80 else COLORS['red'] if latest_val < 60 else COLORS['yellow']
            else:
                value = str(latest_val)
                color = COLORS['gold']
            
            date_str = safe_strftime(latest_date, '%b %d, %Y')
            
            # Add sparkline if we have data in the last 3 years
            col_data = three_years[three_years[col].notna()]
            if not col_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=col_data['date'],
                        y=col_data[col],
                        mode='lines',
                        line=dict(color=color, width=2),
                        name=col,
                        showlegend=False
                    ),
                    row=row, col=col_pos
                )
            
            # Add value annotation as x-axis title
            fig.update_xaxes(
                title_text=f"<b>{value}</b><br><span style='font-size:10px;'>as of {date_str}</span>",
                title_font=dict(color=color, size=14),
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                row=row, col=col_pos
            )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="📋 Complete Dashboard - Economy in 3 Seconds",
            font=dict(color=COLORS['gold'], size=24, family='Arial Black'),
            x=0.5,
            xanchor='center'
        ),
        height=700,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    # Update all y-axes
    for i in range(1, 9):
        row = (i-1) // 4 + 1
        col = (i-1) % 4 + 1
        
        fig.update_yaxes(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            row=row, col=col
        )
    
    return fig

# ============================================================================
# MAIN TAB FUNCTION - UPDATED WITH MINARD-INSPIRED CHART 1 AND DOCUMENTATION
# ============================================================================

def create_vault_tab(df, historical_events):
    """Main function to create the Visual Vault tab"""
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="color: #FFD700; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">🎨 Visual Vault</h1>
        <p style="color: #888; font-size: 1.2rem;">Economic history, reimagined — every visual tells a story</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # ADD DOCUMENTATION BOX ABOUT VULNERABILITY INDEX VS VIX
    # =========================================================================
    st.markdown("""
    <div style="background: rgba(255,215,0,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #FFD700;">
        <h4 style="color: #FFD700; margin: 0 0 10px 0;">🔴 Understanding the Vulnerability Index™</h4>
        <p style="color: white; margin: 5px 0;">
            <strong>Important:</strong> The Vulnerability Index™ is <strong>NOT the VIX</strong>. 
            The VIX measures only stock market fear.
        </p>
        <p style="color: #ccc; margin: 10px 0 0 0;">
            The Vulnerability Index™ combines <strong>4 components</strong>:<br>
            • <span style="color: #FFD700;">Curve Stress</span> (yield curve inversion)<br>
            • <span style="color: #FFD700;">Credit Stress</span> (high yield spreads)<br>
            • <span style="color: #FFD700;">VIX Stress</span> (market fear) ← this is where the VIX appears<br>
            • <span style="color: #FFD700;">Systemic Stress</span> (financial conditions)
        </p>
        <p style="color: #888; font-size: 0.9rem; margin: 10px 0 0 0; font-style: italic;">
            Think of it this way: VIX is your heart rate. The Vulnerability Index™ is your doctor's full check-up.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Today's Highlight
    df_vuln = calculate_vulnerability_index(df)
    latest_vuln = df_vuln['VULNERABILITY_INDEX'].iloc[-1]
    
    # Check if we got a valid number
    if pd.isna(latest_vuln):
        valid_indices = df_vuln['VULNERABILITY_INDEX'].notna()
        if valid_indices.any():
            latest_vuln = df_vuln.loc[valid_indices, 'VULNERABILITY_INDEX'].iloc[-1]
            status, color = get_vulnerability_status(latest_vuln)
            highlight_message = f"Vulnerability Index at {latest_vuln:.1f} ({status})"
        else:
            status, color = "UNAVAILABLE", COLORS['gray']
            highlight_message = "Vulnerability Index data is currently being updated"
    else:
        status, color = get_vulnerability_status(latest_vuln)
        highlight_message = f"Vulnerability Index at {latest_vuln:.1f} ({status})"
    
    latest_date = df['date'].iloc[-1]
    date_str = safe_strftime(latest_date, '%B %d, %Y')
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #00267F 0%, #0033A0 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 25px;
                border-left: 6px solid {color}; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h4 style="color: #FFD700; margin: 0; font-size: 1.3rem;">🔍 Today's Highlight</h4>
        <p style="color: white; margin: 8px 0 0; font-size: 1.1rem;">{highlight_message}</p>
        <p style="color: #888; font-size: 0.8rem; margin: 5px 0 0;">
            Data as of {date_str}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if any chart is in fullscreen mode
    fullscreen_active = False
    for chart in CHART_METADATA:
        if st.session_state.get(f'fullscreen_{chart["id"]}', False):
            fullscreen_active = True
            
            # Header with close button
            col1, col2, col3 = st.columns([1, 6, 1])
            with col2:
                st.markdown(f"<h2 style='color: {COLORS['gold']}; text-align: center;'>{chart['title']} - Full Screen</h2>", unsafe_allow_html=True)
            with col3:
                if st.button("✕ Close", key=f"close_modal_{chart['id']}"):
                    st.session_state[f'fullscreen_{chart["id"]}'] = False
                    st.rerun()
            
            # Generate and display the fullscreen chart
            if chart['id'] == 1:
                fig = create_american_yield_eras(df)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 2:
                fig = create_vulnerability_index(df, historical_events)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 3:
                fig = create_economic_carousel(df, chart_key=f"fullscreen_{chart['id']}")
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}_chart")
            
            elif chart['id'] == 4:
                fig = create_economic_compass(df)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 5:
                fig = create_fed_footprint(df)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 6:
                fig = create_real_unemployment_gap(df)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 7:
                fig = create_inflation_story(df)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 8:
                fig = create_vulnerability_clock(df)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 9:
                fig = create_era_comparison_figure(df)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 10:
                fig = create_fear_timeline(df, historical_events)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 11:
                fig = create_housing_cycle(df)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            elif chart['id'] == 12:
                fig = create_dashboard_figure(df)
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True, key=f"fullscreen_{chart['id']}")
            
            break
    
    if not fullscreen_active:
        # Create tabs for Charts and Maps
        chart_tab, map_tab = st.tabs(["📊 12 Charts", "🗺️ 6 Maps (Coming Soon)"])
        
        with chart_tab:
            # Create 3x4 grid
            for row in range(3):
                cols = st.columns(4)
                for col_idx in range(4):
                    chart_idx = row * 4 + col_idx
                    if chart_idx < len(CHART_METADATA):
                        chart = CHART_METADATA[chart_idx]
                        with cols[col_idx]:
                            with st.expander(f"{chart['icon']} {chart['title']}", expanded=False):
                                st.markdown(f"*{chart['description']}*")
                                
                                # Full screen button
                                if st.button("🔍 Full Screen", key=f"fs_btn_{chart['id']}"):
                                    st.session_state[f'fullscreen_{chart["id"]}'] = True
                                    st.rerun()
                                
                                # Route to appropriate chart (thumbnail view)
                                if chart['id'] == 1:
                                    fig = create_american_yield_eras(df)
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}")
                                
                                elif chart['id'] == 2:
                                    fig = create_vulnerability_index(df, historical_events)
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}")
                                
                                elif chart['id'] == 3:
                                    fig = create_economic_carousel(df, chart_key=f"thumb_{chart['id']}")
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}_chart")
                                
                                elif chart['id'] == 4:
                                    fig = create_economic_compass(df)
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}")
                                
                                elif chart['id'] == 5:
                                    fig = create_fed_footprint(df)
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}")
                                
                                elif chart['id'] == 6:
                                    fig = create_real_unemployment_gap(df)
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}")
                                
                                elif chart['id'] == 7:
                                    fig = create_inflation_story(df)
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}")
                                
                                elif chart['id'] == 8:
                                    fig = create_vulnerability_clock(df)
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}")
                                
                                elif chart['id'] == 9:
                                    create_era_comparison(df)
                                
                                elif chart['id'] == 10:
                                    fig = create_fear_timeline(df, historical_events)
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}")
                                
                                elif chart['id'] == 11:
                                    fig = create_housing_cycle(df)
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True, key=f"thumb_{chart['id']}")
                                
                                elif chart['id'] == 12:
                                    create_complete_dashboard(df)
        
        with map_tab:
            st.markdown("""
            <div style="text-align: center; padding: 50px; background: rgba(255,215,0,0.05); border-radius: 10px;">
                <h2 style="color: #FFD700;">🗺️ Maps Coming Soon in Phase 2</h2>
                <p style="color: #888;">Six interactive maps showing:</p>
                <ul style="color: #ccc; list-style-type: none; padding: 0;">
                    <li>• The Recession Map - Watch unemployment spread like a virus</li>
                    <li>• The Migration Story - Where are Americans voting with their feet?</li>
                    <li>• The Affordability Crisis - Where can you still buy a home?</li>
                    <li>• The Two Americas - Coast vs. Heartland</li>
                    <li>• The Banking Stress Map - Where are banks in trouble?</li>
                    <li>• The Inflation Map - What's driving inflation where</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    return None