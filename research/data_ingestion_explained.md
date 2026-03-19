# Data Ingestion คืออะไร? และโปรเจกต์นี้ทำอยู่ตรงไหน?

*เอกสารนี้ช่วยให้เข้าใจว่า "Ingest" คืออะไร แตกต่างจาก ETL อย่างไร และโปรเจกต์นี้ทำอะไรไปแล้วบ้าง*

---

## สารบัญ

1. [Data Ingestion คืออะไร](#1-data-ingestion-คืออะไร)
2. [Ingestion vs ETL vs Pipeline ต่างกันอย่างไร](#2-ingestion-vs-etl-vs-pipeline-ต่างกันอย่างไร)
3. [รูปแบบของ Data Ingestion](#3-รูปแบบของ-data-ingestion)
4. [โปรเจกต์นี้อยู่ตรงไหน](#4-โปรเจกต์นี้อยู่ตรงไหน)
5. [ศัพท์ที่มักสับสน](#5-ศัพท์ที่มักสับสน)
6. [สรุป](#6-สรุป)

---

## 1. Data Ingestion คืออะไร

**Data Ingestion = การนำข้อมูลเข้าสู่ระบบ**

เปรียบเหมือน **"การดูดน้ำเข้าโรงกรองน้ำ"** — เป็นขั้นตอนแรกสุดก่อนจะทำอะไรกับข้อมูลได้

```text
┌──────────────┐        Ingestion         ┌──────────────────┐
│  แหล่งข้อมูล   │ ─────────────────────▶  │  ระบบของเรา       │
│  (ภายนอก)     │   ดูดข้อมูลเข้ามา         │  (ภายใน)          │
└──────────────┘                          └──────────────────┘
   API, ไฟล์,                                Database, Storage,
   เว็บไซต์, IoT                              Data Lake
```

### ตัวอย่างในชีวิตจริง

| แหล่งข้อมูล | Ingestion | ปลายทาง |
|------------|-----------|---------|
| API ราคาน้ำมัน | ดึงข้อมูลผ่าน HTTP request | บันทึกเป็น JSON/JSONL |
| ไฟล์ CSV จากอีเมล | อ่านไฟล์แล้วโหลดเข้าระบบ | บันทึกใน Database |
| Sensor อุณหภูมิ (IoT) | รับข้อมูลแบบ streaming | บันทึกใน Time-series DB |
| เว็บไซต์ | Scrape/Crawl | บันทึกเป็น HTML/JSON |

---

## 2. Ingestion vs ETL vs Pipeline ต่างกันอย่างไร

คำเหล่านี้มักใช้ปนกัน แต่จริง ๆ แล้วหมายถึงคนละส่วน:

```text
┌─────────────────────────── Data Pipeline (ทั้งกระบวนการ) ──────────────────────────┐
│                                                                                     │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐      ┌───────────┐            │
│  │  Ingestion │─────▶│ Transform  │─────▶│   Load    │─────▶│  Serve    │            │
│  │  ดูดข้อมูล   │      │  แปลง/ทำสะอาด│      │  บันทึก    │      │  ให้บริการ  │            │
│  └───────────┘      └───────────┘      └───────────┘      └───────────┘            │
│       ▲                   ▲                  ▲                  ▲                   │
│       │                   │                  │                  │                   │
│  Ingestion            Transform            Load              Serving               │
│  (ส่วนหนึ่ง)          (ส่วนหนึ่ง)          (ส่วนหนึ่ง)         (ส่วนหนึ่ง)            │
│                                                                                     │
│  ◀────────────── ETL (Extract-Transform-Load) ──────────────▶                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### เปรียบเทียบ

| คำศัพท์ | ความหมาย | ขอบเขต |
|--------|---------|--------|
| **Ingestion** | ดูดข้อมูลเข้าระบบ | แค่ขั้นตอนแรก (รับเข้า) |
| **ETL** | Extract → Transform → Load | 3 ขั้นตอน (ดึง → แปลง → บันทึก) |
| **Pipeline** | กระบวนการทั้งหมดตั้งแต่ต้นจนจบ | ครอบคลุมทุกขั้นตอน รวมถึง Serving |

### ความสัมพันธ์

```text
Ingestion ⊂ ETL ⊂ Pipeline

Ingestion เป็นส่วนหนึ่งของ ETL
ETL เป็นส่วนหนึ่งของ Pipeline
```

---

## 3. รูปแบบของ Data Ingestion

### 3.1 Batch Ingestion (ดูดทีละก้อน)

ดึงข้อมูลเป็นชุดตามรอบเวลา เช่น ทุก 1 ชั่วโมง, ทุกวัน

```text
ทุก 1 ชั่วโมง:  API ──── 100 records ────▶ ระบบ
ทุก 1 ชั่วโมง:  API ──── 100 records ────▶ ระบบ
```

**เหมาะกับ:** ข้อมูลที่ไม่ต้องเร็วมาก, รายงานสรุป, Analytics
**ตัวอย่าง:** โปรเจกต์นี้ — ดึงข้อมูลจาก thaipumpradar.com ทีละ 100 records

### 3.2 Streaming Ingestion (ดูดแบบต่อเนื่อง)

รับข้อมูลแบบ Real-time ทุกวินาที

```text
ทุกวินาที:  API ── 1 record ──▶ ระบบ
ทุกวินาที:  API ── 1 record ──▶ ระบบ
ทุกวินาที:  API ── 1 record ──▶ ระบบ
```

**เหมาะกับ:** ข้อมูลที่ต้องเร็ว เช่น ราคาหุ้น, IoT sensor, แจ้งเตือนภัย
**เครื่องมือ:** Kafka, Apache Flink, AWS Kinesis

### 3.3 Event-driven Ingestion (ดูดเมื่อมีเหตุการณ์)

ดึงข้อมูลเมื่อเกิดเหตุการณ์บางอย่าง

```text
มีรายงานใหม่  ──trigger──▶ ดึงข้อมูล ──▶ ระบบ
มีรายงานใหม่  ──trigger──▶ ดึงข้อมูล ──▶ ระบบ
```

**เหมาะกับ:** Webhook, การแจ้งเตือน, ข้อมูลที่ไม่แน่นอนว่ามาเมื่อไหร่
**เครื่องมือ:** Webhook, Message Queue (RabbitMQ, SQS)

### เปรียบเทียบ 3 แบบ

| | Batch | Streaming | Event-driven |
|---|---|---|---|
| **ความถี่** | ตามรอบ (ชม./วัน) | ตลอดเวลา | เมื่อเกิดเหตุการณ์ |
| **ความเร็ว** | นาที - ชั่วโมง | วินาที - มิลลิวินาที | วินาที |
| **ความซับซ้อน** | ง่าย | ซับซ้อน | ปานกลาง |
| **ค่าใช้จ่าย** | ต่ำ | สูง | ปานกลาง |
| **โปรเจกต์นี้** | ✅ ใช้แบบนี้ | ❌ | ❌ |

---

## 4. โปรเจกต์นี้อยู่ตรงไหน

### Data Pipeline ทั้งหมดของโปรเจกต์นี้

```text
┌──────────────────────────── Data Pipeline ─────────────────────────────┐
│                                                                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌────────┐ │
│  │  Ingestion   │───▶│  Transform   │───▶│    Load     │───▶│ Serve  │ │
│  │              │    │              │    │             │    │        │ │
│  │  fetch_radar │    │  process_data│    │ save_ai_ready│   │  MCP   │ │
│  │  _data()     │    │  ()          │    │ ()          │    │ Server │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └────────┘ │
│                                                                        │
│  ไฟล์: pipeline/process_radar.py                    pipeline/mcp_server │
│                                                     _modern.py         │
└────────────────────────────────────────────────────────────────────────┘
```

### แต่ละขั้นตอนทำอะไร

#### Ingestion: `fetch_radar_data()`

```python
# pipeline/process_radar.py (บรรทัด 6-15)
def fetch_radar_data(limit=100):
    url = f"https://thaipumpradar.com/api/reports/feed?limit={limit}"
    response = requests.get(url, timeout=10)
    return response.json()
```

- **ทำอะไร:** ดึงข้อมูลจาก API ของ thaipumpradar.com
- **รูปแบบ:** Batch Ingestion (ดึงทีละ 100 records)
- **ผลลัพธ์:** ข้อมูลดิบ (raw data) ในรูปแบบ JSON
- **บันทึกเป็น:** `data/raw.json`

#### Transform: `process_data()`

```python
# pipeline/process_radar.py (บรรทัด 17-44)
def process_data(data):
    df = pd.DataFrame(reports)
    df = df[df['confidence'] >= 0.3].copy()   # กรอง
    df = df[[...]]                             # เลือก fields
    return df
```

- **ทำอะไร:** ทำความสะอาด + กรองข้อมูล
- **กรอง:** เฉพาะ Confidence Score >= 0.3
- **เลือก:** 11 fields ที่จำเป็น

#### Load: `save_ai_ready()`

```python
# pipeline/process_radar.py (บรรทัด 46-55)
def save_ai_ready(df, base_path):
    df.to_json(..., orient='records', lines=True)   # JSONL
    df.to_parquet(...)                                # Parquet
```

- **ทำอะไร:** บันทึกข้อมูลที่สะอาดแล้ว
- **รูปแบบ:** JSONL (สำหรับ AI/RAG) + Parquet (สำหรับ Analytics)

#### Serve: MCP Server

```python
# pipeline/mcp_server_modern.py
@mcp.tool()
def search_fuel_status(query: str) -> str:
    ...
```

- **ทำอะไร:** ให้ AI Agent เข้าถึงข้อมูลผ่าน MCP Protocol

### สรุปตำแหน่งของ Ingestion

| ขั้นตอน | ฟังก์ชัน | ไฟล์ | บรรทัด |
|---------|---------|------|--------|
| **Ingestion** | `fetch_radar_data()` | `pipeline/process_radar.py` | 6-15 |
| Transform | `process_data()` | `pipeline/process_radar.py` | 17-44 |
| Load | `save_ai_ready()` | `pipeline/process_radar.py` | 46-55 |
| Serve | MCP Tools | `pipeline/mcp_server_modern.py` | 22-57 |

---

## 5. ศัพท์ที่มักสับสน

| คำศัพท์ | ความหมาย | เปรียบเทียบ |
|--------|---------|------------|
| **Ingestion** | ดูดข้อมูลเข้าระบบ | เหมือนดูดน้ำเข้าโรงกรอง |
| **Extraction** | ดึงข้อมูลออกจากแหล่ง | เหมือนตักน้ำจากแม่น้ำ (ใกล้เคียง Ingestion แต่เน้น "ดึงออก") |
| **ETL** | Extract → Transform → Load | กระบวนการ 3 ขั้นตอน |
| **ELT** | Extract → Load → Transform | โหลดก่อน แปลงทีหลัง (ใช้กับ Data Warehouse) |
| **Pipeline** | ทั้งกระบวนการ | สายท่อทั้งเส้นตั้งแต่ต้นจนจบ |
| **Crawling** | ดึงข้อมูลจากเว็บ (หลายหน้า) | Ingestion ประเภทหนึ่ง |
| **Scraping** | ดึงข้อมูลจากหน้าเว็บเฉพาะ | Ingestion ประเภทหนึ่ง |
| **Streaming** | รับข้อมูลแบบต่อเนื่อง | Ingestion ที่ไม่หยุดพัก |

### Ingestion vs Extraction

สองคำนี้ใกล้เคียงกันมาก:

```text
Extraction:  เน้นมุมมอง "ดึงออก" จากแหล่งข้อมูล   (มองจากฝั่งต้นทาง)
Ingestion:   เน้นมุมมอง "รับเข้า" สู่ระบบของเรา    (มองจากฝั่งปลายทาง)
```

ในทางปฏิบัติ มักใช้แทนกันได้ — โค้ดเดียวกัน แค่มองคนละมุม

---

## 6. สรุป

```text
┌─────────────────────────────────────────────────┐
│              Data Ingestion                      │
│                                                  │
│  คือ: ขั้นตอนแรกของ Data Pipeline               │
│       การดูดข้อมูลจากภายนอกเข้าสู่ระบบของเรา      │
│                                                  │
│  ในโปรเจกต์นี้:                                   │
│  ✅ มี — fetch_radar_data() ใน process_radar.py  │
│  ✅ ดึงจาก thaipumpradar.com API                 │
│  ✅ แบบ Batch (ทีละ 100 records)                 │
│                                                  │
│  เป็นส่วนหนึ่งของ:                                │
│  Ingestion ⊂ ETL ⊂ Pipeline                     │
└─────────────────────────────────────────────────┘
```

> **Key Takeaway:**
> - **Ingestion** = ดูดข้อมูลเข้า (ขั้นแรก)
> - **ETL** = ดูด + แปลง + บันทึก (3 ขั้น)
> - **Pipeline** = ทุกอย่างรวมกัน (ดูด + แปลง + บันทึก + ให้บริการ)
> - โปรเจกต์นี้ครบทั้ง Pipeline: Ingestion → Transform → Load → Serve (MCP)
