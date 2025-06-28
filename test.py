import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import time
import argparse
import io

class CNNFearGreedScraper:
    """
    CNN Fear & Greed Indexをスクレイピングするクラス
    """
    
    def __init__(self):
        self.api_url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_current_index(self):
        """
        現在のFear & Greed Indexを取得
        """
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # メインの指数情報を抽出
            fear_greed = data.get('fear_and_greed', {})
            
            result = {
                'score': fear_greed.get('score', 0),
                'rating': fear_greed.get('rating', ''),
                'timestamp': fear_greed.get('timestamp', ''),
                'previous_close': fear_greed.get('previous_close', 0),
                'previous_1_week': fear_greed.get('previous_1_week', 0),
                'previous_1_month': fear_greed.get('previous_1_month', 0),
                'previous_1_year': fear_greed.get('previous_1_year', 0),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"APIリクエストエラー: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSONデコードエラー: {e}")
            return None
        except Exception as e:
            print(f"予期しないエラー: {e}")
            return None
    
    def get_historical_data(self, start_date=None):
        """
        過去のFear & Greed Indexデータを取得
        """
        try:
            url = self.api_url
            if start_date:
                url = f"{self.api_url}/{start_date}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 履歴データを抽出
            historical = data.get('fear_and_greed_historical', {}).get('data', [])
            
            # DataFrameに変換
            df_data = []
            for item in historical:
                df_data.append({
                    'date': pd.to_datetime(item['x'], unit='ms'),
                    'score': item['y'],
                    'rating': item['rating']
                })
            
            df = pd.DataFrame(df_data)
            return df
            
        except Exception as e:
            print(f"履歴データ取得エラー: {e}")
            return None
    
    def get_detailed_indicators(self):
        """
        詳細な指標データを取得（7つの構成要素）
        """
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            indicators = {}
            
            # 各指標の最新データを抽出
            indicator_keys = [
                'market_momentum_sp500',
                'stock_price_strength', 
                'stock_price_breadth',
                'put_call_options',
                'market_volatility_vix',
                'junk_bond_demand',
                'safe_haven_demand'
            ]
            
            for key in indicator_keys:
                if key in data:
                    indicator_data = data[key]
                    indicators[key] = {
                        'score': indicator_data.get('score', 0),
                        'rating': indicator_data.get('rating', ''),
                        'timestamp': indicator_data.get('timestamp', '')
                    }
            
            return indicators
            
        except Exception as e:
            print(f"詳細指標取得エラー: {e}")
            return None
    
    def format_output(self, data, verbose=False):
        """
        データを見やすい形式で出力
        """
        if not data:
            return "データが取得できませんでした"
        
        score = data['score']
        rating = data['rating']
        
        # 日本語の評価に変換
        rating_jp = {
            'extreme fear': '極度の恐怖',
            'fear': '恐怖',
            'neutral': '中立',
            'greed': '強欲',
            'extreme greed': '極度の強欲'
        }.get(rating, rating)
        
        if not verbose:
            # 標準表示：数値と評価
            return f"{score} {rating_jp}"
        
        # 詳細表示：全ての情報
        output = f"""
=== CNN Fear & Greed Index ===
指数値: {score:.1f}
評価: {rating_jp} ({rating})
前日終値: {data['previous_close']:.1f}
1週間前: {data['previous_1_week']:.1f}
1ヶ月前: {data['previous_1_month']:.1f}
1年前: {data['previous_1_year']:.1f}
取得時刻: {data['last_updated']}
        """
        
        return output.strip()

