from .imports import *
import yfinance as yf
import plotly.graph_objects as go

def plot_quarterly_financials(ticker):
    """Displays quarterly financial data charts in Streamlit."""
    stock = yf.Ticker(ticker)

    try:
        financials_quarterly = stock.quarterly_financials
    except:
        st.write("No quarterly financial data available in yfinance.")
        return

    def safe_loc(df, row):
        try:
            return df.loc[row]
        except KeyError:
            return pd.Series(dtype="float64")

    revenue = safe_loc(financials_quarterly, "Total Revenue")
    cost_of_revenue = safe_loc(financials_quarterly, "Cost Of Revenue")
    gross_profit = safe_loc(financials_quarterly, "Gross Profit")
    net_income = safe_loc(financials_quarterly, "Net Income")
    operating_expenses = safe_loc(financials_quarterly, "Operating Expense")
    r_and_d = safe_loc(financials_quarterly, "Research And Development")
    sga = safe_loc(financials_quarterly, "Selling General And Administration")
    ebitda = safe_loc(financials_quarterly, "Operating Income")

    # 1) Revenue, Costs, and Gross Profit
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=revenue.index,
        y=revenue.values,
        name="Revenue"
    ))
    fig1.add_trace(go.Bar(
        x=cost_of_revenue.index,
        y=cost_of_revenue.values,
        name="Cost of Revenue"
    ))
    fig1.add_trace(go.Bar(
        x=gross_profit.index,
        y=gross_profit.values,
        name="Gross Profit"
    ))
    fig1.update_layout(
        title="Revenue, Costs, and Gross Profit (Quarterly)",
        xaxis_title="Quarterly",
        yaxis_title="USD",
        barmode='group',
        showlegend=True
    )
    # Minimal tooltip
    fig1.update_traces(
        hovertemplate="%{y}",
        hoverinfo="text"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 2) EBIT / Operating Income
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=ebitda.index,
        y=ebitda.values,
        name="EBIT (Operating Income)"
    ))
    fig2.update_layout(
        title="EBIT / Operating Income (Quarterly)",
        xaxis_title="Quarterly",
        yaxis_title="USD",
        showlegend=True
    )
    fig2.update_traces(
        hovertemplate="%{y}",
        hoverinfo="text"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 3) Operating Expenses
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=operating_expenses.index,
        y=operating_expenses.values,
        name="Operating Expenses"
    ))
    fig3.add_trace(go.Bar(
        x=r_and_d.index,
        y=r_and_d.values,
        name="R&D (Research and Development)"
    ))
    fig3.add_trace(go.Bar(
        x=sga.index,
        y=sga.values,
        name="SGA (Selling, General, and Administrative)"
    ))
    fig3.update_layout(
        title="Operating Expenses (Quarterly)",
        xaxis_title="Quarterly",
        yaxis_title="USD",
        barmode='stack',
        showlegend=True
    )
    fig3.update_traces(
        hovertemplate="%{y}",
        hoverinfo="text"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # 4) Net Income
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=net_income.index,
        y=net_income.values,
        name="Net Income"
    ))
    fig4.update_layout(
        title="Net Income (Quarterly)",
        xaxis_title="Quarterly",
        yaxis_title="USD",
        showlegend=True
    )
    fig4.update_traces(
        hovertemplate="%{y}",
        hoverinfo="text"
    )
    st.plotly_chart(fig4, use_container_width=True)
