// WebSocket endpoint for real-time price feeds
// Uses Vercel Edge runtime for low-latency streaming

export const runtime = "edge";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const symbols = searchParams.get("symbols")?.split(",") || ["BTC", "ETH", "AAPL"];

  // Create WebSocket connection to price feed
  // In production, this would connect to:
  // - Binance WebSocket for crypto: wss://stream.binance.com:9443/ws
  // - Alpaca WebSocket for stocks: wss://stream.data.alpaca.markets/v2/iex
  // - Polygon WebSocket: wss://socket.polygon.io/stocks

  const { readable, writable } = new TransformStream();
  const writer = writable.getWriter();
  const encoder = new TextEncoder();

  // Mock price stream - replace with real WebSocket in production
  const sendPrice = (symbol: string) => {
    const basePrice = symbol === "BTC" ? 95000 : symbol === "ETH" ? 3200 : symbol === "AAPL" ? 228 : 1000;
    const volatility = symbol === "BTC" ? 0.002 : symbol === "ETH" ? 0.003 : 0.001;
    const randomChange = (Math.random() - 0.5) * 2 * volatility;
    const price = basePrice * (1 + randomChange);

    return {
      symbol,
      price: price.toFixed(2),
      change: (randomChange * 100).toFixed(3),
      timestamp: new Date().toISOString(),
    };
  };

  // Send initial data
  const initialData = symbols.map((s) => sendPrice(s.trim()));
  writer.write(
    encoder.encode(
      `data: ${JSON.stringify({ type: "init", prices: initialData })}\n\n`
    )
  );

  // Stream updates every second
  const interval = setInterval(() => {
    const prices = symbols.map((s) => sendPrice(s.trim()));
    writer.write(
      encoder.encode(
        `data: ${JSON.stringify({ type: "update", prices })}\n\n`
      )
    );
  }, 1000);

  // Cleanup on disconnect
  request.signal.addEventListener("abort", () => {
    clearInterval(interval);
    writer.close();
  });

  return new Response(readable, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    },
  });
}
