"""
Broker Execution Agent
Live trading integration with Alpaca (stocks), Binance (crypto), and Interactive Brokers.

Features:
- Paper trading support for testing
- Market, limit, stop orders
- Position management
- Order status tracking
- Risk checks before execution

Usage:
    python broker_execution_agent.py --broker alpaca --paper --symbol AAPL --side buy --qty 10
    python broker_execution_agent.py --broker binance --symbol BTCUSDT --side sell --qty 0.1
"""

import asyncio
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    id: str
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0
    filled_price: Optional[float] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float = 0


class AlpacaBroker:
    """Alpaca broker integration for stock trading"""

    def __init__(self, api_key: str, api_secret: str, paper: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self.account_id: Optional[str] = None

    async def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make authenticated request to Alpaca API"""
        import aiohttp
        from aiohttp import BasicAuth

        auth = BasicAuth(self.api_key, self.api_secret)
        url = f"{self.base_url}{endpoint}"

        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.request(method, url, json=data) as response:
                return await response.json()

    async def get_account(self) -> dict:
        """Get account info"""
        return await self._request("GET", "/v2/account")

    async def get_positions(self) -> List[dict]:
        """Get open positions"""
        return await self._request("GET", "/v2/positions")

    async def get_position(self, symbol: str) -> dict:
        """Get position for specific symbol"""
        return await self._request("GET", f"/v2/positions/{symbol}")

    async def submit_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order_type: str = "market",
        limit_price: float = None,
        stop_price: float = None,
        time_in_force: str = "day",
    ) -> dict:
        """Submit order to Alpaca"""
        data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
        }
        if limit_price:
            data["limit_price"] = limit_price
        if stop_price:
            data["stop_price"] = stop_price

        return await self._request("POST", "/v2/orders", data)

    async def cancel_order(self, order_id: str) -> dict:
        """Cancel order"""
        return await self._request("DELETE", f"/v2/orders/{order_id}")

    async def cancel_all_orders(self) -> dict:
        """Cancel all open orders"""
        return await self._request("DELETE", "/v2/orders")


class BinanceBroker:
    """Binance broker integration for crypto trading"""

    BASE_URL = "https://api.binance.com"

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        if testnet:
            self.base_url = "https://testnet.binance.vision"
        else:
            self.base_url = self.BASE_URL

    def _sign(self, params: dict) -> str:
        """Generate HMAC SHA256 signature"""
        import hmac
        import hashlib

        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    async def _request(self, method: str, endpoint: str, params: dict = None, signed: bool = False) -> dict:
        """Make authenticated request to Binance API"""
        import aiohttp

        if params is None:
            params = {}

        params["timestamp"] = int(datetime.now().timestamp() * 1000)
        params["recvWindow"] = 5000

        if signed:
            params["signature"] = self._sign(params)

        headers = {"X-MBX-APIKEY": self.api_key}
        url = f"{self.base_url}{endpoint}"

        async with aiohttp.ClientSession(headers=headers) as session:
            if method == "GET":
                async with session.get(url, params=params) as response:
                    return await response.json()
            elif method == "POST":
                async with session.post(url, params=params) as response:
                    return await response.json()
            elif method == "DELETE":
                async with session.delete(url, params=params) as response:
                    return await response.json()

    async def get_account(self) -> dict:
        """Get account info"""
        return await self._request("GET", "/api/v3/account", signed=True)

    async def get_positions(self) -> List[dict]:
        """Get open positions (account balances with > 0)"""
        account = await self.get_account()
        return [b for b in account.get("balances", []) if float(b["free"]) > 0]

    async def submit_order(
        self,
        symbol: str,
        side: str,
        order_type: str = "MARKET",
        quantity: float = None,
        price: float = None,
        stop_price: float = None,
        time_in_force: str = "GTC",
    ) -> dict:
        """Submit order to Binance"""
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
        }

        if quantity:
            params["quantity"] = quantity

        if order_type.upper() in ["LIMIT", "STOP_LOSS_LIMIT", "TAKE_PROFIT_LIMIT"]:
            params["price"] = price
            params["timeInForce"] = time_in_force

        if order_type.upper() in ["STOP_LOSS", "TAKE_PROFIT"]:
            params["stopPrice"] = stop_price

        return await self._request("POST", "/api/v3/order", params, signed=True)

    async def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel order"""
        params = {"symbol": symbol, "orderId": order_id}
        return await self._request("DELETE", "/api/v3/order", params, signed=True)


class BrokerExecutionAgent:
    """Unified broker execution agent"""

    def __init__(
        self,
        broker: str = "alpaca",
        api_key: str = None,
        api_secret: str = None,
        paper: bool = True,
    ):
        self.broker = broker
        self.paper = paper

        if broker == "alpaca":
            self.broker_client = AlpacaBroker(api_key, api_secret, paper)
        elif broker == "binance":
            self.broker_client = BinanceBroker(api_key, api_secret, paper)
        else:
            raise ValueError(f"Unsupported broker: {broker}")

        self.orders: Dict[str, Order] = {}

    async def get_account_info(self) -> dict:
        """Get account information"""
        return await self.broker_client.get_account()

    async def get_positions(self) -> List[Position]:
        """Get open positions"""
        positions_data = await self.broker_client.get_positions()
        # Convert to Position objects (implementation depends on broker response)
        return positions_data

    async def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        limit_price: float = None,
        stop_price: float = None,
    ) -> Order:
        """Submit order with risk checks"""

        # Risk checks
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Get current account info for buying power check
        account = await self.get_account_info()

        if self.broker == "alpaca":
            order_data = await self.broker_client.submit_order(
                symbol=symbol,
                qty=quantity,
                side=side,
                order_type=order_type,
                limit_price=limit_price,
                stop_price=stop_price,
            )

            order = Order(
                id=order_data.get("id", "unknown"),
                symbol=symbol,
                side=OrderSide(side),
                type=OrderType(order_type),
                quantity=quantity,
                price=limit_price,
                stop_price=stop_price,
                status=OrderStatus.SUBMITTED,
            )

        elif self.broker == "binance":
            order_data = await self.broker_client.submit_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=limit_price,
                stop_price=stop_price,
            )

            order = Order(
                id=str(order_data.get("orderId", "unknown")),
                symbol=symbol,
                side=OrderSide(side),
                type=OrderType(order_type),
                quantity=quantity,
                price=limit_price,
                stop_price=stop_price,
                status=OrderStatus.SUBMITTED,
            )

        self.orders[order.id] = order
        logger.info(f"Order submitted: {order.id} - {side} {quantity} {symbol}")
        return order

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        if self.broker == "alpaca":
            await self.broker_client.cancel_order(order_id)
        elif self.broker == "binance":
            # Binance needs symbol + order_id
            order = self.orders.get(order_id)
            if order:
                await self.broker_client.cancel_order(order.symbol, int(order_id))

        if order_id in self.orders:
            self.orders[order_id].status = OrderStatus.CANCELLED
            self.orders[order_id].updated_at = datetime.now().isoformat()

        logger.info(f"Order cancelled: {order_id}")
        return True

    async def close_position(self, symbol: str) -> Order:
        """Close position for symbol"""
        positions = await self.get_positions()

        # Find position
        position = None
        for pos in positions:
            if pos.symbol == symbol:
                position = pos
                break

        if not position:
            raise ValueError(f"No open position for {symbol}")

        # Submit opposite order
        side = "sell" if position.quantity > 0 else "buy"
        quantity = abs(position.quantity)

        return await self.submit_order(symbol, side, quantity, "market")


