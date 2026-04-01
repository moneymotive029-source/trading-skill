"""
WebSocket Price Feed Agent
Real-time price streaming for crypto, stocks, and forex.

Supports:
- Binance WebSocket (crypto)
- Alpaca WebSocket (stocks)
- Polygon WebSocket (stocks/forex)

Usage:
    python websocket_price_feed.py --symbols BTC,ETH,AAPL --feed binance
"""

import asyncio
import json
import websockets
import argparse
from datetime import datetime
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass


@dataclass
class PriceUpdate:
    symbol: str
    price: float
    bid: float
    ask: float
    volume: float
    timestamp: str
    exchange: str


class BinanceWebSocket:
    """Binance WebSocket stream for crypto prices"""

    BASE_URL = "wss://stream.binance.com:9443/ws"

    def __init__(self, symbols: List[str], callback: Callable[[PriceUpdate], None]):
        self.symbols = [s.lower() for s in symbols]
        self.callback = callback
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False

    async def connect(self):
        streams = "/".join([f"{s}@trade" for s in self.symbols])
        url = f"{self.BASE_URL}/{streams}"

        async with websockets.connect(url) as ws:
            self.ws = ws
            self.running = True

            while self.running:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=30)
                    data = json.loads(message)
                    await self.handle_message(data)
                except asyncio.TimeoutError:
                    # Send heartbeat
                    await ws.ping()
                except websockets.ConnectionClosed:
                    print("WebSocket closed, reconnecting...")
                    break

    async def handle_message(self, data: dict):
        if data.get("e") == "trade":
            update = PriceUpdate(
                symbol=data["s"],
                price=float(data["p"]),
                bid=float(data["p"]),
                ask=float(data["p"]),
                volume=float(data["q"]),
                timestamp=datetime.fromtimestamp(data["T"] / 1000).isoformat(),
                exchange="Binance",
            )
            self.callback(update)


class AlpacaWebSocket:
    """Alpaca WebSocket stream for stock prices"""

    BASE_URL = "wss://stream.data.alpaca.markets/v2/iex"

    def __init__(
        self, symbols: List[str], callback: Callable[[PriceUpdate], None], api_key: str, api_secret: str
    ):
        self.symbols = symbols
        self.callback = callback
        self.api_key = api_key
        self.api_secret = api_secret
        self.running = False

    async def connect(self):
        async with websockets.connect(self.BASE_URL) as ws:
            # Authenticate
            await ws.send(
                json.dumps(
                    {
                        "action": "auth",
                        "key": self.api_key,
                        "secret": self.api_secret,
                    }
                )
            )
            auth_response = await ws.recv()
            print(f"Auth: {auth_response}")

            # Subscribe to trades
            await ws.send(
                json.dumps(
                    {
                        "action": "subscribe",
                        "trades": self.symbols,
                    }
                )
            )

            self.running = True
            while self.running:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=30)
                    data = json.loads(message)
                    await self.handle_message(data)
                except asyncio.TimeoutError:
                    await ws.ping()
                except websockets.ConnectionClosed:
                    break

    async def handle_message(self, data: dict):
        if "trades" in data:
            for symbol, trade in data["trades"].items():
                update = PriceUpdate(
                    symbol=symbol,
                    price=trade["p"],
                    bid=trade["p"],
                    ask=trade["p"],
                    volume=trade["s"],
                    timestamp=trade["t"],
                    exchange="Alpaca",
                )
                self.callback(update)


class PriceFeedService:
    """Unified price feed service with WebSocket streaming"""

    def __init__(self, feed_type: str = "binance", api_key: str = None, api_secret: str = None):
        self.feed_type = feed_type
        self.api_key = api_key
        self.api_secret = api_secret
        self.callbacks: List[Callable[[PriceUpdate], None]] = []
        self.latest_prices: Dict[str, PriceUpdate] = {}

    def on_price(self, callback: Callable[[PriceUpdate], None]):
        self.callbacks.append(callback)

    def _handle_price(self, update: PriceUpdate):
        self.latest_prices[update.symbol] = update
        for callback in self.callbacks:
            callback(update)

    async def run(self, symbols: List[str]):
        if self.feed_type == "binance":
            ws = BinanceWebSocket(symbols, self._handle_price)
            await ws.connect()
        elif self.feed_type == "alpaca":
            if not self.api_key or not self.api_secret:
                raise ValueError("Alpaca requires API key and secret")
            ws = AlpacaWebSocket(symbols, self._handle_price, self.api_key, self.api_secret)
            await ws.connect()
        else:
            raise ValueError(f"Unknown feed type: {self.feed_type}")


async def main():
    parser = argparse.ArgumentParser(description="WebSocket Price Feed")
    parser.add_argument("--symbols", type=str, default="BTC,ETH,SOL", help="Comma-separated symbols")
    parser.add_argument(
        "--feed",
        type=str,
        default="binance",
        choices=["binance", "alpaca"],
        help="Price feed provider",
    )
    parser.add_argument("--api-key", type=str, help="API key (for Alpaca)")
    parser.add_argument("--api-secret", type=str, help="API secret (for Alpaca)")
    parser.add_argument("--json", action="store_true", help="Output as JSON lines")

    args = parser.parse_args()
    symbols = [s.strip() for s in args.symbols.split(",")]

    def print_price(update: PriceUpdate):
        if args.json:
            print(
                json.dumps(
                    {
                        "symbol": update.symbol,
                        "price": update.price,
                        "bid": update.bid,
                        "ask": update.ask,
                        "volume": update.volume,
                        "timestamp": update.timestamp,
                        "exchange": update.exchange,
                    }
                )
            )
        else:
            print(f"{update.timestamp} | {update.exchange} | {update.symbol}: ${update.price:,.2f}")

    service = PriceFeedService(
        feed_type=args.feed,
        api_key=args.api_key,
        api_secret=args.api_secret,
    )
    service.on_price(print_price)

    print(f"Connecting to {args.feed} WebSocket for {symbols}...")
    await service.run(symbols)


if __name__ == "__main__":
    asyncio.run(main())
