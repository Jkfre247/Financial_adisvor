from .imports import *
from .growth_portfolio import *


def run_growth_portfolio():
    st.subheader("Balanced Portfolio")

    st.write("""
    This strategy is a balanced investment option (note that it is a historical analysis).
    Keep in mind that cryptocurrency and stock prices may be slightly skewed due to prolonged bull markets 
    in these sectors. 
    **By investing, you invest at your own risk.**
    """)

    # Cryptocurrency selection
    crypto_choice = st.selectbox(
        "Choose a cryptocurrency",
        ["Bitcoin (BTC)", "Ethereum (ETH)"],
        index=0
    )
    crypto_ticker = "BTC-USD" if crypto_choice == "Bitcoin (BTC)" else "ETH-USD"

    # Starting year
    min_year = 2015 if crypto_ticker == "BTC-USD" else 2018
    current_year = datetime.now().year
    years_list = list(range(min_year, current_year + 1))
    start_year = st.selectbox(
        f"Choose a starting year (for {crypto_choice}, minimum {min_year})",
        years_list,
        index=0
    )

    # Bond yield rate
    yield_options = [0.005 * i for i in range(1, 8)]
    yield_rate = st.selectbox("Bond yield rate (decimal value)", yield_options, index=2)

    # Inflation
    inflation_percent = st.slider("Annual inflation (%)", 1, 5, 3, 1)
    inflation = inflation_percent / 100.0

    # Annual investment
    yearly_investment_input = st.text_input("Annual investment (USD)", "5000")
    try:
        yearly_investment = int(yearly_investment_input)
        if yearly_investment <= 100:
            raise ValueError("Investment amount must be greater than 100!")
    except ValueError as e:
        st.error(f"Error: {e}")
        st.stop()

    st.write("### Set asset proportions")
    col1, col2, col3 = st.columns(3)

    with col1:
        gold_pro = st.slider("Gold (%)", 0, 100, 15, step=1)
        bonds_pro = st.slider("Bonds (%)", 0, 100, 30, step=1)

    with col2:
        etf_em_pro = st.slider("ETF Emerging Markets (%)", 0, 100, 20, step=1)
        etf_msci_pro = st.slider("ETF MSCI World (%)", 0, 100, 30, step=1)

    with col3:
        crypto_pro = st.slider("Cryptocurrencies (%)", 0, 100, 5, step=1)

    # Check if proportions sum to 100%
    total_pro = gold_pro + bonds_pro + etf_em_pro + etf_msci_pro + crypto_pro
    if total_pro != 100:
        st.error(f"Asset proportions must sum to 100%! Current sum: {total_pro}%")
        st.stop()

    if st.button("Run simulation"):
        bond_asset = BondAsset(inflation, yield_rate)
        strategy = InvestmentStrategy(rise_investment=1)

        portfolio = GrowthPortfolio(
            gold_pro=gold_pro / 100.0,  # Convert percentages to fractions
            etf_em_pro=etf_em_pro / 100.0,
            etf_msci_pro=etf_msci_pro / 100.0,
            bonds_pro=bonds_pro / 100.0,
            crypto_pro=crypto_pro / 100.0
        )

        assets = {
            "gold": Asset("GC=F"),
            "etf_em": Asset("EEM"),
            "etf_msci": Asset("URTH"),
            "crypto": Asset(crypto_ticker)
        }

        current_year_num = datetime.now().year
        duration_years = current_year_num - start_year

        sim = GrowthSimulation(
            portfolio=portfolio,
            assets=assets,
            bond_asset=bond_asset,
            strategy=strategy,
            start_year=start_year,
            years=duration_years
        )

        results = sim.run(yearly_investment)
        df_results = pd.DataFrame(results)

        df_results['Gold Value'] = df_results['Gold Units'] * df_results['Gold Price']
        df_results['ETF EM Value'] = df_results['ETF EM Units'] * df_results['ETF EM Price']
        df_results['ETF MSCI Value'] = df_results['ETF MSCI Units'] * df_results['ETF MSCI Price']
        df_results['Crypto Value'] = df_results['Crypto Units'] * df_results['Crypto Price']

        # ========== Drawing charts ==========

        # Chart 1: Assets + Total and Invested
        fig_assets = go.Figure()
        fig_assets.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Gold Value'],
            mode='lines',
            name='Gold Value',
            line=dict(color='gold')
        ))
        fig_assets.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Bonds'],
            mode='lines',
            name='Bond Value',
            line=dict(color='orange')
        ))
        fig_assets.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['ETF MSCI Value'],
            mode='lines',
            name='ETF MSCI World',
            line=dict(color='blue')
        ))
        fig_assets.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['ETF EM Value'],
            mode='lines',
            name='ETF Emerging Markets',
            line=dict(color='green')
        ))
        fig_assets.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Crypto Value'],
            mode='lines',
            name='Cryptocurrency Value',
            line=dict(color='purple')
        ))
        fig_assets.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Invested'],
            mode='lines',
            name='Invested Funds',
            line=dict(color='blue', dash='dot')
        ))
        fig_assets.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Total'],
            mode='lines',
            name='Total Portfolio Value',
            line=dict(color='green', dash='dot')
        ))
        fig_assets.update_layout(
            title='Portfolio Breakdown: Gold, Bonds, ETFs, Cryptocurrencies, and Total Value',
            xaxis_title='Date',
            yaxis_title='Value (USD)',
            legend_title='Assets',
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_assets, use_container_width=True)

        # Calculations summary
        total_invested = df_results['Invested'].iloc[-1]
        total_value = df_results['Total'].iloc[-1]
        growth_percent = ((total_value - total_invested) / total_invested) * 100

        # Asset quantities
        gold_units = df_results['Gold Units'].iloc[-1]
        gold_value = df_results['Gold Value'].iloc[-1]
        bonds_value = df_results['Bonds'].iloc[-1]
        etf_em_units = df_results['ETF EM Units'].iloc[-1]
        etf_em_value = df_results['ETF EM Value'].iloc[-1]
        etf_msci_units = df_results['ETF MSCI Units'].iloc[-1]
        etf_msci_value = df_results['ETF MSCI Value'].iloc[-1]
        crypto_units = df_results['Crypto Units'].iloc[-1]
        crypto_value = df_results['Crypto Value'].iloc[-1]

        # Display summary
        st.write("### Portfolio Summary")
        st.markdown(f"**Invested amount:** {total_invested:,.2f} USD  \n"
                    f"**Total portfolio value:** {total_value:,.2f} USD  \n"
                    f"**Portfolio growth:** {growth_percent:,.2f}%  \n")

        st.write("### Asset Details")
        st.markdown(f"**Gold:** {gold_units:,.2f} units - {gold_value:,.2f} USD  \n"
                    f"**Bonds:** {bonds_value:,.2f} USD  \n"
                    f"**ETF Emerging Markets:** {etf_em_units:,.2f} units - {etf_em_value:,.2f} USD  \n"
                    f"**ETF MSCI World:** {etf_msci_units:,.2f} units - {etf_msci_value:,.2f} USD  \n"
                    f"**Cryptocurrencies:** {crypto_units:,.2f} units - {crypto_value:,.2f} USD  \n")

        st.write("### Asset Charts")

        # Chart 2: Gold (price)
        fig_gold = go.Figure()
        fig_gold.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Gold Price'],
            mode='lines',
            name='Gold Price',
            line=dict(color='gold')
        ))
        fig_gold.update_layout(
            title='Gold Price Chart',
            xaxis_title='Date',
            yaxis_title='Gold Price (USD)',
            legend_title='Gold',
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_gold, use_container_width=True)

        # Chart 3: Cryptocurrency (price)
        fig_crypto = go.Figure()
        fig_crypto.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Crypto Price'],
            mode='lines',
            name='Cryptocurrency Price',
            line=dict(color='purple')
        ))
        fig_crypto.update_layout(
            title=f'{crypto_choice} Price Over Time',
            xaxis_title='Date',
            yaxis_title='Cryptocurrency Price (USD)',
            legend_title='Cryptocurrency',
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_crypto, use_container_width=True)

        # Chart 4: ETFs (prices)
        fig_etfs = go.Figure()
        fig_etfs.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['ETF MSCI Price'],
            mode='lines',
            name='ETF MSCI Price',
            line=dict(color='blue')
        ))
        fig_etfs.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['ETF EM Price'],
            mode='lines',
            name='ETF EM Price',
            line=dict(color='green')
        ))
        fig_etfs.update_layout(
            title='ETF Prices: MSCI World (URTH) and EM (EEM)',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            legend_title='ETF Prices',
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_etfs, use_container_width=True)

    st.write("**By investing, you invest at your own risk.**")
