import argparse
import time
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup


def get_sp500_tickers():
    """
    Fetch the list of S&P 500 tickers from Wikipedia.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "constituents"})

    if table is None:
        raise Exception("Could not find the S&P 500 constituents table on Wikipedia")

    tickers = []
    for row in table.find_all("tr")[1:]:
        ticker = row.find_all("td")[0].text.strip()
        if "." in ticker:
            ticker = ticker.replace(".", "-")
        tickers.append(ticker)
    return tickers


def fetch_stock_metrics(tickers):
    """
    Fetch daily candles and compute 200-day moving-average proximity for each ticker.
    """
    results = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2y", interval="1d")
            if hist.empty or len(hist.index) < 200:
                continue

            hist = hist.copy()
            hist["SMA200"] = hist["Close"].rolling(window=200).mean()
            latest = hist.dropna(subset=["SMA200"]).iloc[-1]

            current_price = float(latest["Close"])
            sma_200 = float(latest["SMA200"])
            distance_pct = ((current_price - sma_200) / sma_200) * 100

            results.append(
                {
                    "Ticker": ticker,
                    "Current Price": round(current_price, 2),
                    "SMA200": round(sma_200, 2),
                    "Distance %": round(distance_pct, 2),
                    "Abs Distance %": round(abs(distance_pct), 2),
                }
            )
            time.sleep(0.2)
        except Exception as exc:
            print(f"Error processing {ticker}: {exc}")
            continue
    return results


def find_stocks_near_sma200(metrics, threshold=0.03):
    """
    Return stocks whose close is within threshold distance of the 200-day moving average.
    """
    max_distance_percent = threshold * 100
    return [item for item in metrics if item["Abs Distance %"] <= max_distance_percent]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find S&P 500 stocks near their 200-day moving average."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.03,
        help="Distance from 200-day moving average as decimal (default: 0.03 = 3%%).",
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
        default="yahoo_ma200_metrics_cache.csv",
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

    print("Analyzing stocks near 200-day moving average...")
    near_ma200 = find_stocks_near_sma200(all_metrics, args.threshold)

    if near_ma200:
        df = pd.DataFrame(
            near_ma200,
            columns=["Ticker", "Current Price", "SMA200", "Distance %", "Abs Distance %"],
        ).sort_values(by="Abs Distance %")

        print("\nBuffett stocks near 200-day moving average (CSV):")
        print(df.to_csv(index=False, float_format="%.2f"), end="")
    else:
        print("No stocks found within the specified threshold.")
