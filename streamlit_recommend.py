# top20_crypto_analysis/streamlit_recommend.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from recommend_coins import (
    fetch_top_20_coins,
    fetch_historical_data,
    compute_coin_stats,
    rank_coins_by_strategy,
    allocate_portfolio
)

st.set_page_config(layout="wide", page_title="Crypto Investment Recommender")

st.title("🚀 Top-20 Crypto Investment Recommender")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Investment Parameters")
    investment_amount = st.number_input(
        "How much do you want to invest? (PKR)",
        min_value=100,
        max_value=1_000_000,
        value=10000,
        step=1000
    )
    
    strategy = st.selectbox(
        "Investment Strategy",
        options=['conservative', 'balanced', 'aggressive'],
        help="Conservative: Low risk, lower returns | Balanced: Good risk-return | Aggressive: High risk, high returns"
    )
    
    num_coins = st.slider(
        "Number of coins to invest in",
        min_value=1,
        max_value=20,
        value=5
    )
    
    refresh = st.button("🔄 Analyze Top 20 & Get Recommendations", use_container_width=True)

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = None
    st.session_state.ranked_df = None
    st.session_state.last_params = None

# Run analysis on button click or if params changed
current_params = (investment_amount, strategy, num_coins)
should_analyze = refresh or st.session_state.last_params != current_params

if should_analyze:
    st.session_state.last_params = current_params
    
    st.info("📊 Fetching top 20 coins and historical data from CoinGecko... (this may take 1-2 minutes)")
    
    try:
        top_coins = fetch_top_20_coins()
        
        stats_list = []
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        for idx, coin in enumerate(top_coins):
            coin_id = coin['id']
            progress_val = (idx + 1) / len(top_coins)
            status_placeholder.write(f"⏳ Analyzing {coin['name']} ({coin['symbol'].upper()})... [{idx+1}/{len(top_coins)}]")
            progress_placeholder.progress(progress_val)
            
            hist = fetch_historical_data(coin_id, days=365)
            if hist:
                stats = compute_coin_stats(coin, hist)
                if stats:
                    stats_list.append(stats)
            time.sleep(0.5)
        
        if stats_list:
            # Rank by strategy
            st.session_state.ranked_df = rank_coins_by_strategy(stats_list, strategy=strategy)
            
            # Allocate portfolio
            st.session_state.portfolio = allocate_portfolio(st.session_state.ranked_df, investment_amount, top_n=num_coins)
            
            progress_placeholder.empty()
            status_placeholder.empty()
            st.success("✅ Analysis complete!")
        else:
            st.error("No data collected. Please check your internet connection.")
            
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.info("Troubleshooting: Make sure you have internet access and pycoingecko is installed.")

# Display results if available
if st.session_state.portfolio is not None and st.session_state.ranked_df is not None:
    portfolio = st.session_state.portfolio
    ranked_df = st.session_state.ranked_df
    
    # Display recommendations
    st.header(f"📈 Portfolio Recommendation ({strategy.capitalize()})")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Investment", f"₨{investment_amount:,.2f}")
    with col2:
        avg_volatility = portfolio['annual_volatility'].mean()
        st.metric("Portfolio Annual Volatility", f"{avg_volatility:.2%}")
    with col3:
        avg_sharpe = portfolio['sharpe_ratio'].mean()
        st.metric("Avg Sharpe Ratio", f"{avg_sharpe:.3f}")
    
    st.subheader("💰 Recommended Coins")
    display_cols = ['symbol', 'name', 'current_price', 'amount', 'quantity', 'sharpe_ratio', 'annual_volatility']
    st.dataframe(
        portfolio[display_cols].style.format({
            'current_price': '₨{:.2f}',
            'amount': '₨{:,.2f}',
            'quantity': '{:.4f}',
            'sharpe_ratio': '{:.3f}',
            'annual_volatility': '{:.2%}'
        }),
        use_container_width=True
    )
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        fig_alloc = px.pie(
            portfolio,
            values='amount',
            names='symbol',
            title="Portfolio Allocation by Amount"
        )
        st.plotly_chart(fig_alloc, use_container_width=True)
    
    with col2:
        fig_risk = px.bar(
            portfolio.sort_values('annual_volatility'),
            x='symbol',
            y='annual_volatility',
            title="Annual Volatility by Coin",
            labels={'annual_volatility': 'Volatility (%)'}
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    
    fig_sharpe = px.bar(
        portfolio.sort_values('sharpe_ratio', ascending=False),
        x='symbol',
        y='sharpe_ratio',
        title="Sharpe Ratio by Coin (Risk-Adjusted Return)",
        labels={'sharpe_ratio': 'Sharpe Ratio'}
    )
    st.plotly_chart(fig_sharpe, use_container_width=True)
    
    # Full ranking table
    st.subheader("🏆 Full Top-20 Ranking")
    ranking_cols = ['symbol', 'name', 'current_price', 'annual_return', 'annual_volatility', 'sharpe_ratio', 'score']
    st.dataframe(
        ranked_df[ranking_cols].reset_index(drop=True).style.format({
            'current_price': '₨{:.2f}',
            'annual_return': '{:.2%}',
            'annual_volatility': '{:.2%}',
            'sharpe_ratio': '{:.3f}',
            'score': '{:.3f}'
        }),
        use_container_width=True
    )
else:
    st.info("👈 Click the **Analyze Top 20 & Get Recommendations** button in the sidebar to get started!")