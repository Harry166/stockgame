# Stock/Term (Pygame)

A Bloomberg-terminal-inspired stock investing game built with Pygame.

## Features

- Starts with **$100,000** in cash.
- Multiple stocks with unique ticker, name, sector, volatility, and trend.
- Live-updating prices with per-stock line charts.
- Terminal-style command input for trading:
  - `BUY <TICKER> <QTY>`
  - `SELL <TICKER> <QTY>`
  - `INFO <TICKER>`
  - `CASH`
  - `PORT`
- Portfolio tracking (cash, holdings, equity, P/L).

## Run

```bash
python -m pip install pygame
python game.py
```

## Controls

- `Up/Down`: change selected stock
- `Enter`: execute typed command
- `Backspace`: edit command
- `Esc`: quit
