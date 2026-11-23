"""Dip-buy mean-reversion bot for make.fun btc-race-24h-20261123-0511.

Trades Coinbase Wrapped BTC (CBBTC) against USDC, one minute bar at a time,
over the agent-fun/bars-replay/v1 protocol (hello, one batch per bar, done).
Long only, one open position, full cash in and full quantity out.

Strategy (tuned by grid search on the kit's 24 h dev window, 1,440 bars):
  - Entry: the close is at least DIP_BPS below the highest close of the
    LOOKBACK bars before it -> buy with all cash.
  - Exit: take profit at TP_BPS above the entry close, stop loss at SL_BPS
    below it, or a time stop after MAX_HOLD bars, whichever comes first.
  - No new entry in the last NO_ENTRY_LAST bars of the window.
  - One order per reply, max_slippage_bps 100 (1% past the deciding close).

Determinism: integer math only, no clock, no randomness, no network, no
files outside the repository. The entry reference is the close of the bar
the buy was decided on; a buy whose fill is rejected clears its pending
entry instead of pretending to hold.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
DIP_BPS = 90
LOOKBACK = 180
TP_BPS = 125
SL_BPS = 80
MAX_HOLD = 600
NO_ENTRY_LAST = 60
MAX_SLIPPAGE_BPS = 100
TOTAL_BARS = 1440
BAR_MS = 60_000

closes = []
entry_close = None
entry_seq = None
pending_entry = None  # (close, seq) of a buy order sent, fill not yet seen
first_close_ms = None


def sell_order(qty):
    """One order selling the whole position, capped at 1% past the close."""
    return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
             "max_slippage_bps": MAX_SLIPPAGE_BPS}]


def on_hello(state):
    global first_close_ms
    first_close_ms = state.hello.get("first_close_ms")


def on_batch(state, batch):
    global entry_close, entry_seq, pending_entry
    bar = None
    for b in batch["bars"]:
        if b["symbol"] == SYMBOL:
            bar = b
            break
    if bar is None:
        return []
    if state.warming_up:
        return []
    close = int(bar["c"])
    closes.append(close)
    seq = state.seq

    holding = state.positions.get(SYMBOL)
    qty = holding.qty if holding is not None else 0

    # Settle a pending entry: promoted once the fill shows up in the account,
    # dropped once its fill bar has passed without a position.
    if pending_entry is not None:
        if qty > 0:
            entry_close, entry_seq = pending_entry
            pending_entry = None
        elif seq > pending_entry[1] + 1:
            pending_entry = None

    if qty > 0:
        if entry_close is None:
            # Position appeared without a recorded entry (defensive only):
            # measure take-profit / stop-loss from the first close seen held.
            entry_close = close
            entry_seq = seq
        if close * 10000 >= entry_close * (10000 + TP_BPS):
            entry_close = None
            return sell_order(qty)
        if close * 10000 <= entry_close * (10000 - SL_BPS):
            entry_close = None
            return sell_order(qty)
        if entry_seq is not None and seq - entry_seq >= MAX_HOLD:
            entry_close = None
            return sell_order(qty)
        return []

    # Flat: look for a dip to buy.
    if first_close_ms is not None and batch["t"] >= first_close_ms + (TOTAL_BARS - NO_ENTRY_LAST) * BAR_MS:
        return []
    if len(closes) < LOOKBACK + 1:
        return []
    high = max(closes[-LOOKBACK - 1:-1])
    if close * 10000 <= high * (10000 - DIP_BPS):
        pending_entry = (close, seq)
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": state.cash,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    return []


makefun_bars.run(on_batch, on_hello=on_hello)
