import json
import requests
import time
from datetime import datetime, timezone, timedelta

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
    """
    取昨日正式收盘价：
    用 v8/finance/chart 的日线历史数据，取最近已完成交易日的收盘价。
    range=5d 返回最近5个交易日，timestamps 对应每天开盘时间。
    过滤掉今天的数据，取最后一个完整交易日的 close。
    """
    # 用 period1/period2 明确指定日期范围，避免取到今天盘中数据
    now_utc = datetime.now(timezone.utc)
    # period2 = 今天0点UTC（不含今天）
    period2 = int(now_utc.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    # period1 = 7天前
    period1 = period2 - 7 * 86400

    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + yahoo_ticker
        + "?interval=1d"
        + "&period1=" + str(period1)
        + "&period2=" + str(period2)
    )
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
        closes = result['indicators']['quote'][0]['close']

        # 取最后一个非空收盘价（period2=今天0点，所以全是昨天或更早的数据）
        valid = [c for c in closes if c is not None]
        if not valid:
            print("FAIL " + yahoo_ticker + ": no close data")
            return None

        price = round(valid[-1], 4)
        print("OK " + yahoo_ticker + ": " + str(price))
        return price

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

    print("Updating " + str(len(active_tickers)) + " tickers...")

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