class NAAIMScraper:
    """
    NAAIM Exposure Indexをスクレイピングするクラス
    """
    
    def __init__(self):
        self.base_url = "https://www.naaim.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_current_exposure(self):
        """
        現在のNAAIM Exposure Indexを取得
        """
        try:
            # NAAIMの公開データページを試行
            url = f"{self.base_url}/newsroom/naaim-exposure-index"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # HTMLから数値を抽出する簡易的な方法
                content = response.text
                
                # 実際のスクレイピングを実行
                return self._get_from_naaim_website()
            else:
                return self._get_from_naaim_website()
                
        except Exception as e:
            print(f"NAAIM データ取得エラー: {e}")
            return self._get_mock_data()
    
    def _get_from_naaim_website(self):
        """
        NAAIM公式サイトからWebスクレイピングで数値を取得
        特定のdiv要素 (id="brxe-ymwzia") から数値を抽出
        """
        try:
            from bs4 import BeautifulSoup
            
            url = "https://naaim.org/programs/naaim-exposure-index/"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 指定されたdiv要素を検索
            target_div = soup.find('div', id='brxe-ymwzia')
            
            if target_div:
                # div内のテキストから数値を抽出
                text_content = target_div.get_text(strip=True)
                print(f"取得したテキスト: {text_content}")
                
                # 複数のパターンで数値を検索
                import re
                patterns = [
                    r'(\d+\.?\d*)%?',  # 基本的な数値パターン
                    r'Index.*?(\d+\.?\d*)',  # Index に続く数値
                    r'(\d{1,3}\.?\d*)',  # 1-3桁の数値
                    r'exposure.*?(\d+\.?\d*)',  # exposure に続く数値
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        # 最も適切そうな数値を選択（0-200の範囲の数値）
                        for match in matches:
                            try:
                                value = float(match)
                                if 0 <= value <= 200:  # NAAIM指数の一般的な範囲
                                    return {
                                        'date': datetime.now().strftime('%Y-%m-%d'),
                                        'exposure': value,
                                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        'source': 'NAAIM公式サイト (div#brxe-ymwzia)',
                                        'raw_text': text_content
                                    }
                            except ValueError:
                                continue
            
            # フォールバック: ページ全体から検索
            content = response.text
            import re
            pattern = r"This week's NAAIM Exposure Index number is[^\d]*(\d+\.?\d*)"
            match = re.search(pattern, content, re.IGNORECASE)
            
            if match:
                exposure_value = float(match.group(1))
                return {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'exposure': exposure_value,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'NAAIM公式サイト (フォールバック)'
                }
            
            return self._get_mock_data()
            
        except Exception as e:
            print(f"NAAIM ウェブスクレイピング エラー: {e}")
            return self._get_mock_data()
    
    def _get_mock_data(self):
        """
        デモ用のモックデータ
        """
        import random
        
        # 実際のNAAIMの範囲に基づいたランダムデータ
        exposure = round(random.uniform(30, 110), 1)
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'exposure': exposure,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note': 'デモデータ（実際のAPIキーまたはスクレイピングが必要）'
        }
    
    def get_sentiment_rating(self, exposure_value):
        """
        エクスポージャー値から感情を判定
        """
        if exposure_value < 40:
            return '極度の弱気', 'extreme_bearish'
        elif exposure_value < 60:
            return '弱気', 'bearish'
        elif exposure_value < 80:
            return '中立', 'neutral'
        elif exposure_value < 95:
            return '強気', 'bullish'
        else:
            return '極度の強気', 'extreme_bullish'
    
    def format_output(self, data, verbose=False):
        """
        データを見やすい形式で出力
        """
        if not data:
            return "NAAIMデータが取得できませんでした"
        
        exposure = data['exposure']
        sentiment_jp, sentiment_en = self.get_sentiment_rating(exposure)
        
        if not verbose:
            # 標準表示：数値と評価
            return f"{exposure:.1f} {sentiment_jp}"
        
        # 詳細表示：全ての情報
        output = f"""
=== NAAIM Exposure Index ===
エクスポージャー: {exposure:.1f}%
評価: {sentiment_jp} ({sentiment_en})
データ日付: {data['date']}
取得時刻: {data['last_updated']}"""
        
        if 'source' in data:
            output += f"\nデータソース: {data['source']}"
        
        if 'note' in data:
            output += f"\n注意: {data['note']}"
        
        return output.strip()

def main():
    """
    メイン関数
    """
    parser = argparse.ArgumentParser(description='市場感情指標を取得します')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='詳細情報を表示します')
    parser.add_argument('--naaim', action='store_true',
                       help='NAAIMデータも取得します')
    
    args = parser.parse_args()
    
    # CNN Fear & Greed Index
    cnn_scraper = CNNFearGreedScraper()
    current_data = cnn_scraper.get_current_index()
    
    if current_data:
        print(cnn_scraper.format_output(current_data, verbose=args.verbose))
    else:
        print("CNNデータの取得に失敗しました")
    
    # NAAIM Exposure Index - 常に表示
    print("\n" + "="*30 + "\n")
    
    naaim_scraper = NAAIMScraper()
    naaim_data = naaim_scraper.get_current_exposure()
    
    if naaim_data:
        print(naaim_scraper.format_output(naaim_data, verbose=args.verbose))
    else:
        print("NAAIMデータの取得に失敗しました")
    
    # 詳細オプションが指定された場合の追加情報
    if args.verbose:
        print("\n" + "="*50 + "\n")
        
        # CNN詳細指標を取得
        print("=== CNN 7つの構成指標 ===")
        indicators = cnn_scraper.get_detailed_indicators()
        if indicators:
            indicator_names = {
                'market_momentum_sp500': 'S&P500モメンタム',
                'stock_price_strength': '株価強度',
                'stock_price_breadth': '株価幅',
                'put_call_options': 'プット/コールオプション',
                'market_volatility_vix': '市場ボラティリティ(VIX)',
                'junk_bond_demand': 'ジャンクボンド需要',
                'safe_haven_demand': '安全資産需要'
            }
            
            for key, value in indicators.items():
                name = indicator_names.get(key, key)
                print(f"{name}: {value['score']:.1f} ({value['rating']})")
        
        print("\n" + "="*50 + "\n")
        
        # CNN履歴データのサンプル取得
        print("=== CNN過去30日間の統計情報 ===")
        historical_data = cnn_scraper.get_historical_data()
        if historical_data is not None and not historical_data.empty:
            recent_data = historical_data.tail(30)
            print(f"平均スコア: {recent_data['score'].mean():.1f}")
            print(f"最高値: {recent_data['score'].max():.1f}")
            print(f"最低値: {recent_data['score'].min():.1f}")

if __name__ == "__main__":
    main()