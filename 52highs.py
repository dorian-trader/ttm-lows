import yfinance as yf  # yfinance is an open-source Python library that allows users to download historical market data from Yahoo Finance
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import argparse
from pathlib import Path


def get_sp500_tickers():
    """
    Fetches the list of S&P 500 tickers from Wikipedia.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "constituents"})

    if table is None:
        raise Exception("Could not find the S&P 500 constituents table on Wikipedia")

    tickers = []
    for row in table.find_all("tr")[1:]:
        ticker = row.find_all("td")[0].text.strip()
        # Adjust ticker symbol for yfinance if needed
        if "." in ticker:
            ticker = ticker.replace(".", "-")
        tickers.append(ticker)
    return tickers


def fetch_stock_metrics(tickers):
    """
    Fetch 1-year pricing metrics for each ticker from Yahoo Finance.
    """
    results = []
    for i, ticker in enumerate(tickers):
        # print(f"Processing {ticker} ({i+1}/{len(tickers)})")
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if hist.empty:
                continue
            current_price = hist["Close"].iloc[-1]
            high_52wk = hist["Close"].max()
            distance = (high_52wk - current_price) / high_52wk
            results.append(
                {
                    "Ticker": ticker,
                    "Current Price": round(current_price, 2),
                    "52-Week Low": round(hist["Close"].min(), 2),
                    "52-Week High": round(high_52wk, 2),
                    "Distance %": round(distance * 100, 2),
                }
            )
            time.sleep(0.2)  # throttle requests
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    return results


def find_stocks_near_52_week_highs(metrics, threshold=0.15):
    """
    Filter pre-fetched metrics to stocks within threshold distance of 52-week highs.
    """
    max_distance_percent = threshold * 100
    return [item for item in metrics if item["Distance %"] <= max_distance_percent]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find S&P 500 stocks near their 52-week highs."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.15,
        help="Distance from 52-week high as decimal (default: 0.15 = 15%%).",
    )
    parser.add_argument(
        "--save-fetches",
        action="store_true",
        help="Fetch live Yahoo data and save full metrics to disk cache.",
    )
    parser.add_argument(
        "--load-fetches",
        action="store_true",
        help="Load previously saved metrics from disk cache instead of live Yahoo fetches.",
    )
    parser.add_argument(
        "--cache-file",
        default="yahoo_metrics_cache.csv",
        help="Path to CSV cache file used by --save-fetches/--load-fetches.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    cache_file = Path(args.cache_file)

    if args.load_fetches:
        if not cache_file.exists():
            raise FileNotFoundError(
                f"Cache file not found: {cache_file}. Run with --save-fetches first."
            )
        print(f"Loading cached Yahoo metrics from: {cache_file}")
        all_metrics = pd.read_csv(cache_file).to_dict(orient="records")
    else:
        print("Fetching S&P 500 tickers...")
        sp500_tickers = get_sp500_tickers()
        print(f"Total tickers retrieved: {len(sp500_tickers)}")
        print("Fetching live Yahoo metrics...")
        all_metrics = fetch_stock_metrics(sp500_tickers)

        if args.save_fetches:
            pd.DataFrame(all_metrics).to_csv(cache_file, index=False, float_format="%.2f")
            print(f"Saved Yahoo metrics cache to: {cache_file}")

    print("Analyzing stocks near 52-week highs...")
    near_highs = find_stocks_near_52_week_highs(all_metrics, args.threshold)

    if near_highs:
        df = pd.DataFrame(
            near_highs,
            columns=["Ticker", "Current Price", "52-Week Low", "52-Week High", "Distance %"],
        ).sort_values(by="Distance %")

        print("\nStocks near 52-week highs (CSV):")
        print(df.to_csv(index=False, float_format="%.2f"), end="")
    else:
        print("No stocks found within the specified threshold.")
