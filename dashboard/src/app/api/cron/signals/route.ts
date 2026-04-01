import { NextResponse } from "next/server";
import { waitUntil } from "@vercel/functions";

// CRON_SECRET should be set in Vercel environment variables
// Verify the request is from Vercel Cron
function verifyCronAuth(request: Request): boolean {
  const authHeader = request.headers.get("authorization");
  const expectedToken = process.env.CRON_SECRET;

  if (!expectedToken) {
    console.warn("CRON_SECRET not configured");
    return true; // Allow in development
  }

  return authHeader === `Bearer ${expectedToken}`;
}

export async function GET(request: Request) {
  // Verify authentication
  if (!verifyCronAuth(request)) {
    return new Response("Unauthorized", { status: 401 });
  }

  console.log(`[${new Date().toISOString()}] Running scheduled signal update`);

  // Process signal updates in background using native waitUntil pattern
  const backgroundWork = (async () => {
    try {
      // List of assets to monitor
      const assets = [
        { symbol: "BTC", assetClass: "cryptocurrency" },
        { symbol: "ETH", assetClass: "cryptocurrency" },
        { symbol: "AAPL", assetClass: "stock" },
        { symbol: "TSLA", assetClass: "stock" },
        { symbol: "EURUSD", assetClass: "forex" },
        { symbol: "XAUUSD", assetClass: "commodity" },
      ];

      // Run analysis for each asset
      const analysisPromises = assets.map(async (asset) => {
        try {
          const response = await fetch(
            `${process.env.VERCEL_URL || "http://localhost:3010"}/api/analyze`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(asset),
            }
          );

          if (!response.ok) {
            console.error(`Failed to analyze ${asset.symbol}: ${response.statusText}`);
            return null;
          }

          return response.json();
        } catch (err) {
          console.error(`Error analyzing ${asset.symbol}:`, err);
          return null;
        }
      });

      const results = (await Promise.all(analysisPromises)).filter(Boolean);

      console.log(`Updated ${results.length} signals successfully`);
    } catch (error) {
      console.error("Cron job failed:", error);
    }
  })();

  // Use waitUntil if available, otherwise just let the promise run
  if (typeof waitUntil === "function" && request.signal) {
    try {
      waitUntil(backgroundWork);
    } catch {
      // Ignore if waitUntil not available in dev
    }
  }

  return NextResponse.json({
    status: "queued",
    timestamp: new Date().toISOString(),
  });
}
