# COMP4145_lab2

## Trading strategy dashboard

This project backtests a Microsoft golden-cross strategy using five years of
historical data. The Streamlit dashboard provides:

- A price chart with the closing price, 50-day moving average, 200-day moving
  average, and buy/sell markers.
- Overall trade statistics.
- A detailed trade record.

## Run the dashboard

Install the dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start the dashboard:

```bash
python3 -m streamlit run app.py
```

The application requires internet access to download market data through
`yfinance`.
