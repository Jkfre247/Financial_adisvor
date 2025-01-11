from .imports import *
import yfinance as yf
import plotly.graph_objects as go

def plot_closing_price(ticker):
    """Fetch and plot the closing price of the selected company's stock."""
    try:
        # Fetch the maximum historical data for the ticker
        data = yf.Ticker(ticker).history(period="max")
        if data.empty:
            st.warning(f"Could not fetch data for {ticker}. Please check the ticker and try again.")
            return

        # Check if the data covers less than 5 years
        if len(data) < 252 * 5:  # Approx. 252 trading days per year
            st.info(f"The company {ticker} has been on the stock market for less than 5 years. Data unavailable.")
        else:
            # Filter data to the last 5 years if sufficient data exists
            data = data.tail(252 * 5)

        # Reset index and ensure 'Date' is a column
        data.reset_index(inplace=True)
        data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d')

        # Filter only the 'Date' and 'Close' columns
        df = data[['Date', 'Close']].copy()
        df['Close'] = df['Close'].round(2)

        # Create a Plotly figure for closing prices
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Close'],
            name="Closing Price",
            line=dict(color='royalblue', width=2)
        ))
        fig.update_layout(
            title={
                'text': f"Stock price for {ticker}",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title="Date",
                tickformat="%b %Y",
                showgrid=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            yaxis=dict(
                title="Price (USD)",
                showgrid=True
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            template="plotly_white",
            font=dict(family="Arial, sans-serif", size=12),
            showlegend=False
        )

        # Display the Plotly chart
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while fetching or processing data for {ticker}: {e}")
