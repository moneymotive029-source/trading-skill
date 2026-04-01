import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_AGENT_PATH = path.join(
  __dirname,
  "../../../../agents/financial_intelligence_trading_agent.py"
);

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { symbol, assetClass = "cryptocurrency" } = body;

    if (!symbol) {
      return NextResponse.json(
        { error: "Symbol is required" },
        { status: 400 }
      );
    }

    // Run Python agent as subprocess
    const result = await runPythonAgent(symbol, assetClass);

    return NextResponse.json({
      success: true,
      data: result,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Analysis error:", error);
    return NextResponse.json(
      {
        error: "Failed to run analysis",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

async function runPythonAgent(
  symbol: string,
  assetClass: string
): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python", [
      PYTHON_AGENT_PATH,
      "--symbol",
      symbol,
      "--asset-class",
      assetClass,
    ]);

    let stdout = "";
    let stderr = "";

    pythonProcess.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code === 0) {
        try {
          // Parse JSON output from Python agent
          const result = JSON.parse(stdout);
          resolve(result);
        } catch {
          // If not JSON, return raw output
          resolve({ rawOutput: stdout });
        }
      } else {
        reject(new Error(stderr || `Python process exited with code ${code}`));
      }
    });

    pythonProcess.on("error", (err) => {
      reject(err);
    });

    // Timeout after 60 seconds
    setTimeout(() => {
      pythonProcess.kill();
      reject(new Error("Analysis timed out after 60 seconds"));
    }, 60000);
  });
}

// GET endpoint for health check
export async function GET() {
  return NextResponse.json({
    status: "healthy",
    pythonAgentPath: PYTHON_AGENT_PATH,
  });
}
