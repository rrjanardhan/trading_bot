import pandas as pd
from src.backtest import Backtest

class DummyStrategy:
    def __init__(self, positions):
        # positions: dict index -> position value (1 buy, -1 sell, 0 hold)
        self.positions = positions
        self.name = 'Dummy'

    def generate_signals(self, data):
        df = data.copy()
        df['Position'] = 0
        for idx, pos in self.positions.items():
            df.at[df.index[idx], 'Position'] = pos
        return df


def test_backtest_buy_sell_cycle():
    # Construct small deterministic price series
    dates = pd.date_range(start='2025-01-01', periods=5, freq='D')
    # Prices chosen so that (initial_capital*0.95)/buy_price is integer
    prices = [100, 95, 95, 105, 105]
    df = pd.DataFrame({'Close': prices}, index=dates)

    # Positions: buy on index 1 (second row), sell on index 3
    positions = {1: 1, 3: -1}
    strat = DummyStrategy(positions)

    bt = Backtest(initial_capital=10000, commission=0)
    metrics = bt.run(df.copy(), strat)

    # Expected: buy at price 95 -> shares = (10000*0.95)//95 = 100
    # Sell at price 105 -> final portfolio = cash + holdings = (100*105) + remaining_cash
    # After buy, cash = 10000 - (100*95) = 10000 - 9500 = 500
    # After sell cash = 500 + 100*105 = 500 + 10500 = 11000
    assert metrics['Final Value ($)'] == 11000.0
    assert metrics['Total Trades'] >= 1
