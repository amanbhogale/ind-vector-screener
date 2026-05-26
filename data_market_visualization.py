# Indian Market Data Analysis - Undervalued Stock Finder
# Required installations: pip install yfinance pandas numpy plotly matplotlib seaborn fpdf2 scipy

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import json
import os
warnings.filterwarnings('ignore')

# ============================================================
# SECTION 1: INDIAN MARKET STOCK UNIVERSE BY SECTOR
# ============================================================

INDIAN_STOCKS = {
    "Banking": {
        "HDFCBANK.NS": "HDFC Bank",
        "ICICIBANK.NS": "ICICI Bank",
        "SBIN.NS": "SBI",
        "KOTAKBANK.NS": "Kotak Mahindra Bank",
        "AXISBANK.NS": "Axis Bank",
        "INDUSINDBK.NS": "IndusInd Bank",
        "BANKBARODA.NS": "Bank of Baroda",
        "PNB.NS": "Punjab National Bank",
        "FEDERALBNK.NS": "Federal Bank",
        "IDFCFIRSTB.NS": "IDFC First Bank"
    },
    "IT": {
        "TCS.NS": "TCS",
        "INFY.NS": "Infosys",
        "WIPRO.NS": "Wipro",
        "HCLTECH.NS": "HCL Tech",
        "TECHM.NS": "Tech Mahindra",
        "TATAELXSI.NS": "Tata Elxsi",
        "MPHASIS.NS": "Mphasis",
        "COFORGE.NS": "Coforge",
        "PERSISTENT.NS": "Persistent Systems",
        "LTTS.NS": "L&T Technology"
    },
    "Pharma": {
        "SUNPHARMA.NS": "Sun Pharma",
        "DRREDDY.NS": "Dr. Reddy's",
        "CIPLA.NS": "Cipla",
        "DIVISLAB.NS": "Divi's Labs",
        "AUROPHARMA.NS": "Aurobindo Pharma",
        "BIOCON.NS": "Biocon",
        "LUPIN.NS": "Lupin",
        "TORNTPHARM.NS": "Torrent Pharma",
        "ALKEM.NS": "Alkem Labs",
        "IPCALAB.NS": "IPCA Labs"
    },
    "Auto": {
        "MARUTI.NS": "Maruti Suzuki",
        "TMPV.NS": "Tata Motors PV",
        "TMCV.NS": "Tata Motors CV",
        "M&M.NS": "Mahindra & Mahindra",
        "BAJAJ-AUTO.NS": "Bajaj Auto",
        "HEROMOTOCO.NS": "Hero MotoCorp",
        "EICHERMOT.NS": "Eicher Motors",
        "ASHOKLEY.NS": "Ashok Leyland",
        "TVSMOTOR.NS": "TVS Motor",
        "MRF.NS": "MRF"
    },
    "FMCG": {
        "HINDUNILVR.NS": "Hindustan Unilever",
        "ITC.NS": "ITC",
        "NESTLEIND.NS": "Nestle India",
        "BRITANNIA.NS": "Britannia",
        "DABUR.NS": "Dabur India",
        "MARICO.NS": "Marico",
        "GODREJCP.NS": "Godrej Consumer",
        "COLPAL.NS": "Colgate-Palmolive",
        "TATACONSUM.NS": "Tata Consumer",
        "VBL.NS": "Varun Beverages"
    },
    "Energy": {
        "RELIANCE.NS": "Reliance Industries",
        "ONGC.NS": "ONGC",
        "NTPC.NS": "NTPC",
        "POWERGRID.NS": "Power Grid",
        "TATAPOWER.NS": "Tata Power",
        "BPCL.NS": "BPCL",
        "IOC.NS": "Indian Oil Corp",
        "COALINDIA.NS": "Coal India",
        "IREDA.NS": "IREDA",
        "GENUSPOWER.NS": "Genus Power"
    },
    "Metals & Mining": {
        "TATASTEEL.NS": "Tata Steel",
        "HINDALCO.NS": "Hindalco",
        "JSWSTEEL.NS": "JSW Steel",
        "VEDL.NS": "Vedanta",
        "COALINDIA.NS": "Coal India",
        "NMDC.NS": "NMDC",
        "SAIL.NS": "SAIL",
        "NATIONALUM.NS": "National Aluminium",
        "HINDCOPPER.NS": "Hindustan Copper",
        "MOIL.NS": "MOIL"
    },
    "Real Estate": {
        "DLF.NS": "DLF",
        "GODREJPROP.NS": "Godrej Properties",
        "OBEROIRLTY.NS": "Oberoi Realty",
        "PHOENIXLTD.NS": "Phoenix Mills",
        "PRESTIGE.NS": "Prestige Estates",
        "BRIGADE.NS": "Brigade Enterprises",
        "SOBHA.NS": "Sobha Ltd",
        "SUNTECK.NS": "Sunteck Realty",
        "LODHA.NS": "Macrotech Developers",
        "RAYMOND.NS": "Raymond"
    },
    "DEFENCE": {
        "HAL.NS": "Hindustan Aeronautics",
        "BEL.NS": "Bharat Electronics",
        "BHEL.NS": "Bharat Heavy Electricals",
        "LT.NS": "Larsen & Toubro",
        "MAZDOCK.NS": "Mazagon Dock Shipbuilders",
        "GRSE.NS": "Garden Reach Shipbuilders",
        "BDL.NS": "Bharat Dynamics",
        "BEML.NS": "BEML",
        "COCHINSHIP.NS": "Cochin Shipyard",
        "PARAS.NS": "Paras Defence"
    }
}


# ============================================================
# SECTION 2: DATA FETCHING ENGINE
# ============================================================

