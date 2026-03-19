import sys
import json
import os
import argparse
import asyncio
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import uvicorn

# Define the data path relative to this script
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'radar_clean.jsonl')

def search_fuel_status_logic(query):
    results = []
    if not os.path.exists(DATA_PATH):
        return "Data file not found. Please run process_radar.py first."
    
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                report = json.loads(line)
                search_text = f"{report.get('stationName')} {report.get('province')} {report.get('district')}".lower()
                if query.lower() in search_text:
                    results.append(report)
            except: continue
    
    if not results:
        return f"No reports found for: {query}"
    
    output = f"Found {len(results)} reports:\n"
    for r in results[:5]: 
        output += f"- {r.get('stationName')} ({r.get('province')}): Diesel: {r.get('diesel')}, B95: {r.get('benzine95')}, Confidence: {r.get('confidence')}\n"
    return output

def get_fuel_summary_logic():
    if not os.path.exists(DATA_PATH):
        return "Data file not found."
    
    stats = {"total": 0, "diesel_out": 0, "provinces": {}}
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                r = json.loads(line)
                stats["total"] += 1
                if r.get('diesel') == 'out':
                    stats["diesel_out"] += 1
                prov = r.get('province')
                stats["provinces"][prov] = stats["provinces"].get(prov, 0) + (1 if r.get('diesel') == 'out' else 0)
            except: continue
            
    summary = f"Summary:\n- Total reports: {stats['total']}\n- Diesel Out: {stats['diesel_out']}\n"
    top_provinces = sorted(stats["provinces"].items(), key=lambda x: x[1], reverse=True)[:3]
    summary += "Top provinces with diesel out:\n"
    for p, c in top_provinces:
        summary += f"  - {p}: {c} reports\n"
    return summary

def handle_rpc(request):
    msg_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "fuel-radar-mcp", "version": "1.0.0"}}}
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": [
            {"name": "search_fuel_status", "description": "Search for fuel availability in Thailand.", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
            {"name": "get_fuel_summary", "description": "Get overall summary of fuel status.", "inputSchema": {"type": "object", "properties": {}}}
        ]}}
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        if tool_name == "search_fuel_status": res = search_fuel_status_logic(tool_args.get("query", ""))
        elif tool_name == "get_fuel_summary": res = get_fuel_summary_logic()
        else: res = f"Tool {tool_name} not found."
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": res}]}}
    elif method == "notifications/initialized": return None
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}

# --- Transport: Stdio ---
def run_stdio():
    while True:
        line = sys.stdin.readline()
        if not line: break
        try:
            req = json.loads(line)
            resp = handle_rpc(req)
            if resp:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}) + "\n")
            sys.stdout.flush()

# --- Transport: SSE (via FastAPI) ---
app = FastAPI()
queue = asyncio.Queue()

@app.get("/mcp")
async def sse(request: Request):
    async def event_generator():
        # MCP SSE requires sending the endpoint for messages
        yield {"data": json.dumps({"endpoint": "/mcp"})}
        while True:
            msg = await queue.get()
            yield {"data": json.dumps(msg)}
            queue.task_done()
    return EventSourceResponse(event_generator())

@app.post("/mcp")
async def messages(request: Request):
    try:
        req = await request.json()
        resp = handle_rpc(req)
        if resp:
            await queue.put(resp)
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    parser.add_argument("--port", type=int, default=3000)
    args = parser.parse_args()

    if args.transport == "stdio":
        run_stdio()
    else:
        print(f"Starting SSE server on port {args.port}...")
        uvicorn.run(app, host="0.0.0.0", port=args.port)
