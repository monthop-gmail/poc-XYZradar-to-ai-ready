# คู่มือการทดสอบและ Debug MCP Tools ก่อน Deploy

คู่มือนี้เขียนสำหรับ developer ที่ต้องการทดสอบ MCP Server ของโปรเจกต์ Fuel Radar (ข้อมูลสถานะน้ำมันปั๊มในประเทศไทย) ก่อนนำไป deploy จริง

## สารบัญ

1. [ทำไมต้องทดสอบ MCP Tool](#1-ทำไมต้องทดสอบ-mcp-tool)
2. [ทดสอบฟังก์ชัน Python โดยตรง (Unit Test)](#2-ทดสอบฟังก์ชัน-python-โดยตรง-unit-test)
3. [ทดสอบ MCP Server ด้วย MCP Inspector](#3-ทดสอบ-mcp-server-ด้วย-mcp-inspector)
4. [ทดสอบด้วย curl](#4-ทดสอบด้วย-curl)
5. [ทดสอบด้วย AI Client จริง](#5-ทดสอบด้วย-ai-client-จริง)
6. [Debug เมื่อ AI เรียก Tool ผิดตัว](#6-debug-เมื่อ-ai-เรียก-tool-ผิดตัว)
7. [Debug เมื่อ Tool return ข้อมูลผิด](#7-debug-เมื่อ-tool-return-ข้อมูลผิด)
8. [Checklist การทดสอบก่อน Deploy](#8-checklist-การทดสอบก่อน-deploy)

---

## 1. ทำไมต้องทดสอบ MCP Tool

MCP (Model Context Protocol) เป็น protocol ที่ให้ AI client (เช่น Claude, Cursor) เรียกใช้ tool ที่เราสร้างขึ้น ถ้าไม่ทดสอบก่อน deploy อาจเจอปัญหาเหล่านี้:

- **Tool return ข้อมูลผิด** -- เช่น search ไม่เจอปั๊มที่ควรเจอ หรือแสดงสถานะน้ำมันผิด
- **AI เรียก Tool ผิดตัว** -- เช่น user ถามสรุปภาพรวม แต่ AI เรียก `search_fuel_status` แทน `get_fuel_summary` เพราะ description ไม่ชัดเจน
- **Server crash** -- เช่น ไฟล์ข้อมูลไม่มี หรือ JSON format ผิด
- **Performance ช้า** -- เช่น อ่านไฟล์ใหญ่ทุกครั้งที่มี request

การทดสอบแบ่งเป็นหลายระดับ ตั้งแต่ทดสอบ function ตรง ๆ ไปจนถึงทดสอบกับ AI client จริง

---

## 2. ทดสอบฟังก์ชัน Python โดยตรง (Unit Test)

### ทดสอบอะไร
ทดสอบว่า logic ของ function ทำงานถูกต้อง โดยไม่ต้องผ่าน MCP protocol เลย เป็นการเช็คว่า "ถ้าส่ง input แบบนี้เข้าไป จะได้ output ถูกต้องไหม"

### ใช้เมื่อไหร่
- ตอนเขียน function ใหม่ หรือแก้ไข logic
- ตอนแก้ bug ที่เกี่ยวกับ data processing
- ก่อนจะเริ่มทดสอบขั้นต่อไป (ถ้า function ผิด ไม่ต้องเสียเวลา test MCP)

### วิธีทำ

#### 2.1 ทดสอบใน Python REPL

เปิด terminal แล้วรันคำสั่ง:

```bash
cd /opt/docker-test/server-dataradar/poc-radar-to-ai-ready

# เปิด Python REPL
python3
```

จากนั้นลองเรียก function ตรง ๆ:

```python
# import function จาก mcp_server.py (version ที่มี logic แยกออกมา)
import sys
sys.path.insert(0, 'pipeline')
from mcp_server import search_fuel_status_logic, get_fuel_summary_logic

# ทดสอบ search_fuel_status_logic
result = search_fuel_status_logic("กรุงเทพ")
print(result)

# ทดสอบ get_fuel_summary_logic
result = get_fuel_summary_logic()
print(result)

# ทดสอบ case ที่หาไม่เจอ
result = search_fuel_status_logic("ดาวอังคาร")
print(result)
```

#### ตัวอย่าง output ที่คาดหวัง

`search_fuel_status_logic("กรุงเทพ")`:
```
Found 2 reports:
- ปั๊มน้ำมัน (กรุงเทพมหานคร): Diesel: available, B95: available, Confidence: 0.3
- Shell (กรุงเทพมหานคร): Diesel: available, B95: unknown, Confidence: 0.3
```

`get_fuel_summary_logic()`:
```
Summary:
- Total reports: 5
- Diesel Out: 1
Top provinces with diesel out:
  - None: 1 reports
```

`search_fuel_status_logic("ดาวอังคาร")`:
```
No reports found for: ดาวอังคาร
```

#### 2.2 เขียน Unit Test แบบ pytest

สร้างไฟล์ test เพื่อรัน automated ได้:

```python
# tests/test_fuel_logic.py
import sys
sys.path.insert(0, 'pipeline')
from mcp_server import search_fuel_status_logic, get_fuel_summary_logic

def test_search_found():
    result = search_fuel_status_logic("กรุงเทพ")
    assert "Found" in result
    assert "กรุงเทพ" in result

def test_search_not_found():
    result = search_fuel_status_logic("ดาวอังคาร")
    assert "No reports found" in result

def test_summary_has_total():
    result = get_fuel_summary_logic()
    assert "Total reports:" in result
    assert "Diesel Out:" in result

def test_search_case_insensitive():
    result = search_fuel_status_logic("shell")
    assert "Found" in result or "SHELL" in result.upper()
```

รัน test:

```bash
pip install pytest
pytest tests/test_fuel_logic.py -v
```

ตัวอย่าง output:

```
tests/test_fuel_logic.py::test_search_found PASSED
tests/test_fuel_logic.py::test_search_not_found PASSED
tests/test_fuel_logic.py::test_summary_has_total PASSED
tests/test_fuel_logic.py::test_search_case_insensitive PASSED
```

---

## 3. ทดสอบ MCP Server ด้วย MCP Inspector

### ทดสอบอะไร
ทดสอบว่า MCP Server ทำงานถูกต้องในฐานะ MCP protocol -- tool registration, input schema, และ tool execution ทำงานครบถ้วน

### ใช้เมื่อไหร่
- ตอนต้องการดูว่า tool list แสดงผลถูกต้อง
- ตอนต้องการทดสอบ tool call แบบ interactive โดยไม่ต้องเขียน code
- ตอนต้องการ debug ว่า MCP protocol ทำงานถูกไหม

### วิธีทำ

#### 3.1 ทดสอบกับ mcp_server_modern.py (FastMCP - แนะนำ)

FastMCP (`mcp_server_modern.py`) รองรับ MCP Inspector โดยตรง:

```bash
# ติดตั้ง Node.js (ถ้ายังไม่มี)
# MCP Inspector ต้องใช้ npx

# รัน MCP Inspector กับ server ของเรา
npx @modelcontextprotocol/inspector python3 pipeline/mcp_server_modern.py
```

Inspector จะเปิด browser ขึ้นมาที่ `http://localhost:5173` (หรือ port อื่นที่แจ้ง)

#### 3.2 สิ่งที่ต้องตรวจสอบใน Inspector

1. **Tools tab** -- ดูว่า tool ทั้ง 2 ตัวแสดงครบ:
   - `search_fuel_status` -- มี parameter `query` (type: string)
   - `get_fuel_summary` -- ไม่มี parameter

2. **ลองเรียก Tool** -- กดที่ tool แล้วกรอก input:
   - เลือก `search_fuel_status` แล้วใส่ query: `"ราชบุรี"`
   - เลือก `get_fuel_summary` แล้วกด Execute

3. **ตรวจสอบ Response** -- ดูว่า response มี format ถูกต้อง

#### ตัวอย่าง output ที่คาดหวัง

เมื่อกดดู Tools list ใน Inspector:

```json
{
  "tools": [
    {
      "name": "search_fuel_status",
      "description": "Search for fuel availability in Thailand by station name, province, or district.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": { "type": "string" }
        },
        "required": ["query"]
      }
    },
    {
      "name": "get_fuel_summary",
      "description": "Get overall summary of fuel status and provinces with fuel shortages.",
      "inputSchema": {
        "type": "object",
        "properties": {}
      }
    }
  ]
}
```

เมื่อเรียก `search_fuel_status` ด้วย query `"ราชบุรี"`:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 1 reports:\n- Mobil โชคอนันต์ด่านทับตะโก (ราชบุรี): Diesel: available, B95: available\n"
    }
  ]
}
```

#### 3.3 ถ้า Inspector ไม่สามารถเชื่อมต่อได้

ตรวจสอบว่า:
- ไฟล์ `data/radar_clean.jsonl` มีอยู่จริง (ถ้ารันนอก Docker ต้องแก้ `DATA_PATH` ใน `mcp_server_modern.py` เป็น path ที่ถูกต้อง)
- Python มี package `mcp` ติดตั้งแล้ว: `pip install mcp[cli]`

---

## 4. ทดสอบด้วย curl

### ทดสอบอะไร
ทดสอบว่า MCP Server ที่รันเป็น HTTP service (SSE transport) ตอบ JSON-RPC request ได้ถูกต้อง เหมาะสำหรับทดสอบ `mcp_server.py` (version ที่ใช้ FastAPI)

### ใช้เมื่อไหร่
- ตอน server รันอยู่แล้ว (ใน Docker หรือ local) และต้องการทดสอบ endpoint
- ตอนต้องการดู raw JSON-RPC request/response
- ตอนต้องการ automate test ด้วย script

### วิธีทำ

#### 4.1 รัน Server ก่อน

```bash
# วิธี 1: รันด้วย Docker
cd /opt/docker-test/server-dataradar/poc-radar-to-ai-ready
docker compose up -d

# วิธี 2: รันตรง ๆ (mcp_server.py version)
python3 pipeline/mcp_server.py --transport sse --port 3000

# วิธี 3: รันตรง ๆ (mcp_server_modern.py version ผ่าน mcp CLI)
mcp run pipeline/mcp_server_modern.py --transport sse --port 3000
```

#### 4.2 ทดสอบ initialize

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {}
  }'
```

ตัวอย่าง output ที่คาดหวัง:

```json
{"status": "ok"}
```

(response จริงจะถูกส่งผ่าน SSE stream -- สำหรับ `mcp_server.py` version response จะถูก put เข้า queue แล้วส่งผ่าน GET `/mcp`)

#### 4.3 ทดสอบ tools/list

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

#### 4.4 ทดสอบ tools/call -- search_fuel_status

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "search_fuel_status",
      "arguments": {
        "query": "อุบลราชธานี"
      }
    }
  }'
```

ตัวอย่าง output ที่คาดหวัง (จาก SSE stream):

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 1 reports:\n- เซลล์ (อุบลราชธานี): Diesel: available, B95: unknown, Confidence: 0.3\n"
      }
    ]
  }
}
```

#### 4.5 ทดสอบ tools/call -- get_fuel_summary

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "get_fuel_summary",
      "arguments": {}
    }
  }'
```

#### 4.6 ทดสอบ error case -- tool ไม่มีอยู่

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "nonexistent_tool",
      "arguments": {}
    }
  }'
```

ตัวอย่าง output ที่คาดหวัง:

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Tool nonexistent_tool not found."
      }
    ]
  }
}
```

> **หมายเหตุ:** เนื่องจาก `mcp_server.py` ใช้ SSE transport จริง ๆ response จะถูกส่งผ่าน Server-Sent Events ที่ GET `/mcp` ไม่ใช่ใน response ของ POST โดยตรง ดังนั้นต้องเปิด SSE listener ด้วย:
>
> ```bash
> # เปิด terminal แรก -- listen SSE stream
> curl -N http://localhost:3000/mcp
>
> # เปิด terminal ที่สอง -- ส่ง request
> curl -X POST http://localhost:3000/mcp \
>   -H "Content-Type: application/json" \
>   -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_fuel_summary","arguments":{}}}'
> ```

---

## 5. ทดสอบด้วย AI Client จริง

### ทดสอบอะไร
ทดสอบ end-to-end ว่า AI client สามารถค้นพบ tool, เลือก tool ที่ถูกต้อง, ส่ง parameter ถูกต้อง, และแสดงผลลัพธ์ให้ user ได้อย่างเหมาะสม

### ใช้เมื่อไหร่
- ตอนทดสอบขั้นสุดท้ายก่อน deploy
- ตอนต้องการดูว่า AI เข้าใจ tool description ไหม
- ตอนต้องการดูว่า AI แสดงผลลัพธ์ให้ user ยังไง

### วิธีทำ

#### 5.1 ตั้งค่า MCP Server ใน Claude Desktop

แก้ไขไฟล์ config ของ Claude Desktop:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fuel-radar": {
      "command": "python3",
      "args": ["pipeline/mcp_server_modern.py"],
      "cwd": "/opt/docker-test/server-dataradar/poc-radar-to-ai-ready"
    }
  }
}
```

