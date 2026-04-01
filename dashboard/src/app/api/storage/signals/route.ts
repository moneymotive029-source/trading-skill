/**
 * API endpoint for persisting and retrieving trading signals
 * Uses Vercel KV Storage (Upstash Redis)
 */

import { NextResponse } from "next/server";
import { saveSignal, getSignals, deleteSignal, addToSignalHistory, StoredSignal } from "@/lib/storage";

// GET /api/storage/signals - Retrieve stored signals
export async function GET() {
  try {
    const signals = await getSignals();
    return NextResponse.json({
      success: true,
      signals,
      count: signals.length,
    });
  } catch (error) {
    console.error("Failed to get signals:", error);
    return NextResponse.json(
      {
        success: false,
        error: "Failed to retrieve signals",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

// POST /api/storage/signals - Store a new signal
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { signal, addToHistory = false } = body;

    if (!signal || !signal.symbol) {
      return NextResponse.json(
        { success: false, error: "Signal data is required" },
        { status: 400 }
      );
    }

    // Validate signal structure
    const storedSignal: StoredSignal = {
      id: signal.id || `signal_${Date.now()}`,
      symbol: signal.symbol,
      assetClass: signal.assetClass || "unknown",
      direction: signal.direction,
      confidence: signal.confidence,
      entryZone: signal.entryZone,
      stopLoss: signal.stopLoss,
      takeProfit: signal.takeProfit,
      riskReward: signal.riskReward,
      timestamp: signal.timestamp || new Date().toISOString(),
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24 hours
    };

    // Save signal
    await saveSignal(storedSignal);

    // Optionally add to history
    if (addToHistory) {
      await addToSignalHistory(storedSignal);
    }

    return NextResponse.json({
      success: true,
      signal: storedSignal,
    });
  } catch (error) {
    console.error("Failed to save signal:", error);
    return NextResponse.json(
      {
        success: false,
        error: "Failed to save signal",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

// DELETE /api/storage/signals - Remove a signal
export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const id = await searchParams.get("id");

    if (!id) {
      return NextResponse.json(
        { success: false, error: "Signal ID is required" },
        { status: 400 }
      );
    }

    await deleteSignal(id);

    return NextResponse.json({
      success: true,
      message: `Signal ${id} deleted`,
    });
  } catch (error) {
    console.error("Failed to delete signal:", error);
    return NextResponse.json(
      {
        success: false,
        error: "Failed to delete signal",
      },
      { status: 500 }
    );
  }
}
