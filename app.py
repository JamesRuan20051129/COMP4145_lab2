import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from trading_strategy import run_strategy


st.set_page_config(page_title="Golden Cross Trading Dashboard", page_icon="📈", layout="wide")


@st.cache_data(ttl=900)
def load_strategy_results(ticker):
    return run_strategy(ticker=ticker, period="5y")


def format_date(value):
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def show_price_chart(data, positions, ticker):
    st.title(f"{ticker} Price and Trading Signals")
    st.caption("Five years of historical closing prices with 50-day and 200-day moving averages.")

    figure = go.Figure()
    figure.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close", mode="lines",
                                line={"color": "#2563eb", "width": 2}))
    figure.add_trace(go.Scatter(x=data.index, y=data["MA50"], name="50-day MA", mode="lines",
                                line={"color": "#f59e0b", "width": 1.5}))
    figure.add_trace(go.Scatter(x=data.index, y=data["MA200"], name="200-day MA", mode="lines",
                                line={"color": "#7c3aed", "width": 1.5}))

    valid_positions = positions.dropna(subset=["BuyPrice", "SellPrice"])
    figure.add_trace(go.Scatter(
        x=valid_positions["BuyDate"], y=valid_positions["BuyPrice"],
        name="Buy", mode="markers", marker={"color": "#16a34a", "size": 10, "symbol": "triangle-up"},
        hovertemplate="Buy: %{x|%Y-%m-%d}<br>Price: $%{y:.2f}<extra></extra>",
    ))
    figure.add_trace(go.Scatter(
        x=valid_positions["SellDate"], y=valid_positions["SellPrice"],
        name="Sell", mode="markers", marker={"color": "#dc2626", "size": 10, "symbol": "triangle-down"},
        hovertemplate="Sell: %{x|%Y-%m-%d}<br>Price: $%{y:.2f}<extra></extra>",
    ))
    figure.update_layout(height=620, hovermode="x unified", margin={"l": 10, "r": 10, "t": 20, "b": 10},
                         yaxis_title="Price (USD)", legend_title="Series")
    st.plotly_chart(figure, use_container_width=True)


def show_statistics(positions, ticker):
    st.title("Overall Trade Statistics")
    st.caption(f"Summary of the golden-cross trades generated for {ticker}.")

    if positions.empty:
        st.info("No trading signals detected.")
        return

    wins = positions[positions["ProfitPct"] > 0]
    losses = positions[positions["ProfitPct"] <= 0]
    metrics = [
        ("Total trades", len(positions)),
        ("Winning trades", len(wins)),
        ("Losing trades", len(losses)),
        ("Win rate", f"{len(wins) / len(positions) * 100:.2f}%"),
        ("Average profit", f"{positions['ProfitPct'].mean():.2f}%"),
        ("Average holding period", f"{positions['HoldingDays'].mean():.1f} days"),
    ]
    columns = st.columns(len(metrics))
    for column, (label, value) in zip(columns, metrics):
        column.metric(label, value)

    reason_counts = positions["SellReason"].value_counts()
    st.subheader("Exit reasons")
    st.bar_chart(reason_counts)


def show_detailed_trades(positions):
    st.title("Detailed Trades")
    if positions.empty:
        st.info("No trading signals detected.")
        return

    display = positions.copy()
    for column in ["BuyDate", "SellDate"]:
        display[column] = display[column].map(format_date)
    for column in ["BuyPrice", "SellPrice"]:
        display[column] = display[column].map(lambda value: f"${value:.2f}" if pd.notna(value) else "N/A")
    display["ProfitPct"] = display["ProfitPct"].map(
        lambda value: f"{value:.2f}%" if pd.notna(value) else "N/A"
    )
    st.dataframe(display, use_container_width=True, hide_index=True)


st.sidebar.title("Trading Dashboard")
ticker = st.sidebar.text_input("Ticker", value="MSFT").strip().upper() or "MSFT"
page = st.sidebar.radio("Page", ["Price Chart", "Trade Statistics", "Detailed Trades"])

try:
    with st.spinner(f"Loading {ticker} data..."):
        stock_data, trade_positions = load_strategy_results(ticker)
except Exception as error:
    st.error(f"Unable to load data for {ticker}: {error}")
    st.stop()

if page == "Price Chart":
    show_price_chart(stock_data, trade_positions, ticker)
elif page == "Trade Statistics":
    show_statistics(trade_positions, ticker)
else:
    show_detailed_trades(trade_positions)
