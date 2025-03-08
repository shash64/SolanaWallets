import requests
from datetime import datetime

def get_memecoin_info(contract_address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def calculate_risk_percentage(risk_factors):

    total_weight = sum(risk_factors.values())
    max_weight = 100  
    risk_percentage = (total_weight / max_weight) * 100
    return min(risk_percentage, 100) 

def is_honeypot(token_info):
    pairs = token_info.get('pairs', [])
    if not pairs:
        return "Alert: No pairs found for this token.", 100

    pair = pairs[0]  
    txns_24h = pair.get('txns', {}).get('h24', {})
    txns_6h = pair.get('txns', {}).get('h6', {})
    txns_1h = pair.get('txns', {}).get('h1', {})
    buys_24h = txns_24h.get('buys', 0)
    sells_24h = txns_24h.get('sells', 0)
    buys_6h = txns_6h.get('buys', 0)
    sells_6h = txns_6h.get('sells', 0)
    buys_1h = txns_1h.get('buys', 0)
    sells_1h = txns_1h.get('sells', 0)
    price_change_24h = pair.get('priceChange', {}).get('h24', 0)
    liquidity_usd = pair.get('liquidity', {}).get('usd', 0)
    pair_created_at = pair.get('pairCreatedAt', 0) / 1000  
    market_cap = pair.get('marketCap', 0)  
    info = pair.get('info', {}) 

    # ratio
    buy_sell_ratio_threshold_24h = 2.2
    buy_sell_ratio_threshold_6h = 2.3
    buy_sell_ratio_threshold_1h = 2.5
    price_change_threshold = 100000
    min_liquidity_threshold = 10000
    very_min_liquidity = 1000
    recent_pair_threshold = 2 * 3600 
    very_recent_pair_threshold = 1 * 3600 
    market_cap_threshold_high = 250000000 
    market_cap_threshold_low = 100000000 
    price_change_market_cap_threshold = 100000
  
    risk_factors = {}

    # check criteria
    if datetime.now().timestamp() - pair_created_at < very_recent_pair_threshold and market_cap > market_cap_threshold_low:
        risk_factors["The pair was created less than an hour ago and the Market Cap is over 100 million."] = 30

    if datetime.now().timestamp() - pair_created_at < recent_pair_threshold:
        risk_factors["The pair was created recently."] = 5

    if sells_24h == 0 and buys_24h > 0 or (sells_24h > 0 and buys_24h / sells_24h > buy_sell_ratio_threshold_24h):
        risk_factors["The buy/sell ratio in the last 24 hours is anormally high or there are no sells."] = 20

    if sells_6h == 0 and buys_6h > 0 or (sells_6h > 0 and buys_6h / sells_6h > buy_sell_ratio_threshold_6h):
        risk_factors["The buy/sell ratio in the last 6 hours is anormally high or there are no sells."] = 15

    if sells_1h == 0 and buys_1h > 0 or (sells_1h > 0 and buys_1h / sells_1h > buy_sell_ratio_threshold_1h):
        risk_factors["The buy/sell ratio in the last hour is anormally high or there are no sells."] = 10

    if price_change_24h > price_change_threshold:
        risk_factors["The price change in the last 24 hours is anormally high."] = 15

    if liquidity_usd < min_liquidity_threshold and liquidity_usd > very_min_liquidity:
        risk_factors["Liquidity is low."] = 5

    if liquidity_usd < very_min_liquidity:
        risk_factors["Liquidity is very low."] = 10

    if market_cap > market_cap_threshold_high and price_change_24h > price_change_market_cap_threshold:
        risk_factors["The Market Cap is over 250 million and the price change in the last 24 hours is over 100,000."] = 20

    if market_cap > market_cap_threshold_low and not info:
        risk_factors["The Market Cap is over 100 million and the crypto has no information."] = 25

    if not info:
        risk_factors["The crypto has no information."] = 5
    risk_percentage = calculate_risk_percentage(risk_factors)

    if risk_factors:
        alerts = "\n".join(risk_factors.keys())
        return f"Alert: The token may be a honeypot.\nRisk factors:\n{alerts}\nRisk percentage: {risk_percentage:.2f}%", risk_percentage
    else:
        return None, 0

if __name__ == "__main__":
    contract_address = input("Enter the memecoin contract address: ")
    memecoin_info = get_memecoin_info(contract_address)

    if memecoin_info:
        alert, risk_percentage = is_honeypot(memecoin_info)
        if alert:
            print(alert)
        else:
            print("The token does not appear to be a honeypot.")
    else:
        print("Unable to retrieve memecoin information.")
