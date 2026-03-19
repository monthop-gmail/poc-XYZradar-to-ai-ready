from mcp.server.fastmcp import FastMCP
import json
import os

# Define the data path
# Note: In Docker, we map the volume to /app/data
DATA_PATH = "/app/data/radar_clean.jsonl"

# Create a FastMCP server
mcp = FastMCP("Fuel Radar Modern", dependencies=["pandas", "pyarrow", "requests"])

def get_data():
    results = []
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    results.append(json.loads(line))
                except: continue
    return results

@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search for fuel availability in Thailand by station name, province, or district."""
    data = get_data()
    matches = []
    for r in data:
        search_all = f"{r.get('stationName')} {r.get('province')} {r.get('district')}".lower()
        if query.lower() in search_all:
            matches.append(r)
    
    if not matches:
        return f"No reports found for: {query}"
    
    output = f"Found {len(matches)} reports:\n"
    for r in matches[:5]:
        output += f"- {r.get('stationName')} ({r.get('province')}): Diesel: {r.get('diesel')}, B95: {r.get('benzine95')}\n"
    return output

@mcp.tool()
def get_fuel_summary() -> str:
    """Get overall summary of fuel status and provinces with fuel shortages."""
    data = get_data()
    total = len(data)
    out = sum(1 for r in data if r.get('diesel') == 'out')
    
    prov_out = {}
    for r in data:
        if r.get('diesel') == 'out':
            p = r.get('province')
            prov_out[p] = prov_out.get(p, 0) + 1
            
    summary = f"Summary:\n- Total: {total}\n- Diesel Out: {out}\n"
    top = sorted(prov_out.items(), key=lambda x: x[1], reverse=True)[:3]
    for p, c in top:
        summary += f"  - {p}: {c} reports\n"
    return summary

if __name__ == "__main__":
    mcp.run()
