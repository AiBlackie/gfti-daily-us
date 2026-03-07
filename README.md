Here's a complete professional README.md for your repository:

```markdown
# GFTI Daily™ - US Economic History Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gftidaily.com)

A comprehensive dashboard tracking **84 economic indicators** across the US economy from **1962-2026**. Includes proprietary indices, real-time crisis monitoring, and historical event analysis.

![Dashboard Preview](https://via.placeholder.com/800x400?text=GFTI+Daily+Dashboard+Preview)

---

## 📊 **Features**

### Core Dashboard
- **84 economic indicators** covering:
  - 💰 Rates & Fed (yield curve, Fed policy, balance sheet)
  - 👥 Labor Market (unemployment, JOLTS, claims)
  - 📈 Inflation (CPI, PCE, expectations)
  - 🏠 Housing (starts, permits, homeownership)
  - 📉 Market Fear (VIX, credit spreads)
  - 💵 Money & Credit (M2, household net worth)

### Proprietary Indices
- 🔴 **Vulnerability Index™** - Composite crisis warning system combining:
  - Curve Stress (yield curve inversion)
  - Credit Stress (high yield spreads)
  - VIX Stress (market fear)
  - Systemic Stress (financial conditions)

### Real-Time Monitoring
- 🚨 **Iran-USA War Impact** - Daily tracking since Feb 23, 2026
- ⏰ **Crisis Watch** - 6 key indicators with color-coded alerts
- 📅 **War Impact Timeline** - Before/after comparison

### Historical Analysis
- 📜 **64 Years of History** - Every major crisis since 1962
- 🔍 **Historical Matches** - Find similar periods to today
- 🎨 **Visual Vault** - 12 custom chart visualizations

---

## 🚀 **Live Demo**

The app is live at: [**gftidaily.com**](https://gftidaily.com) (coming soon)

Streamlit URL: [https://gfti-daily-us.streamlit.app](https://gfti-daily-us.streamlit.app)

---

## 📋 **Getting Started**

### Prerequisites
- Python 3.9+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/gfti-daily-us.git
cd gfti-daily-us
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run locally**
```bash
streamlit run app.py
```

4. **View in browser**
```
http://localhost:8501
```

---

## 📁 **Project Structure**

```
gfti-daily-us/
├── app.py                 # Main application
├── visual_vault.py        # Chart library (12 visualizations)
├── master_dataset.csv     # 84 indicators (1962-2026)
├── requirements.txt       # Python dependencies
├── .gitignore            # Files to exclude from git
└── README.md             # This file
```

---

## 📦 **Dependencies**

```
streamlit==1.32.0
pandas==2.2.0
plotly==5.18.0
numpy==1.26.0
```

---

## 🔑 **Key Features Explained**

### The Vulnerability Index™
```
Components:
- CURVE_STRESS: Yield curve inversion (10Y2Y)
- CREDIT_STRESS: High yield spreads
- VIX_STRESS: Market fear/volatility
- SYSTEMIC_STRESS: Financial conditions

Range:
- <40: LOW stress
- 40-70: ELEVATED stress
- >70: HIGH stress
```

### Crisis Watch Thresholds
| Indicator | Warning | Critical |
|-----------|---------|----------|
| VIX | >25 | >30 |
| Oil | >$80 | >$90 |
| Yield Curve | <0.2% | <0% |
| Credit Spreads | >4% | >5% |
| Consumer Sentiment | <60 | <50 |
| Jobless Claims | >300K | >350K |

---

## 📊 **Data Sources**

All data is sourced from:
- 🏦 **FRED®** (Federal Reserve Economic Data, St. Louis Fed)
- 📈 **Yahoo Finance** (VIX)

*GFTI Daily™ is an independent provider of cleaned and enhanced economic data and is not affiliated with, endorsed by, or sponsored by the Federal Reserve Bank of St. Louis or Yahoo! Inc.*

---

## 📝 **Waitlist**

The interactive dashboard is **completely FREE**. Join the waitlist for:
- 📥 Full 84-indicator dataset in CSV format
- 🔄 Daily automated updates
- ⚡ Proprietary calculations pre-built
- 🧹 No cleaning needed (gaps removed, weekends handled)

👉 [Join the waitlist](https://gftidaily.com) in the app!

---

## 🤝 **Contact**

- **Email**: [hello@gftidaily.com](mailto:hello@gftidaily.com)
- **Website**: [gftidaily.com](https://gftidaily.com)

---

## ⚖️ **Legal**

© 2026 Matthew A.A. Blackman. All Rights Reserved.

**Trademarks:**
- GFTI Daily™
- Vulnerability Index™
- Trust Tax™

This software and methodology are protected by copyright law and international treaties.

---

## 🙏 **Acknowledgments**

- Federal Reserve Bank of St. Louis for FRED® data
- Yahoo Finance for VIX data
- Streamlit for the amazing framework

---

**Built with ❤️ by Matthew A.A. Blackman**
```

## 📝 **Also Create a `.gitignore` File:**

```gitignore
# Streamlit
.streamlit/
*.toml

# Data files
master_dataset.csv
waitlist.json
waitlist.csv

# Python
__pycache__/
*.pyc
.env
venv/
env/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```
