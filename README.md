# 🚀 จากข้อมูลสาธารณะ (Open Data) สู่ความพร้อมทาง AI (AI-Ready)

[![Status](https://img.shields.io/badge/Status-AI--Ready-success)](https://thaipumpradar.com/)
[![MCP](https://img.shields.io/badge/Protocol-MCP-blue)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-cyan)](https://www.docker.com/)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/monthop-gmail/poc-radar-to-ai-ready)

โปรเจกต์นี้เป็นตัวอย่างการยกระดับการเปิดเผยข้อมูลสาธารณะตามโมเดล **5+1 Star Open Data** โดยเปลี่ยนข้อมูลจากเว็บไซต์รายงานสถานะน้ำมันให้พร้อมสำหรับการใช้งานกับ AI/ML และ RAG (Retrieval-Augmented Generation)

---

## 📂 โครงสร้างโครงการ (Project Structure)

```text
.
├── .devcontainer/         # GitHub Codespaces config
│   └── devcontainer.json
├── research/              # ผลการวิจัยและโมเดลข้อมูล
│   ├── open_data_model.md
│   ├── thaipumpradar_analysis_th.md
│   ├── ai_ready_audit.md       # เกณฑ์การตรวจสอบความพร้อม (Audit)
│   └── ai_governance_framework.md # กรอบธรรมาภิบาล (Governance) 🆕
├── pipeline/              # ส่วนจัดการข้อมูลและเซิร์ฟเวอร์
│   ├── process_radar.py   # ดึงและคลีนข้อมูล (ETL)
│   ├── datacard.md        # คำอธิบายชุดข้อมูล (Metadata)
│   ├── mcp_server.py      # Stdio MCP Server (Legacy/Windows)
│   └── mcp_server_modern.py # Streamable HTTP MCP Server (Modern)
├── demo/                  # ส่วนสาธิตการใช้งาน
│   ├── demonstrate_ai.py  # โค้ดทดสอบ AI Analysis/RAG
│   └── demonstration_results.md
├── data/                  # ข้อมูลที่ผ่านการประมวลผลแล้ว
│   ├── radar_clean.parquet # สำหรับ Analytics
│   └── radar_clean.jsonl   # สำหรับ AI/RAG
├── Dockerfile             # สำหรับรันแบบ Container
└── docker-compose.yml     # สำหรับการปรับใช้งานในทีม
```

---

## 🔍 กรณีศึกษา: Thai Pump Radar

เราได้วิเคราะห์ข้อมูลรายงานน้ำมันจากชุมชนของ [thaipumpradar.com](https://thaipumpradar.com/) เพื่อนำมาสาธิตกระบวนการยกระดับข้อมูล

### 1. การวิจัยและวิเคราะห์ (Research)
- ศึกษาโมเดล [5+1 Star Open Data](./research/open_data_model.md)
- วิเคราะห์โครงสร้างข้อมูล [Thai Pump Radar](./research/thaipumpradar_analysis_th.md)
- ตรวจสอบความพร้อมด้วย [AI-Ready Audit Checklist](./research/ai_ready_audit.md)
- ศึกษากรอบ [AI & Data Governance Framework](./research/ai_governance_framework.md) 🆕

### 2. กระบวนการเตรียมข้อมูล (AI-Ready Pipeline)
- **ETL:** [pipeline/process_radar.py](./pipeline/process_radar.py) ทำการคลีนข้อมูลและตรวจสอบ Confidence Score
- **Metadata:** กำกับดูแลข้อมูลด้วย [pipeline/datacard.md](./pipeline/datacard.md)
- **Formats:** แปลงข้อมูลเป็น Parquet/JSONL เพื่อประสิทธิภาพสูงสุด

### 3. การแสดงผลด้วย AI (Mock RAG)
- 👉 [สรุปผลการรัน AI Demo (demo/demonstration_results.md)](./demo/demonstration_results.md)

---

## 🛠️ วิธีการติดตั้งและใช้งาน (Getting Started)

### GitHub Codespaces (แนะนำ - เริ่มใช้งานได้ทันที)
1. กดปุ่ม **"Open in GitHub Codespaces"** ด้านบน หรือไปที่ [codespaces.new/monthop-gmail/poc-radar-to-ai-ready](https://codespaces.new/monthop-gmail/poc-radar-to-ai-ready)
2. รอสักครู่ให้ Codespace สร้างเสร็จ - MCP Server จะเริ่มทำงานอัตโนมัติ
3. เข้าใช้งานได้ที่ `http://localhost:3000/mcp`

### การติดตั้ง Dependency (สำหรับรันในเครื่อง)
```bash
pip install pandas pyarrow requests fastapi uvicorn sse-starlette
```

### การตั้งค่า MCP Server (สำหรับ AI Agents)

#### **รูปแบบที่ 1: Docker Compose (แนะนำ)**
```bash
docker-compose up -d --build
```
💡 **Config URL:** `http://localhost:3000/mcp`

#### **รูปแบบที่ 2: Stdio (สำหรับใช้งานในเครื่อง)**
เพิ่มการตั้งค่าในโปรแกรม (เช่น `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "fuel-radar-stdio": {
      "command": "python",
      "args": ["C:/absolute/path/to/pipeline/mcp_server.py", "--transport", "stdio"]
    }
  }
}
```

---

## 🏗️ เครื่องมือที่มีให้ใน MCP (AI Tools)
เมือเชื่อมต่อแล้ว AI จะสามารถเรียกใช้เครื่องมือเหล่านี้ได้ทันที:
1. `search_fuel_status(query)`: ค้นหาสถานะน้ำมันในพื้นที่ที่ระบุ
2. `get_fuel_summary()`: ดูภาพรวมน้ำมันขาดช่วงทั่วประเทศ

---

## 🎯 สรุปสิ่งที่ทีมงานจะได้รับ
- **เข้าใจมาตรฐานใหม่:** เห็นภาพชัดเจนว่า AI-Ready Data มีองค์ประกอบอย่างไร (Level 6)
- **ลดระยะเวลา:** มีต้นแบบโค้ด (Pipeline) ที่สามารถนำไปปรับใช้กับแหล่งข้อมูลอื่นได้ทันที
- **เพิ่มมูลค่าข้อมูล:** เปลี่ยนจาก "ข้อมูลดิบ" ให้กลายเป็น "ฐานความรู้" (Knowledge Base) สำหรับ AI Agent

---
*จัดทำขึ้นโดย Antigravity เพื่อสาธิตการเปลี่ยนผ่านข้อมูลสาธารณะสู่ยุค AI อย่างเป็นรูปธรรม*
