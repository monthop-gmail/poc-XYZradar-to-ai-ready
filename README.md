# จากข้อมูลสาธารณะ (Open Data) สู่ความพร้อมทาง AI (AI-Ready)

[![Status](https://img.shields.io/badge/Status-AI--Ready-success)](https://thaipumpradar.com/)
[![MCP](https://img.shields.io/badge/Protocol-MCP-blue)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-cyan)](https://www.docker.com/)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/monthop-gmail/poc-XYZradar-to-ai-ready)

โปรเจกต์นี้สาธิตกระบวนการยกระดับ **ข้อมูลสาธารณะ (Open Data)** ให้เป็น **AI-Ready Data (Level 6)** ตามโมเดล **5+1 Star Open Data** พร้อม MCP Server ที่ทำให้ AI Agent เข้าถึงข้อมูลได้ทันที

โดยใช้ข้อมูลรายงานสถานะน้ำมันจากชุมชนของ [thaipumpradar.com](https://thaipumpradar.com/) เป็นกรณีศึกษา

---

## แนวคิด: 5+1 Star Open Data Model

```text
★       Level 1: PDF, DOCX              → มนุษย์อ่านได้
★★      Level 2: Excel, CSV             → มีโครงสร้าง
★★★     Level 3: JSON, XML + Metadata   → รูปแบบเปิด
★★★★    Level 4: REST API               → เข้าถึงแบบ Real-time
★★★★★   Level 5: RDF, Linked Data       → เชื่อมโยงเชิงความหมาย
★★★★★★  Level 6: AI-Ready Data          → พร้อมใช้กับ AI/ML ทันที  ← เป้าหมายของโปรเจกต์นี้
```

รายละเอียดเพิ่มเติม: [research/open_data_model.md](./research/open_data_model.md)

---

## Architecture Overview

```text
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│   Data Source        │     │   ETL Pipeline       │     │   AI-Ready Output   │
│                      │     │                      │     │                     │
│  thaipumpradar.com   │────▶│  process_radar.py    │────▶│  radar_clean.jsonl  │
│  (REST API)          │     │  - Fetch             │     │  radar_clean.parquet│
│                      │     │  - Validate (≥0.3)   │     │  datacard.md        │
└─────────────────────┘     │  - Clean & Normalize │     └────────┬────────────┘
                             └──────────────────────┘              │
                                                                   ▼
                             ┌──────────────────────┐     ┌─────────────────────┐
                             │   AI Agent           │     │   MCP Server        │
                             │                      │◀───▶│                     │
                             │  Claude, Cursor,     │     │  search_fuel_status │
                             │  หรือ AI อื่น ๆ       │     │  get_fuel_summary   │
                             └──────────────────────┘     │  (port 3000)        │
                                                          └─────────────────────┘
```

---

## โครงสร้างโครงการ (Project Structure)

```text
.
├── .devcontainer/             # GitHub Codespaces config
│   └── devcontainer.json
├── pipeline/                  # Data Pipeline & MCP Server
│   ├── process_radar.py       # ETL: ดึง → ตรวจสอบ → ทำความสะอาด → บันทึก
│   ├── datacard.md            # Data Card: metadata ของชุดข้อมูล
│   ├── mcp_server.py          # MCP Server แบบ Stdio (Legacy/Windows)
│   └── mcp_server_modern.py   # MCP Server แบบ HTTP/SSE (Modern/Docker)
├── data/                      # ข้อมูลที่ผ่านการประมวลผล
│   ├── raw.json               # ข้อมูลดิบจาก API
│   ├── radar_clean.jsonl      # สำหรับ AI/RAG (1 record ต่อ 1 บรรทัด)
│   └── radar_clean.parquet    # สำหรับ Analytics (columnar format)
├── demo/                      # ตัวอย่างการใช้งาน
│   ├── demonstrate_ai.py      # สคริปต์สาธิต AI Analysis + Mock RAG
│   └── demonstration_results.md
├── research/                  # เอกสารวิจัยและกรอบการทำงาน
│   ├── open_data_model.md     # โมเดล 5+1 Star Open Data
│   ├── thaipumpradar_analysis_th.md  # วิเคราะห์แหล่งข้อมูล
│   ├── ai_ready_audit.md      # เกณฑ์ตรวจสอบ AI-Ready Checklist
│   ├── ai_governance_framework.md    # กรอบธรรมาภิบาล AI & Data
│   └── how_to_add_mcp_tools.md      # คู่มือเพิ่ม MCP Tools + Prompt Templates
├── Dockerfile                 # Container image (Python 3.12)
├── docker-compose.yml         # Multi-service deployment
└── requirements.txt           # Python dependencies
```

---

## วิธีการติดตั้งและใช้งาน (Getting Started)

### Prerequisites

- **Docker** & **Docker Compose** (สำหรับรันแบบ Container)
- หรือ **Python 3.12+** (สำหรับรันในเครื่อง)

### วิธีที่ 1: GitHub Codespaces (เริ่มใช้งานได้ทันที)

1. กดปุ่ม **"Open in GitHub Codespaces"** ด้านบน
2. รอให้ Codespace สร้างเสร็จ — MCP Server จะเริ่มทำงานอัตโนมัติ
3. ดู URL ของ MCP Server ที่แท็บ **Ports** (port 3000) จะได้ URL ในรูปแบบ:
   ```
   https://<codespace-name>-3000.app.github.dev/mcp
   ```
4. ตั้ง visibility ของ port เป็น **Public** เพื่อให้ AI Client ภายนอกเชื่อมต่อได้

### วิธีที่ 2: Docker Compose (แนะนำสำหรับรันในเครื่อง)

```bash
# Clone repo
git clone https://github.com/monthop-gmail/poc-XYZradar-to-ai-ready.git
cd poc-XYZradar-to-ai-ready

# รัน MCP Server
docker-compose up -d --build
```

MCP Server พร้อมใช้งานที่ `http://localhost:3000/mcp`

### การตั้งค่า MCP ในแอป AI (Claude Desktop, Cursor, Windsurf, etc.)

เมื่อ MCP Server ทำงานแล้ว ให้ตั้งค่า URL ตามวิธีที่ใช้:

| วิธีการรัน | MCP URL |
|-----------|---------|
| Codespaces | `https://<codespace-name>-3000.app.github.dev/mcp` |
| Docker Compose (ในเครื่อง) | `http://localhost:3000/mcp` |

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "fuel-radar": {
      "url": "https://<codespace-name>-3000.app.github.dev/mcp"
    }
  }
}
```

**Cursor** (Settings → MCP Servers → Add):
```
URL: https://<codespace-name>-3000.app.github.dev/mcp
```

**Claude Code** (CLI):
```bash
claude mcp add fuel-radar https://<codespace-name>-3000.app.github.dev/mcp
```

> แทนที่ `<codespace-name>` ด้วยชื่อ Codespace ของคุณ หรือใช้ `http://localhost:3000/mcp` หากรันในเครื่อง
>
> หลังจากเพิ่มแล้ว AI จะสามารถเรียกใช้ `search_fuel_status()` และ `get_fuel_summary()` ได้ทันที

### วิธีที่ 3: Stdio (สำหรับ Claude Desktop / AI Client)

```bash
# ติดตั้ง dependencies
pip install pandas pyarrow requests fastapi uvicorn sse-starlette mcp[cli]

# รัน ETL เพื่อดึงข้อมูลล่าสุด
python pipeline/process_radar.py

# รัน MCP Server แบบ Stdio
python pipeline/mcp_server.py --transport stdio
```

ตัวอย่างการตั้งค่าใน `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "fuel-radar": {
      "command": "python",
      "args": ["/absolute/path/to/pipeline/mcp_server.py", "--transport", "stdio"]
    }
  }
}
```

---

## MCP Tools ที่พร้อมใช้งาน

เมื่อเชื่อมต่อ MCP Server แล้ว AI Agent จะเรียกใช้เครื่องมือเหล่านี้ได้ทันที:

### `search_fuel_status(query)`

ค้นหาสถานะน้ำมันตามชื่อปั๊ม, จังหวัด, หรืออำเภอ

```
query: "กรุงเทพ"

→ Found 5 reports:
  - ปั๊ม ปตท. สาขาลาดพร้าว (กรุงเทพมหานคร): Diesel: out, B95: available
  - ปั๊ม Shell สาขาสุขุมวิท (กรุงเทพมหานคร): Diesel: available, B95: available
  ...
```

### `get_fuel_summary()`

ดูภาพรวมสถานะน้ำมันทั่วประเทศ และจังหวัดที่มีน้ำมันขาดช่วงมากที่สุด

```
→ Summary:
  - Total: 50
  - Diesel Out: 12
    - เชียงใหม่: 4 reports
    - กรุงเทพมหานคร: 3 reports
    - ขอนแก่น: 2 reports
```

> **อยากเพิ่ม MCP Tool?** ดูคู่มือ [How to Add MCP Tools](./research/how_to_add_mcp_tools.md) พร้อม Prompt Templates สำหรับให้ AI ช่วยเขียนโค้ด

---

## Data Pipeline (ETL)

`pipeline/process_radar.py` ทำงานตามขั้นตอน:

1. **Fetch** — ดึงข้อมูลจาก `thaipumpradar.com/api/reports/feed`
2. **Validate** — กรองเฉพาะรายงานที่มี Confidence Score >= 0.3 (production ใช้ >= 0.7)
3. **Clean** — เลือกเฉพาะฟิลด์ที่จำเป็น 11 ฟิลด์ (stationName, brandId, province, diesel, ฯลฯ)
4. **Save** — บันทึกเป็น 2 รูปแบบ:
   - **JSONL** — เหมาะสำหรับ AI/RAG (อ่านทีละบรรทัด, ใช้กับ LangChain, LlamaIndex)
   - **Parquet** — เหมาะสำหรับ Analytics (columnar, ใช้กับ Pandas, DuckDB, Spark)

รายละเอียดชุดข้อมูล: [pipeline/datacard.md](./pipeline/datacard.md)

---

## เอกสารวิจัยและกรอบการทำงาน (Research & Governance)

| เอกสาร | เนื้อหา |
|--------|---------|
| [open_data_model.md](./research/open_data_model.md) | อธิบายโมเดล 5+1 Star Open Data ตั้งแต่ Level 1-6 |
| [thaipumpradar_analysis_th.md](./research/thaipumpradar_analysis_th.md) | วิเคราะห์โครงสร้างข้อมูลจาก API และแผนทำ AI-Ready |
| [ai_ready_audit.md](./research/ai_ready_audit.md) | Checklist ตรวจสอบว่าข้อมูลผ่านเกณฑ์ AI-Ready หรือไม่ |
| [ai_governance_framework.md](./research/ai_governance_framework.md) | กรอบธรรมาภิบาล AI & Data ตามมาตรฐาน PDPA และ DGS |
| [how_to_add_mcp_tools.md](./research/how_to_add_mcp_tools.md) | คู่มือเพิ่ม MCP Tools + Prompt Templates สำหรับใช้ AI ช่วยเขียนโค้ด |

---

## สิ่งที่ทีมงานจะได้รับ

- **เข้าใจมาตรฐาน AI-Ready:** เห็นภาพว่า Level 6 มีองค์ประกอบอะไรบ้าง
- **ต้นแบบ Pipeline:** โค้ด ETL + MCP Server ที่นำไปปรับใช้กับแหล่งข้อมูลอื่นได้ทันที
- **เพิ่มมูลค่าข้อมูล:** เปลี่ยน "ข้อมูลดิบ" ให้เป็น "ฐานความรู้" (Knowledge Base) สำหรับ AI Agent
- **กรอบ Governance:** มีแนวทางดูแลข้อมูลและ AI ตามมาตรฐานสากล

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| Data Processing | Pandas, PyArrow |
| MCP Server | FastMCP (mcp[cli]) |
| Web Framework | FastAPI, Uvicorn |
| Streaming | SSE (Server-Sent Events) |
| Container | Docker, Docker Compose |
| Data Formats | Parquet, JSONL |

---

*จัดทำขึ้นโดย Antigravity เพื่อสาธิตการเปลี่ยนผ่านข้อมูลสาธารณะสู่ยุค AI อย่างเป็นรูปธรรม*
