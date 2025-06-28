# Market Sentiment Dashboard

リアルタイムで市場感情指標を表示するStreamlitダッシュボードです。

## 機能

- **CNN Fear & Greed Index**: 市場の恐怖と強欲指数をリアルタイム表示
- **NAAIM Exposure Index**: 投資顧問の株式エクスポージャー指数
- **ゲージチャート**: 視覚的でわかりやすい表示
- **自動更新**: 30秒間隔での自動データ更新
- **詳細表示**: 7つの構成指標と過去データ

## Streamlit Cloudでの使用方法

1. このリポジトリをGitHubにプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
3. GitHubアカウントでログイン
4. "New app" をクリック
5. リポジトリを選択し、`app.py` を指定
6. "Deploy!" をクリック

## ローカル実行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## データソース

- CNN Fear & Greed Index API
- NAAIM公式ウェブサイト

## 注意事項

- データ取得に失敗した場合はエラーメッセージが表示されます
- NAAIMデータが取得できない場合はデモデータが使用されます