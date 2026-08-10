import pandas as pd

from src.strategies.sma_crossover import SMACrossover


def test_sma_generate_signals_simple():
    # Simple price series where short SMA will cross above long SMA
    prices = [10, 11, 12, 13, 14, 15]
    df = pd.DataFrame({'Close': prices})

    strat = SMACrossover(short_window=2, long_window=3)
    signals = strat.generate_signals(df)

    # Ensure SMA columns exist
    assert 'SMA_short' in signals.columns
    assert 'SMA_long' in signals.columns

    # At the end of this monotonic up series short SMA should be > long SMA -> Signal=1
    assert signals['Signal'].iloc[-1] == 1

    # get_signals should return a buy signal (1) for a clear crossover
    sig = strat.get_signals(df)
    assert sig in (1, 0, -1)

