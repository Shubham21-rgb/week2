from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import os
from fastapi.responses import JSONResponse

app = FastAPI()

# Enable CORS for all origins, all methods, all headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains
    allow_methods=["*"],  # allow GET, POST, OPTIONS, etc.
    allow_headers=["*"]
)

# Load telemetry data
file_path = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
with open(file_path, "r") as f:
    telemetry = json.load(f)

df = pd.DataFrame(telemetry)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/index")
async def compute_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    response = {}

    for region in regions:
        region_df = df[df["region"] == region]

        if region_df.empty:
            response[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        avg_latency = region_df["latency_ms"].mean()
        p95_latency = region_df["latency_ms"].quantile(0.95)
        avg_uptime = region_df["uptime_pct"].mean()
        breaches = (region_df["latency_ms"] > threshold).sum()

        response[region] = {
            "avg_latency": float(avg_latency),
            "p95_latency": float(p95_latency),
            "avg_uptime": float(avg_uptime),
            "breaches": int(breaches)
        }

    return JSONResponse(
        content=response,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )
