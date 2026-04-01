/**
 * Health check endpoint for Vercel Storage
 */

import { NextResponse } from "next/server";
import { checkStorageHealth } from "@/lib/storage";

export async function GET() {
  const health = await checkStorageHealth();

  return NextResponse.json({
    status: health.connected ? "healthy" : "degraded",
    storage: {
      kv: health.connected,
      provider: process.env.UPSTASH_REDIS_REST_URL ? "upstash" : "local",
    },
    timestamp: new Date().toISOString(),
  });
}
