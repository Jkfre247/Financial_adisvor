import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from .predictions_utils import *
from .stock_prediction import *
from .day2day_trading import *


def run_roulette():
    st.title("Roulette – Predicting Stock Increases or Decreases for the Next Day")

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

        # Day-to-day trading simulation
        st.subheader("20-Day Trading Simulation")
        trading_results = day2day_trading(model, data_rel, window_size, df_raw)

        # Display portfolio value chart
        fig_trading = px.line(
            trading_results,
            x='Date',
            y='Balance',
            title="Portfolio Value Over Time",
            labels={'Date': 'Date', 'Balance': 'Portfolio Value'}
        )
        st.plotly_chart(fig_trading, use_container_width=True)

        # Calculate percentage accuracy of Predicted_Action and Actual_Action
        correct_predictions = (trading_results['Predicted_Action'] == trading_results['Actual_Action']).sum()
        total_predictions = len(trading_results)
        accuracy = (correct_predictions / total_predictions) * 100

        # Display accuracy
        st.subheader("Prediction Accuracy Compared to Reality")
        st.markdown(f"**Accuracy Percentage:** {accuracy:.2f}%")

        # Prediction for the next day
        st.subheader("Predicted Change for the Next Day")
        predicted_change, prediction_text, prediction_color = predict_next_day(model, data_rel, window_size)
        st.markdown(
            f"<h2 style='text-align: center; color: {prediction_color};'>{prediction_text}</h2>",
            unsafe_allow_html=True
        )

        # Button to retrain the model
        if st.button(f"Retrain the model for sector: {chosen_sector}"):
            predictor.models[chosen_sector] = predictor.create_or_load_model(chosen_sector, force_update=True)
            st.success(f"The model for sector {chosen_sector} has been retrained!")

            # Refresh results after retraining
            trading_results = day2day_trading(model, data_rel, window_size, df_raw)
            correct_predictions = (trading_results['Predicted_Action'] == trading_results['Actual_Action']).sum()
            accuracy = (correct_predictions / len(trading_results)) * 100
            predicted_change, prediction_text, prediction_color = predict_next_day(model, data_rel, window_size)

            # Refresh chart and accuracy
            fig_trading = px.line(
                trading_results,
                x='Date',
                y='Balance',
                title="Portfolio Value Over Time (Updated)"
            )
            st.plotly_chart(fig_trading, use_container_width=True)
            st.markdown(f"**Accuracy Percentage:** {accuracy:.2f}%")
            st.markdown(
                f"<h2 style='text-align: center; color: {prediction_color};'>{prediction_text}</h2>",
                unsafe_allow_html=True
            )

    else:
        st.warning(f"The model for sector {chosen_sector} has not been loaded yet.")

    # Footer note
    st.markdown("---")
    st.markdown("<h4 style='text-align: center;'>Invest at your own risk</h4>", unsafe_allow_html=True)
