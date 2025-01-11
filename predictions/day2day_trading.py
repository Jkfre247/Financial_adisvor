import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Improved predict_next_day function
def predict_next_day(model, data, window_size):
    # Check if there is enough data
    if len(data) < window_size:
        return None, "Not enough data for prediction!", "black"

    current_window = data.iloc[-window_size:].values
    input_data = np.reshape(current_window, (1, window_size, current_window.shape[1]))
    predicted_change = model.predict(input_data)[0][0]

    if predicted_change > 0:
        return predicted_change, "The stock price will increase tomorrow", "green"
    else:
        return predicted_change, "The stock price will decrease tomorrow", "red"


def day2day_trading(model, data, window_size, df, initial_balance=1000):
    """
    Simulates day-to-day trading with predicted stock movements (buy/sell)
    and portfolio value changes.

    Parameters:
    - model: Trained model (e.g., LSTM).
    - data: Input data (pandas DataFrame), where column 0 is the target value.
    - window_size: Window size (number of rows used as input for the model).
    - df: Original DataFrame containing data with a 'Close' column.
    - initial_balance: Initial portfolio value (e.g., 1000).

    Returns:
    - result_df: DataFrame with columns:
        - 'Date': The date of the trading decision.
        - 'Predicted_Action': Predicted action (1: Buy, -1: Sell, 0: No action).
        - 'Actual_Action': Actual movement (1: Increase, -1: Decrease, 0: No change).
        - 'Balance': Portfolio value after each decision.
    """
    result_df = pd.DataFrame(columns=['Date', 'Predicted_Action', 'Actual_Action', 'Balance'])

    # Check if there is enough data for trading simulation
    if len(data) < window_size + 20:
        print("Not enough data for trading simulation!")
        return result_df

    # Initialize variables
    current_balance = initial_balance

    # Loop for 20 trading days
    for i in range(20, 0, -1):
        # Prepare the current data window for prediction
        current_window = data.iloc[-(window_size + i):-i].values
        input_data = np.reshape(current_window, (1, window_size, current_window.shape[1]))

        # Predict the relative price change
        predicted_change = model.predict(input_data)[0][0]

        # Determine predicted action: buy (1), sell (-1), no action (0)
        predicted_action = 1 if predicted_change > 0 else (-1 if predicted_change < 0 else 0)

        # Actual price change
        next_actual_change = data.iloc[-i, 0]
        actual_action = 1 if next_actual_change > 0 else (-1 if next_actual_change < 0 else 0)

        # Update portfolio value based on action
        if predicted_action == 1:  # Buy
            current_balance *= (1 + next_actual_change)
        elif predicted_action == -1:  # Sell
            current_balance *= (1 - next_actual_change)

        # Add results to DataFrame
        result_df.loc[len(result_df)] = {
            'Date': df.index[-i],  # Decision date
            'Predicted_Action': predicted_action,  # Predicted action
            'Actual_Action': actual_action,  # Actual movement
            'Balance': current_balance  # Portfolio value
        }

    return result_df
