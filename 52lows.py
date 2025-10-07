import yfinance as yf # yfinance is an open-source Python library that allows users to download historical market data from Yahoo Finance
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def get_sp500_tickers():
    """
    Fetches the list of S&P 500 tickers from Wikipedia.
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    
    if table is None:
        raise Exception("Could not find the S&P 500 constituents table on Wikipedia")
    
    tickers = []
    for row in table.find_all('tr')[1:]:
        ticker = row.find_all('td')[0].text.strip()
        # Adjust ticker symbol for yfinance if needed
        if '.' in ticker:
            ticker = ticker.replace('.', '-')
        tickers.append(ticker)
    return tickers

def find_stocks_near_52_week_lows(tickers, threshold=0.10):
    results = []
    for i, ticker in enumerate(tickers):
        # print(f"Processing {ticker} ({i+1}/{len(tickers)})")
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if hist.empty:
                continue
            current_price = hist['Close'].iloc[-1]
            low_52wk = hist['Close'].min()
            distance = (current_price - low_52wk) / low_52wk
            if distance <= threshold:
                results.append({
                    'Ticker': ticker,
                    'Current Price': round(current_price, 2),
                    '52-Week Low': round(low_52wk, 2),
                    '52-Week High': round(hist['Close'].max(), 2),
                    'Distance %': round(distance * 100, 2)
                })
            time.sleep(0.2)  # throttle requests
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    return results

if __name__ == "__main__":
    threshold = 0.15  # less than 15% off 52 weeks low
    print("Fetching S&P 500 tickers...")
    sp500_tickers = get_sp500_tickers()
    print(f"Total tickers retrieved: {len(sp500_tickers)}")
    print("Analyzing stocks near 52-week lows...")
    near_lows = find_stocks_near_52_week_lows(sp500_tickers, threshold)

if near_lows:
    df = pd.DataFrame(near_lows, columns=["Ticker", "Current Price", "52-Week Low", "52-Week High", "Distance %"])
    df = df.sort_values(by='Distance %')
    
    print("\nStocks near 52-week lows:\n")
    print("Stock | Current Price | 52-Week Low | 52-Week High")
    print("------|---------------|-------------|--------------")
    
    for row in df.itertuples(index=False):
        print(f"{row.Ticker:<5} | ${row._1:<13} | ${row._2:<11} | ${row._3:<12}")
        print(f"       ↳ Distance from low: {row._4:.2f}%\n")
else:
    print("No stocks found within the specified threshold.")