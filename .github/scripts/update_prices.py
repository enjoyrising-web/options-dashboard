import json
import requests
import time
from datetime import datetime, timezone

TICKER_MAP = {
    '700.HK':  '0700.HK',
    '3800.HK': '3800.HK',
    '9988.HK': '9988.HK',
    '3690.HK': '3690.HK',
    '9660.HK': '9660.HK',
    '981.HK':  '0981.HK',
    '9863.HK': '9863.HK',
    '9999.HK': '9999.HK',
    '175.HK':  '0175.HK',
    '883.HK':  '0883.HK',
    '1093.HK': '1093.HK',
    '9626.HK': '9626.HK',
    '2269.HK': '2269.HK',
    '1347.HK': '1347.HK',
    'AMD':    'AMD',
    'TSM':    'TSM',
    'GOOGL':  'GOOGL',
    'GOOG':   'GOOG',
    'AAPL':   'AAPL',
    'PLTR':   'PLTR',
    'INTC':   'INTC',
    'PDD':    'PDD',
    'MU':     'MU',
    '9984.T': '9984.T',
    '6762.T': '6762.T',
    '6981.T': '6981.T',
}

def fetch_prev_close(yahoo_ticker):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + yahoo_ticker + "?interval=1d&range=5d"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print("FAIL " + yahoo_ticker + ": HTTP " + str(r.status_code))
            return None

        data = r.json()
        result = data['chart']['result'][0]

        # Use previousClose from meta - always yesterday's close regardless of market hours
        meta = result.get('meta', {})
        prev_close = meta.get('previousClose') or meta.get('chartPreviousClose')

        if prev_close:
            price = round(float(prev_close), 4)
            print("OK " + yahoo_ticker + ": " + str(price) + " (previousClose)")
            return price

        # Fallback: get last close before today
        timestamps = result.get('timestamp', [])
        closes = result['indicators']['quote'][0]['close']
        now_utc = datetime.now(timezone.utc)
        today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

        prev_closes = [cl for ts, cl in zip(timestamps, closes) if cl is not None and ts < today_start]
        if prev_closes:
            price = round(prev_closes[-1], 4)
            print("OK " + yahoo_ticker + ": " + str(price) + " (historical close)")
            return price

        print("FAIL " + yahoo_ticker + ": no valid close found")
        return None

    except Exception as e:
        print("FAIL " + yahoo_ticker + ": " + str(e))
        return None

def main():
    with open('data/products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data['products']
    active_tickers = set()
    for p in products:
        ticker = p.get('ticker', '')
        if ticker and p.get('status') == '\u5b58\u7eed\u4e2d':
            active_tickers.add(ticker)

    print("Updating " + str(len(active_tickers)) + " tickers (previousClose)...")

    prices = {}
    for our_ticker in sorted(active_tickers):
        yahoo_ticker = TICKER_MAP.get(our_ticker, our_ticker)
        price = fetch_prev_close(yahoo_ticker)
        if price:
            prices[our_ticker] = price
        time.sleep(0.5)

    updated = 0
    for p in products:
        ticker = p.get('ticker', '')
        if ticker in prices:
            old_close = p.get('close')
            p['close'] = prices[ticker]
            if old_close != prices[ticker]:
                updated += 1

    now = datetime.now(timezone.utc)
    data['priceUpdatedAt'] = now.strftime('%Y-%m-%d %H:%M UTC')
    data['updatedAt'] = now.strftime('%Y-%m-%d')

    with open('data/products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Done: updated " + str(updated) + " of " + str(len(prices)) + "/" + str(len(active_tickers)))

if __name__ == '__main__':
    main()
