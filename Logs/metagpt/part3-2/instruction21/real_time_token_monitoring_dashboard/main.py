import asyncio
from typing import List, Dict
from dex_fetcher import DEXFetcher, TokenData, UNISWAP_V3_ENDPOINT, PANCAKESWAP_ENDPOINT, SUSHISWAP_ENDPOINT
from token_analyzer import TokenAnalyzer, ArbitrageOpportunity
from dashboard import Dashboard
import streamlit as st

# Configuration
DEX_CONFIGS = [
    {"name": "Uniswap", "endpoint": UNISWAP_V3_ENDPOINT},
    {"name": "PancakeSwap", "endpoint": PANCAKESWAP_ENDPOINT},
    {"name": "Sushiswap", "endpoint": SUSHISWAP_ENDPOINT},
]
ARBITRAGE_THRESHOLD = 1.8  # percent

def create_dex_fetchers() -> List[DEXFetcher]:
    return [DEXFetcher(cfg["name"], cfg["endpoint"]) for cfg in DEX_CONFIGS]

async def fetch_all_tokens(dex_fetchers: List[DEXFetcher]) -> List[Dict[str, TokenData]]:
    return await asyncio.gather(*(dex.fetch_tokens() for dex in dex_fetchers))

def fetch_and_analyze_callback_factory(dex_fetchers, analyzer):
    """
    Returns a callback function for the dashboard to fetch and analyze arbitrage opportunities.
    This function will be called by the dashboard every second.
    """
    def fetch_and_analyze_callback():
        # Run async fetching in a synchronous context for Streamlit
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tokens_by_dex = loop.run_until_complete(fetch_all_tokens(dex_fetchers))
        opportunities = analyzer.find_arbitrage_opportunities(tokens_by_dex, threshold=ARBITRAGE_THRESHOLD)
        return opportunities
    return fetch_and_analyze_callback

def main():
    dex_fetchers = create_dex_fetchers()
    analyzer = TokenAnalyzer(dex_fetchers)
    dashboard = Dashboard(analyzer)
    fetch_and_analyze_callback = fetch_and_analyze_callback_factory(dex_fetchers, analyzer)
    dashboard.run(fetch_and_analyze_callback)

if __name__ == "__main__":
    main()