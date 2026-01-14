# top20_crypto_analysis/recommend_coins.py
import os
import numpy as np
import pandas as pd
from pycoingecko import CoinGeckoAPI
from sklearn.preprocessing import MinMaxScaler
import joblib

CACHE_DIR = "data"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_top_20_coins():
    """Fetch top 20 coins by market cap from CoinGecko."""
    cg = CoinGeckoAPI()
    top = cg.get_coins_markets(
        vs_currency='usd',
        order='market_cap_desc',
        per_page=20,
        page=1,
        sparkline=True,
        price_change_percentage='24h,7d,30d'
    )
    return top

def fetch_historical_data(coin_id, days=365):
    """Fetch 1 year of historical price data."""
    cg = CoinGeckoAPI()
    try:
        data = cg.get_coin_market_chart_by_id(
            id=coin_id,
            vs_currency='usd',
            days=days
        )
        prices = np.array(data['prices'])[:, 1]
        returns = np.diff(prices) / prices[:-1]
        return {
            'prices': prices,
            'returns': returns,
            'current_price': prices[-1],
            'start_price': prices[0],
            'total_return': (prices[-1] / prices[0]) - 1
        }
    except Exception as e:
        print(f"Error fetching history for {coin_id}: {e}")
        return None

def compute_coin_stats(coin_data, hist_data):
    """Compute risk/return metrics for a coin."""
    if not hist_data:
        return None
    
    name = coin_data['name']
    symbol = coin_data['symbol'].upper()
    current_price = coin_data['current_price']
    market_cap = coin_data['market_cap'] or 0
    volume_24h = coin_data['total_volume'] or 0
    
    returns = hist_data['returns']
    daily_volatility = np.std(returns) if len(returns) > 0 else 0
    annual_volatility = daily_volatility * np.sqrt(365)
    avg_daily_return = np.mean(returns) if len(returns) > 0 else 0
    annual_return = (1 + avg_daily_return) ** 365 - 1
    
    # Sharpe ratio (assuming risk-free rate = 3%)
    risk_free = 0.03
    sharpe_ratio = (annual_return - risk_free) / annual_volatility if annual_volatility > 0 else 0
    
    # Price change percentages
    change_24h = coin_data.get('price_change_percentage_24h_in_currency', 0) or 0
    change_7d = coin_data.get('price_change_percentage_7d_in_currency', 0) or 0
    change_30d = coin_data.get('price_change_percentage_30d_in_currency', 0) or 0
    
    return {
        'symbol': symbol,
        'name': name,
        'current_price': current_price,
        'market_cap': market_cap,
        'volume_24h': volume_24h,
        'total_return_1y': hist_data['total_return'],
        'annual_return': annual_return,
        'daily_volatility': daily_volatility,
        'annual_volatility': annual_volatility,
        'sharpe_ratio': sharpe_ratio,
        'change_24h': change_24h,
        'change_7d': change_7d,
        'change_30d': change_30d
    }

def rank_coins_by_strategy(stats_list, strategy='balanced'):
    """
    Rank coins by investment strategy.
    Strategies:
      - 'conservative': low volatility, positive returns
      - 'balanced': good Sharpe ratio
      - 'aggressive': high returns, high volatility
    """
    df = pd.DataFrame(stats_list)
    df = df.dropna(subset=['sharpe_ratio', 'annual_volatility'])
    
    if strategy == 'conservative':
        # Low volatility, positive return
        df['score'] = (
            (1 - df['annual_volatility'].rank(pct=True)) * 0.6 +
            df['annual_return'].rank(pct=True) * 0.4
        )
    elif strategy == 'aggressive':
        # High return, willing to accept volatility
        df['score'] = (
            df['annual_return'].rank(pct=True) * 0.7 +
            (1 - df['annual_volatility'].rank(pct=True)) * 0.3
        )
    else:  # balanced
        # Maximize Sharpe ratio
        df['score'] = df['sharpe_ratio'].rank(pct=True)
    
    return df.sort_values('score', ascending=False)

def allocate_portfolio(ranked_df, investment_amount, top_n=5):
    """Allocate investment across top N coins equally or by score."""
    top_coins = ranked_df.head(top_n)
    
    # Equal weight allocation
    allocation = pd.DataFrame({
        'symbol': top_coins['symbol'],
        'name': top_coins['name'],
        'current_price': top_coins['current_price'],
        'amount': investment_amount / top_n,
        'quantity': (investment_amount / top_n) / top_coins['current_price'].values,
        'score': top_coins['score'].values,
        'annual_volatility': top_coins['annual_volatility'].values,
        'sharpe_ratio': top_coins['sharpe_ratio'].values
    }).reset_index(drop=True)
    
    return allocation

def main():
    print("Fetching top 20 coins...")
    top_coins = fetch_top_20_coins()
    
    stats_list = []
    for coin in top_coins:
        coin_id = coin['id']
        print(f"Analyzing {coin['name']} ({coin['symbol'].upper()})...")
        hist = fetch_historical_data(coin_id, days=365)
        if hist:
            stats = compute_coin_stats(coin, hist)
            if stats:
                stats_list.append(stats)
    
    df_stats = pd.DataFrame(stats_list)
    df_stats.to_csv(os.path.join(CACHE_DIR, "top20_stats.csv"), index=False)
    print(f"Saved stats to {os.path.join(CACHE_DIR, 'top20_stats.csv')}")
    
    # Example: invest 10k in balanced portfolio
    investment = 10000
    ranked = rank_coins_by_strategy(stats_list, strategy='balanced')
    portfolio = allocate_portfolio(ranked, investment, top_n=5)
    
    print(f"\nRecommended Portfolio (${investment:,.2f} balanced):")
    print(portfolio[['symbol', 'name', 'amount', 'quantity', 'sharpe_ratio']])
    
    return df_stats, ranked, portfolio

if __name__ == "__main__":
    main()