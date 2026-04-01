/**
 * Vercel Storage Integration
 * Uses Upstash Redis for persisting trading signals and user preferences
 *
 * Setup:
 * 1. Add Upstash Redis from Vercel Marketplace
 * 2. Environment variables will be auto-configured
 *
 * Or set manually:
 * UPSTASH_REDIS_REST_URL
 * UPSTASH_REDIS_REST_TOKEN
 */

import { Redis } from "@upstash/redis";

// Initialize Redis client (lazy - only connects when used)
let redisClient: Redis | null = null;

export function getRedisClient() {
  if (!redisClient) {
    redisClient = new Redis({
      url: process.env.UPSTASH_REDIS_REST_URL || "http://localhost:8079",
      token: process.env.UPSTASH_REDIS_REST_TOKEN || "local_token",
    });
  }
  return redisClient;
}

// Storage keys
export const KEYS = {
  SIGNALS: "trading:signals",
  SIGNAL_HISTORY: "trading:signal:history",
  USER_PREFS: "trading:user:prefs",
  PORTFOLIO: "trading:portfolio",
  ALERTS: "trading:alerts",
};

export interface StoredSignal {
  id: string;
  symbol: string;
  assetClass: string;
  direction: "LONG" | "SHORT" | "NEUTRAL";
  confidence: "High" | "Medium" | "Low";
  entryZone: string;
  stopLoss: string;
  takeProfit: string;
  riskReward: string;
  timestamp: string;
  expiresAt: string;
}

export interface UserPreferences {
  theme: "dark" | "light";
  notifications: boolean;
  riskPerTrade: number;
  accountSize: number;
  favoriteAssets: string[];
}

// Signal storage functions
export async function saveSignal(signal: StoredSignal): Promise<void> {
  const redis = getRedisClient();
  await redis.lpush(KEYS.SIGNALS, JSON.stringify(signal));
  await redis.ltrim(KEYS.SIGNALS, 0, 99); // Keep last 100 signals
}

export async function getSignals(limit = 20): Promise<StoredSignal[]> {
  const redis = getRedisClient();
  const signals = await redis.lrange<StoredSignal>(KEYS.SIGNALS, 0, limit - 1);
  return signals || [];
}

export async function deleteSignal(id: string): Promise<void> {
  const redis = getRedisClient();
  const signals = await getSignals(100);
  const filtered = signals.filter((s) => s.id !== id);
  await redis.del(KEYS.SIGNALS);
  if (filtered.length > 0) {
    await redis.rpush(KEYS.SIGNALS, ...filtered);
  }
}

// Signal history (for backtracking and analytics)
export async function addToSignalHistory(signal: StoredSignal): Promise<void> {
  const redis = getRedisClient();
  const key = `${KEYS.SIGNAL_HISTORY}:${signal.symbol}`;
  await redis.lpush(key, JSON.stringify(signal));
  await redis.ltrim(key, 0, 999); // Keep last 1000 entries per symbol
}

export async function getSignalHistory(symbol: string, limit = 50): Promise<StoredSignal[]> {
  const redis = getRedisClient();
  const key = `${KEYS.SIGNAL_HISTORY}:${symbol}`;
  const history = await redis.lrange<StoredSignal>(key, 0, limit - 1);
  return history || [];
}

// User preferences
export async function saveUserPreferences(prefs: UserPreferences): Promise<void> {
  const redis = getRedisClient();
  await redis.set(KEYS.USER_PREFS, JSON.stringify(prefs));
}

export async function getUserPreferences(): Promise<UserPreferences | null> {
  const redis = getRedisClient();
  const data = await redis.get<string>(KEYS.USER_PREFS);
  if (!data) return null;
  return JSON.parse(data);
}

// Portfolio tracking
export async function updatePortfolio(data: {
  totalValue: number;
  positions: number;
  dayPnl: number;
  riskExposure: number;
}): Promise<void> {
  const redis = getRedisClient();
  await redis.set(
    KEYS.PORTFOLIO,
    JSON.stringify({
      ...data,
      updatedAt: new Date().toISOString(),
    })
  );
}

export async function getPortfolio(): Promise<{
  totalValue: number;
  positions: number;
  dayPnl: number;
  riskExposure: number;
  updatedAt: string;
} | null> {
  const redis = getRedisClient();
  const data = await redis.get<string>(KEYS.PORTFOLIO);
  if (!data) return null;
  return JSON.parse(data);
}

// Alerts
export async function createAlert(alert: {
  id: string;
  symbol: string;
  condition: string;
  triggered: boolean;
}): Promise<void> {
  const redis = getRedisClient();
  await redis.lpush(KEYS.ALERTS, JSON.stringify(alert));
  await redis.ltrim(KEYS.ALERTS, 0, 49); // Keep last 50 alerts
}

export async function getAlerts(): Promise<any[]> {
  const redis = getRedisClient();
  const alerts = await redis.lrange(KEYS.ALERTS, 0, 49);
  return alerts.map((a) => JSON.parse(a));
}

// Analytics helpers
export async function getSignalStats(symbol?: string): Promise<{
  total: number;
  longCount: number;
  shortCount: number;
  neutralCount: number;
  highConfidenceCount: number;
}> {
  const signals = await getSignals(100);
  const filtered = symbol ? signals.filter((s) => s.symbol === symbol) : signals;

  return {
    total: filtered.length,
    longCount: filtered.filter((s) => s.direction === "LONG").length,
    shortCount: filtered.filter((s) => s.direction === "SHORT").length,
    neutralCount: filtered.filter((s) => s.direction === "NEUTRAL").length,
    highConfidenceCount: filtered.filter((s) => s.confidence === "High").length,
  };
}

// Health check
export async function checkStorageHealth(): Promise<{
  connected: boolean;
  error?: string;
}> {
  try {
    const redis = getRedisClient();
    await redis.ping();
    return { connected: true };
  } catch (error) {
    return {
      connected: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}
