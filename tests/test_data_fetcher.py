import pandas as pd
import numbers

from src.utils.data_fetcher import DataFetcher

class DummyTicker:
    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, **kwargs):
        # Return a small DataFrame suitable for tests
        dates = pd.date_range(start='2025-01-01', periods=5, freq='D')
        df = pd.DataFrame({
            'Open': [100,101,102,103,104],
            'High': [101,102,103,104,105],
            'Low': [99,100,101,102,103],
            'Close': [100,101,102,103,104],
            'Volume': [1000,1100,1200,1300,1400]
        }, index=dates)
        return df

    @property
    def info(self):
        return {
            'longName': 'Dummy Corp',
            'sector': 'Technology',
            'industry': 'Software',
            'marketCap': 123456789,
            'trailingPE': 25.0,
            'fiftyTwoWeekHigh': 150.0,
            'fiftyTwoWeekLow': 50.0,
            'dividendYield': 0.01
        }

def test_get_historical_and_live(monkeypatch):
    # Monkeypatch yfinance.Ticker
    import yfinance as yf
    monkeypatch.setattr(yf, 'Ticker', DummyTicker)

    df = DataFetcher.get_historical_data('DUMMY', '2025-01-01', '2025-01-06')
    assert df is not None
    assert len(df) == 5

    price = DataFetcher.get_live_price('DUMMY')
    # Accept any numeric type (int, float, numpy.number, Decimal, etc.)
    assert isinstance(price, numbers.Number)

    info = DataFetcher.get_company_info('DUMMY')
    assert info['Name'] == 'Dummy Corp'

def test_save_and_load_csv(tmp_path):
    dates = pd.date_range(start='2025-01-01', periods=3, freq='D')
    df = pd.DataFrame({'Close': [1,2,3]}, index=dates)
    fn = tmp_path / 'test.csv'

    saved = DataFetcher.save_to_csv(df, str(fn))
    assert saved is True

    loaded = DataFetcher.load_from_csv(str(fn))
    assert loaded is not None
    assert len(loaded) == 3
