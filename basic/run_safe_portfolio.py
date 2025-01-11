from .imports import *
from .assets import *
from .safe_portfolio import *

def run_defensive_portfolio():
    st.subheader("Defensive Portfolio (Bonds + Gold)")

    st.write("""
    This option is a safe choice, based on the most stable assets. 
    Gold, although characterized by small price fluctuations, retains its value in the long term. 
    Bonds, especially in stable countries, pose minimal risk to an investment portfolio.
    """)

    # SELECT STARTING YEAR
    current_year = datetime.now().year
    years_list = list(range(2002, current_year + 1))
    start_year = st.selectbox(
        "Select starting year",
        years_list,
        index=(years_list.index(2015) if 2015 in years_list else 0)
    )

    # LIST OF POSSIBLE BOND YIELDS (from 0.005 to 0.035 in 0.005 increments)
    yield_options = [0.005 * i for i in range(1, 8)]  # 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035
    yield_rate = st.selectbox("Bond yield rate (choose a decimal value)", yield_options, index=1)

    # INFLATION FROM 1% TO 5%
    inflation_percent = st.slider("Annual inflation (%)", min_value=1, max_value=5, value=3, step=1)
    inflation = inflation_percent / 100.0

    # ANNUAL INVESTMENT (ONLY INTEGER)
    yearly_investment_input = st.text_input("Annual investment (USD)", "5000")
    try:
        yearly_investment = int(yearly_investment_input)
        if yearly_investment <= 100:
            raise ValueError("Investment amount must be greater than 100!")
    except ValueError as e:
        st.error(f"Error: {e}")
        st.stop()

    # SLIDER TO SET PROPORTIONS
    proportions = st.slider(
        "Set proportions between bonds and gold (%)",
        min_value=0,
        max_value=100,
        value=70,
        step=5
    )
    bonds_pro = proportions / 100
    gold_pro = 1 - bonds_pro

    # RUN SIMULATION BUTTON
    if st.button("Run simulation"):
        bond_asset = BondAsset(inflation, yield_rate)
        strategy = InvestmentStrategy(rise_investment=1)
        portfolio = SafePortfolio(bonds_pro=bonds_pro, gold_pro=gold_pro)

        current_year_num = datetime.now().year
        duration_years = current_year_num - start_year

        sim = SafeSimulation(
            portfolio=portfolio,
            bond_asset=bond_asset,
            strategy=strategy,
            start_year=int(start_year),
            years=duration_years
        )

        results = sim.run(yearly_investment)
        df_results = pd.DataFrame(results)

        df_results['Gold Value'] = df_results['Gold Price'] * df_results['Gold Units']

        # --- Plotting charts ---
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Gold Value'],
            mode='lines',
            name='Gold Value',
            line=dict(color='gold')
        ))
        fig.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Bonds'],
            mode='lines',
            name='Bond Value',
            line=dict(color='orange')
        ))
        fig.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Total'],
            mode='lines',
            name='Total Portfolio Value',
            line=dict(color='green')
        ))
        fig.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Invested'],
            mode='lines',
            name='Invested Funds',
            line=dict(color='blue')
        ))
        fig.update_layout(
            title='Defensive Portfolio Simulation',
            xaxis_title='Date',
            yaxis_title='Value (USD)',
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary calculations
        total_invested = df_results['Invested'].iloc[-1]
        total_value = df_results['Total'].iloc[-1]
        growth_percent = ((total_value - total_invested) / total_invested) * 100

        # Asset quantities
        gold_units = df_results['Gold Units'].iloc[-1]
        gold_value = df_results['Gold Value'].iloc[-1]
        bonds_value = df_results['Bonds'].iloc[-1]

        # Display portfolio summary
        st.write("### Portfolio Summary")
        st.markdown(f"**Invested amount:** {total_invested:,.2f} USD  \n"
                    f"**Total portfolio value:** {total_value:,.2f} USD  \n"
                    f"**Portfolio growth:** {growth_percent:,.2f}%  \n")

        st.write("### Asset Details")
        st.markdown(f"**Gold:** {gold_units:,.2f} units - {gold_value:,.2f} USD  \n"
                    f"**Bonds:** {bonds_value:,.2f} USD")

        st.write("### Gold Charts")

        # Additional chart: gold price
        fig_gold_price = go.Figure()
        fig_gold_price.add_trace(go.Scatter(
            x=df_results['Date'],
            y=df_results['Gold Price'],
            mode='lines',
            name='Gold Price',
            line=dict(color='gold')
        ))
        fig_gold_price.update_layout(
            title='Gold Price Over Time',
            xaxis_title='Date',
            yaxis_title='Gold Price (USD)',
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_gold_price, use_container_width=True)