หรือถ้าใช้ SSE transport (เช่น server รันอยู่ใน Docker):

```json
{
  "mcpServers": {
    "fuel-radar": {
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

#### 5.2 ตั้งค่าใน Cursor

เปิด Cursor Settings > MCP > Add Server:
- Name: `fuel-radar`
- Type: `sse`
- URL: `http://localhost:3000/mcp`

#### 5.3 คำถามที่ควรลองถาม

ลองถามคำถามเหล่านี้แล้วดูว่า AI เรียก tool ถูกตัว:

| คำถาม | Tool ที่ควรถูกเรียก | เหตุผล |
|--------|---------------------|--------|
| "ปั๊มน้ำมันในกรุงเทพมีน้ำมันไหม" | `search_fuel_status` (query: "กรุงเทพ") | ถามเฉพาะจังหวัด |
| "สรุปสถานะน้ำมันทั้งหมด" | `get_fuel_summary` | ถามภาพรวม |
| "ปั๊ม Shell มีดีเซลไหม" | `search_fuel_status` (query: "shell") | ถามเฉพาะแบรนด์ |
| "จังหวัดไหนน้ำมันหมด" | `get_fuel_summary` | ถามภาพรวมการขาดแคลน |
| "ปั๊มในราชบุรี จอมบึง" | `search_fuel_status` (query: "จอมบึง" หรือ "ราชบุรี") | ถามเฉพาะอำเภอ/จังหวัด |

