Here's the updated README.md with accurate information (58 indicators, honest coverage, etc.):

```markdown
# GFTI Daily™ - US Economic History Dashboard

A comprehensive dashboard tracking **58 economic indicators** across the US economy from **1960-2026**. Includes proprietary indices, real-time crisis monitoring, and historical event analysis.
 
---

## 📊 **Features**

### Core Dashboard
- **58 economic indicators** covering:
  - 💰 **Rates & Fed** (15) - Complete yield curve, Fed policy, balance sheet
  - 👥 **Labor Market** (10) - Unemployment (U3 & U6), JOLTS, claims, hours worked
  - 📈 **Inflation** (7) - CPI, Core CPI, PCE, Core PCE, breakeven expectations
  - 🏠 **Housing** (3) - Starts, permits, homeownership rate
  - 📊 **Growth** (4) - Real GDP, industrial production, retail sales, consumer sentiment
  - 📉 **Market Fear** (5) - VIX, financial stress, oil, dollar, credit spreads
  - 💵 **Money & Credit** (5) - M2, household net worth, credit spreads
  - 🌎 **Demographics** (1) - Median household income

### Coverage by Era
| Era | Indicators |
|-----|------------|
| **1960-1985** | 29+ core indicators (yields, inflation, unemployment) |
| **1986-1995** | 41+ indicators (adds oil, credit spreads, claims) |
| **1996-2005** | 49+ indicators (adds VIX, labor depth, high yield) |
| **2006-2026** | 58 indicators (full modern dataset) |

### Proprietary Indices
- 🔴 **Vulnerability Index™** - Composite crisis warning system combining:
  - Curve Stress (yield curve inversion)
  - Credit Stress (high yield spreads)
  - VIX Stress (market fear)
  - Systemic Stress (financial conditions)

### Real-Time Monitoring
- 🚨 **Iran-USA War Impact** - Daily tracking since Feb 23, 2026
- ⏰ **Crisis Watch** - 6 key indicators with color-coded alerts
- 📅 **War Impact Timeline** - Before/after comparison with change tracking

### Historical Analysis
- 📜 **64 Years of History** - Every major recession and crisis since 1960
- 🔍 **Historical Matches** - Find similar periods to today's yield curve
- 🎨 **Visual Vault** - 12 custom chart visualizations including:
  - The American Yield (Minard-inspired era visualization)
  - The Vulnerability Clock™ (8 dimensions of stress)
  - The Economic Compass (inflation vs unemployment)
  - The Fear Timeline (every crisis measured in VIX)

---

## 🚀 **Live Demo**

The app is live at: [**gftidaily.com**](https://gftidaily.com)

Streamlit URL: [https://gfti-daily-us.streamlit.app](https://gfti-daily-us.streamlit.app)

---

## 📋 **Getting Started**

### Prerequisites
- Python 3.9+
- pip
- FRED API key (free from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html))

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

3. **Set up API keys**
Create a `.streamlit/secrets.toml` file:
```toml
FRED_API_KEY = "your_fred_api_key_here"
FORMSPREE_ENDPOINT = "https://formspree.io/f/your-form-id"
```

4. **Run the app locally**
```bash
streamlit run app.py
```

---

## 📦 **Data Update Process**

The dataset updates automatically daily via GitHub Actions. The update script:
- Downloads new data from FRED for all 58 indicators
- Fetches VIX from Yahoo Finance
- Cleans and forward-fills gaps appropriately
- Calculates all proprietary spreads and indices
- Saves to `master_dataset.csv`

To run manually:
```bash
python appdupdate.py
```

---

## 🗂️ **Repository Structure**

```
gfti-daily-us/
├── app.py                 # Main Streamlit application
├── appdupdate.py          # Daily data update script
├── visual_vault.py        # Custom chart visualizations
├── master_dataset.csv     # Complete dataset (gitignored)
├── requirements.txt       # Python dependencies
├── .streamlit/            # Streamlit configuration
│   └── secrets.toml       # API keys (gitignored)
├── backups/               # Daily dataset backups
└── .github/workflows/     # GitHub Actions automation
    └── daily_update.yml   # Daily update workflow
```

---

## 🔧 **Technologies Used**

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Data Sources**: [FRED](https://fred.stlouisfed.org/), [Yahoo Finance](https://finance.yahoo.com/)
- **Visualization**: [Plotly](https://plotly.com/), [Matplotlib](https://matplotlib.org/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Automation**: GitHub Actions
- **Email Capture**: Formspree

---

## 📝 **Attribution & Legal**

GFTI Daily™ is built on public data from trusted sources:

- **FRED®** (Federal Reserve Economic Data) - Federal Reserve Bank of St. Louis
- **Yahoo Finance** - VIX data

We are an independent data provider, not affiliated with, endorsed by, or sponsored by the Federal Reserve Bank of St. Louis or Yahoo! Inc.

If you publish or distribute any part of this dataset, you must include:
> "Data sourced from FRED® (Federal Reserve Economic Data), Federal Reserve Bank of St. Louis, and Yahoo Finance."

---

## 📬 **Contact**

- **Email**: hello@gftidaily.com
- **Website**: [gftidaily.com](https://gftidaily.com)


---

## ⚖️ **License**

© 2026 GFTI Daily™. All rights reserved. GFTI Daily™ is a trademark of Matthew A.A. Blackman.

This project is for demonstration purposes. The underlying data remains the property of its respective owners (FRED®, Yahoo Finance). The code is provided for educational use.

---

## 🙏 **Acknowledgments**

- Federal Reserve Bank of St. Louis for providing FRED®
- Yahoo Finance for VIX data
- Streamlit for the amazing framework
- All users who provide feedback and support
```

