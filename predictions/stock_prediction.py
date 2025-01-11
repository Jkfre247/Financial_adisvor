from .imports import *

class StockPrediction:
    def __init__(self, sectors, window_size=50, test_split=0.95, epochs=10, batch_size=32):
        self.sectors = sectors
        self.window_size = window_size
        self.test_split = test_split
        self.epochs = epochs
        self.batch_size = batch_size
        self.dataframes = {}
        self.relative_data = {}
        self.lstm_train_data = {}
        self.lstm_test_data = {}
        self.models = {}

    def download_data(self):
        """
        Pobiera dane dla zdefiniowanych w słowniku self.sectors sektorów.
        """
        self.dataframes = {
            sector: self.preprocess_data(
                yf.download(ticker, start='2010-01-01').dropna()
            )
            for sector, ticker in self.sectors.items()
        }

    def preprocess_data(self, df):
        """
        Proste czyszczenie i resetowanie indeksu.
        """
        df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        df.columns.name = None
        return df

    def compute_rsi(self, series, period=14):
        """
        Oblicza wskaźnik RSI.
        """
        delta = series.diff().fillna(0)
        gains = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        losses = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gains / (losses + 1e-9)
        return 100 - (100 / (1 + rs))

    def preprocess_features(self):
        """
        Tworzy i dodaje kolumny z dodatkowymi wskaźnikami (MA, RSI, itp.).
        """
        for sector, df in self.dataframes.items():
            df['Rel_Close'] = (df['Close'] / df['Close'].shift(1)) - 1
            df['MA_50'] = (df['Close'].rolling(window=50).mean() / df['Close'].shift(1)) - 1
            df['MA_200'] = (df['Close'].rolling(window=200).mean() / df['Close'].shift(1)) - 1
            df['Daily_Range_%'] = (df['High'] - df['Low']) / df['Low']
            df['Open_High_%'] = (df['High'] - df['Open']) / df['Open']
            df['Open_Low_%'] = (df['Open'] - df['Low']) / df['Open']
            df['RSI'] = self.compute_rsi(df['Close'])
            df.dropna(inplace=True)
            self.relative_data[sector] = df[
                ['Rel_Close', 'MA_50', 'MA_200', 'Daily_Range_%',
                 'Open_High_%', 'Open_Low_%', 'RSI']
            ]

    def create_lstm_data(self):
        """
        Tworzy sekwencje (okna) do trenowania i testowania modelu LSTM.
        """
        for sector, data in self.relative_data.items():
            train_size = int(len(data) * self.test_split)
            train_data = data.iloc[:train_size]
            test_data = data.iloc[train_size:]

            if len(train_data) > self.window_size and len(test_data) > self.window_size:
                self.lstm_train_data[sector] = self._generate_sequences(train_data)
                self.lstm_test_data[sector] = self._generate_sequences(test_data)

    def _generate_sequences(self, data):
        X, y = [], []
        for i in range(len(data) - self.window_size):
            X.append(data.iloc[i : i + self.window_size].values)
            y.append(data.iloc[i + self.window_size, 0])
        return np.array(X), np.array(y)

    def build_model(self, input_shape):
        """
        Buduje nowy model LSTM.
        """
        model = Sequential([
            Input(shape=input_shape),
            LSTM(64, return_sequences=True), Dropout(0.2),
            LSTM(64, return_sequences=True), Dropout(0.2),
            LSTM(32), Dropout(0.2),
            Dense(64, activation='relu'),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model

    def create_or_load_model(self, sector, force_update=False):
        """
        Tworzy lub ładuje (jeśli istnieje) gotowy model z dysku dla wskazanego sektora.
        """
        model_path = f"lstm_model_{sector}.keras"
        train_X, train_y = self.lstm_train_data[sector]
        test_X, test_y = self.lstm_test_data[sector]
        input_shape = (train_X.shape[1], train_X.shape[2])

        if os.path.exists(model_path) and not force_update:
            print(f"[INFO] Loading existing model for {sector}")
            model = tf.keras.models.load_model(model_path)
        else:
            print(f"[INFO] Training new model for {sector}")
            model = self.build_model(input_shape)
            model.fit(train_X, train_y,
                      epochs=self.epochs,
                      batch_size=self.batch_size,
                      validation_data=(test_X, test_y))
            model.save(model_path)
        return model

    def train_models(self, force_update=False):
        """
        Trenuje (lub ładuje) modele dla wszystkich sektorów.
        """
        for sector in self.lstm_train_data.keys():
            self.models[sector] = self.create_or_load_model(sector, force_update)