#### 5.4 สิ่งที่ต้องสังเกต

- **AI เรียก tool ถูกตัวไหม** -- ถ้าถามภาพรวมแล้วเรียก `search_fuel_status` แสดงว่า description ไม่ชัดเจนพอ
- **AI ส่ง parameter ถูกไหม** -- ถ้า user พูดว่า "กรุงเทพ" แต่ AI ส่ง query: "Bangkok" จะไม่เจอข้อมูล
- **AI แสดงผลลัพธ์เข้าใจง่ายไหม** -- AI ควรจะสรุปผลลัพธ์เป็นภาษาที่ user เข้าใจ

---

## 6. Debug เมื่อ AI เรียก Tool ผิดตัว

### ปัญหา
AI เลือก tool ที่ไม่ถูกต้อง เช่น ถาม "สรุปภาพรวม" แต่ AI เรียก `search_fuel_status` แทน `get_fuel_summary`

### สาเหตุหลัก
AI เลือก tool จาก **description** ของ tool ถ้า description คล้ายกันเกินไปหรือไม่ชัดเจน AI จะสับสน

### วิธี debug

#### 6.1 ตรวจสอบ description ปัจจุบัน

ดูไฟล์ `pipeline/mcp_server_modern.py`:

```python
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search for fuel availability in Thailand by station name, province, or district."""

@mcp.tool()
def get_fuel_summary() -> str:
    """Get overall summary of fuel status and provinces with fuel shortages."""
```

