import { NextResponse } from "next/server";

// Mock signals - will be replaced with live Python agent integration
const signals = [
  {
    id: "1",
    symbol: "BTC/USD",
    assetClass: "Crypto",
    direction: "LONG",
    confidence: "High",
    entryZone: "$94,200 - $95,500",
    stopLoss: "$91,800",
    takeProfit: "$102,000",
    riskReward: "1:3.2",
    timestamp: new Date().toISOString(),
    thesis: "Bitcoin breaking above key resistance with strong momentum. RSI showing bullish divergence, MACD crossover confirmed. On-chain metrics indicate accumulation by whales.",
    technicals: {
      rsi: 58.4,
      macd: "Bullish",
      trend: "Uptrend",
      support: "$91,800",
      resistance: "$98,000",
    },
  },
  {
    id: "2",
    symbol: "AAPL",
    assetClass: "Stock",
    direction: "SHORT",
    confidence: "Medium",
    entryZone: "$228 - $230",
    stopLoss: "$235",
    takeProfit: "$215",
    riskReward: "1:2.1",
    timestamp: new Date().toISOString(),
    thesis: "Apple showing weakness ahead of earnings. Technical breakdown below 50-day MA, increasing put/call ratio. Concerns over China demand weighing on sentiment.",
    technicals: {
      rsi: 42.1,
      macd: "Bearish",
      trend: "Downtrend",
      support: "$220",
      resistance: "$235",
    },
  },
  {
    id: "3",
    symbol: "EUR/USD",
    assetClass: "Forex",
    direction: "LONG",
    confidence: "High",
    entryZone: "1.0850 - 1.0870",
    stopLoss: "1.0820",
    takeProfit: "1.0950",
    riskReward: "1:2.7",
    timestamp: new Date().toISOString(),
    thesis: "ECB hawkish pivot vs Fed dovish stance creating yield differential. EUR breaking above key resistance. Dollar weakness on soft US data.",
    technicals: {
      rsi: 61.2,
      macd: "Bullish",
      trend: "Uptrend",
      support: "1.0820",
      resistance: "1.0950",
    },
  },
];

export async function GET() {
  // TODO: Call Python trading agent API
  // const response = await fetch(`${PROCESS_API_URL}/api/analyze`, {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({ symbols: ["BTC", "AAPL", "EURUSD"] }),
  // });
  // const data = await response.json();

  return NextResponse.json({
    signals,
    generatedAt: new Date().toISOString(),
  });
}

export async function POST(request: Request) {
  const body = await request.json();
  const { symbol } = body;

  if (!symbol) {
    return NextResponse.json(
      { error: "Symbol is required" },
      { status: 400 }
    );
  }

  // TODO: Call Python trading agent for specific symbol analysis
  // const response = await fetch(`${PROCESS_API_URL}/api/analyze`, {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({ symbol, assetClass: "auto" }),
  // });
  // const analysis = await response.json();

  const mockAnalysis = {
    symbol,
    timestamp: new Date().toISOString(),
    signal: {
      direction: "LONG",
      confidence: "High",
      entryZone: "$94,200 - $95,500",
      stopLoss: "$91,800",
      takeProfit1: "$98,000",
      takeProfit2: "$102,000",
      riskReward: "1:3.2",
    },
    technicals: {
      rsi: 58.4,
      macd: { histogram: 124, signal: "Bullish" },
      movingAverages: {
        sma20: "$93,100",
        sma50: "$89,500",
        sma200: "$72,300",
      },
      bollingerBands: {
        upper: "$97,200",
        middle: "$93,500",
        lower: "$89,800",
      },
    },
    fundamentals: {
      marketCap: "$1.87T",
      volume24h: "$42.3B",
      dominance: "54.2%",
    },
    sentiment: {
      score: 72,
      classification: "Greed",
      socialVolume: "High",
    },
    pestle: {
      political: "Neutral",
      economic: "Positive",
      technological: "Positive",
      legal: "Neutral",
      environmental: "Neutral",
    },
    riskMetrics: {
      var95: "$3,200",
      cvar95: "$4,800",
      kellyPosition: "4.2%",
      recommendedPosition: "2.1%",
    },
  };

  return NextResponse.json(mockAnalysis);
}
