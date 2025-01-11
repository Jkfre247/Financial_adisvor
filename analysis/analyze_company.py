from .imports import *
from .plot_yearly_financials import plot_yearly_financials
from .plot_quarterly_financials import plot_quarterly_financials
from .fair_price_estimation import fair_price_estimation
from .plot_closing_price import plot_closing_price

def analyze_company():
    st.subheader("Analysis of the selected company")

    # Example (shortened) list of S&P 500 companies
    sp500_companies = [
        "AAPL", "MSFT", "AMZN", "TSLA", "GOOGL", "META", "JNJ", "WMT",
        "JPM", "V", "PG", "NVDA", "HD", "MA", "DIS", "BAC", "PFE", "XOM",
        "KO", "INTC"
    ]

    selected = st.selectbox(
        "Select a company from the S&P500 list or 'other...' to enter a company ticker:",
        options=sp500_companies + ["other..."]
    )

    if selected == "other...":
        ticker = st.text_input("Enter the company ticker (e.g., NFLX, PLTR, etc.):", value="AAPL")
    else:
        ticker = selected

    if st.button("Download and analyze"):
        if not ticker:
            st.warning("Please enter a valid company ticker.")
            return

        # 1. Stock price chart
        st.write(f"**Stock price chart for {ticker}:**")
        plot_closing_price(ticker)

        # 2. Annual financial data
        st.write(f"**Annual financial data for {ticker}:**")
        plot_yearly_financials(ticker)

        # 3. Quarterly financial data
        st.write(f"**Quarterly financial data for {ticker}:**")
        plot_quarterly_financials(ticker)

        # 4. Key metrics and fair value calculations
        st.write("**Key metrics and fair value calculations:**")
        results = fair_price_estimation(ticker)

        # -- Split the screen into two columns --
        col1, col2 = st.columns(2)

        # COLUMN 1: FAIR PRICES (fair_price_*)
        with col1:
            st.markdown("### **Calculated fair prices**")
            if results.get("fair_price_PE") is not None:
                val = results["fair_price_PE"]
                st.markdown(f"**FAIR_PRICE_PE:** {val:,.2f} USD  \n"
                            "*Price based on P/E (EPS * 15).*")

            if results.get("fair_price_PS") is not None:
                val = results["fair_price_PS"]
                st.markdown(f"**FAIR_PRICE_PS:** {val:,.2f} USD  \n"
                            "*Price based on P/S (3 * revenue per share).*")

            if results.get("fair_price_EV_EBITDA") is not None:
                val = results["fair_price_EV_EBITDA"]
                st.markdown(f"**FAIR_PRICE_EV_EBITDA:** {val:,.2f} USD  \n"
                            "*Price based on EV/EBITDA (8 * EBITDA - debt + cash).*")

            if results.get("fair_price_P_FCF") is not None:
                val = results["fair_price_P_FCF"]
                st.markdown(f"**FAIR_PRICE_P_FCF:** {val:,.2f} USD  \n"
                            "*Price based on P/FCF (15 * free cash flow).*")

            if results.get("fair_price_average") is not None:
                val = results["fair_price_average"]
                st.markdown(f"**FAIR_PRICE_AVERAGE:** {val:,.2f} USD  \n"
                            "*Average fair price from the above methods.*")

        # COLUMN 2: FINANCIAL RATIOS (P/E, P/S, EV/EBITDA, etc.)
        with col2:
            st.markdown("### **Financial ratios**")
            pe = results.get("P/E")
            if pe is not None:
                st.markdown(f"**P/E (Price/Earnings):** {pe:,.2f}  \nPrice-to-earnings ratio.")

            ps = results.get("P/S")
            if ps is not None:
                st.markdown(f"**P/S (Price/Sales):** {ps:,.2f}  \nPrice-to-sales ratio.")

            ev_ebitda = results.get("EV/EBITDA")
            if ev_ebitda is not None:
                st.markdown(f"**EV/EBITDA (Enterprise Value / EBITDA):** {ev_ebitda:,.2f}  \n"
                            "Indicates how many years it would take for the company to 'pay off' its EV with EBITDA.")

            p_fcf = results.get("P/FCF")
            if p_fcf is not None:
                st.markdown(f"**P/FCF (Price/Free Cash Flow):** {p_fcf:,.2f}  \n"
                            "Price-to-free cash flow ratio.")

            eps = results.get("EPS")
            if eps is not None:
                st.markdown(f"**EPS (Earnings per Share):** {eps:,.2f}  \nEarnings per share.")

        # 5. Summary of main values (e.g., current price, revenue, EBITDA, annual costs, net income)
        st.write("---")
        st.markdown("### Summary of selected values (Annually)")

        # Current stock price
        if results.get("current_price") is not None:
            st.write(f"**Current stock price:** {results['current_price']:.2f} USD")

        # Revenue
        if results.get("revenue") is not None:
            st.write(f"**Revenue:** {results['revenue']:,} USD")

        # EBITDA
        if results.get("ebitda") is not None:
            st.write(f"**EBITDA:** {results['ebitda']:,} USD")

        # Annual costs
        if results.get("operating_expense") is not None:
            st.write(f"**Annual costs (Operating Expense):** {results['operating_expense']:,} USD")

        # Net income – "Company profit"
        if results.get("net_income") is not None:
            st.write(f"**Net income (Company profit):** {results['net_income']:,} USD")

        # Disclaimer
        st.caption("""
*The above metrics are very basic and do not fully reflect market conditions, technological advancements, or the company's market position. They are intended to serve only as a starting point for further, more detailed analysis.*
        """)