#### 6.2 หลักการเขียน description ที่ดี

- **บอกให้ชัดว่า tool ทำอะไร** -- ไม่ใช่แค่ "search fuel" แต่ต้องบอกว่า search จากอะไร (ชื่อปั๊ม, จังหวัด, อำเภอ)
- **บอกว่า tool นี้ไม่ทำอะไร** -- ช่วยให้ AI แยกแยะ tool ได้
- **บอก input ที่รับ** -- เช่น "takes a Thai text query"
- **บอก output ที่ได้** -- เช่น "returns list of matching stations with diesel and benzine status"

#### 6.3 ตัวอย่างการแก้ description

**ก่อนแก้ (ไม่ชัดเจน):**
```python
"""Search for fuel availability in Thailand."""
"""Get overall summary of fuel status."""
```

**หลังแก้ (ชัดเจนขึ้น):**
```python
"""Search for fuel availability at a SPECIFIC station, province, or district in Thailand.
Use this tool when the user asks about a specific location or station name.
Input: a Thai text query (e.g. station name, province, or district).
Output: list of matching fuel stations with diesel and benzine95 status.
Do NOT use this tool for overall summaries -- use get_fuel_summary instead."""

"""Get OVERALL summary of fuel status across all of Thailand.
Use this tool when the user asks for a general overview, statistics, or wants to know which provinces have fuel shortages.
Input: none.
Output: total number of reports, count of diesel-out stations, top provinces with shortages.
Do NOT use this tool to search for a specific station -- use search_fuel_status instead."""
```

