import pandas as pd
import yfinance as yf

class DCFEngine:
    def __init__(self):
        # Default Parameters
        self.default_params = {
            'risk_free_rate': 0.07,
            'market_risk_premium': 0.08,
            'pre_tax_debt_cost': 0.09,
            'tax_rate': 0.25,
            'stage_1_growth': 0.12,
            'stage_2_growth': 0.08,
            'terminal_growth': 0.05
        }

    def fetch_stock_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'Ticker': ticker,
                'Company': info.get('shortName', ticker),
                'Sector': info.get('sector', 'N/A'),
                'Market Cap (Cr)': info.get('marketCap', 0) / 10000000 if info.get('marketCap') else 0,
                'Current Price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'PE Ratio': info.get('trailingPE', info.get('forwardPE', 0)),
                'Beta': info.get('beta', 1.0),
                'Debt/Equity': info.get('debtToEquity', 20.0)
            }
        except Exception as e:
            return None

    def calculate_dcf(self, stock_data, user_params=None, ticker=None):
        """
        stock_data: dict containing 'Ticker', 'Market Cap (Cr)', 'Current Price', 'PE Ratio', 'Beta', 'Debt/Equity'
        user_params: dict containing custom overrides for rates and growth
        """
        if not stock_data and ticker:
            stock_data = self.fetch_stock_data(ticker)
            
        if not stock_data:
            return {"error": "Could not load stock data for valuation."}
            
        params = self.default_params.copy()
        if user_params:
            for k, v in user_params.items():
                if v is not None:
                    params[k] = float(v)

        market_cap = float(stock_data.get('Market Cap (Cr)') or 0)
        current_price = float(stock_data.get('Current Price') or 0)
        pe_ratio = float(stock_data.get('PE Ratio') or 0)
        beta = float(stock_data.get('Beta') or 1.0)
        
        # Debt to Equity could be represented as percentage (e.g. 20 means 20% or 0.20)
        # Assuming it is passed as a direct ratio or percentage. Let's assume ratio if < 10, else %.
        de_raw = stock_data.get('Debt/Equity', 0)
        if de_raw is None: de_raw = 0.20
        debt_to_equity = float(de_raw) / 100.0 if float(de_raw) > 10 else float(de_raw)

        if market_cap <= 0 or current_price <= 0:
            return {"error": "Invalid Market Cap or Current Price for DCF."}

        shares_out = market_cap / current_price

        # --- WACC Calculation ---
        cost_of_equity = params['risk_free_rate'] + (beta * params['market_risk_premium'])
        after_tax_debt_cost = params['pre_tax_debt_cost'] * (1 - params['tax_rate'])
        
        weight_equity = 1.0 / (1.0 + debt_to_equity)
        weight_debt = debt_to_equity / (1.0 + debt_to_equity)
        
        wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_debt_cost)
        
        # Guard against mathematically invalid WACC
        if wacc <= params['terminal_growth']:
            wacc = params['terminal_growth'] + 0.01

        # --- Base FCF Calculation ---
        if pe_ratio > 0:
            base_fcf = (market_cap / pe_ratio) * 0.85
        else:
            base_fcf = market_cap * 0.05

        # --- 10 Year Projection ---
        projections = []
        current_fcf = base_fcf
        total_pv_fcf = 0.0

        for year in range(1, 11):
            if year <= 5:
                current_fcf *= (1 + params['stage_1_growth'])
            else:
                current_fcf *= (1 + params['stage_2_growth'])
                
            discount_factor = 1.0 / ((1 + wacc) ** year)
            pv_fcf = current_fcf * discount_factor
            total_pv_fcf += pv_fcf
            
            projections.append({
                'year': year,
                'fcf': round(current_fcf, 2),
                'discount_factor': round(discount_factor, 4),
                'pv': round(pv_fcf, 2)
            })

        # --- Terminal Value ---
        fcf_10 = projections[-1]['fcf']
        terminal_value = (fcf_10 * (1 + params['terminal_growth'])) / (wacc - params['terminal_growth'])
        pv_terminal_value = terminal_value / ((1 + wacc) ** 10)

        # --- Intrinsic Value Calculation ---
        enterprise_value = total_pv_fcf + pv_terminal_value
        debt_value = market_cap * debt_to_equity
        equity_value = enterprise_value - debt_value
        
        intrinsic_price = equity_value / shares_out
        upside = ((intrinsic_price / current_price) - 1) * 100

        return {
            'wacc_details': {
                'cost_of_equity': round(cost_of_equity * 100, 2),
                'cost_of_debt_after_tax': round(after_tax_debt_cost * 100, 2),
                'weight_equity': round(weight_equity * 100, 2),
                'weight_debt': round(weight_debt * 100, 2),
                'wacc': round(wacc * 100, 2)
            },
            'dcf_details': {
                'base_fcf': round(base_fcf, 2),
                'shares_out': round(shares_out, 2),
                'total_pv_fcf': round(total_pv_fcf, 2),
                'terminal_value': round(terminal_value, 2),
                'pv_terminal_value': round(pv_terminal_value, 2),
                'enterprise_value': round(enterprise_value, 2),
                'debt_value': round(debt_value, 2),
                'equity_value': round(equity_value, 2)
            },
            'projections': projections,
            'outcome': {
                'intrinsic_price': round(intrinsic_price, 2),
                'current_price': round(current_price, 2),
                'upside_pct': round(upside, 2)
            },
            'stock_data': stock_data
        }

if __name__ == "__main__":
    # Test block
    engine = DCFEngine()
    test_data = {
        'Ticker': 'RELIANCE.NS',
        'Market Cap (Cr)': 2000000,
        'Current Price': 2900,
        'PE Ratio': 25,
        'Beta': 1.1,
        'Debt/Equity': 0.3
    }
    res = engine.calculate_dcf(test_data)
    print("Test DCF:", res)