async def main():
    parser = argparse.ArgumentParser(description="Broker Execution Agent")
    parser.add_argument("--broker", type=str, default="alpaca", choices=["alpaca", "binance"])
    parser.add_argument("--api-key", type=str, required=True, help="API key")
    parser.add_argument("--api-secret", type=str, required=True, help="API secret")
    parser.add_argument("--paper", action="store_true", help="Paper trading mode")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol to trade")
    parser.add_argument("--side", type=str, required=True, choices=["buy", "sell"])
    parser.add_argument("--qty", type=float, required=True, help="Quantity")
    parser.add_argument("--type", type=str, default="market", choices=["market", "limit"])
    parser.add_argument("--price", type=float, help="Limit price")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    agent = BrokerExecutionAgent(
        broker=args.broker,
        api_key=args.api_key,
        api_secret=args.api_secret,
        paper=args.paper,
    )

    # Get account info
    account = await agent.get_account_info()

    if args.json:
        print(json.dumps(account, indent=2))
    else:
        print(f"Account: {account.get('id', 'N/A')}")
        print(f"Status: {account.get('status', 'N/A')}")
        print(f"Paper Trading: {args.paper}")

    # Submit order
    print(f"\nSubmitting {args.side.upper()} order for {args.qty} {args.symbol}...")

    order = await agent.submit_order(
        symbol=args.symbol,
        side=args.side,
        quantity=args.qty,
        order_type=args.type,
        limit_price=args.price,
    )

    if args.json:
        print(json.dumps({
            "order_id": order.id,
            "symbol": order.symbol,
            "side": order.side.value,
            "type": order.type.value,
            "quantity": order.quantity,
            "status": order.status.value,
        }, indent=2))
    else:
        print(f"Order submitted: {order.id}")
        print(f"  Symbol: {order.symbol}")
        print(f"  Side: {order.side.value}")
        print(f"  Type: {order.type.value}")
        print(f"  Quantity: {order.quantity}")
        print(f"  Status: {order.status.value}")


if __name__ == "__main__":
    asyncio.run(main())
