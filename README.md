# makefun-btc-race-24h-20261123-0511

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/danzzkeceh4-bit/makefun-btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/danzzkeceh4-bit/makefun-btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

Dip-buy mean-reversion bot trading Coinbase Wrapped BTC (cbBTC) against USDC on 1-minute on-chain bars, for make.fun's "Race a BTC trading bot live for 24 hours". It buys with all cash when the close is at least 90 bps below the highest close of the previous 180 bars, and exits the whole position at +125 bps take-profit, −80 bps stop-loss, or after 600 bars — whichever comes first. Long only, one position, one order per reply, deterministic integer math, standard library only. Dev window (24 h to the opening, 1,440 bars): net PnL +$29.59, 8 trades, 1.82% max drawdown.

## Run it

```sh
python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=0t26xkzp&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
