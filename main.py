"""Capitulation buyer for the btc-race-24h bars-replay competitions.

Strategy (kept deliberately rare-trading: a full-size round trip costs ~26-48
bps in fees, slippage and impact, so only deep capitulation dips are worth
buying):
  entry : flat, close at least 7.5% below the session high AND RSI(14) < 40
  size  : 95% of cash, one position at most
  exit  : take profit +3% / stop loss -1.5% from the entry fill price,
          or after 120 bars held, whichever comes first
  halt  : equity down 20% from its peak -> sell and stop trading
Everything is decided on bar closes; the replay fills at the next bar's open.
Deterministic: no clock, no environment, no randomness.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
DROP = 0.075          # entry: close >= 7.5% under the session high
RSI_MAX = 40.0        # entry: RSI(14) below this
RSI_PERIOD = 14
TP = 0.03             # take profit +3%
SL = 0.015            # stop loss -1.5%
MAX_HOLD = 120        # bars
SIZE_FRAC = 0.95      # 95% of cash per trade
DD_HALT = 0.20        # 20% drawdown halt
MAX_SLIP = 500        # max_slippage_bps on every order

closes = []
session_high = 0.0
rsi_avg_gain = None
rsi_avg_loss = None
prev_close = None
entry_price = None    # USD per asset, fees included (from position cost)
entry_seq = None
peak_equity = None
halted = False


def rsi_update(close):
    """Wilder RSI state update; returns the RSI value or None while warming up."""
    global rsi_avg_gain, rsi_avg_loss, prev_close
    if prev_close is None:
        prev_close = close
        return None
    change = close - prev_close
    prev_close = close
    gain = change if change > 0 else 0.0
    loss = -change if change < 0 else 0.0
    if rsi_avg_gain is None:
        # seed with simple averages over the first RSI_PERIOD changes
        rsi_update.seed_gains.append(gain)
        rsi_update.seed_losses.append(loss)
        if len(rsi_update.seed_gains) < RSI_PERIOD:
            return None
        rsi_avg_gain = sum(rsi_update.seed_gains) / RSI_PERIOD
        rsi_avg_loss = sum(rsi_update.seed_losses) / RSI_PERIOD
    else:
        rsi_avg_gain = (rsi_avg_gain * (RSI_PERIOD - 1) + gain) / RSI_PERIOD
        rsi_avg_loss = (rsi_avg_loss * (RSI_PERIOD - 1) + loss) / RSI_PERIOD
    if rsi_avg_loss == 0:
        return 100.0
    rs = rsi_avg_gain / rsi_avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


rsi_update.seed_gains = []
rsi_update.seed_losses = []


def on_batch(state, batch):
    global session_high, entry_price, entry_seq, peak_equity, halted
    bar = state.latest.get(SYMBOL)
    if bar is None:
        return []
    price_scale = state.symbols[SYMBOL]["price_scale"]
    qty_scale = state.symbols[SYMBOL]["qty_scale"]
    quote_scale = state.hello["capital"]["quote_scale"]
    close = int(bar["c"]) / 10 ** price_scale
    high = int(bar["h"]) / 10 ** price_scale
    closes.append(close)
    if high > session_high:
        session_high = high
    rsi = rsi_update(close)

    equity = state.equity / 10 ** quote_scale
    if peak_equity is None or equity > peak_equity:
        peak_equity = equity
    if peak_equity and equity <= peak_equity * (1 - DD_HALT):
        halted = True

    holding = state.positions.get(SYMBOL)
    if holding is not None and entry_price is None and holding.qty > 0:
        entry_price = (holding.cost / 10 ** quote_scale) / (holding.qty / 10 ** qty_scale)
        entry_seq = state.seq

    if holding is not None and holding.qty > 0:
        # manage the open position
        if halted:
            return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty, "max_slippage_bps": MAX_SLIP}]
        if entry_price is not None:
            if close >= entry_price * (1 + TP) or close <= entry_price * (1 - SL):
                return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty, "max_slippage_bps": MAX_SLIP}]
            if entry_seq is not None and state.seq - entry_seq >= MAX_HOLD:
                return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty, "max_slippage_bps": MAX_SLIP}]
        return []

    # flat: a filled sell clears the entry marks
    entry_price = None
    entry_seq = None
    if halted or state.warming_up:
        return []
    if rsi is None or session_high <= 0:
        return []
    if close <= session_high * (1 - DROP) and rsi < RSI_MAX:
        notional = int(state.cash * SIZE_FRAC)
        if notional >= 1_000_000:
            return [{"side": "buy", "symbol": SYMBOL, "notional_quote_units": notional,
                     "max_slippage_bps": MAX_SLIP}]
    return []


if __name__ == "__main__":
    makefun_bars.run(on_batch)
