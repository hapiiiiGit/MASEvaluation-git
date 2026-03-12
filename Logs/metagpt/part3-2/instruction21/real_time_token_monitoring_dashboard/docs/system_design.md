## Implementation approach

We will use Python for both backend and dashboard UI. For the dashboard, Streamlit is chosen for its simplicity and real-time update capabilities. Data fetching will use the official subgraph APIs (GraphQL) for Uniswap, PancakeSwap, and Sushiswap. The system will consist of modular fetchers for each DEX, a token analyzer to compare prices and filter opportunities, and a dashboard component for display. Async programming (asyncio, aiohttp) will be used for efficient real-time updates. Error handling and rate limiting will be built in.

## File list

- main.py
- dex_fetcher.py
- token_analyzer.py
- dashboard.py
- config.py
- requirements.txt
- docs/system_design.md

## Data structures and interfaces:

```mermaid
classDiagram
    class DEXFetcher {
        +__init__(name: str, endpoint: str)
        +fetch_tokens() -> dict[str, TokenData]
    }
    class TokenData {
        +name: str
        +contract_address: str
        +price: float
        +exchange: str
    }
    class TokenAnalyzer {
        +__init__(dex_fetchers: list[DEXFetcher])
        +get_common_tokens() -> dict[str, list[TokenData]]
        +find_arbitrage_opportunities(threshold: float=1.8) -> list[ArbitrageOpportunity]
    }
    class ArbitrageOpportunity {
        +token_name: str
        +contract_address: str
        +lowest_price: float
        +highest_price: float
        +lowest_exchange: str
        +highest_exchange: str
        +price_diff_percent: float
    }
    class Dashboard {
        +__init__(analyzer: TokenAnalyzer)
        +render_table(opportunities: list[ArbitrageOpportunity])
        +run()
    }
    DEXFetcher <.. TokenAnalyzer
    TokenAnalyzer <.. Dashboard
    TokenData <.. ArbitrageOpportunity
```

## Program call flow:

```mermaid
sequenceDiagram
    participant M as main.py
    participant DFU as DEXFetcher(Uniswap)
    participant DFP as DEXFetcher(PancakeSwap)
    participant DFS as DEXFetcher(Sushiswap)
    participant TA as TokenAnalyzer
    participant DB as Dashboard
    M->>DFU: fetch_tokens()
    M->>DFP: fetch_tokens()
    M->>DFS: fetch_tokens()
    DFU-->>M: return tokens
    DFP-->>M: return tokens
    DFS-->>M: return tokens
    M->>TA: get_common_tokens()
    TA-->>M: return common tokens
    M->>TA: find_arbitrage_opportunities(threshold=1.8)
    TA-->>M: return opportunities
    M->>DB: render_table(opportunities)
    DB-->>M: display dashboard
    Note over M,DB: Repeat every second
```

## Anything UNCLEAR

- Preferred dashboard framework: Streamlit is chosen for now, but Dash or Flask could be considered.
- Should the dashboard support mobile devices? (Streamlit is responsive but not optimized for mobile)
- Is user authentication required, or is public access sufficient?
- Should historical data be stored for later analysis?
