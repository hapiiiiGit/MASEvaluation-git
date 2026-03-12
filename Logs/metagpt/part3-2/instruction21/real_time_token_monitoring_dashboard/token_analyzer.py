from typing import List, Dict, Optional
from dex_fetcher import TokenData

class ArbitrageOpportunity:
    def __init__(
        self,
        token_name: str,
        contract_address: str,
        lowest_price: float,
        highest_price: float,
        lowest_exchange: str,
        highest_exchange: str,
        price_diff_percent: float,
    ):
        self.token_name = token_name
        self.contract_address = contract_address
        self.lowest_price = lowest_price
        self.highest_price = highest_price
        self.lowest_exchange = lowest_exchange
        self.highest_exchange = highest_exchange
        self.price_diff_percent = price_diff_percent

class TokenAnalyzer:
    def __init__(self, dex_fetchers: List):
        """
        dex_fetchers: List of DEXFetcher instances
        """
        self.dex_fetchers = dex_fetchers

    def get_common_tokens(
        self, tokens_by_dex: List[Dict[str, TokenData]]
    ) -> Dict[str, List[TokenData]]:
        """
        Finds tokens available on at least two exchanges.
        Returns a dict mapping contract_address to list of TokenData (from different exchanges).
        """
        token_map: Dict[str, List[TokenData]] = {}
        for dex_tokens in tokens_by_dex:
            for contract_address, token_data in dex_tokens.items():
                if contract_address not in token_map:
                    token_map[contract_address] = []
                token_map[contract_address].append(token_data)
        # Filter: only tokens present on at least two exchanges
        common_tokens = {
            k: v for k, v in token_map.items() if len(v) >= 2
        }
        return common_tokens

    def find_arbitrage_opportunities(
        self,
        tokens_by_dex: List[Dict[str, TokenData]],
        threshold: float = 1.8,
    ) -> List[ArbitrageOpportunity]:
        """
        Finds arbitrage opportunities for tokens available on at least two exchanges.
        Returns a list of ArbitrageOpportunity objects where price difference > threshold (%).
        """
        opportunities: List[ArbitrageOpportunity] = []
        common_tokens = self.get_common_tokens(tokens_by_dex)
        for contract_address, token_datas in common_tokens.items():
            # Find lowest and highest price and corresponding exchanges
            lowest: Optional[TokenData] = None
            highest: Optional[TokenData] = None
            for td in token_datas:
                if lowest is None or td.price < lowest.price:
                    lowest = td
                if highest is None or td.price > highest.price:
                    highest = td
            if lowest is None or highest is None or lowest.price == 0:
                continue
            price_diff_percent = ((highest.price - lowest.price) / lowest.price) * 100
            if price_diff_percent > threshold:
                opportunity = ArbitrageOpportunity(
                    token_name=lowest.name,
                    contract_address=contract_address,
                    lowest_price=lowest.price,
                    highest_price=highest.price,
                    lowest_exchange=lowest.exchange,
                    highest_exchange=highest.exchange,
                    price_diff_percent=price_diff_percent,
                )
                opportunities.append(opportunity)
        return opportunities