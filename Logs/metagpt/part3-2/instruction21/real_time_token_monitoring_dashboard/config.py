# config.py
# Configuration for real_time_token_monitoring_dashboard

# DEX GraphQL endpoints
UNISWAP_V3_ENDPOINT = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
PANCAKESWAP_ENDPOINT = "https://bsc.streamingfast.io/subgraphs/name/pancakeswap/exchange-v2"
SUSHISWAP_ENDPOINT = "https://api.thegraph.com/subgraphs/name/sushiswap/exchange"

DEX_CONFIGS = [
    {"name": "Uniswap", "endpoint": UNISWAP_V3_ENDPOINT},
    {"name": "PancakeSwap", "endpoint": PANCAKESWAP_ENDPOINT},
    {"name": "Sushiswap", "endpoint": SUSHISWAP_ENDPOINT},
]

# Arbitrage threshold in percent
ARBITRAGE_THRESHOLD = 1.8

# Number of tokens to fetch per DEX (can be tuned for performance)
TOKENS_FETCH_LIMIT = 100

# GraphQL query for fetching tokens (used in dex_fetcher.py)
GRAPHQL_TOKEN_QUERY = """
{
  tokens(first: %d, orderBy: volumeUSD, orderDirection: desc) {
    id
    symbol
    name
    derivedETH
    derivedUSD
  }
}
""" % TOKENS_FETCH_LIMIT

# CoinGecko API endpoint for ETH price (used as fallback in dex_fetcher.py)
COINGECKO_ETH_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"

# Dashboard settings
DASHBOARD_TITLE = "Real-Time DEX Arbitrage Dashboard"
DASHBOARD_REFRESH_INTERVAL = 1  # seconds

# Error handling
API_TIMEOUT_SECONDS = 15
API_RETRY_COUNT = 2

# You can add more configuration options as needed for future features.