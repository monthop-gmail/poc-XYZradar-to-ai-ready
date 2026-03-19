import sys
import json
import os

# Define the data path relative to this script
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'radar_clean.jsonl')

def search_fuel_status(query):
    results = []
    if not os.path.exists(DATA_PATH):
        return "Data file not found. Please run process_radar.py first."
    
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            report = json.loads(line)
            # Search in stationName, province, district
            search_text = f"{report.get('stationName')} {report.get('province')} {report.get('district')}".lower()
            if query.lower() in search_text:
                results.append(report)
    
    if not results:
        return f"No reports found for: {query}"
    
    output = f"Found {len(results)} reports:\n"
    for r in results[:5]: # Show top 5
        output += f"- {r.get('stationName')} ({r.get('province')}): Diesel: {r.get('diesel')}, B95: {r.get('benzine95')}, Confidence: {r.get('confidence')}\n"
    return output

def get_fuel_summary():
    if not os.path.exists(DATA_PATH):
        return "Data file not found."
    
    stats = {"total": 0, "diesel_out": 0, "provinces": {}}
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            stats["total"] += 1
            if r.get('diesel') == 'out':
                stats["diesel_out"] += 1
            prov = r.get('province')
            stats["provinces"][prov] = stats["provinces"].get(prov, 0) + (1 if r.get('diesel') == 'out' else 0)
            
    summary = f"Summary:\n- Total reports: {stats['total']}\n- Diesel Out: {stats['diesel_out']}\n"
    top_provinces = sorted(stats["provinces"].items(), key=lambda x: x[1], reverse=True)[:3]
    summary += "Top provinces with diesel out:\n"
    for p, c in top_provinces:
        summary += f"  - {p}: {c} reports\n"
    return summary

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            msg_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "fuel-radar-mcp", "version": "1.0.0"}
                    }
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "search_fuel_status",
                                "description": "Search for fuel availability in Thailand by station name, province, or district.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "Keyword to search (e.g., 'Bangkok', 'PTT')"}
                                    },
                                    "required": ["query"]
                                }
                            },
                            {
                                "name": "get_fuel_summary",
                                "description": "Get overall summary of fuel status and provinces with fuel shortages.",
                                "inputSchema": {"type": "object", "properties": {}}
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                if tool_name == "search_fuel_status":
                    res_text = search_fuel_status(tool_args.get("query", ""))
                elif tool_name == "get_fuel_summary":
                    res_text = get_fuel_summary()
                else:
                    res_text = f"Tool {tool_name} not found."
                
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": res_text}]
                    }
                }
            elif method == "notifications/initialized":
                continue # No response needed
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": "Method not found"}
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            # Errors should also be sent as JSON-RPC errors if possible
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
