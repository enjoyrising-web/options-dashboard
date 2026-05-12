bash

cat /home/claude/github_actions/.github/scripts/update_prices.py
Output

"""
每日自动更新收盘价脚本
从 Yahoo Finance 查询收盘价，更新 data/products.json
"""
import json, requests, time
from datetime import datetime, timezone

# ── 标的 ticker 映射 ─────────────────────────────────────────
# 格式: products.json里的ticker → Yahoo Finance ticker
TICKER_MAP = {
    # 港股（加 .HK 后缀）
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
    # 美股（直接用 ticker）
    'AMD':   'AMD',
    'TSM':   'TSM',
    'GOOGL': 'GOOGL',
    'GOOG':  'GOOG',
    'AAPL':  'AAPL',
    'PLTR':  'PLTR',
    'INTC':  'INTC',
    'PDD':   'PDD',
    'MU':    'MU',
    # 日股（加 .T 后缀）
    '9984.T': '9984.T',
    '6762.T': '6762.T',
    '6981.T': '6981.T',
}

def fetch_close(yahoo_ticker):
    """从 Yahoo Finance 获取最新收盘价"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_ticker}?interval=1d&range=5d"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"  ✗ {yahoo_ticker}: HTTP {r.status_code}")
            return None
        data = r.json()
        result = data['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        close = [c for c in closes if c is not None]
        if not close:
            return None
        price = round(close[-1], 4)
        print(f"  ✓ {yahoo_ticker}: {price}")
        return price
    except Exception as e:
        print(f"  ✗ {yahoo_ticker}: {e}")
        return None

def main():
    # 读取现有数据
    with open('data/products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data['products']

    # 获取所有需要更新的 tickers（只更新存续中的产品）
    active_tickers = set()
    for p in products:
        ticker = p.get('ticker', '')
        if ticker and p.get('status') == '存续中':
            active_tickers.add(ticker)

    print(f"需要更新 {len(active_tickers)} 个标的收盘价...")

    # 查询收盘价
    prices = {}
    for our_ticker in sorted(active_tickers):
        yahoo_ticker = TICKER_MAP.get(our_ticker, our_ticker)
        price = fetch_close(yahoo_ticker)
        if price:
            prices[our_ticker] = price
        time.sleep(0.5)  # 避免请求过快

    # 更新 products
    updated = 0
    for p in products:
        ticker = p.get('ticker', '')
        if ticker in prices:
            old_close = p.get('close')
            p['close'] = prices[ticker]
            if old_close != prices[ticker]:
                updated += 1

    # 更新时间戳
    now = datetime.now(timezone.utc)
    data['priceUpdatedAt'] = now.strftime('%Y-%m-%d %H:%M UTC')
    data['updatedAt'] = now.strftime('%Y-%m-%d')

    # 保存
    with open('data/products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n完成：更新了 {updated} 个标的，共查询 {len(prices)}/{len(active_tickers)} 成功")
    print(f"更新时间: {data['priceUpdatedAt']}")

if __name__ == '__main__':
    main()
