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

  // Process signal updates in background
  waitUntil(async () => {
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
        // Call the Python trading agent
        const response = await fetch(
          `${process.env.VERCEL_URL || "localhost:3000"}/api/analyze`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(asset),
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to analyze ${asset.symbol}`);
        }

        return response.json();
      });

      const results = await Promise.all(analysisPromises);

      // Store results (would integrate with database in production)
      console.log(`Updated ${results.length} signals successfully`);

      // Here you would:
      // 1. Save to database (PostgreSQL via Neon/Supabase)
      // 2. Check for significant changes
      // 3. Send alerts if new high-conviction signals
      // 4. Update cached signal data
    } catch (error) {
      console.error("Cron job failed:", error);
    }
  });

  return NextResponse.json({
    status: "queued",
    timestamp: new Date().toISOString(),
  });
}
