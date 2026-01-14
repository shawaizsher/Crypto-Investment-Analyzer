🚀 Top-20 Cryptocurrency Market Analysis & Investment Recommender

A data-driven investment analysis system that fetches real-time data for the top 20 cryptocurrencies by market cap and provides intelligent investment recommendations based on risk-adjusted returns.

## Features
✨ **Live Data Integration** - Automatically fetches top-20 coins from CoinGecko API
📊 **Advanced Analytics** - Computes annual returns, volatility, Sharpe ratio, and risk metrics
🎯 **Smart Recommendations** - Allocates portfolio based on investment strategy:
   - Conservative (low volatility, steady returns)
   - Balanced (optimal risk-return via Sharpe ratio)
   - Aggressive (high returns, higher risk tolerance)
💰 **Portfolio Optimization** - Equal-weight allocation across selected coins with detailed metrics
📈 **Interactive Dashboard** - Streamlit web interface with real-time visualizations:
   - Portfolio allocation pie charts
   - Risk/volatility comparison
   - Sharpe ratio rankings
   - Historical performance tables
🤖 **Predictive Modeling** - LSTM neural networks for price forecasting (TensorFlow/Keras)

## Tech Stack
- **Data**: CoinGecko API, Pandas, NumPy
- **ML/Analysis**: Scikit-learn, TensorFlow Keras, Scipy
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Web**: Streamlit
- **Language**: Python 3.x

## Quick Start
```bash
pip install -r [requirements.txt](http://_vscodecontentref_/0)
streamlit run [streamlit_recommend.py](http://_vscodecontentref_/1)
