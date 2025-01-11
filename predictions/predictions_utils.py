import numpy as np
import pandas as pd


def predict_20_days(model, data, window_size, df):
    """
    Predicts the next 20 days of relative price changes along with actual prices, dates, and original values.
    Returns a DataFrame with: Date, Predicted_Price, Original_Price, Predictions (% change).
    """
    predictions = []
    predicted_prices = []
    dates = []
    original_prices = []

    last_window = data.iloc[-(window_size + 20):-20].values
    last_close_price = df['Close'].iloc[-20]

    for i in range(20):
        # Prepare data for the model
        input_data = np.reshape(last_window, (1, window_size, last_window.shape[1]))

        # Predict relative price change
        next_price_change = model.predict(input_data)[0][0]
        predictions.append(next_price_change)

        # Calculate the next actual price
        next_close_price = last_close_price * (1 + next_price_change)
        predicted_prices.append(next_close_price)

        # Prediction date
        dates.append(df['Date'].iloc[-20 + i])

        # Original price (if available)
        if len(df) > (window_size + i):
            original_prices.append(df['Close'].iloc[-20 + i])
        else:
            original_prices.append(None)

        # Update the window
        next_row = np.zeros(last_window.shape[1])
        next_row[0] = next_price_change
        last_window = np.vstack((last_window[1:], next_row))

        # Update the last price
        last_close_price = next_close_price

    result_df = pd.DataFrame({
        'Date': dates,
        'Predicted_Price': predicted_prices,
        'Original_Price': original_prices,
        'Predictions': predictions
    })

    return result_df


def predict_20_days_future_only(model, data, window_size, df):
    """
    Predicts the next 20 days of relative price changes into the future (without backward history),
    compares the last predicted price with the last closing price in the DataFrame,
    and returns a DataFrame with predicted prices along with text indicating rise/fall.

    Parameters:
    - model: Trained model (e.g., LSTM).
    - data: Input data (pandas DataFrame), where column 0 is the target value.
    - window_size: Window size (number of rows used as input for the model).
    - df: Original DataFrame containing data with a 'Close' column.

    Returns:
    - result_df: DataFrame with predicted prices.
    - text: Text ("Stock prices will rise" or "Stock prices will fall").
    """
    predictions = []
    predicted_prices = []

    # Last known price in df
    last_close_price = df["Close"].iloc[-1]
    current_price = last_close_price

    # Input window for prediction
    last_window = data.iloc[-window_size:].values

    for _ in range(20):
        # Prepare data for the model
        input_data = np.reshape(last_window, (1, window_size, last_window.shape[1]))

        next_price_change = model.predict(input_data)[0][0]
        predictions.append(next_price_change)

        current_price *= (1 + next_price_change)
        predicted_prices.append(current_price)

        # Update the window
        next_row = np.zeros(last_window.shape[1])
        next_row[0] = next_price_change
        last_window = np.vstack((last_window[1:], next_row))

    # Compare the last predicted price with the last known price
    if predicted_prices[-1] > last_close_price:
        text = "Stock prices will rise"
    else:
        text = "Stock prices will fall"

    # Create a DataFrame
    result_df = pd.DataFrame({
        'Predicted_Price': predicted_prices
    })

    return result_df, text
