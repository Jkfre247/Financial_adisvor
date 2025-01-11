import streamlit as st
import pandas as pd
import plotly.express as px
from .predictions_utils import *
from .stock_prediction import *

def run_risky():
    st.title("Risky – Stock Price Prediction for 20 Days with Rise or Fall Recommendation")

    # Example tickers for different sectors
    sectors = {
        'Technology': 'AAPL',
        'Healthcare': 'JNJ',
        'Finance': 'JPM',
        'Energy': 'XOM',
        'Consumer Goods': 'PG'
    }

    # Initialize the StockPrediction object
    predictor = StockPrediction(sectors, window_size=50, test_split=0.95, epochs=5, batch_size=32)
    predictor.download_data()
    predictor.preprocess_features()
    predictor.create_lstm_data()
    predictor.train_models(force_update=False)

    # Select sector for prediction
    chosen_sector = st.selectbox("Select a sector:", list(sectors.keys()))
    ticker = sectors[chosen_sector]  # Stock code

    # Prediction section – if a model exists for the chosen sector
    if chosen_sector in predictor.models:
        model = predictor.models[chosen_sector]
        df_raw = predictor.dataframes[chosen_sector]  # Original DataFrame
        data_rel = predictor.relative_data[chosen_sector]  # Data with relative features
        window_size = predictor.window_size

        # Historical prediction
        result_history = predict_20_days(model, data_rel, window_size, df_raw)

        # Future prediction
        result_future, future_text = predict_20_days_future_only(model, data_rel, window_size, df_raw)
        future_dates = pd.date_range(start=df_raw['Date'].iloc[-1] + pd.Timedelta(days=1), periods=20, freq='B')
        result_future['Date'] = future_dates

        # Top section with charts
        st.subheader(f"Prediction for Sector: {chosen_sector} ({ticker})")

        col1, col2 = st.columns(2)

        # Historical chart (on the left)
        with col1:
            st.write("Comparison: Actual vs. Predicted (20 Historical Days)")
            fig_history = px.line(
                result_history,
                x='Date',
                y=['Original_Price', 'Predicted_Price'],
                title="Historical Data"
            )
            st.plotly_chart(fig_history, use_container_width=True)

        # Future chart (on the right)
        with col2:
            st.write("Price Forecast for the Next 20 Days")
            fig_future = px.line(
                result_future,
                x='Date',
                y='Predicted_Price',
                title="Future Price Forecast"
            )
            st.plotly_chart(fig_future, use_container_width=True)

        # Large prediction text (centered)
        st.markdown(f"<h1 style='text-align: center; color: green;'>{future_text}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>Stock Code: {ticker}</h2>", unsafe_allow_html=True)

        # Button to retrain the model
        if st.button(f"Retrain the model for sector: {chosen_sector}"):
            predictor.models[chosen_sector] = predictor.create_or_load_model(chosen_sector, force_update=True)
            st.success(f"The model for sector {chosen_sector} has been retrained!")

            # Refresh results after retraining
            result_history = predict_20_days(model, data_rel, window_size, df_raw)
            result_future, future_text = predict_20_days_future_only(model, data_rel, window_size, df_raw)

            # Refresh charts after retraining
            st.write("Updated Results")

            with col1:
                fig_history = px.line(
                    result_history,
                    x='Date',
                    y=['Original_Price', 'Predicted_Price'],
                    title="Historical Data (Updated)",
                    labels={
                        'Date': 'Date',
                        'Original_Price': 'Original Price',
                        'Predicted_Price': 'Predicted Price'
                    }
                )
                st.plotly_chart(fig_history, use_container_width=True)

            with col2:
                fig_future = px.line(
                    result_future,
                    x='Date',
                    y='Predicted_Price',
                    title="Future Price Forecast (Updated)",
                    labels={
                        'Date': 'Date',
                        'Predicted_Price': 'Predicted Price'
                    }
                )
                st.plotly_chart(fig_future, use_container_width=True)

            # Updated prediction text
            st.markdown(f"<h1 style='text-align: center; color: green;'>{future_text}</h1>", unsafe_allow_html=True)

    else:
        st.warning(f"The model for sector {chosen_sector} has not been loaded yet.")

    # Footer note
    st.markdown("---")
    st.markdown("<h4 style='text-align: center;'>Invest at your own risk</h4>", unsafe_allow_html=True)
