"""Run a deterministic example backtest without network calls.
This script builds a synthetic price series, runs two strategies (SMA and RSI)
and saves a comparison CSV for reproducible examples or CI smoke tests.
"""
from datetime import datetime, timedelta
import pandas as pd

from src.backtest import Backtest
from src.strategies.sma_crossover import SMACrossover
from src.strategies.rsi_strategy import RSIStrategy


def make_synthetic_prices(days=60, start_price=100):
    dates = pd.date_range(end=datetime.today(), periods=days, freq='D')
    # Create a simple synthetic price series: uptrend then downtrend
    half = days // 2
    up = [start_price + i * 0.5 for i in range(half)]
    down = [up[-1] - i * 0.7 for i in range(days - half)]
    prices = up + down
    df = pd.DataFrame({'Close': prices}, index=dates)
    return df


def main():
    df = make_synthetic_prices(days=60, start_price=80)

    # Strategies to test
    strategies = {
        'SMA (5,15)': SMACrossover(5, 15),
        'RSI (14,70,30)': RSIStrategy(14, 70, 30)
    }

    backtest = Backtest(initial_capital=10000, commission=0)

    results = {}
    for name, strat in strategies.items():
        print(f"Running {name}...")
        # Backtest.run expects strategy.generate_signals to add Position column
        metrics = backtest.run(df.copy(), strat)
        results[name] = metrics

    comp_df = pd.DataFrame(results).T
    comp_file = f"comparison_example_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    comp_df.to_csv(comp_file)
    print(f"Saved comparison to {comp_file}")


if __name__ == '__main__':
    main()
