from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# Root page for GET requests
@app.get("/", response_class=HTMLResponse)
async def homepage():
    return """
    <h1>Welcome to Metrics API</h1>
    <p>Send POST requests to <code>/api/index</code> with JSON body:</p>
    <pre>{
  "regions": ["us-east", "eu-west"],
  "threshold_ms": 180
}</pre>
    """

# POST endpoint for computing metrics
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
        avg_uptime = region_df["uptime"].mean()
        breaches = (region_df["latency_ms"] > threshold).sum()

        response[region] = {
            "avg_latency": float(avg_latency),
            "p95_latency": float(p95_latency),
            "avg_uptime": float(avg_uptime),
            "breaches": int(breaches)
        }

    return response