import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import random
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Input, Bidirectional, BatchNormalization
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from keras.optimizers import Adam
import tensorflow as tf
from typing import Tuple, List
import seaborn as sns
from datetime import datetime, timedelta

def set_seeds(seed: int = 42) -> None:
    """Set random seeds for reproducibility"""
    np.random.seed(seed)
    tf.random.set_seed(seed)
    random.seed(seed)

class StockPredictor:
    def __init__(self, ticker: str, start_date: str, end_date: str):
        """Initialize the StockPredictor class

        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            start_date: Start date for historical data
            end_date: End date for historical data
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.scaler = StandardScaler()
        self.model = None
        self.seq_length = 90

    def load_data(self) -> pd.DataFrame:
        """Load and preprocess stock data with technical indicators"""
        print(f"Loading data for {self.ticker}...")
        stock = yf.Ticker(self.ticker)
        df = stock.history(start=self.start_date, end=self.end_date)

        # Basic features
        df['RSI'] = self._calculate_rsi(df['Close'])
        df['MACD'] = self._calculate_macd(df['Close'])
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['Volatility'] = df['Close'].rolling(window=20).std()
        df['Price_Change'] = df['Close'].pct_change()

        # Volume indicators
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']

        # Bollinger Bands
        df['BB_Upper'], df['BB_Lower'] = self._calculate_bollinger_bands(df['Close'])

        # Drop any rows with NaN values
        df = df.dropna()
        print(f"Data loaded successfully. Shape: {df.shape}")
        return df

    def _calculate_rsi(self, prices: pd.Series, periods: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # Fill NaN values with neutral RSI

    def _calculate_macd(self, prices: pd.Series) -> pd.Series:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        return macd

    def _calculate_bollinger_bands(self, prices: pd.Series, window: int = 20) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        ma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper_band = ma + (std * 2)
        lower_band = ma - (std * 2)
        return upper_band, lower_band

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare data for model training"""
        print("Preparing data for training...")

        # Select features for training
        features = [
            'Close', 'High', 'Low', 'Volume', 'RSI', 'MACD',
            'MA20', 'MA50', 'Volatility', 'Volume_Ratio',
            'BB_Upper', 'BB_Lower', 'Price_Change'
        ]

        data = df[features].values
        scaled_data = self.scaler.fit_transform(data)

        # Create sequences
        X, y = self._create_sequences(scaled_data)

        # Split data
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        print(f"Training set shape: {X_train.shape}")
        print(f"Test set shape: {X_test.shape}")

        return X_train, X_test, y_train, y_test

    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        X, y = [], []
        for i in range(len(data) - self.seq_length):
            X.append(data[i:(i + self.seq_length), :])
            y.append(data[i + self.seq_length, 0])  # 0 index for Close price
        return np.array(X), np.array(y)

    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Build the LSTM model architecture"""
        print("Building model...")
        model = Sequential([
            Input(shape=input_shape),
            BatchNormalization(),
            Bidirectional(LSTM(100, return_sequences=True)),
            Dropout(0.3),
            BatchNormalization(),
            Bidirectional(LSTM(50, return_sequences=False)),
            Dropout(0.3),
            BatchNormalization(),
            Dense(50, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='huber'
        )
        print("Model built successfully")
        return model

    def train_model(self, X_train: np.ndarray, y_train: np.ndarray,
                    X_val: np.ndarray, y_val: np.ndarray) -> tf.keras.callbacks.History:
        """Train the model with the provided data"""
        print("Training model...")
        self.model = self.build_model((X_train.shape[1], X_train.shape[2]))

        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                mode='min'
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=5,
                min_lr=0.00001
            ),
            ModelCheckpoint(
                'best_model.keras',
                monitor='val_loss',
                save_best_only=True,
                mode='min'
            )
        ]

        history = self.model.fit(
            X_train, y_train,
            epochs=150,
            batch_size=32,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )

        print("Model training completed")
        return history

    def predict_future(self, last_sequence: np.ndarray, n_future: int) -> Tuple[np.ndarray, np.ndarray]:
        """Predict future values with uncertainty estimation"""
        print(f"Predicting next {n_future} days...")
        future_predictions = []
        prediction_std = []

        current_sequence = last_sequence.copy()

        # Monte Carlo simulation
        n_simulations = 100
        for _ in range(n_future):
            mc_predictions = []

            # Run multiple predictions with dropout enabled
            for _ in range(n_simulations):
                pred = self.model.predict(
                    current_sequence.reshape(1, *current_sequence.shape),
                    verbose=0
                )
                mc_predictions.append(pred[0, 0])

            # Calculate mean and standard deviation
            mean_pred = np.mean(mc_predictions)
            std_pred = np.std(mc_predictions)

            future_predictions.append(mean_pred)
            prediction_std.append(std_pred)

            # Update sequence for next prediction
            current_sequence = np.roll(current_sequence, -1, axis=0)
            current_sequence[-1, 0] = mean_pred

        # Transform predictions back to original scale
        future_predictions = np.array(future_predictions).reshape(-1, 1)
        padding = np.zeros((len(future_predictions), self.scaler.scale_.shape[0] - 1))
        future_predictions = np.concatenate((future_predictions, padding), axis=1)
        future_predictions = self.scaler.inverse_transform(future_predictions)[:, 0]

        return future_predictions, np.array(prediction_std)

    def plot_results(self, df: pd.DataFrame, train_pred: np.ndarray,
                    test_pred: np.ndarray, future_pred: np.ndarray,
                    future_std: np.ndarray) -> None:
        """Create comprehensive visualizations of the results"""
        print("Generating plots...")
        last_date = df.index[-1]
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=len(future_pred)
        )

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))

        # Plot 1: Historical and Predicted Prices
        axes[0, 0].plot(df.index, df['Close'], label='Actual', alpha=0.7)
        axes[0, 0].plot(df.index[-len(test_pred):], test_pred,
                       label='Test Predictions', color='red')
        axes[0, 0].plot(future_dates, future_pred,
                       label='Future Predictions', color='green')

        # Add confidence intervals
        axes[0, 0].fill_between(
            future_dates,
            future_pred - 2 * future_std,
            future_pred + 2 * future_std,
            color='green', alpha=0.1,
            label='95% Confidence Interval'
        )
        axes[0, 0].set_title(f'{self.ticker} Stock Price Predictions')
        axes[0, 0].legend()

        # Plot 2: Technical Indicators
        axes[0, 1].plot(df.index, df['RSI'], label='RSI')
        axes[0, 1].plot(df.index, df['MACD'], label='MACD')
        axes[0, 1].set_title('Technical Indicators')
        axes[0, 1].legend()

        # Plot 3: Volume Analysis
        axes[1, 0].bar(df.index, df['Volume'], label='Volume', alpha=0.3)
        axes[1, 0].plot(df.index, df['Volume_MA20'],
                       label='Volume MA20', color='red')
        axes[1, 0].set_title('Trading Volume Analysis')
        axes[1, 0].legend()

        # Plot 4: Bollinger Bands
        axes[1, 1].plot(df.index, df['Close'], label='Close Price')
        axes[1, 1].plot(df.index, df['BB_Upper'], label='Upper BB',
                       linestyle='--')
        axes[1, 1].plot(df.index, df['BB_Lower'], label='Lower BB',
                       linestyle='--')
        axes[1, 1].set_title('Bollinger Bands')
        axes[1, 1].legend()

        plt.tight_layout()
        plt.show()
        print("Plotting completed")

def main():
    # Initialize predictor
    predictor = StockPredictor(
        ticker='MSFT',
        start_date='2015-01-01',
        end_date='2024-10-21'
    )

    # Load and prepare data
    df = predictor.load_data()
    X_train, X_test, y_train, y_test = predictor.prepare_data(df)

    # Train model
    history = predictor.train_model(X_train, y_train, X_test, y_test)

    # Make predictions
    train_predictions = predictor.model.predict(X_train, verbose=0)
    test_predictions = predictor.model.predict(X_test, verbose=0)
    future_predictions, future_std = predictor.predict_future(X_test[-1], 90)

    # Plot results
    predictor.plot_results(
        df,
        train_predictions,
        test_predictions,
        future_predictions,
        future_std
    )

if __name__ == "__main__":
    set_seeds()
    main()