import random
import sys
from collections import deque

import pygame


WIDTH, HEIGHT = 1200, 760
FPS = 60
STARTING_CASH = 100_000

BG = (5, 12, 18)
PANEL = (9, 20, 30)
PANEL_ALT = (12, 28, 42)
TEXT = (142, 250, 160)
TEXT_DIM = (90, 160, 110)
ACCENT = (0, 180, 255)
GREEN = (90, 255, 140)
RED = (255, 110, 110)
YELLOW = (240, 220, 120)


class Stock:
    def __init__(self, ticker, name, sector, price, volatility, growth):
        self.ticker = ticker
        self.name = name
        self.sector = sector
        self.price = price
        self.volatility = volatility
        self.growth = growth
        self.history = deque([price] * 140, maxlen=140)
        self.news = "Stable outlook"

    def update(self):
        shock = random.gauss(self.growth, self.volatility)
        self.price = max(1, self.price * (1 + shock))
        self.history.append(self.price)

    @property
    def change_pct(self):
        if len(self.history) < 2:
            return 0
        prev = self.history[-2]
        return ((self.price - prev) / prev) * 100


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("STOCK/TERM :: Bloomberg-ish Trading Simulator")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.font_small = pygame.font.SysFont("consolas", 16)
        self.font_big = pygame.font.SysFont("consolas", 28, bold=True)

        self.stocks = [
            Stock("NXT", "NextGrid Energy", "Energy", 88, 0.006, 0.0002),
            Stock("BLU", "Blue Harbor Logistics", "Transport", 41, 0.010, 0.0001),
            Stock("AUR", "Aurora Semiconductors", "Tech", 132, 0.013, 0.0005),
            Stock("VRT", "Vertice Biomed", "Healthcare", 57, 0.016, -0.0002),
            Stock("CRN", "Crown Retail Group", "Retail", 29, 0.009, 0.0003),
            Stock("QNT", "Quanta Cloud Systems", "Tech", 210, 0.020, 0.0004),
            Stock("HZN", "Horizon Water", "Utilities", 74, 0.004, 0.0001),
        ]
        self.selected = 0
        self.cash = float(STARTING_CASH)
        self.positions = {s.ticker: 0 for s in self.stocks}
        self.command = ""
        self.messages = deque(maxlen=8)
        self.tick_timer = 0
        self.tick_ms = 500

        self.log("Welcome to STOCK/TERM. Type HELP for commands.")
        self.log(f"Starting balance: ${self.cash:,.2f}")

    def log(self, msg):
        self.messages.appendleft(msg)

    def handle_command(self, raw):
        parts = raw.strip().split()
        if not parts:
            return

        cmd = parts[0].upper()

        if cmd == "HELP":
            self.log("Commands: BUY <TICKER> <QTY>, SELL <TICKER> <QTY>, INFO <TICKER>, CASH, PORT")
            return
        if cmd == "CASH":
            self.log(f"Available cash: ${self.cash:,.2f}")
            return
        if cmd == "PORT":
            self.log(f"Portfolio value: ${self.portfolio_value():,.2f} | Total equity: ${self.total_equity():,.2f}")
            return

        if len(parts) < 2:
            self.log("Invalid command. Type HELP.")
            return

        ticker = parts[1].upper()
        stock = next((s for s in self.stocks if s.ticker == ticker), None)
        if not stock:
            self.log(f"Ticker {ticker} not found.")
            return

        if cmd == "INFO":
            self.selected = self.stocks.index(stock)
            self.log(f"{stock.ticker} {stock.name} [{stock.sector}] @ ${stock.price:,.2f}")
            return

        if len(parts) < 3:
            self.log("Quantity required.")
            return

        try:
            qty = int(parts[2])
        except ValueError:
            self.log("Quantity must be an integer.")
            return

        if qty <= 0:
            self.log("Quantity must be > 0.")
            return

        if cmd == "BUY":
            cost = stock.price * qty
            if cost > self.cash:
                self.log("Insufficient cash.")
                return
            self.cash -= cost
            self.positions[stock.ticker] += qty
            self.log(f"Bought {qty} {stock.ticker} @ ${stock.price:,.2f}")
        elif cmd == "SELL":
            if self.positions[stock.ticker] < qty:
                self.log("Insufficient shares.")
                return
            self.positions[stock.ticker] -= qty
            proceeds = stock.price * qty
            self.cash += proceeds
            self.log(f"Sold {qty} {stock.ticker} @ ${stock.price:,.2f}")
        else:
            self.log("Unknown command. Type HELP.")

    def portfolio_value(self):
        return sum(self.positions[s.ticker] * s.price for s in self.stocks)

    def total_equity(self):
        return self.cash + self.portfolio_value()

    def update_market(self, dt):
        self.tick_timer += dt
        if self.tick_timer < self.tick_ms:
            return
        self.tick_timer = 0
        for s in self.stocks:
            s.update()
            roll = random.random()
            if roll < 0.002:
                s.news = random.choice([
                    "Earnings beat expectations",
                    "Analyst downgrade",
                    "Product launch announced",
                    "Regulatory review underway",
                    "Supply chain disruption",
                ])

    def draw_text(self, txt, x, y, color=TEXT, font=None):
        font = font or self.font
        surf = font.render(txt, True, color)
        self.screen.blit(surf, (x, y))

    def draw_chart(self, stock, rect):
        x, y, w, h = rect
        pygame.draw.rect(self.screen, PANEL_ALT, rect)
        prices = list(stock.history)
        lo, hi = min(prices), max(prices)
        rng = max(0.01, hi - lo)
        points = []
        for i, p in enumerate(prices):
            px = x + int((i / (len(prices) - 1)) * (w - 10)) + 5
            py = y + h - int(((p - lo) / rng) * (h - 20)) - 10
            points.append((px, py))
        if len(points) >= 2:
            pygame.draw.lines(self.screen, ACCENT, False, points, 2)
        self.draw_text(f"{stock.ticker} Price Chart", x + 10, y + 8, YELLOW, self.font_small)
        self.draw_text(f"Low ${lo:,.2f}", x + 10, y + h - 24, TEXT_DIM, self.font_small)
        self.draw_text(f"High ${hi:,.2f}", x + w - 120, y + h - 24, TEXT_DIM, self.font_small)

    def draw(self):
        self.screen.fill(BG)
        pygame.draw.rect(self.screen, PANEL, (16, 16, 1168, 728), border_radius=8)

        self.draw_text("BLOOMBERG-STYLE STOCK/TERM", 28, 28, YELLOW, self.font_big)
        self.draw_text("Commands: BUY <TICKER> <QTY> | SELL <TICKER> <QTY> | INFO <TICKER> | CASH | PORT", 30, 66, TEXT_DIM, self.font_small)

        equity = self.total_equity()
        pnl = equity - STARTING_CASH
        pnl_color = GREEN if pnl >= 0 else RED
        self.draw_text(f"Cash: ${self.cash:,.2f}", 30, 92)
        self.draw_text(f"Portfolio: ${self.portfolio_value():,.2f}", 290, 92)
        self.draw_text(f"Equity: ${equity:,.2f}", 560, 92)
        self.draw_text(f"P/L: ${pnl:,.2f}", 800, 92, pnl_color)

        list_rect = (30, 126, 520, 300)
        pygame.draw.rect(self.screen, PANEL_ALT, list_rect)
        self.draw_text("TICKER  PRICE      CHG%    SHARES   NAME", 40, 136, YELLOW, self.font_small)
        for idx, s in enumerate(self.stocks):
            y = 164 + idx * 34
            if idx == self.selected:
                pygame.draw.rect(self.screen, (22, 52, 76), (36, y - 3, 508, 30))
            chg = s.change_pct
            c = GREEN if chg >= 0 else RED
            line = f"{s.ticker:<6} ${s.price:>7.2f}  {chg:>+6.2f}%   {self.positions[s.ticker]:>5}    {s.name[:20]}"
            self.draw_text(line, 42, y, c if idx == self.selected else TEXT, self.font_small)

        sel = self.stocks[self.selected]
        self.draw_chart(sel, (570, 126, 590, 300))
        info_rect = (30, 440, 1130, 180)
        pygame.draw.rect(self.screen, PANEL_ALT, info_rect)
        self.draw_text(f"{sel.ticker} :: {sel.name}", 42, 452, YELLOW)
        self.draw_text(f"Sector: {sel.sector}", 42, 482)
        self.draw_text(f"Last: ${sel.price:,.2f}   Day Change: {sel.change_pct:+.2f}%", 42, 510)
        self.draw_text(f"News: {sel.news}", 42, 538)

        term_rect = (30, 628, 1130, 104)
        pygame.draw.rect(self.screen, (4, 10, 14), term_rect)
        self.draw_text("TERMINAL LOG", 42, 636, YELLOW, self.font_small)
        for i, msg in enumerate(list(self.messages)[:3]):
            self.draw_text(msg, 42, 656 + i * 20, TEXT_DIM, self.font_small)
        self.draw_text(f"> {self.command}", 700, 698, TEXT, self.font_small)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.stocks)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.stocks)
                    elif event.key == pygame.K_RETURN:
                        self.handle_command(self.command)
                        self.command = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.command = self.command[:-1]
                    elif event.unicode.isprintable():
                        self.command += event.unicode

            self.update_market(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