class IndianMarketAnalyzer:
    def __init__(self):
        self.stock_data = {}
        self.fundamental_data = {}
        self.analysis_results = pd.DataFrame()
        self.sector_analysis = {}
        self.fetch_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    def fetch_stock_data(self, ticker, period="1y"):
        """Fetch historical price data"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                return None
            return hist
        except Exception as e:
            print(f"  ⚠ Error fetching {ticker}: {e}")
            return None

    def fetch_fundamentals(self, ticker):
        """Fetch fundamental data for a stock"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            dy = info.get('dividendYield', None)
            if dy is not None:
                if dy > 0.2:
                    dy = dy / 100.0
            else:
                dy = info.get('trailingAnnualDividendYield', 0.0)
                if dy is None:
                    dy = 0.0

            fundamentals = {
                'Market Cap': info.get('marketCap', None),
                'PE Ratio': info.get('trailingPE', info.get('forwardPE', None)),
                'Forward PE': info.get('forwardPE', None),
                'Trailing PE': info.get('trailingPE', None),
                'PB Ratio': info.get('priceToBook', None),
                'PS Ratio': info.get('priceToSalesTrailing12Months', None),
                'Dividend Yield': dy,
                'ROE': info.get('returnOnEquity', None),
                'ROA': info.get('returnOnAssets', None),
                'Profit Margin': info.get('profitMargins', None),
                'Operating Margin': info.get('operatingMargins', None),
                'Revenue Growth': info.get('revenueGrowth', None),
                'Earnings Growth': info.get('earningsGrowth', None),
                'Quarterly Earnings Growth': info.get('earningsQuarterlyGrowth', None),
                'Quarterly Revenue Growth': info.get('revenueQuarterlyGrowth', None),
                'Debt to Equity': info.get('debtToEquity', None),
                'Current Ratio': info.get('currentRatio', None),
                'Book Value': info.get('bookValue', None),
                'EPS': info.get('trailingEps', None),
                'Forward EPS': info.get('forwardEps', None),
                'Current Price': info.get('currentPrice', info.get('regularMarketPrice', None)),
                'Target Price': info.get('targetMeanPrice', None),
                'Target High': info.get('targetHighPrice', None),
                'Target Low': info.get('targetLowPrice', None),
                '52W High': info.get('fiftyTwoWeekHigh', None),
                '52W Low': info.get('fiftyTwoWeekLow', None),
                'Beta': info.get('beta', None),
                'Free Cash Flow': info.get('freeCashflow', None),
                'Total Revenue': info.get('totalRevenue', None),
                'EBITDA': info.get('ebitda', None),
                'Total Debt': info.get('totalDebt', None),
                'Total Cash': info.get('totalCash', None),
                'Recommendation': info.get('recommendationKey', 'N/A'),
                'Number of Analysts': info.get('numberOfAnalystOpinions', 0)
            }
            return fundamentals
        except Exception as e:
            print(f"  ⚠ Error fetching fundamentals for {ticker}: {e}")
            return None

    def calculate_technical_indicators(self, hist):
        """Calculate technical indicators"""
        if hist is None or hist.empty:
            return {}

        close = hist['Close']
        volume = hist['Volume']

        indicators = {}

        # Moving Averages
        indicators['SMA_20'] = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else None
        indicators['SMA_50'] = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None
        indicators['SMA_200'] = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
        indicators['Current Price'] = close.iloc[-1]

        # Price vs Moving Averages
        if indicators['SMA_50']:
            indicators['Price_vs_SMA50'] = ((close.iloc[-1] / indicators['SMA_50']) - 1) * 100
        if indicators['SMA_200']:
            indicators['Price_vs_SMA200'] = ((close.iloc[-1] / indicators['SMA_200']) - 1) * 100

        # RSI (14-day)
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['RSI'] = (100 - (100 / (1 + rs))).iloc[-1] if len(close) >= 14 else None

        # MACD
        if len(close) >= 26:
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            indicators['MACD'] = macd.iloc[-1]
            indicators['MACD_Signal'] = signal.iloc[-1]
            indicators['MACD_Histogram'] = (macd - signal).iloc[-1]

        # Bollinger Bands
        if len(close) >= 20:
            sma20 = close.rolling(20).mean()
            std20 = close.rolling(20).std()
            indicators['BB_Upper'] = (sma20 + 2*std20).iloc[-1]
            indicators['BB_Lower'] = (sma20 - 2*std20).iloc[-1]
            indicators['BB_Position'] = ((close.iloc[-1] - indicators['BB_Lower']) /
                                         (indicators['BB_Upper'] - indicators['BB_Lower'])) * 100

        # Volatility
        returns = close.pct_change().dropna()
        indicators['Volatility_Annual'] = returns.std() * np.sqrt(252) * 100 if len(returns) > 0 else None

        # Returns
        if len(close) >= 5:
            indicators['Return_1W'] = ((close.iloc[-1] / close.iloc[-5]) - 1) * 100
        if len(close) >= 21:
            indicators['Return_1M'] = ((close.iloc[-1] / close.iloc[-21]) - 1) * 100
        if len(close) >= 63:
            indicators['Return_3M'] = ((close.iloc[-1] / close.iloc[-63]) - 1) * 100
        if len(close) >= 126:
            indicators['Return_6M'] = ((close.iloc[-1] / close.iloc[-126]) - 1) * 100
        if len(close) >= 252:
            indicators['Return_1Y'] = ((close.iloc[-1] / close.iloc[-252]) - 1) * 100

        # Volume Analysis
        indicators['Avg_Volume_20D'] = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else None
        if indicators['Avg_Volume_20D'] and indicators['Avg_Volume_20D'] > 0:
            indicators['Volume_Ratio'] = volume.iloc[-1] / indicators['Avg_Volume_20D']

        return indicators

    def calculate_valuation_score(self, fundamentals, technicals):
        """
        Calculate a composite valuation score (0-100)
        Lower score = More Undervalued
        """
        score = 50  # Start neutral
        factors = 0

        # === VALUE FACTORS (Lower is better) ===

        # PE Ratio Analysis
        pe = fundamentals.get('PE Ratio')
        if pe and pe > 0:
            if pe < 10:
                score -= 10
            elif pe < 15:
                score -= 7
            elif pe < 20:
                score -= 3
            elif pe < 30:
                score += 3
            elif pe < 50:
                score += 7
            else:
                score += 12
            factors += 1

        # PB Ratio Analysis
        pb = fundamentals.get('PB Ratio')
        if pb and pb > 0:
            if pb < 1:
                score -= 10
            elif pb < 2:
                score -= 7
            elif pb < 3:
                score -= 3
            elif pb < 5:
                score += 3
            else:
                score += 7
            factors += 1

        # Dividend Yield
        div_yield = fundamentals.get('Dividend Yield')
        if div_yield and div_yield > 0:
            if div_yield > 0.04:
                score -= 6
            elif div_yield > 0.02:
                score -= 3
            elif div_yield > 0.01:
                score -= 1
            factors += 1

        # === GROWTH FACTORS (Higher is better → reduces score = more attractive) ===

        rev_growth = fundamentals.get('Revenue Growth')
        if rev_growth:
            if rev_growth > 0.25:
                score -= 10
            elif rev_growth > 0.15:
                score -= 7
            elif rev_growth > 0.10:
                score -= 3
            elif rev_growth > 0:
                score -= 1
            else:
                score += 7
            factors += 1

        earnings_growth = fundamentals.get('Earnings Growth')
        if earnings_growth:
            if earnings_growth > 0.30:
                score -= 10
            elif earnings_growth > 0.20:
                score -= 7
            elif earnings_growth > 0.10:
                score -= 3
            elif earnings_growth > 0:
                score -= 1
            else:
                score += 7
            factors += 1

        # === QUALITY FACTORS ===

        roe = fundamentals.get('ROE')
        if roe:
            if roe > 0.20:
                score -= 6
            elif roe > 0.15:
                score -= 3
            elif roe > 0.10:
                score -= 1
            elif roe > 0:
                score += 1
            else:
                score += 7
            factors += 1

        profit_margin = fundamentals.get('Profit Margin')
        if profit_margin:
            if profit_margin > 0.20:
                score -= 5
            elif profit_margin > 0.10:
                score -= 2
            elif profit_margin > 0:
                score += 1
            else:
                score += 5
            factors += 1

        # Debt to Equity
        de = fundamentals.get('Debt to Equity')
        if de is not None:
            if de < 30:
                score -= 3
            elif de < 50:
                score -= 1
            elif de < 100:
                score += 1
            else:
                score += 5
            factors += 1

        # === TECHNICAL FACTORS ===

        rsi = technicals.get('RSI')
        if rsi:
            if rsi < 30:
                score -= 6  # Oversold = potentially undervalued
            elif rsi < 40:
                score -= 3
            elif rsi > 70:
                score += 6  # Overbought
            elif rsi > 60:
                score += 3
            factors += 1

        # Price vs 52W range
        price = fundamentals.get('Current Price')
        high52 = fundamentals.get('52W High')
        low52 = fundamentals.get('52W Low')
        if price and high52 and low52 and (high52 - low52) > 0:
            position = (price - low52) / (high52 - low52)
            if position < 0.3:
                score -= 6  # Near 52W low
            elif position < 0.5:
                score -= 3
            elif position > 0.9:
                score += 6  # Near 52W high
            elif position > 0.7:
                score += 3
            factors += 1

        # Analyst Target Upside
        target = fundamentals.get('Target Price')
        if price and target and price > 0:
            upside = ((target / price) - 1) * 100
            if upside > 30:
                score -= 10
            elif upside > 20:
                score -= 7
            elif upside > 10:
                score -= 3
            elif upside < -10:
                score += 7
            factors += 1

        # Normalize to 0-100 range
        score = max(0, min(100, score))

        return score

    def calculate_growth_score(self, fundamentals):
        """Calculate growth score (0-100, higher = better growth)"""
        score = 40  # Start slightly lower to prevent easy clamping to 100
        factors = 0

        rev_growth = fundamentals.get('Revenue Growth')
        if rev_growth:
            score += min(20, max(-20, rev_growth * 80))
            factors += 1

        earn_growth = fundamentals.get('Earnings Growth')
        if earn_growth:
            score += min(20, max(-20, earn_growth * 60))
            factors += 1

        qtr_earn = fundamentals.get('Quarterly Earnings Growth')
        if qtr_earn:
            score += min(12, max(-12, qtr_earn * 40))
            factors += 1

        roe = fundamentals.get('ROE')
        if roe and roe > 0:
            score += min(8, roe * 30)
            factors += 1

        forward_pe = fundamentals.get('Forward PE')
        trailing_pe = fundamentals.get('Trailing PE')
        if forward_pe and trailing_pe and forward_pe > 0 and trailing_pe > 0:
            pe_improvement = ((trailing_pe / forward_pe) - 1) * 100
            score += min(8, max(-8, pe_improvement * 0.4))
            factors += 1

        return max(0, min(100, score))

    def analyze_all_stocks(self):
        """Main analysis function"""
        print("=" * 70)
        print("🇮🇳  INDIAN STOCK MARKET ANALYZER")
        print(f"📅  Analysis Date: {self.fetch_date}")
        print("=" * 70)

        all_results = []

        for sector, stocks in INDIAN_STOCKS.items():
            print(f"\n📊 Analyzing {sector} sector ({len(stocks)} stocks)...")
            print("-" * 50)

            sector_results = []

            for ticker, name in stocks.items():
                print(f"  📈 {name} ({ticker})...", end=" ")

                # Fetch data
                hist = self.fetch_stock_data(ticker)
                fundas = self.fetch_fundamentals(ticker)

                if fundas is None or hist is None:
                    print("❌ Skipped")
                    continue

                # Calculate indicators
                technicals = self.calculate_technical_indicators(hist)

                # Calculate scores
                valuation_score = self.calculate_valuation_score(fundas, technicals)
                growth_score = self.calculate_growth_score(fundas)

                # Combined Score (lower = more undervalued with good growth)
                # Weight: 60% valuation, 40% inverse growth
                combined_score = valuation_score * 0.6 + (100 - growth_score) * 0.4

                result = {
                    'Ticker': ticker,
                    'Company': name,
                    'Sector': sector,
                    'Current Price': fundas.get('Current Price'),
                    'Market Cap (Cr)': round(fundas.get('Market Cap', 0) / 10000000, 0) if fundas.get('Market Cap') else None,
                    'PE Ratio': round(fundas.get('PE Ratio', 0), 2) if fundas.get('PE Ratio') else None,
                    'PB Ratio': round(fundas.get('PB Ratio', 0), 2) if fundas.get('PB Ratio') else None,
                    'Dividend Yield %': round(fundas.get('Dividend Yield', 0) * 100, 2) if fundas.get('Dividend Yield') else 0,
                    'ROE %': round(fundas.get('ROE', 0) * 100, 2) if fundas.get('ROE') else None,
                    'Profit Margin %': round(fundas.get('Profit Margin', 0) * 100, 2) if fundas.get('Profit Margin') else None,
                    'Revenue Growth %': round(fundas.get('Revenue Growth', 0) * 100, 2) if fundas.get('Revenue Growth') else None,
                    'Earnings Growth %': round(fundas.get('Earnings Growth', 0) * 100, 2) if fundas.get('Earnings Growth') else None,
                    'Debt/Equity': round(fundas.get('Debt to Equity', 0), 2) if fundas.get('Debt to Equity') else None,
                    'RSI': round(technicals.get('RSI', 0), 2) if technicals.get('RSI') else None,
                    'Return 1M %': round(technicals.get('Return_1M', 0), 2) if technicals.get('Return_1M') else None,
                    'Return 3M %': round(technicals.get('Return_3M', 0), 2) if technicals.get('Return_3M') else None,
                    'Return 6M %': round(technicals.get('Return_6M', 0), 2) if technicals.get('Return_6M') else None,
                    'Return 1Y %': round(technicals.get('Return_1Y', 0), 2) if technicals.get('Return_1Y') else None,
                    'Volatility %': round(technicals.get('Volatility_Annual', 0), 2) if technicals.get('Volatility_Annual') else None,
                    '52W High': fundas.get('52W High'),
                    '52W Low': fundas.get('52W Low'),
                    'Target Price': fundas.get('Target Price'),
                    'Upside %': round(((fundas.get('Target Price', 0) / fundas.get('Current Price', 1)) - 1) * 100, 2)
                                if fundas.get('Target Price') and fundas.get('Current Price') else None,
                    'Valuation Score': round(valuation_score, 1),
                    'Growth Score': round(growth_score, 1),
                    'Combined Score': round(combined_score, 1),
                    'Recommendation': fundas.get('Recommendation', 'N/A'),
                    'Beta': round(fundas.get('Beta', 0), 2) if fundas.get('Beta') else None,
                    'SMA_50': round(technicals.get('SMA_50', 0), 2) if technicals.get('SMA_50') else None,
                    'SMA_200': round(technicals.get('SMA_200', 0), 2) if technicals.get('SMA_200') else None,
                }

                all_results.append(result)
                self.stock_data[ticker] = hist
                self.fundamental_data[ticker] = fundas

                # Rating
                if combined_score < 30:
                    rating = "🟢 STRONG BUY"
                elif combined_score < 40:
                    rating = "🟢 BUY"
                elif combined_score < 50:
                    rating = "🟡 HOLD"
                elif combined_score < 60:
                    rating = "🟠 WEAK"
                else:
                    rating = "🔴 OVERVALUED"

                print(f"✅ Score: {combined_score:.0f} {rating}")

            print(f"  ✅ {sector} sector complete!")

        self.analysis_results = pd.DataFrame(all_results)
        print(f"\n{'='*70}")
        print(f"✅ Analysis complete! {len(self.analysis_results)} stocks analyzed.")
        print(f"{'='*70}")

        return self.analysis_results

    # ============================================================
    # SECTION 3: DYNAMIC VISUALIZATIONS
    # ============================================================

    def create_valuation_heatmap(self):
        """Sector-wise valuation heatmap"""
        if self.analysis_results.empty:
            return

        pivot = self.analysis_results.pivot_table(
            values='Combined Score',
            index='Company',
            columns='Sector',
            aggfunc='first'
        )

        fig = go.Figure()

        for sector in self.analysis_results['Sector'].unique():
            sector_data = self.analysis_results[self.analysis_results['Sector'] == sector].sort_values('Combined Score')

            fig.add_trace(go.Bar(
                name=sector,
                x=sector_data['Company'],
                y=sector_data['Combined Score'],
                marker_color=sector_data['Combined Score'].apply(
                    lambda x: f'rgb({min(255, int(x*5))}, {min(255, int((100-x)*5))}, 50)'
                ),
                text=sector_data['Combined Score'].round(1),
                textposition='auto',
                hovertemplate=(
                    '<b>%{x}</b><br>' +
                    'Combined Score: %{y:.1f}<br>' +
                    '<extra></extra>'
                )
            ))

        fig.update_layout(
            title='🎯 Stock Valuation Scores by Sector (Lower = More Undervalued)',
            xaxis_title='Company',
            yaxis_title='Combined Score (Lower = Better Value)',
            template='plotly_dark',
            height=700,
            showlegend=True,
            barmode='group',
            xaxis_tickangle=-45
        )

        fig.write_html('valuation_heatmap.html')
        # fig.show()
        print("📊 Valuation heatmap saved as 'valuation_heatmap.html'")
        return fig

    def create_sector_bubble_chart(self):
        """Bubble chart: PE vs Growth vs Market Cap"""
        df = self.analysis_results.dropna(subset=['PE Ratio', 'Revenue Growth %', 'Market Cap (Cr)'])

        if df.empty:
            print("⚠ Not enough data for bubble chart")
            return

        fig = px.scatter(
            df,
            x='PE Ratio',
            y='Revenue Growth %',
            size='Market Cap (Cr)',
            color='Sector',
            hover_name='Company',
            hover_data={
                'PE Ratio': ':.2f',
                'Revenue Growth %': ':.2f',
                'Market Cap (Cr)': ':,.0f',
                'ROE %': ':.2f',
                'Combined Score': ':.1f'
            },
            size_max=60,
            title='💹 PE Ratio vs Revenue Growth (Bubble Size = Market Cap)'
        )

        fig.update_layout(
            template='plotly_dark',
            height=700,
            xaxis_title='PE Ratio (Lower = Cheaper)',
            yaxis_title='Revenue Growth % (Higher = Better)',
        )

        # Set default visible viewport ranges to prevent outlier squishing,
        # while keeping the full dataset visible by zooming/panning
        fig.update_xaxes(
            range=[0, 80],
            ticks="outside",
            tick0=0,
            dtick=10
        )
        fig.update_yaxes(
            range=[-20, 80],
            ticks="outside",
            tick0=-20,
            dtick=20
        )

        # Add quadrant lines
        if not df['PE Ratio'].empty:
            median_pe = df['PE Ratio'].median()
            median_growth = df['Revenue Growth %'].median()

            fig.add_hline(y=median_growth, line_dash="dash", line_color="white", opacity=0.5)
            fig.add_vline(x=median_pe, line_dash="dash", line_color="white", opacity=0.5)

            # Annotations positioned relative to the visible ranges
            fig.add_annotation(
                x=median_pe / 2, 
                y=median_growth + (80 - median_growth) / 2,
                text="⭐ UNDERVALUED<br>HIGH GROWTH", 
                showarrow=False,
                font=dict(color="lime", size=12)
            )
            fig.add_annotation(
                x=median_pe + (80 - median_pe) / 2, 
                y=median_growth + (80 - median_growth) / 2,
                text="💰 EXPENSIVE<br>HIGH GROWTH", 
                showarrow=False,
                font=dict(color="yellow", size=12)
            )
            fig.add_annotation(
                x=median_pe / 2, 
                y=median_growth - (median_growth + 20) / 2,
                text="🔍 CHEAP<br>LOW GROWTH", 
                showarrow=False,
                font=dict(color="orange", size=12)
            )

        fig.write_html('sector_bubble_chart.html')
        # fig.show()
        print("📊 Bubble chart saved as 'sector_bubble_chart.html'")
        return fig

    def create_undervalued_dashboard(self):
        """Comprehensive dashboard of top undervalued stocks"""
        df = self.analysis_results.sort_values('Combined Score').head(20)

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '🏆 Top 20 Undervalued Stocks (Combined Score)',
                '📊 Growth Score vs Valuation Score',
                '💰 PE Ratio Distribution by Sector',
                '📈 Analyst Upside Potential %'
            ),
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "box"}, {"type": "bar"}]
            ]
        )

        # Plot 1: Top Undervalued Stocks
        colors = ['#00ff88' if s < 30 else '#ffff00' if s < 45 else '#ff6644' for s in df['Combined Score']]
        fig.add_trace(
            go.Bar(
                x=df['Company'],
                y=df['Combined Score'],
                marker_color=colors,
                text=df['Combined Score'].round(1),
                textposition='auto',
                name='Combined Score'
            ),
            row=1, col=1
        )

        # Plot 2: Growth vs Valuation Scatter
        for sector in self.analysis_results['Sector'].unique():
            sector_df = self.analysis_results[self.analysis_results['Sector'] == sector]
            fig.add_trace(
                go.Scatter(
                    x=sector_df['Valuation Score'],
                    y=sector_df['Growth Score'],
                    mode='markers+text',
                    text=sector_df['Company'].str[:8],
                    textposition='top center',
                    textfont=dict(size=8),
                    name=sector,
                    marker=dict(size=10),
                    hovertemplate='<b>%{text}</b><br>Valuation: %{x}<br>Growth: %{y}<extra></extra>'
                ),
                row=1, col=2
            )

        # Plot 3: PE Distribution by Sector
        for sector in self.analysis_results['Sector'].unique():
            sector_df = self.analysis_results[self.analysis_results['Sector'] == sector]
            pe_data = sector_df['PE Ratio'].dropna()
            if not pe_data.empty:
                fig.add_trace(
                    go.Box(y=pe_data, name=sector, showlegend=False),
                    row=2, col=1
                )

        # Plot 4: Upside Potential
        upside_df = self.analysis_results.dropna(subset=['Upside %']).sort_values('Upside %', ascending=False).head(15)
        if not upside_df.empty:
            colors2 = ['#00ff88' if u > 20 else '#ffff00' if u > 0 else '#ff4444' for u in upside_df['Upside %']]
            fig.add_trace(
                go.Bar(
                    x=upside_df['Company'],
                    y=upside_df['Upside %'],
                    marker_color=colors2,
                    text=upside_df['Upside %'].round(1),
                    textposition='auto',
                    name='Upside %',
                    showlegend=False
                ),
                row=2, col=2
            )

        fig.update_layout(
            template='plotly_dark',
            height=1000,
            title_text=f'🇮🇳 Indian Market - Undervalued Stock Dashboard ({self.fetch_date})',
            showlegend=True
        )

        fig.write_html('undervalued_dashboard.html')
        # fig.show()
        print("📊 Dashboard saved as 'undervalued_dashboard.html'")
        return fig

    def create_sector_comparison(self):
        """Radar chart comparing sectors"""
        sector_avg = self.analysis_results.groupby('Sector').agg({
            'PE Ratio': 'median',
            'PB Ratio': 'median',
            'ROE %': 'median',
            'Revenue Growth %': 'median',
            'Dividend Yield %': 'median',
            'Combined Score': 'median',
            'Volatility %': 'median'
        }).reset_index()

        fig = go.Figure()

        metrics = ['PE Ratio', 'PB Ratio', 'ROE %', 'Revenue Growth %', 'Dividend Yield %', 'Volatility %']

        for _, row in sector_avg.iterrows():
            values = []
            for metric in metrics:
                val = row[metric]
                if pd.notna(val):
                    # Normalize to 0-100
                    col_min = sector_avg[metric].min()
                    col_max = sector_avg[metric].max()
                    if col_max - col_min > 0:
                        normalized = ((val - col_min) / (col_max - col_min)) * 100
                    else:
                        normalized = 50
                    values.append(normalized)
                else:
                    values.append(0)

            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=metrics + [metrics[0]],
                name=row['Sector'],
                fill='toself',
                opacity=0.6
            ))

        fig.update_layout(
            template='plotly_dark',
            height=700,
            title='🕸️ Sector Comparison Radar Chart (Normalized Metrics)',
            polar=dict(radialaxis=dict(visible=True, range=[0, 100]))
        )

        fig.write_html('sector_radar.html')
        # fig.show()
        print("📊 Sector radar chart saved as 'sector_radar.html'")
        return fig

    def create_price_performance_chart(self, top_n=10):
        """Price performance chart for top picks"""
        top_stocks = self.analysis_results.sort_values('Combined Score').head(top_n)

        fig = go.Figure()

        for _, row in top_stocks.iterrows():
            ticker = row['Ticker']
            if ticker in self.stock_data:
                hist = self.stock_data[ticker]
                # Normalize to 100
                normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100

                fig.add_trace(go.Scatter(
                    x=normalized.index,
                    y=normalized.values,
                    mode='lines',
                    name=f"{row['Company']} (Score: {row['Combined Score']:.0f})",
                    hovertemplate='%{x}<br>%{y:.1f}<extra></extra>'
                ))

        fig.update_layout(
            template='plotly_dark',
            height=600,
            title=f'📈 1-Year Price Performance - Top {top_n} Undervalued Picks (Normalized to 100)',
            xaxis_title='Date',
            yaxis_title='Normalized Price (Base = 100)',
            hovermode='x unified'
        )

        fig.write_html('price_performance.html')
        # fig.show()
        print("📊 Price performance chart saved as 'price_performance.html'")
        return fig

    def create_correlation_heatmap(self):
        """Correlation between key metrics"""
        metrics = ['PE Ratio', 'PB Ratio', 'ROE %', 'Revenue Growth %',
                   'Earnings Growth %', 'Dividend Yield %', 'Debt/Equity',
                   'RSI', 'Volatility %', 'Return 1Y %', 'Combined Score']

        available_metrics = [m for m in metrics if m in self.analysis_results.columns]
        corr_data = self.analysis_results[available_metrics].dropna()

        if corr_data.empty or len(corr_data) < 5:
            print("⚠ Not enough data for correlation heatmap")
            return

        corr_matrix = corr_data.corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdYlGn_r',
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False,
            zmin=-1, zmax=1
        ))

        fig.update_layout(
            template='plotly_dark',
            height=700,
            title='🔗 Correlation Heatmap - Key Financial Metrics',
            xaxis_tickangle=-45
        )

        fig.write_html('correlation_heatmap.html')
        # fig.show()
        print("📊 Correlation heatmap saved as 'correlation_heatmap.html'")
        return fig

    def create_treemap(self):
        """Market cap treemap colored by valuation score"""
        df = self.analysis_results.dropna(subset=['Market Cap (Cr)', 'Combined Score'])

        if df.empty:
            return

        fig = px.treemap(
            df,
            path=['Sector', 'Company'],
            values='Market Cap (Cr)',
            color='Combined Score',
            color_continuous_scale='RdYlGn_r',
            title='🗺️ Market Cap Treemap (Color = Valuation Score, Green = Undervalued)',
            hover_data={
                'PE Ratio': ':.2f',
                'ROE %': ':.2f',
                'Revenue Growth %': ':.2f',
                'Combined Score': ':.1f'
            }
        )

        fig.update_layout(
            template='plotly_dark',
            height=700
        )

        fig.write_html('market_treemap.html')
        # fig.show()
        print("📊 Market treemap saved as 'market_treemap.html'")
        return fig
        fig.write_html('market_treemap.html')
        # fig.show()
        print("📊 Market treemap saved as 'market_treemap.html'")
        return fig

    def create_unified_dashboard(self):
        """Create a premium, unified HTML dashboard incorporating all charts and a real-time screener"""
        print("\n🏆 Creating Premium Unified Dashboard Hub...")
        print("-" * 50)
        
        # 1. Generate/Get all individual Plotly figures
        fig_dashboard = self.create_undervalued_dashboard()
        fig_heatmap = self.create_valuation_heatmap()
        fig_bubble = self.create_sector_bubble_chart()
        fig_radar = self.create_sector_comparison()
        fig_price = self.create_price_performance_chart()
        fig_corr = self.create_correlation_heatmap()
        fig_treemap = self.create_treemap()
        
        # 2. Export to interactive HTML divs (no standalone JS embedded, we link CDN once)
        def get_div(fig, name):
            if fig is None:
                return f"""
                <div style="padding: 4rem 2rem; text-align: center; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 12px; margin: 1rem 0;">
                    <span style="font-size: 3rem; display: block; margin-bottom: 1rem;">⚠️</span>
                    <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; margin-bottom: 0.5rem; color: #fff;">{name} Unavailable</h3>
                    <p style="color: var(--text-secondary); font-size: 0.95rem;">
                        Not enough stock data was successfully fetched to render this visualization.
                    </p>
                </div>
                """
            return fig.to_html(include_plotlyjs=False, full_html=False)

        div_dashboard = get_div(fig_dashboard, "Top Picks Dashboard")
        div_heatmap = get_div(fig_heatmap, "Valuation Heatmap")
        div_bubble = '<div id="plotly-bubble-chart" style="height: 650px; width: 100%;"></div>'
        div_radar = get_div(fig_radar, "Sector Comparison Radar")
        div_price = get_div(fig_price, "Price Performance Chart")
        div_corr = get_div(fig_corr, "Correlation Heatmap")
        div_treemap = get_div(fig_treemap, "Market Treemap")
        
        # 3. Export all data to JSON
        stocks_json = self.analysis_results.to_json(orient='records')
        
        # 4. Construct beautiful unified index.html template
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🇮🇳 Indian Stock Market Screener & Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {
            --bg-base: #0a0d16;
            --bg-surface: #101624;
            --bg-surface-elevated: #161f33;
            --accent-primary: #00e676;
            --accent-primary-hover: #00c853;
            --accent-blue: #00b0ff;
            --accent-purple: #d500f9;
            --accent-yellow: #ffd600;
            --accent-danger: #ff1744;
            --text-primary: #f5f6f8;
            --text-secondary: #8a96a3;
            --border-color: #1f2a40;
            --glass-blur: blur(12px);
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            overflow-x: hidden;
            display: flex;
            min-height: 100vh;
        }
        
        /* SIDEBAR */
        .sidebar {
            width: 280px;
            background: rgba(16, 22, 36, 0.85);
            border-right: 1px solid var(--border-color);
            padding: 2rem 1.5rem;
            display: flex;
            flex-direction: column;
            position: fixed;
            height: 100vh;
            backdrop-filter: var(--glass-blur);
            z-index: 100;
        }
        
        .sidebar-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
        }
        
        .logo-emoji {
            font-size: 2.2rem;
        }
        
        .logo-text h2 {
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 800;
            letter-spacing: 1px;
            background: linear-gradient(135deg, #fff, #8a96a3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .logo-text p {
            font-size: 0.75rem;
            color: var(--accent-primary);
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .sidebar-menu {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            flex-grow: 1;
        }
        
        .menu-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.85rem 1.2rem;
            border-radius: 10px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            transition: all 0.25s ease;
            border-left: 3px solid transparent;
        }
        
        .menu-item:hover {
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.03);
        }
        
        .menu-item.active {
            color: #fff;
            background: rgba(0, 230, 118, 0.08);
            border-left-color: var(--accent-primary);
            font-weight: 600;
        }
        
        .menu-icon {
            font-size: 1.1rem;
        }
        
        .sidebar-footer {
            margin-top: auto;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-color);
            font-size: 0.75rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }
        
        /* MAIN CONTENT */
        .main-content {
            margin-left: 280px;
            padding: 2.5rem;
            width: calc(100% - 280px);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            margin-bottom: 2rem;
        }
        
        .header h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            color: var(--text-secondary);
            font-size: 1rem;
        }
        
        /* STATS GRID */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }
        
        .stats-card {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .stats-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            border-color: rgba(0, 230, 118, 0.2);
        }
        
        .stats-info h3 {
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        
        .stats-info h2 {
            font-family: 'Outfit', sans-serif;
            font-size: 1.7rem;
            font-weight: 700;
        }
        
        .stats-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
        }
        
        .icon-blue { background: rgba(0, 176, 255, 0.1); color: var(--accent-blue); }
        .icon-green { background: rgba(0, 230, 118, 0.1); color: var(--accent-primary); }
        .icon-yellow { background: rgba(255, 214, 0, 0.1); color: var(--accent-yellow); }
        .icon-purple { background: rgba(213, 0, 249, 0.1); color: var(--accent-purple); }
        
        /* CARD */
        .card {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .card-header h2 {
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 600;
        }
        
        /* FILTERS */
        .filter-controls {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .filter-input {
            background-color: var(--bg-surface-elevated);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            padding: 0.6rem 1.2rem;
            font-size: 0.9rem;
            font-family: inherit;
            outline: none;
            transition: all 0.2s;
        }
        
        .filter-input:focus {
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(0, 230, 118, 0.15);
        }
        
        #search-input {
            width: 250px;
        }
        
        /* TABLE */
        .table-container {
            overflow-x: auto;
            border-radius: 10px;
            border: 1px solid var(--border-color);
        }
        
        .screener-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            text-align: left;
        }
        
        .screener-table th {
            background-color: var(--bg-surface-elevated);
            padding: 1.1rem 1rem;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
            user-select: none;
            transition: all 0.2s;
        }
        
        .screener-table th:hover {
            background-color: #1e2a44;
            color: #fff;
        }
        
        .screener-table td {
            padding: 1.1rem 1rem;
            border-bottom: 1px solid var(--border-color);
            font-weight: 500;
        }
        
        .table-row {
            transition: background-color 0.15s ease;
        }
        
        .table-row:hover {
            background-color: rgba(255, 255, 255, 0.02);
        }
        
        .company-cell {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }
        
        .company-name {
            font-weight: 600;
            color: #fff;
        }
        
        .company-ticker {
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        
        .sector-badge {
            background-color: rgba(0, 176, 255, 0.08);
            color: var(--accent-blue);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .num-cell {
            text-align: right;
            font-family: 'Inter', monospace;
        }
        
        .val-good {
            color: var(--accent-primary);
            font-weight: 600;
        }
        
        .val-bad {
            color: var(--accent-danger);
        }
        
        .verdict-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        
        .pill-strong-buy { background-color: rgba(0, 230, 118, 0.1); color: var(--accent-primary); border: 1px solid rgba(0, 230, 118, 0.25); }
        .pill-buy { background-color: rgba(105, 240, 174, 0.1); color: #69f0ae; border: 1px solid rgba(105, 240, 174, 0.2); }
        .pill-hold { background-color: rgba(255, 214, 0, 0.1); color: var(--accent-yellow); border: 1px solid rgba(255, 214, 0, 0.25); }
        .pill-weak { background-color: rgba(255, 145, 0, 0.1); color: #ff9100; border: 1px solid rgba(255, 145, 0, 0.25); }
        .pill-overvalued { background-color: rgba(255, 23, 68, 0.1); color: var(--accent-danger); border: 1px solid rgba(255, 23, 68, 0.25); }
        
        /* TAB SYSTEM */
        .tab-content {
            display: none;
            animation: fadeIn 0.4s ease;
        }
        
        .tab-content.active-content {
            display: block;
        }
        
        .chart-card {
            padding: 1.5rem;
            min-height: 600px;
        }
        
        .charts-grid-2 {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
        }
        
        @media (min-width: 1200px) {
            .charts-grid-2 {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* WACC & DCF Calculator Styles */
        .calculator-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
            align-items: start;
            animation: fadeIn 0.4s ease-out;
        }
        @media (min-width: 992px) {
            .calculator-container {
                grid-template-columns: 1.1fr 0.9fr;
            }
        }
        .calculator-inputs, .calculator-outcomes {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        .calc-card {
            padding: 1.5rem !important;
            min-height: auto !important;
        }
        .calc-section-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.15rem;
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 1.25rem;
            color: #fff;
            display: flex;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            padding-bottom: 0.75rem;
        }
        .title-icon {
            margin-right: 0.5rem;
            font-size: 1.2rem;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        @media (max-width: 576px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
        }
        .form-group {
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .form-group label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 0.4rem;
            font-weight: 500;
        }
        .form-group input, .form-group select {
            width: 100%;
            box-sizing: border-box;
            padding: 0.65rem 0.8rem;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background: var(--bg-surface-elevated);
            color: #fff;
            font-size: 0.95rem;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.15);
        }
        .calc-stock-meta {
            padding: 1rem;
            background: rgba(255,255,255,0.02);
            border: 1px dashed var(--border-color);
            border-radius: 8px;
            margin-top: 1rem;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .meta-row {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        .meta-row strong {
            color: #fff;
            font-size: 1rem;
        }
        .valuation-glow-box {
            text-align: center;
            padding: 2.25rem 1.5rem;
            background: linear-gradient(135deg, rgba(16,22,36,0.9), rgba(22,31,51,0.9));
            border: 2px solid var(--border-color);
            border-radius: 12px;
            margin-bottom: 1.25rem;
            box-shadow: 0 8px 32px rgba(16, 185, 129, 0.04);
            transition: all 0.3s;
        }
        .calc-large-label {
            font-size: 0.8rem;
            letter-spacing: 1.5px;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        .calc-large-value {
            font-size: 2.75rem;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            color: #fff;
            text-shadow: 0 0 20px rgba(255,255,255,0.05);
            margin-bottom: 0.5rem;
        }
        .calc-upside-badge {
            display: inline-block;
            padding: 0.35rem 0.9rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
        }
        .badge-undervalued {
            background: rgba(16, 185, 129, 0.15) !important;
            color: #10b981 !important;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .badge-overvalued {
            background: rgba(239, 68, 68, 0.15) !important;
            color: #ef4444 !important;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .badge-neutral {
            background: rgba(245, 158, 11, 0.15) !important;
            color: #f59e0b !important;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .valuation-meta-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        .val-meta-card {
            padding: 0.85rem;
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            text-align: center;
        }
        .val-meta-label {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-bottom: 0.25rem;
        }
        .val-meta-val {
            font-weight: 600;
            font-size: 1.1rem;
            color: #fff;
        }
        .wacc-breakdown-box {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .wacc-part {
            padding: 0.85rem 1rem;
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }
        .wacc-part-header {
            display: flex;
            justify-content: space-between;
            font-weight: 600;
            color: #fff;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            padding-bottom: 0.4rem;
            margin-bottom: 0.2rem;
            font-size: 0.9rem;
        }
        .wacc-part-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        .wacc-part-row strong {
            color: #fff;
        }
        .calc-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
        }
        .calc-table th, .calc-table td {
            padding: 0.5rem 0.65rem;
            text-align: center;
            border-bottom: 1px solid var(--border-color);
        }
        .calc-table th {
            color: var(--text-secondary);
            font-weight: 500;
            border-bottom: 2px solid var(--border-color);
        }
        .calc-table td {
            color: #fff;
        }
        .calc-terminal-tv-box {
            padding: 0.85rem 1rem;
            background: rgba(255,255,255,0.02);
            border-top: 1px solid var(--border-color);
            border-radius: 0 0 8px 8px;
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
            box-sizing: border-box;
        }
        .calc-terminal-tv-box strong {
            color: #fff;
            font-size: 0.95rem;
        }
    </style>
</head>
<body>

    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="sidebar-header">
            <span class="logo-emoji">🇮🇳</span>
            <div class="logo-text">
                <h2>IND-VECTORS</h2>
                <p>Stock Screener Hub</p>
            </div>
        </div>
        <div class="sidebar-menu">
            <a href="#" class="menu-item active" onclick="switchTab(event, 'tab-screener')">
                <span class="menu-icon">📋</span> Screener Table
            </a>
            <a href="#" class="menu-item" onclick="switchTab(event, 'tab-subplots')">
                <span class="menu-icon">🏆</span> Unified Dashboard
            </a>
            <a href="#" class="menu-item" onclick="switchTab(event, 'tab-heatmaps')">
                <span class="menu-icon">🕸️</span> Radar & Heatmaps
            </a>
            <a href="#" class="menu-item" onclick="switchTab(event, 'tab-treemap')">
                <span class="menu-icon">🗺️</span> Market Cap Treemap
            </a>
            <a href="#" class="menu-item" onclick="switchTab(event, 'tab-bubble')">
                <span class="menu-icon">💹</span> Sector Bubble Chart
            </a>
            <a href="#" class="menu-item" onclick="switchTab(event, 'tab-price')">
                <span class="menu-icon">📈</span> Price Performance
            </a>
            <a href="#" class="menu-item" onclick="switchTab(event, 'tab-correlation')">
                <span class="menu-icon">🔗</span> Correlation Matrix
            </a>
            <a href="#" class="menu-item" onclick="switchTab(event, 'tab-calculator')">
                <span class="menu-icon">🧮</span> WACC & DCF Calculator
            </a>
        </div>
        <div class="sidebar-footer">
            <p>Analysis Date: {{FETCH_DATE}}</p>
            <p>Data: Yahoo Finance</p>
            <p>SEBI-Registered DYOR</p>
        </div>
    </div>
    
    <!-- MAIN CONTENT -->
    <div class="main-content">
        <div class="header">
            <h1>🇮🇳 Indian Stock Market Analysis Screener</h1>
            <p>Premium dark-themed valuation & growth multi-factor analysis dashboard</p>
        </div>
        
        <!-- STATS CARDS -->
        <div class="stats-grid">
            <div class="stats-card">
                <div class="stats-info">
                    <h3>Total Stocks</h3>
                    <h2 id="stat-total-stocks">-</h2>
                </div>
                <div class="stats-icon icon-blue">📊</div>
            </div>
            <div class="stats-card">
                <div class="stats-info">
                    <h3>Strong Buys</h3>
                    <h2 id="stat-strong-buys">-</h2>
                </div>
                <div class="stats-icon icon-green">🟢</div>
            </div>
            <div class="stats-card">
                <div class="stats-info">
                    <h3>Median P/E</h3>
                    <h2 id="stat-median-pe">-</h2>
                </div>
                <div class="stats-icon icon-yellow">💰</div>
            </div>
            <div class="stats-card">
                <div class="stats-info">
                    <h3>Top Upside Pick</h3>
                    <h2 id="stat-top-upside">-</h2>
                </div>
                <div class="stats-icon icon-purple">🚀</div>
            </div>
        </div>
        
        <!-- TAB CONTENT: SCREENER -->
        <div id="tab-screener" class="tab-content active-content">
            <div class="card">
                <div class="card-header">
                    <h2>🎯 Real-Time Stock Screener</h2>
                    <div class="filter-controls">
                        <input type="text" id="search-input" class="filter-input" placeholder="Search Company or Ticker..." oninput="handleSearch(this.value)">
                        <select id="sector-select" class="filter-input" onchange="handleSectorFilter(this.value)">
                            <option value="">All Sectors</option>
                            <option value="Banking">Banking</option>
                            <option value="IT">IT</option>
                            <option value="Pharma">Pharma</option>
                            <option value="Auto">Auto</option>
                            <option value="FMCG">FMCG</option>
                            <option value="Energy">Energy</option>
                            <option value="Metals & Mining">Metals & Mining</option>
                            <option value="Real Estate">Real Estate</option>
                            <option value="DEFENCE">Defence</option>
                        </select>
                        <select id="rating-select" class="filter-input" onchange="handleRatingFilter(this.value)">
                            <option value="">All Ratings</option>
                            <option value="STRONG BUY">Strong Buy</option>
                            <option value="BUY">Buy</option>
                            <option value="HOLD">Hold</option>
                            <option value="WEAK">Weak</option>
                            <option value="OVERVALUED">Overvalued</option>
                        </select>
                    </div>
                </div>
                <div class="table-container">
                    <table class="screener-table">
                        <thead>
                            <tr>
                                <th onclick="handleSort('Company')">Company ↕</th>
                                <th onclick="handleSort('Sector')">Sector ↕</th>
                                <th onclick="handleSort('Current Price')" class="num-cell">Price ↕</th>
                                <th onclick="handleSort('PE Ratio')" class="num-cell">P/E ↕</th>
                                <th onclick="handleSort('PB Ratio')" class="num-cell">P/B ↕</th>
                                <th onclick="handleSort('Dividend Yield %')" class="num-cell">Div Yield ↕</th>
                                <th onclick="handleSort('ROE %')" class="num-cell">ROE % ↕</th>
                                <th onclick="handleSort('Revenue Growth %')" class="num-cell">Growth % ↕</th>
                                <th onclick="handleSort('Combined Score')" class="num-cell">Score ↕</th>
                                <th onclick="handleSort('Upside %')" class="num-cell">Upside % ↕</th>
                                <th>Verdict</th>
                            </tr>
                        </thead>
                        <tbody id="screener-tbody">
                            <!-- Filled by JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- OTHER TABS -->
        <div id="tab-subplots" class="tab-content">
            <div class="card chart-card">
                {{DIV_DASHBOARD}}
            </div>
        </div>
        
        <div id="tab-heatmaps" class="tab-content">
            <div class="charts-grid-2">
                <div class="card chart-card">
                    {{DIV_HEATMAP}}
                </div>
                <div class="card chart-card">
                    {{DIV_RADAR}}
                </div>
            </div>
        </div>
        
        <div id="tab-treemap" class="tab-content">
            <div class="card chart-card">
                {{DIV_TREEMAP}}
            </div>
        </div>
        
        <div id="tab-bubble" class="tab-content">
            <div class="card chart-card">
                {{DIV_BUBBLE}}
            </div>
        </div>
        
        <div id="tab-price" class="tab-content">
            <div class="card chart-card">
                {{DIV_PRICE}}
            </div>
        </div>
        
        <div id="tab-correlation" class="tab-content">
            <div class="card chart-card">
                {{DIV_CORR}}
            </div>
        </div>
        
        <div id="tab-calculator" class="tab-content">
            <div class="calculator-container">
                <!-- Inputs Section (Left Column) -->
                <div class="calculator-inputs">
                    <!-- Dropdown Select Stock Card -->
                    <div class="card calc-card">
                        <h3 class="calc-section-title"><span class="title-icon">🔍</span> 1. Select Valuation Target</h3>
                        <div class="form-group">
                            <label for="calc-stock-input">Enter Stock Ticker Manually (e.g., RELIANCE.NS):</label>
                            <input type="text" id="calc-stock-input" placeholder="e.g. TCS.NS" onchange="handleCalcStockSelect(this.value)">
                        </div>
                        <div class="calc-stock-meta" id="calc-stock-meta-box">
                            <div class="meta-row"><span>Sector:</span> <strong id="calc-meta-sector">-</strong></div>
                            <div class="meta-row"><span>Current Price:</span> <strong id="calc-meta-price">-</strong></div>
                            <div class="meta-row"><span>Market Cap:</span> <strong id="calc-meta-mcap">-</strong></div>
                        </div>
                    </div>

                    <!-- WACC assumptions -->
                    <div class="card calc-card">
                        <h3 class="calc-section-title"><span class="title-icon">⚖️</span> 2. Capital Structure & Cost of Capital</h3>
                        <div class="form-grid">
                            <!-- CAPM Cost of Equity Inputs -->
                            <div class="form-group">
                                <label for="calc-rf">Risk-Free Rate (Rf %):</label>
                                <input type="number" id="calc-rf" value="7.0" step="0.1" oninput="handleCalcInputChange()">
                            </div>
                            <div class="form-group">
                                <label for="calc-mrp">Market Risk Premium (MRP %):</label>
                                <input type="number" id="calc-mrp" value="8.0" step="0.1" oninput="handleCalcInputChange()">
                            </div>
                            <div class="form-group">
                                <label for="calc-beta">Stock Beta (β):</label>
                                <input type="number" id="calc-beta" value="1.00" step="0.05" oninput="handleCalcInputChange()">
                            </div>
                            <!-- Cost of Debt Inputs -->
                            <div class="form-group">
                                <label for="calc-pretax-debt">Pre-tax Cost of Debt (%):</label>
                                <input type="number" id="calc-pretax-debt" value="9.0" step="0.1" oninput="handleCalcInputChange()">
                            </div>
                            <div class="form-group">
                                <label for="calc-tax-rate">Corporate Tax Rate (%):</label>
                                <input type="number" id="calc-tax-rate" value="25.0" step="0.5" oninput="handleCalcInputChange()">
                            </div>
                            <!-- Debt-to-Equity Ratio -->
                            <div class="form-group">
                                <label for="calc-de-ratio">Debt / Equity Ratio:</label>
                                <input type="number" id="calc-de-ratio" value="0.20" step="0.05" oninput="handleCalcInputChange()">
                            </div>
                        </div>
                    </div>

                    <!-- DCF projections -->
                    <div class="card calc-card">
                        <h3 class="calc-section-title"><span class="title-icon">💸</span> 3. Discounted Cash Flow Growth Assumptions</h3>
                        <div class="form-group">
                            <label for="calc-base-fcf">Base Free Cash Flow (FCF₀, ₹ Cr):</label>
                            <input type="number" id="calc-base-fcf" value="500" step="10" oninput="handleCalcInputChange()">
                        </div>
                        <div class="form-grid">
                            <div class="form-group">
                                <label for="calc-stage1-growth">Stage 1 Growth (Yr 1-5 %):</label>
                                <input type="number" id="calc-stage1-growth" value="12.0" step="0.5" oninput="handleCalcInputChange()">
                            </div>
                            <div class="form-group">
                                <label for="calc-stage2-growth">Stage 2 Growth (Yr 6-10 %):</label>
                                <input type="number" id="calc-stage2-growth" value="8.0" step="0.5" oninput="handleCalcInputChange()">
                            </div>
                            <div class="form-group">
                                <label for="calc-terminal-growth">Terminal Growth Rate (%):</label>
                                <input type="number" id="calc-terminal-growth" value="5.0" step="0.1" oninput="handleCalcInputChange()">
                            </div>
                        </div>
                    </div>
                    
                    <div class="calc-action-row" style="margin-top: 1rem;">
                        <button class="btn btn-primary" style="width: 100%; padding: 1rem; font-size: 1.1rem; font-weight: bold; background: var(--accent-primary); border-radius: 8px; border: none; cursor: pointer;" onclick="fetchValuation()">🚀 Calculate Valuation (Runtime Fetch)</button>
                    </div>
                </div>

                <!-- Outcomes Section (Right Column) -->
                <div class="calculator-outcomes">
                    <!-- Valuation summary -->
                    <div class="card calc-card outcome-card">
                        <h3 class="calc-section-title"><span class="title-icon">💎</span> Intrinsic Valuation Outcome</h3>
                        <div class="valuation-glow-box">
                            <div class="calc-large-label">INTRINSIC VALUE PER SHARE</div>
                            <div class="calc-large-value" id="calc-intrinsic-value">₹-</div>
                            <div class="calc-upside-badge" id="calc-upside-badge">-</div>
                        </div>
                        <div class="valuation-meta-grid">
                            <div class="val-meta-card">
                                <div class="val-meta-label">Current Share Price</div>
                                <div class="val-meta-val" id="calc-outcome-price">₹-</div>
                            </div>
                            <div class="val-meta-card">
                                <div class="val-meta-label">Calculated WACC</div>
                                <div class="val-meta-val" id="calc-outcome-wacc">-%</div>
                            </div>
                        </div>
                    </div>

                    <!-- Cost of Capital Detail Card -->
                    <div class="card calc-card">
                        <h3 class="calc-section-title"><span class="title-icon">📊</span> Cost of Capital & Weights</h3>
                        <div class="wacc-breakdown-box">
                            <div class="wacc-part">
                                <div class="wacc-part-header">
                                    <span>Equity Component</span>
                                    <strong id="calc-eq-weight">-%</strong>
                                </div>
                                <div class="wacc-part-row">Cost of Equity (Ke): <strong id="calc-eq-cost">-%</strong></div>
                                <div class="wacc-part-row">Market Cap Value: <strong id="calc-eq-val">₹- Cr</strong></div>
                            </div>
                            <div class="wacc-part">
                                <div class="wacc-part-header">
                                    <span>Debt Component</span>
                                    <strong id="calc-debt-weight">-%</strong>
                                </div>
                                <div class="wacc-part-row">After-tax Cost of Debt: <strong id="calc-debt-cost">-%</strong></div>
                                <div class="wacc-part-row">Implied Debt Value: <strong id="calc-debt-val">₹- Cr</strong></div>
                            </div>
                        </div>
                    </div>

                    <!-- 10-year projection table -->
                    <div class="card calc-card">
                        <h3 class="calc-section-title"><span class="title-icon">📅</span> Projected Free Cash Flows (10 Years)</h3>
                        <div class="table-container">
                            <table class="calc-table">
                                <thead>
                                    <tr>
                                        <th>Year</th>
                                        <th>Expected FCF</th>
                                        <th>Growth</th>
                                        <th>Discount Fctr</th>
                                        <th>PV of FCF</th>
                                    </tr>
                                </thead>
                                <tbody id="calc-tbody">
                                    <!-- Populated in JS -->
                                </tbody>
                            </table>
                        </div>
                        <div class="calc-terminal-tv-box">
                            <span>Present Value of Terminal Value (Year 10+):</span>
                            <strong id="calc-pv-tv">₹- Cr</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- JAVASCRIPT SCREENER ENGINE -->
    <script>
        const STOCKS_DATA = {{STOCKS_JSON}};
        
        let currentSortColumn = 'Combined Score';
        let currentSortDirection = 'asc';
        let activeFilters = {
            search: '',
            sector: '',
            rating: ''
        };
        
        let lastFilteredData = [];
        
        function getRating(score) {
            if (score === null || score === undefined) return 'N/A';
            if (score < 30) return 'STRONG BUY';
            if (score < 40) return 'BUY';
            if (score < 50) return 'HOLD';
            if (score < 60) return 'WEAK';
            return 'OVERVALUED';
        }
        
        function getRatingClass(score) {
            if (score === null || score === undefined) return '';
            if (score < 30) return 'pill-strong-buy';
            if (score < 40) return 'pill-buy';
            if (score < 50) return 'pill-hold';
            if (score < 60) return 'pill-weak';
            return 'pill-overvalued';
        }
        
        function switchTab(event, tabId) {
            event.preventDefault();
            
            // Remove active classes
            document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active-content'));
            
            // Add active class to clicked menu item and matching tab
            event.currentTarget.classList.add('active');
            document.getElementById(tabId).classList.add('active-content');
            
            // Trigger responsive resize for plotly charts inside tabs
            window.dispatchEvent(new Event('resize'));
            
            if (tabId === 'tab-bubble') {
                setTimeout(() => {
                    renderBubbleChart(lastFilteredData);
                }, 50);
            }
        }
        
        function populateStats() {
            document.getElementById('stat-total-stocks').innerText = STOCKS_DATA.length;
            
            const strongBuys = STOCKS_DATA.filter(s => s['Combined Score'] < 30).length;
            document.getElementById('stat-strong-buys').innerText = strongBuys;
            
            const peList = STOCKS_DATA.map(s => s['PE Ratio']).filter(v => v !== null && v > 0).sort((a,b) => a-b);
            if (peList.length > 0) {
                const mid = Math.floor(peList.length / 2);
                const medianPE = peList.length % 2 !== 0 ? peList[mid] : (peList[mid - 1] + peList[mid]) / 2;
                document.getElementById('stat-median-pe').innerText = medianPE.toFixed(1);
            }
            
            let topUpsideStock = null;
            let maxUpside = -Infinity;
            STOCKS_DATA.forEach(s => {
                if (s['Upside %'] !== null && s['Upside %'] > maxUpside) {
                    maxUpside = s['Upside %'];
                    topUpsideStock = s;
                }
            });
            if (topUpsideStock) {
                document.getElementById('stat-top-upside').innerHTML = 
                    `<span style="color:#fff;">${topUpsideStock.Company}</span> <span style="color:var(--accent-primary); font-size:1rem;">(+${maxUpside.toFixed(0)}%)</span>`;
            }
        }
        
        function handleSearch(val) {
            activeFilters.search = val;
            renderTable();
        }
        
        function handleSectorFilter(val) {
            activeFilters.sector = val;
            renderTable();
        }
        
        function handleRatingFilter(val) {
            activeFilters.rating = val;
            renderTable();
        }
        
        function handleSort(col) {
            if (currentSortColumn === col) {
                currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortColumn = col;
                currentSortDirection = 'asc';
            }
            renderTable();
        }
        
        function renderTable() {
            const tbody = document.getElementById('screener-tbody');
            tbody.innerHTML = '';
            
            let filtered = STOCKS_DATA.filter(stock => {
                // Search match
                const compName = stock.Company ? stock.Company.toLowerCase() : '';
                const compTicker = stock.Ticker ? stock.Ticker.toLowerCase() : '';
                const searchLower = activeFilters.search.toLowerCase();
                const searchMatch = activeFilters.search === '' || compName.includes(searchLower) || compTicker.includes(searchLower);
                
                // Sector match
                const sectorMatch = activeFilters.sector === '' || stock.Sector === activeFilters.sector;
                
                // Rating match
                const rating = getRating(stock['Combined Score']);
                const ratingMatch = activeFilters.rating === '' || rating === activeFilters.rating;
                
                return searchMatch && sectorMatch && ratingMatch;
            });
            
            // Sorting
            filtered.sort((a, b) => {
                let valA = a[currentSortColumn];
                let valB = b[currentSortColumn];
                
                if (valA === null || valA === undefined) return 1;
                if (valB === null || valB === undefined) return -1;
                
                if (typeof valA === 'string') {
                    return currentSortDirection === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
                } else {
                    return currentSortDirection === 'asc' ? valA - valB : valB - valA;
                }
            });
            
            lastFilteredData = filtered;
            renderBubbleChart(filtered);
            
            // Rendering rows
            filtered.forEach(stock => {
                const tr = document.createElement('tr');
                tr.className = 'table-row';
                
                const price = stock['Current Price'] !== null ? '₹' + stock['Current Price'].toLocaleString('en-IN', {maximumFractionDigits: 2}) : 'N/A';
                const pe = stock['PE Ratio'] !== null ? stock['PE Ratio'].toFixed(2) : 'N/A';
                const pb = stock['PB Ratio'] !== null ? stock['PB Ratio'].toFixed(2) : 'N/A';
                const divYield = stock['Dividend Yield %'] !== null ? stock['Dividend Yield %'].toFixed(2) + '%' : '0.00%';
                const roe = stock['ROE %'] !== null ? stock['ROE %'].toFixed(1) + '%' : 'N/A';
                const growth = stock['Revenue Growth %'] !== null ? stock['Revenue Growth %'].toFixed(1) + '%' : 'N/A';
                const score = stock['Combined Score'] !== null ? stock['Combined Score'].toFixed(1) : 'N/A';
                const upside = stock['Upside %'] !== null ? (stock['Upside %'] >= 0 ? '+' : '') + stock['Upside %'].toFixed(1) + '%' : 'N/A';
                
                const scoreClass = stock['Combined Score'] < 40 ? 'val-good' : (stock['Combined Score'] >= 60 ? 'val-bad' : '');
                const upsideClass = stock['Upside %'] > 20 ? 'val-good' : (stock['Upside %'] < 0 ? 'val-bad' : '');
                
                const ratingClass = getRatingClass(stock['Combined Score']);
                const ratingText = getRating(stock['Combined Score']);
                
                tr.innerHTML = `
                    <td>
                        <div class="company-cell">
                            <span class="company-name">${stock.Company}</span>
                            <span class="company-ticker" style="cursor: pointer; color: var(--accent-primary); text-decoration: underline;" onclick="goToCalculator('${stock.Ticker}')" title="Click to analyze WACC & DCF">${stock.Ticker}</span>
                        </div>
                    </td>
                    <td><span class="sector-badge">${stock.Sector}</span></td>
                    <td class="num-cell">${price}</td>
                    <td class="num-cell">${pe}</td>
                    <td class="num-cell">${pb}</td>
                    <td class="num-cell">${divYield}</td>
                    <td class="num-cell">${roe}</td>
                    <td class="num-cell">${growth}</td>
                    <td class="num-cell ${scoreClass}">${score}</td>
                    <td class="num-cell ${upsideClass}">${upside}</td>
                    <td><span class="verdict-pill ${ratingClass}">${ratingText}</span></td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        function renderBubbleChart(filteredData) {
            const chartDiv = document.getElementById('plotly-bubble-chart');
            if (!chartDiv) return;
            
            // 1. Keep only stocks with valid PE, Growth, and Market Cap
            const validData = filteredData.filter(s => 
                s['PE Ratio'] !== null && s['PE Ratio'] !== undefined &&
                s['Revenue Growth %'] !== null && s['Revenue Growth %'] !== undefined &&
                s['Market Cap (Cr)'] !== null && s['Market Cap (Cr)'] !== undefined
            );
            
            if (validData.length === 0) {
                chartDiv.innerHTML = `
                    <div style="padding: 4rem 2rem; text-align: center; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 12px; margin: 1rem 0;">
                        <span style="font-size: 3rem; display: block; margin-bottom: 1rem;">⚠️</span>
                        <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; margin-bottom: 0.5rem; color: #fff;">No Data for Bubble Chart</h3>
                        <p style="color: var(--text-secondary); font-size: 0.95rem;">
                            No stocks matching the current filters have valid P/E, Revenue Growth, and Market Cap data.
                        </p>
                    </div>
                `;
                return;
            }
            
            // 2. Group by sector for legend color-coding and toggles
            const sectors = {};
            validData.forEach(stock => {
                const sec = stock.Sector || 'Others';
                if (!sectors[sec]) {
                    sectors[sec] = [];
                }
                sectors[sec].push(stock);
            });
            
            // 3. Define color scheme matching Python's premium palette
            const sectorColors = {
                'Banking': '#636efa',
                'IT': '#EF553B',
                'Pharma': '#00cc96',
                'Auto': '#ab63fa',
                'FMCG': '#FFA15A',
                'Energy': '#19d3f3',
                'Metals & Mining': '#FF6692',
                'Real Estate': '#B6E880',
                'DEFENCE': '#FF97FF',
                'Others': '#FECB52'
            };
            
            // 4. Calculate dynamic size ref from global data so bubble sizes remain consistent when filtering
            const globalCaps = STOCKS_DATA.map(s => s['Market Cap (Cr)']).filter(v => v !== null && v !== undefined);
            const maxGlobalMarketCap = globalCaps.length > 0 ? Math.max(...globalCaps) : 1000000;
            // standard Plotly formula for area sizing: sizeref = 2.0 * maxVal / (maxSize ** 2)
            const sizeref = (2.0 * maxGlobalMarketCap) / (45 ** 2);
            
            // 5. Build data traces
            const traces = [];
            Object.keys(sectors).forEach(sec => {
                const stocks = sectors[sec];
                
                traces.push({
                    x: stocks.map(s => s['PE Ratio']),
                    y: stocks.map(s => s['Revenue Growth %']),
                    mode: 'markers',
                    name: sec,
                    hovertext: stocks.map(s => s.Company),
                    customdata: stocks.map(s => [
                        s.Sector,
                        s['Market Cap (Cr)'],
                        s['ROE %'],
                        s['Combined Score'],
                        s.Ticker
                    ]),
                    hovertemplate: 
                        '<b>%{hovertext}</b> (%{customdata[4]})<br>' +
                        'Sector: %{customdata[0]}<br>' +
                        'PE Ratio: %{x:.2f}<br>' +
                        'Revenue Growth: %{y:.1f}%<br>' +
                        'Market Cap: ₹%{customdata[1]:,.0f} Cr<br>' +
                        'ROE: %{customdata[2]:.1f}%<br>' +
                        'Combined Score: %{customdata[3]:.1f}<extra></extra>',
                    marker: {
                        size: stocks.map(s => s['Market Cap (Cr)']),
                        sizemode: 'area',
                        sizeref: sizeref,
                        sizemin: 6,
                        color: sectorColors[sec] || '#ffffff',
                        opacity: 0.85,
                        line: {
                            color: '#101624',
                            width: 1
                        }
                    }
                });
            });
            
            // 6. Compute overall market medians from global STOCKS_DATA for visual grids
            const allPEs = STOCKS_DATA.map(s => s['PE Ratio']).filter(v => v !== null && v > 0).sort((a,b) => a-b);
            const allGrowths = STOCKS_DATA.map(s => s['Revenue Growth %']).filter(v => v !== null).sort((a,b) => a-b);
            
            let medianPE = 28.25;
            if (allPEs.length > 0) {
                const mid = Math.floor(allPEs.length / 2);
                medianPE = allPEs.length % 2 !== 0 ? allPEs[mid] : (allPEs[mid - 1] + allPEs[mid]) / 2;
            }
            let medianGrowth = 12.3;
            if (allGrowths.length > 0) {
                const mid = Math.floor(allGrowths.length / 2);
                medianGrowth = allGrowths.length % 2 !== 0 ? allGrowths[mid] : (allGrowths[mid - 1] + allGrowths[mid]) / 2;
            }
            
            // 7. Setup layout, grids, capped viewports, reference lines, and quadrant labels
            const layout = {
                template: 'plotly_dark',
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: '#101624',
                title: {
                    text: '💹 PE Ratio vs Revenue Growth (Bubble Size = Market Cap)',
                    font: { family: 'Outfit, sans-serif', size: 18, color: '#fff' }
                },
                xaxis: {
                    title: { text: 'PE Ratio (Lower = Cheaper)', font: { family: 'Inter, sans-serif', size: 12, color: '#a0aec0' } },
                    range: [0, 80],
                    gridcolor: '#1f2937',
                    zerolinecolor: '#374151',
                    tickfont: { color: '#a0aec0' }
                },
                yaxis: {
                    title: { text: 'Revenue Growth % (Higher = Better)', font: { family: 'Inter, sans-serif', size: 12, color: '#a0aec0' } },
                    range: [-20, 80],
                    gridcolor: '#1f2937',
                    zerolinecolor: '#374151',
                    tickfont: { color: '#a0aec0' }
                },
                margin: { l: 60, r: 40, t: 80, b: 60 },
                hovermode: 'closest',
                legend: {
                    title: { text: 'Sector', font: { color: '#fff' } },
                    font: { color: '#a0aec0' },
                    bgcolor: 'rgba(16, 22, 36, 0.8)',
                    bordercolor: '#1f2937',
                    borderwidth: 1
                },
                shapes: [
                    // Horizontal Median Line
                    {
                        type: 'line',
                        x0: 0,
                        x1: 1,
                        xref: 'paper',
                        y0: medianGrowth,
                        y1: medianGrowth,
                        yref: 'y',
                        line: { color: '#ffffff', width: 1, dash: 'dash' },
                        opacity: 0.4
                    },
                    // Vertical Median Line
                    {
                        type: 'line',
                        x0: medianPE,
                        x1: medianPE,
                        xref: 'x',
                        y0: 0,
                        y1: 1,
                        yref: 'paper',
                        line: { color: '#ffffff', width: 1, dash: 'dash' },
                        opacity: 0.4
                    }
                ],
                annotations: [
                    {
                        x: medianPE / 2,
                        y: medianGrowth + (80 - medianGrowth) / 2,
                        text: '⭐ UNDERVALUED<br>HIGH GROWTH',
                        showarrow: false,
                        font: { color: '#10b981', size: 11, weight: 'bold', family: 'Outfit, sans-serif' }
                    },
                    {
                        x: medianPE + (80 - medianPE) / 2,
                        y: medianGrowth + (80 - medianGrowth) / 2,
                        text: '💰 EXPENSIVE<br>HIGH GROWTH',
                        showarrow: false,
                        font: { color: '#f59e0b', size: 11, weight: 'bold', family: 'Outfit, sans-serif' }
                    },
                    {
                        x: medianPE / 2,
                        y: medianGrowth - (medianGrowth + 20) / 2,
                        text: '🔍 CHEAP<br>LOW GROWTH',
                        showarrow: false,
                        font: { color: '#f97316', size: 11, weight: 'bold', family: 'Outfit, sans-serif' }
                    }
                ]
            };
            
            Plotly.newPlot('plotly-bubble-chart', traces, layout, { responsive: true });
        }
        
        function initCalculator() {
            // Dropdown is removed, so nothing to init here.
        }
        
        let currentCalcStockData = null;
        let currentCalcTicker = null;
        
        function handleCalcStockSelect(ticker) {
            ticker = ticker.trim().toUpperCase();
            if (!ticker) {
                currentCalcStockData = null;
                currentCalcTicker = null;
                document.getElementById('calc-meta-sector').innerText = '-';
                document.getElementById('calc-meta-price').innerText = '-';
                document.getElementById('calc-meta-mcap').innerText = '-';
                return;
            }
            
            currentCalcTicker = ticker;
            const stock = STOCKS_DATA.find(s => s.Ticker === ticker);
            if (stock) {
                currentCalcStockData = stock;
                document.getElementById('calc-meta-sector').innerText = stock.Sector || 'N/A';
                document.getElementById('calc-meta-price').innerText = stock['Current Price'] ? '₹' + stock['Current Price'].toLocaleString() : 'N/A';
                document.getElementById('calc-meta-mcap').innerText = stock['Market Cap (Cr)'] ? '₹' + stock['Market Cap (Cr)'].toLocaleString() + ' Cr' : 'N/A';
                
                if (stock['Beta']) document.getElementById('calc-beta').value = stock['Beta'].toFixed(2);
                if (stock['Debt/Equity']) document.getElementById('calc-de-ratio').value = (stock['Debt/Equity'] / 100 > 10 ? stock['Debt/Equity'] / 100 : stock['Debt/Equity']).toFixed(2);
                
                let baseFCF = 500;
                if (stock['Market Cap (Cr)']) {
                    if (stock['PE Ratio'] && stock['PE Ratio'] > 0) {
                        baseFCF = (stock['Market Cap (Cr)'] / stock['PE Ratio']) * 0.85;
                    } else {
                        baseFCF = stock['Market Cap (Cr)'] * 0.05;
                    }
                }
                document.getElementById('calc-base-fcf').value = baseFCF.toFixed(0);
            } else {
                currentCalcStockData = null;
                // Leave fields alone or show a loading state, backend will fetch data
                document.getElementById('calc-meta-sector').innerText = "Fetching from Server...";
                document.getElementById('calc-meta-price').innerText = "Fetching from Server...";
                document.getElementById('calc-meta-mcap').innerText = "Fetching from Server...";
            }
        }
        
        async function fetchValuation() {
            if (!currentCalcTicker) {
                const manualTicker = document.getElementById('calc-stock-input').value.trim();
                if (manualTicker) {
                    handleCalcStockSelect(manualTicker);
                } else {
                    alert("Please enter a stock ticker first!");
                    return;
                }
            }
            
            const params = {
                risk_free_rate: parseFloat(document.getElementById('calc-rf').value) / 100,
                market_risk_premium: parseFloat(document.getElementById('calc-mrp').value) / 100,
                pre_tax_debt_cost: parseFloat(document.getElementById('calc-pretax-debt').value) / 100,
                tax_rate: parseFloat(document.getElementById('calc-tax-rate').value) / 100,
                stage_1_growth: parseFloat(document.getElementById('calc-stage1-growth').value) / 100,
                stage_2_growth: parseFloat(document.getElementById('calc-stage2-growth').value) / 100,
                terminal_growth: parseFloat(document.getElementById('calc-terminal-growth').value) / 100
            };
            
            document.getElementById('calc-intrinsic-value').innerText = "Loading...";
            
            try {
                const response = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ticker: currentCalcTicker,
                        stock_data: currentCalcStockData,
                        params: params
                    })
                });
                
                if (!response.ok) throw new Error("API Request failed");
                const res = await response.json();
                if (res.error) throw new Error(res.error);
                
                updateOutcomes(res);
                
                // Update meta if it was fetched from backend
                if (!currentCalcStockData && res.stock_data) {
                    document.getElementById('calc-meta-sector').innerText = res.stock_data.Sector || 'N/A';
                    document.getElementById('calc-meta-price').innerText = res.stock_data['Current Price'] ? '₹' + res.stock_data['Current Price'].toLocaleString() : 'N/A';
                    document.getElementById('calc-meta-mcap').innerText = res.stock_data['Market Cap (Cr)'] ? '₹' + res.stock_data['Market Cap (Cr)'].toLocaleString() + ' Cr' : 'N/A';
                    
                    if (res.stock_data['Beta']) document.getElementById('calc-beta').value = res.stock_data['Beta'].toFixed(2);
                    if (res.stock_data['Debt/Equity']) document.getElementById('calc-de-ratio').value = res.stock_data['Debt/Equity'].toFixed(2);
                }
                
            } catch (err) {
                console.error(err);
                alert("Error fetching calculation: " + err.message);
                document.getElementById('calc-intrinsic-value').innerText = "Error";
            }
        }
        
        function updateOutcomes(res) {
            const iv = res.outcome.intrinsic_price;
            document.getElementById('calc-intrinsic-value').innerText = '₹' + iv.toLocaleString('en-IN', {maximumFractionDigits: 2});
            
            const badge = document.getElementById('calc-upside-badge');
            const up = res.outcome.upside_pct;
            badge.innerText = (up >= 0 ? '+' : '') + up.toFixed(2) + '%';
            if (up >= 20) {
                badge.style.background = 'rgba(16, 185, 129, 0.2)';
                badge.style.color = '#10b981';
            } else if (up < 0) {
                badge.style.background = 'rgba(239, 68, 68, 0.2)';
                badge.style.color = '#ef4444';
            } else {
                badge.style.background = 'rgba(245, 158, 11, 0.2)';
                badge.style.color = '#f59e0b';
            }
            
            document.getElementById('calc-outcome-price').innerText = '₹' + res.outcome.current_price.toLocaleString();
            document.getElementById('calc-outcome-wacc').innerText = res.wacc_details.wacc.toFixed(2) + '%';
            
            document.getElementById('calc-eq-weight').innerText = res.wacc_details.weight_equity.toFixed(1) + '%';
            document.getElementById('calc-eq-cost').innerText = res.wacc_details.cost_of_equity.toFixed(2) + '%';
            document.getElementById('calc-eq-val').innerText = '₹' + res.dcf_details.equity_value.toLocaleString('en-IN', {maximumFractionDigits: 0}) + ' Cr';
            
            document.getElementById('calc-debt-weight').innerText = res.wacc_details.weight_debt.toFixed(1) + '%';
            document.getElementById('calc-debt-cost').innerText = res.wacc_details.cost_of_debt_after_tax.toFixed(2) + '%';
            document.getElementById('calc-debt-val').innerText = '₹' + res.dcf_details.debt_value.toLocaleString('en-IN', {maximumFractionDigits: 0}) + ' Cr';
            
            document.getElementById('calc-pv-tv').innerText = '₹' + res.dcf_details.pv_terminal_value.toLocaleString('en-IN', {maximumFractionDigits: 0}) + ' Cr';
            
            const tbody = document.getElementById('calc-tbody');
            tbody.innerHTML = '';
            res.projections.forEach((p, idx) => {
                const tr = document.createElement('tr');
                let growth = '-';
                if (idx > 0) {
                    const prevFcf = res.projections[idx-1].fcf;
                    growth = (((p.fcf / prevFcf) - 1) * 100).toFixed(1) + '%';
                }
                tr.innerHTML = `
                    <td>Year ${p.year}</td>
                    <td>₹${p.fcf.toLocaleString('en-IN', {maximumFractionDigits: 0})}</td>
                    <td style="color:var(--text-secondary)">${growth}</td>
                    <td style="color:var(--text-secondary)">${p.discount_factor.toFixed(4)}</td>
                    <td style="color:var(--accent-primary)">₹${p.pv.toLocaleString('en-IN', {maximumFractionDigits: 0})}</td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        function handleCalcInputChange() {
            // Optional: prompt user to click calculate again
        }
        
        function goToCalculator(ticker) {
            document.getElementById('menu-calculator').click();
            const input = document.getElementById('calc-stock-input');
            input.value = ticker;
            handleCalcStockSelect(ticker);
            fetchValuation();
        }

        // Initial load
        window.addEventListener('DOMContentLoaded', () => {
            populateStats();
            renderTable();
            initCalculator();
        });
    </script>
</body>
</html>
"""
        
        # 5. Populate and write file
        html_content = html_template.replace('{{FETCH_DATE}}', self.fetch_date)
        html_content = html_content.replace('{{DIV_DASHBOARD}}', div_dashboard)
        html_content = html_content.replace('{{DIV_HEATMAP}}', div_heatmap)
        html_content = html_content.replace('{{DIV_BUBBLE}}', div_bubble)
        html_content = html_content.replace('{{DIV_RADAR}}', div_radar)
        html_content = html_content.replace('{{DIV_PRICE}}', div_price)
        html_content = html_content.replace('{{DIV_CORR}}', div_corr)
        html_content = html_content.replace('{{DIV_TREEMAP}}', div_treemap)
        html_content = html_content.replace('{{STOCKS_JSON}}', stocks_json)
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print("🏆 Unified premium dashboard successfully written to 'index.html'!")
        print("-" * 50)
    # ============================================================
    # SECTION 4: REPORT GENERATION
    # ============================================================

    def generate_text_report(self):
        """Generate comprehensive text report"""
        df = self.analysis_results

        report = []
        report.append("=" * 80)
        report.append("🇮🇳  INDIAN STOCK MARKET - UNDERVALUED STOCK ANALYSIS REPORT")
        report.append(f"📅  Generated: {self.fetch_date}")
        report.append(f"📊  Stocks Analyzed: {len(df)}")
        report.append(f"🏭  Sectors Covered: {df['Sector'].nunique()}")
        report.append("=" * 80)

        # ---- TOP UNDERVALUED STOCKS ----
        report.append("\n" + "🏆" * 30)
        report.append("\n🏆  TOP 15 MOST UNDERVALUED STOCKS (With Growth)")
        report.append("=" * 80)

        top15 = df.sort_values('Combined Score').head(15)
        for rank, (_, row) in enumerate(top15.iterrows(), 1):
            report.append(f"\n{'─'*60}")
            report.append(f"  #{rank}  {row['Company']} ({row['Ticker']})")
            report.append(f"  Sector: {row['Sector']}")
            report.append(f"  {'─'*50}")
            report.append(f"  💰 Price: ₹{row['Current Price']:,.2f}" if row['Current Price'] else "  💰 Price: N/A")
            report.append(f"  📊 Market Cap: ₹{row['Market Cap (Cr)']:,.0f} Cr" if row['Market Cap (Cr)'] else "  📊 Market Cap: N/A")
            report.append(f"  📈 PE Ratio: {row['PE Ratio']}" if row['PE Ratio'] else "  📈 PE Ratio: N/A")
            report.append(f"  📘 PB Ratio: {row['PB Ratio']}" if row['PB Ratio'] else "  📘 PB Ratio: N/A")
            report.append(f"  💵 Dividend Yield: {row['Dividend Yield %']}%")
            report.append(f"  📊 ROE: {row['ROE %']}%" if row['ROE %'] else "  📊 ROE: N/A")
            report.append(f"  📈 Revenue Growth: {row['Revenue Growth %']}%" if row['Revenue Growth %'] else "  📈 Revenue Growth: N/A")
            report.append(f"  📈 Earnings Growth: {row['Earnings Growth %']}%" if row['Earnings Growth %'] else "  📈 Earnings Growth: N/A")
            report.append(f"  ⚡ RSI: {row['RSI']}" if row['RSI'] else "  ⚡ RSI: N/A")
            report.append(f"  🎯 Target Price: ₹{row['Target Price']:,.2f} ({row['Upside %']:+.1f}%)" if row['Target Price'] else "  🎯 Target: N/A")
            report.append(f"  📉 52W Range: ₹{row['52W Low']:,.2f} - ₹{row['52W High']:,.2f}" if row['52W Low'] and row['52W High'] else "  📉 52W Range: N/A")

            # Scoring
            report.append(f"  {'─'*50}")
            report.append(f"  🎯 Valuation Score: {row['Valuation Score']}/100 (Lower = More Undervalued)")
            report.append(f"  🚀 Growth Score: {row['Growth Score']}/100 (Higher = Better Growth)")
            report.append(f"  ⭐ Combined Score: {row['Combined Score']}/100")

            if row['Combined Score'] < 30:
                report.append(f"  ✅ VERDICT: 🟢 STRONG UNDERVALUED - High growth potential")
            elif row['Combined Score'] < 40:
                report.append(f"  ✅ VERDICT: 🟢 UNDERVALUED - Good value with growth")
            elif row['Combined Score'] < 50:
                report.append(f"  ✅ VERDICT: 🟡 FAIRLY VALUED - Monitor for dips")

        # ---- SECTOR ANALYSIS ----
        report.append("\n\n" + "=" * 80)
        report.append("📊  SECTOR-WISE ANALYSIS")
        report.append("=" * 80)

        for sector in df['Sector'].unique():
            sector_df = df[df['Sector'] == sector]
            report.append(f"\n{'━'*60}")
            report.append(f"  🏭 {sector.upper()}")
            report.append(f"  Stocks: {len(sector_df)}")
            report.append(f"  Avg PE: {sector_df['PE Ratio'].median():.2f}" if not sector_df['PE Ratio'].dropna().empty else "  Avg PE: N/A")
            report.append(f"  Avg PB: {sector_df['PB Ratio'].median():.2f}" if not sector_df['PB Ratio'].dropna().empty else "  Avg PB: N/A")
            report.append(f"  Avg ROE: {sector_df['ROE %'].median():.2f}%" if not sector_df['ROE %'].dropna().empty else "  Avg ROE: N/A")
            report.append(f"  Avg Growth: {sector_df['Revenue Growth %'].median():.2f}%" if not sector_df['Revenue Growth %'].dropna().empty else "  Avg Growth: N/A")
            report.append(f"  Avg Combined Score: {sector_df['Combined Score'].mean():.1f}")

            best = sector_df.sort_values('Combined Score').iloc[0]
            report.append(f"  ⭐ Best Pick: {best['Company']} (Score: {best['Combined Score']:.1f})")

        # ---- MARKET OVERVIEW ----
        report.append("\n\n" + "=" * 80)
        report.append("📈  OVERALL MARKET OVERVIEW")
        report.append("=" * 80)

        report.append(f"\n  Total Stocks Analyzed: {len(df)}")
        report.append(f"  Undervalued (Score < 40): {len(df[df['Combined Score'] < 40])}")
        report.append(f"  Fairly Valued (40-60): {len(df[(df['Combined Score'] >= 40) & (df['Combined Score'] < 60)])}")
        report.append(f"  Overvalued (Score > 60): {len(df[df['Combined Score'] >= 60])}")

        report.append(f"\n  Market-wide Median PE: {df['PE Ratio'].median():.2f}" if not df['PE Ratio'].dropna().empty else "")
        report.append(f"  Market-wide Median PB: {df['PB Ratio'].median():.2f}" if not df['PB Ratio'].dropna().empty else "")
        report.append(f"  Avg Revenue Growth: {df['Revenue Growth %'].median():.2f}%" if not df['Revenue Growth %'].dropna().empty else "")

        # Best sector
        sector_scores = df.groupby('Sector')['Combined Score'].mean().sort_values()
        report.append(f"\n  🏆 Most Undervalued Sector: {sector_scores.index[0]} (Avg Score: {sector_scores.iloc[0]:.1f})")
        report.append(f"  ⚠ Most Overvalued Sector: {sector_scores.index[-1]} (Avg Score: {sector_scores.iloc[-1]:.1f})")

        # ---- DISCLAIMER ----
        report.append("\n\n" + "=" * 80)
        report.append("⚠️  DISCLAIMER")
        report.append("=" * 80)
        report.append("""
  This report is generated using quantitative analysis of publicly available
  financial data. It should NOT be considered as financial advice.

  Key Limitations:
  • Data is sourced from Yahoo Finance and may have delays/inaccuracies
  • Past performance does not guarantee future results
  • The scoring model is algorithmic and may not capture all factors
  • Qualitative factors (management quality, moats, etc.) are not considered
  • Always consult a SEBI-registered financial advisor before investing
  • Do your own research (DYOR) before making any investment decisions

  The analysis considers: PE, PB, Dividend Yield, ROE, Revenue Growth,
  Earnings Growth, Debt/Equity, RSI, Moving Averages, and Analyst Targets.
        """)

        report_text = "\n".join(report)

        # Save to file
        with open('indian_market_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(report_text)
        print("\n📄 Report saved as 'indian_market_report.txt'")

        return report_text

    def export_to_excel(self):
        """Export all data to Excel"""
        try:
            with pd.ExcelWriter('indian_market_analysis.xlsx', engine='openpyxl') as writer:
                # All stocks
                self.analysis_results.sort_values('Combined Score').to_excel(
                    writer, sheet_name='All Stocks', index=False
                )

                # Top picks
                self.analysis_results.sort_values('Combined Score').head(20).to_excel(
                    writer, sheet_name='Top 20 Undervalued', index=False
                )

                # Sector summary
                sector_summary = self.analysis_results.groupby('Sector').agg({
                    'PE Ratio': 'median',
                    'PB Ratio': 'median',
                    'ROE %': 'median',
                    'Revenue Growth %': 'median',
                    'Dividend Yield %': 'median',
                    'Combined Score': 'mean',
                    'Company': 'count'
                }).rename(columns={'Company': 'Stock Count'}).round(2)
                sector_summary.to_excel(writer, sheet_name='Sector Summary')

                # By sector sheets
                for sector in self.analysis_results['Sector'].unique():
                    sector_df = self.analysis_results[self.analysis_results['Sector'] == sector]
                    sheet_name = sector[:30]  # Excel sheet name limit
                    sector_df.sort_values('Combined Score').to_excel(
                        writer, sheet_name=sheet_name, index=False
                    )

            print("📊 Excel report saved as 'indian_market_analysis.xlsx'")
        except ImportError:
            print("⚠ Install openpyxl for Excel export: pip install openpyxl")
            # Fallback to CSV
            self.analysis_results.sort_values('Combined Score').to_csv(
                'indian_market_analysis.csv', index=False
            )
            print("📊 CSV report saved as 'indian_market_analysis.csv'")

    def export_to_csv(self):
        """Export to CSV"""
        self.analysis_results.sort_values('Combined Score').to_csv(
            'indian_market_analysis.csv', index=False
        )
        print("📊 CSV saved as 'indian_market_analysis.csv'")


# ============================================================
# SECTION 5: RUN THE ANALYSIS
# ============================================================

def main():
    """Main execution function"""

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     🇮🇳  INDIAN STOCK MARKET ANALYZER & SCREENER  🇮🇳       ║
    ║                                                              ║
    ║  Sectors: Banking, IT, Pharma, Auto, FMCG, Energy,         ║
    ║           Metals & Mining, Real Estate, Defence              ║
    ║                                                              ║
    ║  Analysis: Fundamental + Technical + Growth + Value          ║
    ║  Output:   Interactive Charts + Reports + Excel/CSV          ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    analyzer = IndianMarketAnalyzer()

    # Step 1: Fetch and Analyze
    results = analyzer.analyze_all_stocks()

    if results.empty:
        print("❌ No data could be fetched. Check your internet connection.")
        return

    # Step 2: Generate Visualizations & Unified Dashboard Hub
    analyzer.create_unified_dashboard()

    # Step 3: Generate Reports
    print("\n📄 Generating Reports...")
    print("-" * 50)

    analyzer.generate_text_report()
    analyzer.export_to_excel()
    analyzer.export_to_csv()

    # Step 4: Quick Summary
    print("\n" + "=" * 70)
    print("🎯  QUICK TOP 10 PICKS (Most Undervalued with Growth)")
    print("=" * 70)

    top10 = results.sort_values('Combined Score').head(10)
    print(top10[['Company', 'Sector', 'Current Price', 'PE Ratio',
                  'Revenue Growth %', 'ROE %', 'Combined Score',
                  'Upside %']].to_string(index=False))

    print("\n" + "=" * 70)
    print("📁 FILES GENERATED:")
    print("   📊 index.html (PREMIUM UNIFIED DASHBOARD HUB)")
    print("   📊 valuation_heatmap.html")
    print("   📊 sector_bubble_chart.html")
    print("   📊 undervalued_dashboard.html")
    print("   📊 sector_radar.html")
    print("   📊 price_performance.html")
    print("   📊 correlation_heatmap.html")
    print("   📊 market_treemap.html")
    print("   📄 indian_market_report.txt")
    print("   📊 indian_market_analysis.xlsx")
    print("   📊 indian_market_analysis.csv")
    print("=" * 70)
    print("✅ Analysis Complete! Open 'index.html' in your browser to access the premium dashboard hub.")


if __name__ == "__main__":
    main()
