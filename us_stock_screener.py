import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
import time
import warnings
warnings.filterwarnings('ignore')

class USStockScreener:
    def __init__(self):
        self.sp500_tickers = self._get_sp500_tickers()
    
    def _get_sp500_tickers(self) -> List[str]:
        """S&P500の銘柄リストを取得"""
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_table = tables[0]
            return sp500_table['Symbol'].tolist()
        except:
            # フォールバック用の主要銘柄
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B', 'JNJ', 'V']
    
    def get_financial_data(self, ticker: str) -> Optional[Dict]:
        """銘柄の財務データを取得"""
        try:
            stock = yf.Ticker(ticker)
            
            # 基本情報
            info = stock.info
            market_cap = info.get('marketCap', 0)
            
            # キャッシュフロー計算書
            cashflow = stock.cashflow
            if cashflow.empty:
                return None
            
            # フリーキャッシュフロー計算
            operating_cf = cashflow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cashflow.index else 0
            capex = cashflow.loc['Capital Expenditure'].iloc[0] if 'Capital Expenditure' in cashflow.index else 0
            free_cash_flow = operating_cf + capex  # CAPEXは負の値なので加算
            
            # 売上成長率（CAGR）計算
            financials = stock.financials
            if financials.empty or len(financials.columns) < 3:
                return None
            
            revenues = financials.loc['Total Revenue']
            if len(revenues) >= 3:
                current_revenue = revenues.iloc[0]
                past_revenue = revenues.iloc[2]  # 3年前
                cagr = ((current_revenue / past_revenue) ** (1/3) - 1) * 100
            else:
                return None
            
            return {
                'ticker': ticker,
                'market_cap': market_cap,
                'free_cash_flow': free_cash_flow,
                'cagr': cagr,
                'company_name': info.get('longName', ticker)
            }
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def calculate_screening_ratio(self, market_cap: float, free_cash_flow: float, cagr: float) -> Optional[float]:
        """スクリーニング条件の計算: (Market Cap / Free Cash Flow) / CAGR"""
        if free_cash_flow <= 0 or cagr <= 0:
            return None
        
        pcf_ratio = market_cap / free_cash_flow
        screening_ratio = pcf_ratio / cagr
        return screening_ratio
    
    def screen_stocks(self, tickers: List[str] = None, max_ratio: float = 3.0) -> pd.DataFrame:
        """条件に合致する銘柄をスクリーニング"""
        if tickers is None:
            # API制限を考慮して10銘柄に限定
            tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JNJ', 'V', 'JPM']
        
        results = []
        
        for i, ticker in enumerate(tickers):
            print(f"Processing {ticker} ({i+1}/{len(tickers)})")
            
            data = self.get_financial_data(ticker)
            if data is None:
                continue
            
            ratio = self.calculate_screening_ratio(
                data['market_cap'], 
                data['free_cash_flow'], 
                data['cagr']
            )
            
            if ratio is not None and ratio <= max_ratio:
                pcf_ratio = data['market_cap'] / data['free_cash_flow']
                results.append({
                    'Ticker': data['ticker'],
                    'Company': data['company_name'],
                    'Market Cap (B)': data['market_cap'] / 1e9,
                    'Free Cash Flow (B)': data['free_cash_flow'] / 1e9,
                    'CAGR (%)': data['cagr'],
                    'P/FCF Ratio': pcf_ratio,
                    'Screening Ratio': ratio
                })
            
            # API制限対策
            time.sleep(2)
        
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values('Screening Ratio')
        
        return df

def main():
    """メイン実行関数"""
    import sys
    
    screener = USStockScreener()
    
    # コマンドライン引数でティッカーシンボルを指定
    if len(sys.argv) > 1:
        ticker_symbols = [arg.upper() for arg in sys.argv[1:]]
        print(f"指定銘柄のスクリーニング: {', '.join(ticker_symbols)}")
    else:
        ticker_symbols = None
        print("デフォルト10銘柄のスクリーニング")
    
    print("条件: (Market Cap / Free Cash Flow) / CAGR <= 3.0")
    print("-" * 50)
    
    # スクリーニング実行
    results = screener.screen_stocks(tickers=ticker_symbols)
    
    if results.empty:
        print("条件に合致する銘柄が見つかりませんでした。")
    else:
        print(f"\n条件に合致する銘柄: {len(results)}社")
        print("\n結果:")
        print(results.to_string(index=False, float_format='%.2f'))
        
        # CSV出力
        filename = 'us_stock_screening_results.csv'
        if ticker_symbols:
            filename = f"screening_{'_'.join(ticker_symbols)}.csv"
        results.to_csv(filename, index=False)
        print(f"\n結果を{filename}に保存しました。")

if __name__ == "__main__":
    main()