#### 6.4 ตรวจสอบว่าแก้แล้วดีขึ้นไหม

1. แก้ description ใน code
2. restart MCP Server
3. ลองถามคำถามเดิมใน AI client ดูว่าเรียก tool ถูกตัวไหม
4. ดูใน MCP Inspector ว่า tool list แสดง description ใหม่ถูกต้อง

---

## 7. Debug เมื่อ Tool return ข้อมูลผิด

### ปัญหา
Tool ถูกเรียกถูกตัวแล้ว แต่ข้อมูลที่ return กลับมาผิด เช่น:
- search ไม่เจอปั๊มที่ควรเจอ
- จำนวนรายงานไม่ตรง
- สถานะน้ำมันแสดงผิด

### วิธี debug

#### 7.1 ตรวจสอบไฟล์ข้อมูล

```bash
# ดูว่าไฟล์ข้อมูลมีอยู่ไหม
ls -la data/radar_clean.jsonl

# ดูจำนวน record
wc -l data/radar_clean.jsonl

# ดูตัวอย่างข้อมูล 3 record แรก
head -3 data/radar_clean.jsonl | python3 -m json.tool
```

#### 7.2 ตรวจสอบ search logic

ปัญหาที่พบบ่อยคือ search ใช้ `query.lower() in search_text` ซึ่งเป็น substring match:

```python
# ทดสอบใน Python REPL
search_text = "Mobil โชคอนันต์ด่านทับตะโก ราชบุรี จอมบึง".lower()

# ทดสอบ query ต่าง ๆ
print("ราชบุรี" in search_text)      # True
print("จอมบึง" in search_text)      # True
print("mobil" in search_text)        # True
print("โชคอนันต์" in search_text)   # True
print("ราช" in search_text)         # True (partial match!)
print("บุรี" in search_text)        # True (partial match!)
```

#### 7.3 ตรวจสอบ data path ใน Docker vs Local

สิ่งสำคัญ: `mcp_server_modern.py` ใช้ path `/app/data/radar_clean.jsonl` (สำหรับ Docker) แต่ `mcp_server.py` ใช้ relative path จาก script

```python
# mcp_server_modern.py -- hardcoded Docker path
DATA_PATH = "/app/data/radar_clean.jsonl"

# mcp_server.py -- relative path
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'radar_clean.jsonl')
```

ถ้ารันนอก Docker แล้วใช้ `mcp_server_modern.py` จะหาไฟล์ไม่เจอ ต้องแก้ `DATA_PATH` หรือใช้ `mcp_server.py` แทน

#### 7.4 ตรวจสอบ field ในข้อมูล

```python
import json

with open('data/radar_clean.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        record = json.loads(line)
        print(record.keys())
        break

# ดู field ที่มี:
# stationName, brandId, province, district, diesel, benzine91, benzine95, e20, lpg, confidence, createdAt
```

ตรวจสอบว่า code อ้างอิง field name ตรงกับข้อมูลจริง เช่น ใน code ใช้ `r.get('benzine95')` ซึ่งตรงกับ field ในข้อมูล

#### 7.5 ตรวจสอบ edge cases

