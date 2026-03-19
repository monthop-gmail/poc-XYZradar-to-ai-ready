# คู่มือการเพิ่ม MCP Tools สำหรับนักพัฒนา

*เอกสารนี้อธิบายกระบวนการ และวิธี prompt AI เพื่อเพิ่ม MCP Tools ต่อยอดจากโปรเจกต์นี้*

---

## สารบัญ

1. [MCP Tool คืออะไร](#1-mcp-tool-คืออะไร)
2. [กระบวนการเพิ่ม MCP Tool (Step-by-Step)](#2-กระบวนการเพิ่ม-mcp-tool-step-by-step)
3. [Anatomy ของ MCP Tool ที่ดี](#3-anatomy-ของ-mcp-tool-ที่ดี)
4. [ตัวอย่าง: เพิ่ม Tool ใหม่ทีละขั้น](#4-ตัวอย่าง-เพิ่ม-tool-ใหม่ทีละขั้น)
5. [วิธี Prompt AI เพื่อเพิ่ม MCP Tool](#5-วิธี-prompt-ai-เพื่อเพิ่ม-mcp-tool)
6. [Prompt Templates สำเร็จรูป](#6-prompt-templates-สำเร็จรูป)
7. [Checklist ก่อน Deploy](#7-checklist-ก่อน-deploy)
8. [แนวทางต่อยอดจากโปรเจกต์นี้](#8-แนวทางต่อยอดจากโปรเจกต์นี้)

---

## 1. MCP Tool คืออะไร

**MCP Tool** คือฟังก์ชันที่ AI Agent สามารถเรียกใช้ได้ผ่าน [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) เปรียบเหมือน "ทักษะ" ที่เราสอนให้ AI ทำงานเฉพาะทางได้

```text
ผู้ใช้ถาม  →  AI คิด  →  เรียก MCP Tool  →  ได้ข้อมูล  →  AI ตอบ
"ดีเซลหมดที่ไหนบ้าง?"     search_fuel_status("ดีเซล")      AI สรุปให้
```

### Tool ที่มีอยู่ในโปรเจกต์นี้

| Tool | หน้าที่ | ไฟล์ |
|------|---------|------|
| `search_fuel_status(query)` | ค้นหาสถานะน้ำมันตามชื่อ/จังหวัด | `pipeline/mcp_server_modern.py` |
| `get_fuel_summary()` | ดูภาพรวมน้ำมันทั่วประเทศ | `pipeline/mcp_server_modern.py` |

---

## 2. กระบวนการเพิ่ม MCP Tool (Step-by-Step)

กระบวนการนี้เรียกว่า **"Tool Development Workflow"** มี 5 ขั้นตอน:

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  1.ออกแบบ │───▶│ 2.เขียนโค้ด│───▶│  3.ทดสอบ  │───▶│ 4.เอกสาร  │───▶│ 5.Deploy │
│  (Design) │    │  (Code)  │    │  (Test)  │    │  (Docs)  │    │  (Ship)  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### ขั้นที่ 1: ออกแบบ Tool (Design)

ตอบคำถามเหล่านี้ก่อนเขียนโค้ด:

- **AI จะใช้ Tool นี้เมื่อไหร่?** — ผู้ใช้จะถามคำถามแบบไหน
- **ต้องการ input อะไร?** — parameters ที่จำเป็น
- **จะ return อะไร?** — ข้อมูลที่ AI จะนำไปตอบผู้ใช้
- **ข้อมูลมาจากไหน?** — ไฟล์ JSONL, API, database

> **สำคัญ:** ชื่อ Tool และ description ต้องชัดเจน เพราะ AI ใช้สิ่งนี้ตัดสินใจว่าจะเรียก Tool ไหน

### ขั้นที่ 2: เขียนโค้ด (Code)

เพิ่มฟังก์ชันใน `pipeline/mcp_server_modern.py`:

```python
@mcp.tool()
def ชื่อ_tool(parameter: str) -> str:
    """อธิบายให้ AI เข้าใจว่า Tool นี้ทำอะไร เมื่อไหร่ควรใช้"""
    # 1. ดึงข้อมูล
    data = get_data()

    # 2. ประมวลผล
    result = ...

    # 3. Return เป็น string ที่ AI อ่านแล้วเข้าใจ
    return result
```

### ขั้นที่ 3: ทดสอบ (Test)

```bash
# รัน server ใหม่
docker-compose up -d --build

# ทดสอบผ่าน AI client หรือ curl
# ถาม AI คำถามที่ควรจะ trigger tool ใหม่
```

### ขั้นที่ 4: อัปเดตเอกสาร (Docs)

- เพิ่ม Tool ใหม่ใน `README.md` ส่วน "MCP Tools ที่พร้อมใช้งาน"
- อัปเดต `pipeline/datacard.md` ถ้าใช้ข้อมูลใหม่

### ขั้นที่ 5: Deploy

```bash
docker-compose up -d --build
git add . && git commit -m "Add new MCP tool: ชื่อ tool"
git push
```

---

## 3. Anatomy ของ MCP Tool ที่ดี

```python
@mcp.tool()
def get_brand_statistics(brand: str) -> str:          # ← ชื่อชัดเจน, มี type hints
    """Get fuel availability statistics for a specific brand (e.g. PTT, Shell, Bangchak).
    Use this when users ask about a specific gas station brand."""  # ← description ดี

    data = get_data()                                  # ← ดึงข้อมูล

    matches = [r for r in data                         # ← ประมวลผล
               if r.get('brandId', '').lower() == brand.lower()]

    if not matches:                                    # ← จัดการกรณีไม่พบข้อมูล
        return f"No data found for brand: {brand}"

    total = len(matches)                               # ← คำนวณสถิติ
    diesel_out = sum(1 for r in matches if r.get('diesel') == 'out')

    return (f"Brand: {brand}\n"                        # ← Return อ่านง่าย
            f"Total stations: {total}\n"
            f"Diesel out: {diesel_out}/{total}")
```

### หลักการตั้งชื่อและเขียน Description

| องค์ประกอบ | แนวทาง | ตัวอย่าง |
|-----------|--------|---------|
| **ชื่อ Tool** | ใช้ verb_noun, snake_case | `search_fuel_status`, `get_brand_statistics` |
| **Description** | บอก AI ว่า "ทำอะไร" และ "เมื่อไหร่ควรใช้" | `"Get fuel stats for a brand. Use when users ask about PTT, Shell, etc."` |
| **Parameter** | ระบุ type + ชื่อที่สื่อความหมาย | `brand: str`, `province: str`, `limit: int` |
| **Return** | เป็น string ที่ AI อ่านแล้วสรุปให้ผู้ใช้ได้ | ข้อมูลที่จัดรูปแบบอ่านง่าย |

---

## 4. ตัวอย่าง: เพิ่ม Tool ใหม่ทีละขั้น

สมมติต้องการเพิ่ม Tool **"ดูสถิติแยกตามแบรนด์"**

### 4.1 ออกแบบ

```text
ชื่อ:        get_brand_statistics
คำถามผู้ใช้:  "ปั๊ม ปตท. มีน้ำมันหมดกี่สาขา?"
Input:       brand (str) — ชื่อแบรนด์ เช่น PTT, Shell
Output:      จำนวนสาขาทั้งหมด, จำนวนที่น้ำมันหมด, จังหวัดที่หมดมากสุด
ข้อมูล:      radar_clean.jsonl (field: brandId)
```

### 4.2 เขียนโค้ด

เปิดไฟล์ `pipeline/mcp_server_modern.py` แล้วเพิ่ม:

```python
@mcp.tool()
def get_brand_statistics(brand: str) -> str:
    """Get fuel availability statistics for a specific gas station brand.
    Use this when users ask about PTT, Shell, Bangchak, Caltex, or other brands."""
    data = get_data()

    matches = [r for r in data
               if brand.lower() in (r.get('brandId') or '').lower()]

    if not matches:
        return f"No data found for brand: {brand}. Available brands: PTT, SHELL, BANGCHAK, etc."

    total = len(matches)
    diesel_out = sum(1 for r in matches if r.get('diesel') == 'out')

    # หาจังหวัดที่หมดมากสุด
    prov_count = {}
    for r in matches:
        if r.get('diesel') == 'out':
            p = r.get('province', 'Unknown')
            prov_count[p] = prov_count.get(p, 0) + 1

    output = f"Brand: {brand.upper()}\n"
    output += f"Total stations reported: {total}\n"
    output += f"Diesel out: {diesel_out}/{total}\n"

    if prov_count:
        output += "Provinces with diesel out:\n"
        for p, c in sorted(prov_count.items(), key=lambda x: x[1], reverse=True)[:3]:
            output += f"  - {p}: {c} stations\n"

    return output
```

### 4.3 ทดสอบ

```bash
docker-compose up -d --build
# แล้วถาม AI: "ปั๊ม PTT มีน้ำมันหมดกี่สาขา?"
# AI ควรเรียก get_brand_statistics("PTT") อัตโนมัติ
```

---

## 5. วิธี Prompt AI เพื่อเพิ่ม MCP Tool

การใช้ AI (Claude, Cursor, etc.) ช่วยเขียน MCP Tool มีกระบวนการเรียกว่า **"AI-Assisted Tool Development"** โดยใช้ prompt ที่มีโครงสร้างชัดเจน

### หลักการ Prompt ที่ดี

```text
1. บอก Context     → โปรเจกต์คืออะไร, โค้ดอยู่ที่ไหน
2. บอก Goal        → อยากได้ Tool อะไร, ทำอะไร
3. บอก Constraints → ข้อจำกัด, รูปแบบที่ต้องการ
4. ให้ Example      → ตัวอย่าง Tool ที่มีอยู่แล้ว
```

### ตัวอย่าง Prompt แบบเต็ม

```
ช่วยเพิ่ม MCP Tool ใหม่ในไฟล์ pipeline/mcp_server_modern.py

โปรเจกต์นี้เป็น MCP Server ที่ให้บริการข้อมูลสถานะน้ำมันจาก thaipumpradar.com
ข้อมูลอยู่ในไฟล์ data/radar_clean.jsonl มี fields: stationName, brandId,
province, district, diesel, benzine91, benzine95, e20, lpg, confidence, createdAt

ต้องการ Tool ใหม่ชื่อ "get_brand_statistics" ที่:
- รับ parameter: brand (str) — ชื่อแบรนด์ เช่น PTT, Shell
- Return: จำนวนสาขาทั้งหมด, จำนวนที่ดีเซลหมด, top 3 จังหวัดที่หมดมากสุด
- ใช้ pattern เดียวกับ Tool ที่มีอยู่แล้ว (ใช้ get_data() และ @mcp.tool())

ตัวอย่าง Tool ที่มีอยู่:
[แปะโค้ด search_fuel_status ที่มีอยู่]
```

---

## 6. Prompt Templates สำเร็จรูป

### Template 1: เพิ่ม Tool ใหม่จากข้อมูลที่มีอยู่

```
ช่วยเพิ่ม MCP Tool ใน pipeline/mcp_server_modern.py

ข้อมูล: data/radar_clean.jsonl
Fields ที่มี: [ระบุ fields]

ต้องการ Tool ที่: [อธิบายว่าทำอะไร]
ผู้ใช้จะถามแบบนี้: [ตัวอย่างคำถาม]
ใช้ pattern เดียวกับ Tool search_fuel_status ที่มีอยู่แล้ว
อัปเดต README.md ส่วน MCP Tools ด้วย
```

### Template 2: เพิ่ม Tool ที่ดึงข้อมูลจาก API ภายนอก

```
ช่วยเพิ่ม MCP Tool ใน pipeline/mcp_server_modern.py ที่ดึงข้อมูลจาก API

API Endpoint: [URL]
Response format: [ตัวอย่าง JSON]

ต้องการ Tool ที่: [อธิบาย]
ต้องจัดการ error กรณี API ล่มด้วย
อัปเดต README.md และ requirements.txt ถ้าต้องใช้ library เพิ่ม
```

### Template 3: Refactor Tool ที่มีอยู่

```
ช่วยปรับปรุง Tool [ชื่อ Tool] ใน pipeline/mcp_server_modern.py

ปัญหาปัจจุบัน: [อธิบายปัญหา]
อยากให้: [อธิบายสิ่งที่ต้องการ]
ห้ามเปลี่ยนชื่อ Tool หรือ parameters (เพราะ AI client ที่ใช้อยู่จะพัง)
```

### Template 4: สร้าง MCP Server ใหม่จากข้อมูลอื่น

```
ช่วยสร้าง MCP Server ใหม่สำหรับข้อมูล [ชื่อข้อมูล]

ใช้โปรเจกต์ poc-XYZradar-to-ai-ready เป็นต้นแบบ โดย:
1. สร้าง process_[ชื่อ].py สำหรับ ETL (ดึงจาก [แหล่งข้อมูล])
2. สร้าง mcp_server_[ชื่อ].py ที่มี Tools: [ระบุ Tools ที่ต้องการ]
3. อัปเดต Dockerfile และ docker-compose.yml
4. สร้าง datacard.md สำหรับชุดข้อมูลใหม่

ข้อมูลต้นทาง: [อธิบายโครงสร้างข้อมูล]
```

---

## 7. Checklist ก่อน Deploy

- [ ] **ชื่อ Tool** สื่อความหมายชัดเจน (verb_noun)
- [ ] **Description** บอก AI ได้ว่า "ทำอะไร" และ "เมื่อไหร่ควรใช้"
- [ ] **Parameters** มี type hints ครบ
- [ ] **Error handling** จัดการกรณีไม่พบข้อมูล ไม่ให้ crash
- [ ] **Return format** เป็น string ที่ AI อ่านแล้วสรุปได้
- [ ] **ทดสอบ** ถาม AI ด้วยคำถามจริง ดูว่าเรียก Tool ถูกตัว
- [ ] **README.md** อัปเดตส่วน MCP Tools แล้ว
- [ ] **docker-compose up --build** ผ่าน ไม่มี error

---

## 8. แนวทางต่อยอดจากโปรเจกต์นี้

### ไอเดีย Tool ที่น่าเพิ่ม (จากข้อมูลที่มีอยู่)

| Tool | หน้าที่ | Prompt ตัวอย่าง |
|------|---------|----------------|
| `get_brand_statistics(brand)` | สถิติแยกตามแบรนด์ | "ปั๊ม PTT มีน้ำมันหมดกี่สาขา?" |
| `get_province_detail(province)` | รายละเอียดรายจังหวัด | "เชียงใหม่มีปั๊มไหนบ้างที่ยังมีน้ำมัน?" |
| `compare_fuel_types()` | เปรียบเทียบสถานะน้ำมันแต่ละประเภท | "ดีเซลกับเบนซิน 95 อันไหนหมดเยอะกว่า?" |
| `get_latest_reports(limit)` | รายงานล่าสุด | "มีรายงานใหม่อะไรบ้าง?" |
| `get_high_confidence_stations(province)` | สถานีที่ข้อมูลน่าเชื่อถือ | "ปั๊มไหนในขอนแก่นที่ข้อมูลน่าเชื่อถือที่สุด?" |

### ต่อยอดกับข้อมูลอื่น

สามารถนำ pattern เดียวกันไปใช้กับข้อมูลสาธารณะอื่น ๆ เช่น:

- **ข้อมูลคุณภาพอากาศ** — Air4Thai API
- **ข้อมูลน้ำท่วม** — กรมชลประทาน
- **ข้อมูลแผ่นดินไหว** — กรมอุตุนิยมวิทยา
- **ข้อมูลราคาสินค้าเกษตร** — สำนักงานเศรษฐกิจการเกษตร

กระบวนการเหมือนกัน:
1. หา API / ดาวน์โหลดข้อมูล
2. สร้าง ETL Pipeline (`process_xxx.py`)
3. บันทึกเป็น JSONL + Parquet
4. สร้าง MCP Tools
5. เขียน Data Card
6. Deploy ด้วย Docker

---

> **หมายเหตุ:** เอกสารนี้ออกแบบให้นักพัฒนาที่เริ่มต้นใหม่สามารถเพิ่ม MCP Tool ได้ด้วยตัวเอง หรือใช้ AI ช่วยเขียนโค้ดโดย prompt ตาม Template ที่ให้ไว้
