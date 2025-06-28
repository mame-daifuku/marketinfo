import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time
from bs4 import BeautifulSoup
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Streamlit設定
st.set_page_config(
    page_title="Market Sentiment Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

class CNNFearGreedScraper:
    def __init__(self):
        self.api_url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_current_index(self):
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
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
            
        except Exception as e:
            st.error(f"CNN Fear & Greed Index取得エラー: {e}")
            return None

    def get_detailed_indicators(self):
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            indicators = {}
            
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
            st.error(f"詳細指標取得エラー: {e}")
            return None

class NAAIMScraper:
    def __init__(self):
        self.base_url = "https://www.naaim.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_current_exposure(self):
        try:
            url = "https://naaim.org/programs/naaim-exposure-index/"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            target_div = soup.find('div', id='brxe-ymwzia')
            
            if target_div:
                text_content = target_div.get_text(strip=True)
                
                patterns = [
                    r'(\d+\.?\d*)%?',
                    r'Index.*?(\d+\.?\d*)',
                    r'(\d{1,3}\.?\d*)',
                    r'exposure.*?(\d+\.?\d*)',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        for match in matches:
                            try:
                                value = float(match)
                                if 0 <= value <= 200:
                                    return {
                                        'date': datetime.now().strftime('%Y-%m-%d'),
                                        'exposure': value,
                                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        'source': 'NAAIM公式サイト',
                                        'raw_text': text_content
                                    }
                            except ValueError:
                                continue
            
            return self._get_mock_data()
            
        except Exception as e:
            st.error(f"NAAIM データ取得エラー: {e}")
            return self._get_mock_data()
    
    def _get_mock_data(self):
        import random
        exposure = round(random.uniform(30, 110), 1)
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'exposure': exposure,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note': 'デモデータ'
        }
    
    def get_sentiment_rating(self, exposure_value):
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

def create_gauge_chart(value, title, max_val=100):
    """ゲージチャートを作成"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        title = {'text': title},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "red"},
                {'range': [25, 50], 'color': "orange"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def main():
    st.title("📈 Market Sentiment Dashboard")
    st.markdown("---")
    
    # サイドバー
    st.sidebar.title("設定")
    auto_refresh = st.sidebar.checkbox("自動更新 (30秒)")
    show_details = st.sidebar.checkbox("詳細表示")
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # メインコンテンツ
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 CNN Fear & Greed Index")
        
        cnn_scraper = CNNFearGreedScraper()
        
        with st.spinner("CNN Fear & Greed Index取得中..."):
            cnn_data = cnn_scraper.get_current_index()
        
        if cnn_data:
            score = cnn_data['score']
            rating = cnn_data['rating']
            
            # 日本語の評価に変換
            rating_jp = {
                'extreme fear': '極度の恐怖',
                'fear': '恐怖',
                'neutral': '中立',
                'greed': '強欲',
                'extreme greed': '極度の強欲'
            }.get(rating, rating)
            
            # ゲージチャート
            fig_cnn = create_gauge_chart(score, "CNN Fear & Greed Index")
            st.plotly_chart(fig_cnn, use_container_width=True)
            
            # メトリクス表示
            st.metric(
                label="現在の指数",
                value=f"{score:.1f}",
                delta=f"{score - cnn_data['previous_close']:.1f} (前日比)"
            )
            
            st.info(f"**評価**: {rating_jp}")
            
            if show_details:
                st.write("**過去の値**")
                st.write(f"- 前日終値: {cnn_data['previous_close']:.1f}")
                st.write(f"- 1週間前: {cnn_data['previous_1_week']:.1f}")
                st.write(f"- 1ヶ月前: {cnn_data['previous_1_month']:.1f}")
                st.write(f"- 1年前: {cnn_data['previous_1_year']:.1f}")
        else:
            st.error("CNNデータの取得に失敗しました")
    
    with col2:
        st.subheader("🟢 NAAIM Exposure Index")
        
        naaim_scraper = NAAIMScraper()
        
        with st.spinner("NAAIM Exposure Index取得中..."):
            naaim_data = naaim_scraper.get_current_exposure()
        
        if naaim_data:
            exposure = naaim_data['exposure']
            sentiment_jp, sentiment_en = naaim_scraper.get_sentiment_rating(exposure)
            
            # ゲージチャート
            fig_naaim = create_gauge_chart(exposure, "NAAIM Exposure Index", max_val=200)
            st.plotly_chart(fig_naaim, use_container_width=True)
            
            # メトリクス表示
            st.metric(
                label="エクスポージャー",
                value=f"{exposure:.1f}%"
            )
            
            st.info(f"**評価**: {sentiment_jp}")
            
            if show_details and 'raw_text' in naaim_data:
                st.write("**取得データ**")
                st.text(naaim_data['raw_text'])
        else:
            st.error("NAAIMデータの取得に失敗しました")
    
    # 詳細指標（CNNのみ）
    if show_details and cnn_data:
        st.markdown("---")
        st.subheader("📊 CNN 構成指標の詳細")
        
        with st.spinner("詳細指標取得中..."):
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
            
            cols = st.columns(4)
            for i, (key, value) in enumerate(indicators.items()):
                col_idx = i % 4
                with cols[col_idx]:
                    name = indicator_names.get(key, key)
                    st.metric(
                        label=name,
                        value=f"{value['score']:.1f}",
                        delta=value['rating']
                    )
    
    # 更新時刻表示
    st.markdown("---")
    if cnn_data and naaim_data:
        st.caption(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()