```python
# ดู record ที่มี province เป็น null
import json
with open('data/radar_clean.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        if r.get('province') is None:
            print(f"province=None: {r.get('stationName')}")
        if r.get('district') is None:
            print(f"district=None: {r.get('stationName')}")
```

ถ้า province หรือ district เป็น `None` จะทำให้ search text มีคำว่า "None" ซึ่งอาจทำให้ search "none" เจอ record ที่ไม่ควรเจอ แก้ได้โดย:

```python
# แก้จาก
search_text = f"{r.get('stationName')} {r.get('province')} {r.get('district')}".lower()

# เป็น
search_text = f"{r.get('stationName', '')} {r.get('province', '')} {r.get('district', '')}".lower()
```

---

## 8. Checklist การทดสอบก่อน Deploy

ใช้ checklist นี้ทุกครั้งก่อน deploy MCP Server:

### ข้อมูล (Data)
- [ ] ไฟล์ `data/radar_clean.jsonl` มีอยู่และไม่ว่างเปล่า
- [ ] JSON format ถูกต้องทุก line (`python3 -c "import json; [json.loads(l) for l in open('data/radar_clean.jsonl')]"`)
- [ ] ข้อมูลเป็นข้อมูลล่าสุด (ตรวจสอบ `createdAt` field)

### Function Logic
- [ ] `search_fuel_status` -- search ด้วยชื่อปั๊มแล้วเจอ
- [ ] `search_fuel_status` -- search ด้วยจังหวัดแล้วเจอ
- [ ] `search_fuel_status` -- search ด้วยอำเภอแล้วเจอ
- [ ] `search_fuel_status` -- search ด้วยคำที่ไม่มีแล้วได้ "No reports found"
- [ ] `get_fuel_summary` -- แสดงจำนวน total ถูกต้อง
- [ ] `get_fuel_summary` -- แสดงจำนวน diesel out ถูกต้อง
- [ ] `get_fuel_summary` -- แสดง top provinces ถูกต้อง

### MCP Protocol
- [ ] MCP Inspector แสดง tool list ครบ 2 ตัว
- [ ] MCP Inspector เรียก `search_fuel_status` แล้วได้ผลลัพธ์
- [ ] MCP Inspector เรียก `get_fuel_summary` แล้วได้ผลลัพธ์
- [ ] Tool description ชัดเจน แยกแยะได้ว่า tool ไหนใช้ตอนไหน

### HTTP Endpoint (ถ้าใช้ SSE transport)
- [ ] `POST /mcp` กับ method `initialize` ตอบกลับถูกต้อง
- [ ] `POST /mcp` กับ method `tools/list` ตอบกลับ tool ครบ
- [ ] `POST /mcp` กับ method `tools/call` เรียก tool ได้ถูกต้อง
- [ ] `GET /mcp` เปิด SSE stream ได้

### Docker
- [ ] `docker compose build` สำเร็จไม่มี error
- [ ] `docker compose up` server เริ่มทำงานได้
- [ ] Volume mount `/app/data` ทำงานถูกต้อง (ข้อมูลอ่านได้)
- [ ] Port 3000 เข้าถึงได้จากภายนอก container

### AI Client
- [ ] ถาม "ปั๊มในกรุงเทพ" --> AI เรียก `search_fuel_status`
- [ ] ถาม "สรุปภาพรวม" --> AI เรียก `get_fuel_summary`
- [ ] AI ส่ง parameter เป็นภาษาไทยถูกต้อง
- [ ] AI แสดงผลลัพธ์เข้าใจง่าย

---

## สรุปลำดับการทดสอบที่แนะนำ

```
1. Unit Test (Python REPL / pytest)
   --> ตรวจว่า logic ถูกต้อง

2. MCP Inspector
   --> ตรวจว่า MCP protocol ทำงานถูกต้อง, tool list ครบ

3. curl (ถ้าใช้ SSE transport)
   --> ตรวจว่า HTTP endpoint ทำงาน

4. Docker
   --> ตรวจว่า containerized server ทำงานได้

5. AI Client จริง
   --> ตรวจว่า AI เลือก tool ถูกตัวและแสดงผลดี
```

ทดสอบตามลำดับนี้จะช่วยให้ debug ได้ง่าย -- ถ้า step 1 fail ไม่ต้องเสียเวลาทดสอบ step ถัดไป
