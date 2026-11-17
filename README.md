# btc-race-btc-race-24h-20261117-0603

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/fadliferdian74-lgtm/btc-race-btc-race-24h-20261117-0603/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/fadliferdian74-lgtm/btc-race-btc-race-24h-20261117-0603/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

Capitulation buyer for make.fun's btc-race-24h: it buys cbBTC only after a close at least 7.5% below the session high with RSI(14) under 40, sizing 95% of cash, and exits at +3% take-profit / -1.5% stop-loss or after 120 bars, with a 20% drawdown halt. One position at most, deterministic, standard library only. On the previous race's dev window it made +$29.71 net PnL (1 trade); on this race's dev window the 7.5% trigger never fired (max drop -2.12%), so it made $0.00 and does not pass the dev gate as-is.

## Run it

```sh
PYTHONHASHSEED=0 python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>
