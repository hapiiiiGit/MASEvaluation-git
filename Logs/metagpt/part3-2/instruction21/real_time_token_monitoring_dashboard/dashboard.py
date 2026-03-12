import streamlit as st
import pandas as pd
from typing import List
from token_analyzer import ArbitrageOpportunity, TokenAnalyzer
import time

class Dashboard:
    def __init__(self, analyzer: TokenAnalyzer):
        self.analyzer = analyzer

    def render_table(self, opportunities: List[ArbitrageOpportunity]):
        """
        Renders the arbitrage opportunities in a Streamlit table.
        """
        if not opportunities:
            st.info("No arbitrage opportunities found with price difference > 1.8%.")
            return

        # Prepare data for DataFrame
        data = []
        for opp in opportunities:
            data.append({
                "Token Name": opp.token_name,
                "Contract Address": opp.contract_address,
                "Lowest Price Exchange": opp.lowest_exchange,
                "Lowest Price (USD)": f"${opp.lowest_price:.6f}",
                "Highest Price Exchange": opp.highest_exchange,
                "Highest Price (USD)": f"${opp.highest_price:.6f}",
                "Price Difference (%)": f"{opp.price_diff_percent:.2f}%",
            })
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

    def run(self, fetch_and_analyze_callback):
        """
        Main dashboard loop. Calls fetch_and_analyze_callback to get arbitrage opportunities.
        Updates every second.
        """
        st.set_page_config(page_title="Real-Time DEX Arbitrage Dashboard", layout="wide")
        st.title("Real-Time DEX Arbitrage Dashboard")
        st.caption("Monitoring Uniswap, PancakeSwap, and Sushiswap for arbitrage opportunities (refreshes every second)")

        refresh_interval = 1  # seconds

        # Streamlit's session state to persist data between reruns
        if "last_update" not in st.session_state:
            st.session_state["last_update"] = 0

        # Main loop
        while True:
            start_time = time.time()
            with st.spinner("Fetching latest token data and analyzing opportunities..."):
                opportunities = fetch_and_analyze_callback()
            st.subheader("Arbitrage Opportunities (>1.8% price difference)")
            self.render_table(opportunities)
            st.write(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            # Wait for the next refresh
            elapsed = time.time() - start_time
            if elapsed < refresh_interval:
                time.sleep(refresh_interval - elapsed)
            # Rerun Streamlit script
            st.experimental_rerun()

# Example usage (for main.py):
# from token_analyzer import TokenAnalyzer
# analyzer = TokenAnalyzer([...])
# dashboard = Dashboard(analyzer)
# dashboard.run(fetch_and_analyze_callback)