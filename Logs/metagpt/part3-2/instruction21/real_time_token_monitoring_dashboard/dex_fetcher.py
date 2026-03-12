import asyncio
import aiohttp
from typing import Dict

class TokenData:
    def __init__(self, name: str, contract_address: str, price: float, exchange: str):
        self.name = name
        self.contract_address = contract_address
        self.price = price
        self.exchange = exchange

class DEXFetcher:
    def __init__(self, name: str, endpoint: str):
        self.name = name
        self.endpoint = endpoint

    async def fetch_tokens(self) -> Dict[str, TokenData]:
        """
        Fetches token data from the DEX GraphQL endpoint.
        Returns a dict mapping contract_address to TokenData.
        """
        # GraphQL queries for each DEX (Uniswap, PancakeSwap, Sushiswap)
        # These queries fetch top tokens by liquidity and their price.
        # For production, you may want to paginate or fetch more tokens.
        query = """
        {
          tokens(first: 100, orderBy: volumeUSD, orderDirection: desc) {
            id
            symbol
            name
            derivedETH
            derivedUSD
          }
        }
        """
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "query": query
        }
        tokens = {}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, json=payload, headers=headers, timeout=15) as resp:
                    if resp.status != 200:
                        print(f"[{self.name}] Error: Received status {resp.status}")
                        return tokens
                    data = await resp.json()
                    for token in data.get("data", {}).get("tokens", []):
                        contract_address = token.get("id")
                        name = token.get("name") or token.get("symbol") or contract_address
                        # Prefer derivedUSD if available, else fallback to derivedETH (approximate with ETH price)
                        price = None
                        if token.get("derivedUSD") is not None:
                            try:
                                price = float(token["derivedUSD"])
                            except Exception:
                                price = None
                        elif token.get("derivedETH") is not None:
                            # Fallback: Use ETH price from CoinGecko (could cache for efficiency)
                            eth_price = await self._get_eth_price()
                            try:
                                price = float(token["derivedETH"]) * eth_price
                            except Exception:
                                price = None
                        if price is not None:
                            tokens[contract_address] = TokenData(
                                name=name,
                                contract_address=contract_address,
                                price=price,
                                exchange=self.name
                            )
        except Exception as e:
            print(f"[{self.name}] Exception during fetch: {e}")
        return tokens

    async def _get_eth_price(self) -> float:
        """
        Fetches the current ETH price in USD from CoinGecko.
        Used as a fallback if derivedUSD is not available.
        """
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status != 200:
                        return 0.0
                    data = await resp.json()
                    return float(data.get("ethereum", {}).get("usd", 0.0))
        except Exception:
            return 0.0

# Example DEX endpoints (mainnet)
UNISWAP_V3_ENDPOINT = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
PANCAKESWAP_ENDPOINT = "https://bsc.streamingfast.io/subgraphs/name/pancakeswap/exchange-v2"
SUSHISWAP_ENDPOINT = "https://api.thegraph.com/subgraphs/name/sushiswap/exchange"

# For testing purposes
if __name__ == "__main__":
    async def main():
        fetchers = [
            DEXFetcher("Uniswap", UNISWAP_V3_ENDPOINT),
            DEXFetcher("PancakeSwap", PANCAKESWAP_ENDPOINT),
            DEXFetcher("Sushiswap", SUSHISWAP_ENDPOINT)
        ]
        results = await asyncio.gather(*(f.fetch_tokens() for f in fetchers))
        for dex, tokens in zip(fetchers, results):
            print(f"--- {dex.name} ---")
            for t in list(tokens.values())[:5]:  # Print top 5 tokens for brevity
                print(f"{t.name} ({t.contract_address}): ${t.price:.4f}")

    asyncio.run(main())