# Common Mistakes: MCP Tools & AI-Ready Data Pipelines

> คู่มือรวมข้อผิดพลาดที่ junior developers มักทำเมื่อสร้าง MCP Server และ AI-Ready data pipeline
> ใช้ตัวอย่างจากโปรเจค Fuel Radar MCP Server (ข้อมูลสถานีน้ำมันในไทย)

---

## 1. MCP Tool Description ที่ไม่ดี

Tool description คือสิ่งที่ AI (เช่น Claude, GPT) ใช้ตัดสินใจว่าจะเรียก tool ไหน ถ้า description ไม่ดี AI จะเรียก tool ผิด หรือไม่เรียกเลย

---

### ❌ ข้อผิดพลาด 1.1: Description กว้างเกินไป — AI ไม่รู้จะเรียกเมื่อไหร่

**ปัญหา:** ถ้า description บอกแค่กว้างๆ เช่น "Get data" หรือ "Process information" AI จะไม่รู้ว่า tool นี้ทำอะไรได้ เมื่อไหร่ควรเรียก ส่งค่าอะไรเข้าไป

**ตัวอย่าง:**
```python
# ❌ แย่ — AI ไม่รู้ว่า "data" คืออะไร, search ยังไง
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search data."""
```

**✅ แก้ไข:**
```python
# ✅ ดี — บอกชัดว่า search อะไร, ใช้ field ไหน, return อะไร
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search for fuel availability in Thailand by station name, province, or district.
    Returns up to 5 matching reports with diesel and benzine95 status.
    Use this when the user asks about fuel at a specific location."""
```

**ทำไม:** AI ใช้ description เป็น "คู่มือ" ในการเลือก tool ยิ่ง description ละเอียด AI ยิ่งเรียก tool ถูกต้อง ลดการเรียกซ้ำหรือเรียกผิด

---

### ❌ ข้อผิดพลาด 1.2: Description ซ้ำกัน — AI สับสนเลือกไม่ถูก

**ปัญหา:** ถ้ามีหลาย tools ที่ description คล้ายกันมาก AI จะไม่รู้จะเลือกตัวไหน อาจเรียกผิดตัว หรือเรียกทั้งสองตัวโดยไม่จำเป็น

**ตัวอย่าง:**
```python
# ❌ แย่ — ทั้งสอง tool มี description แทบเหมือนกัน
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Get fuel status information."""

@mcp.tool()
def get_fuel_summary() -> str:
    """Get fuel status information."""
```

**✅ แก้ไข:**
```python
# ✅ ดี — แต่ละ tool บอกชัดว่าทำอะไรต่างกัน
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search for fuel availability at a specific station, province, or district.
    Use when the user asks about a PARTICULAR location."""

@mcp.tool()
def get_fuel_summary() -> str:
    """Get overall nationwide summary of fuel shortages and top affected provinces.
    Use when the user asks about the OVERALL situation, not a specific location."""
```

**ทำไม:** AI เลือก tool โดยเปรียบเทียบ description ทุกตัว ถ้าซ้ำกัน AI จะเดา ซึ่งอาจผิด ควร highlight ความแตกต่างให้ชัดเจน เช่น "specific location" vs "overall summary"

---

### ❌ ข้อผิดพลาด 1.3: ไม่บอกว่า "เมื่อไหร่ควรใช้"

**ปัญหา:** Description บอกแค่ว่า tool ทำอะไร แต่ไม่บอกว่าควรเรียกเมื่อไหร่ AI ก็จะเรียกทุกครั้งที่เห็นคำเกี่ยวข้อง แม้ไม่จำเป็น

**ตัวอย่าง:**
```python
# ❌ แย่ — บอกแค่ว่าทำอะไร ไม่บอกว่าเมื่อไหร่ควรใช้
@mcp.tool()
def get_fuel_summary() -> str:
    """Get overall summary of fuel status and provinces with fuel shortages."""
```

**✅ แก้ไข:**
```python
# ✅ ดี — เพิ่ม "Use this when..." เพื่อบอก AI ว่าเรียกเมื่อไหร่
@mcp.tool()
def get_fuel_summary() -> str:
    """Get overall summary of fuel status and provinces with fuel shortages.
    Use this when the user asks about general fuel situation in Thailand,
    nationwide statistics, or which provinces are most affected.
    Do NOT use this for specific station lookups — use search_fuel_status instead."""
```

**ทำไม:** การเพิ่ม "Use this when..." และ "Do NOT use this for..." ช่วยให้ AI ตัดสินใจได้แม่นยำขึ้น ลดการเรียก tool ที่ไม่ตรงกับคำถาม

---

### ❌ ข้อผิดพลาด 1.4: Description เป็นภาษาไทย

**ปัญหา:** AI models (Claude, GPT) เข้าใจ English ดีกว่าภาษาไทยมาก โดยเฉพาะในการ match intent กับ tool description ถ้าเขียน description เป็นภาษาไทย AI อาจเข้าใจผิดหรือ match ไม่ถูก

**ตัวอย่าง:**
```python
# ❌ แย่ — AI อาจ match intent ผิดเมื่อ description เป็นภาษาไทย
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """ค้นหาสถานะน้ำมันจากชื่อปั๊ม จังหวัด หรืออำเภอ"""

@mcp.tool()
def get_fuel_summary() -> str:
    """ดูสรุปภาพรวมสถานะน้ำมันทั้งประเทศ"""
```

**✅ แก้ไข:**
```python
# ✅ ดี — Description เป็น English, ผลลัพธ์จะ return เป็นภาษาอะไรก็ได้
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search for fuel availability in Thailand by station name, province, or district.
    The query can be in Thai (e.g., 'กรุงเทพ') or English."""

@mcp.tool()
def get_fuel_summary() -> str:
    """Get overall summary of fuel status and provinces with fuel shortages."""
```

**ทำไม:** Tool description ถูกใช้ใน system-level decision making ของ AI ซึ่ง training data ส่วนใหญ่เป็น English การเขียน description เป็น English ช่วยให้ AI เข้าใจและเลือก tool ได้ถูกต้องกว่า แต่ข้อมูลที่ return กลับไปจะเป็นภาษาไทยได้ปกติ

---

### ❌ ข้อผิดพลาด 1.5: ชื่อ Tool ไม่สื่อ

**ปัญหา:** ชื่อ tool ที่ไม่สื่อความหมาย (เช่น `tool1`, `process`, `do_thing`) ทำให้ทั้ง AI และ developer คนอื่นไม่เข้าใจ

**ตัวอย่าง:**
```python
# ❌ แย่ — ชื่อไม่บอกอะไรเลย
@mcp.tool()
def tool1(q: str) -> str:
    """Search fuel."""

@mcp.tool()
def process() -> str:
    """Get summary."""

@mcp.tool()
def get_data(x: str) -> str:
    """Get data for x."""
```

**✅ แก้ไข:**
```python
# ✅ ดี — ชื่อบอก action + domain ชัดเจน, parameter ชื่อสื่อ
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search for fuel availability in Thailand by station name, province, or district."""

@mcp.tool()
def get_fuel_summary() -> str:
    """Get overall summary of fuel status and provinces with fuel shortages."""
```

**ทำไม:** AI ใช้ทั้งชื่อ tool และ description ในการตัดสินใจ ชื่อที่ดีควรเป็น `verb_noun` pattern เช่น `search_fuel_status`, `get_fuel_summary` ทำให้ทั้ง AI และ developer เข้าใจได้ทันที

---

## 2. Return Value ที่ไม่ดี

สิ่งที่ MCP tool return กลับไปให้ AI คือข้อมูลที่ AI จะใช้ตอบผู้ใช้ ถ้า return ไม่ดี AI จะตอบผิดหรือตอบไม่ได้

---

### ❌ ข้อผิดพลาด 2.1: Return ข้อมูลมากเกินไป (ส่ง 1000 records กลับ)

**ปัญหา:** ถ้า tool return ข้อมูลทั้งหมดโดยไม่จำกัด จะกินพื้นที่ context window ของ AI ทำให้ช้า แพง และอาจ exceed token limit

**ตัวอย่าง:**
```python
# ❌ แย่ — ส่ง records ทั้งหมดกลับ อาจเป็น 1000+ รายการ
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    matches = [r for r in data if query.lower() in
               f"{r.get('stationName')} {r.get('province')}".lower()]
    # ส่งกลับทั้งหมด!
    return json.dumps(matches, ensure_ascii=False)
```

**✅ แก้ไข:**
```python
# ✅ ดี — จำกัดจำนวน และบอก AI ว่ามีเพิ่มอีก
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search for fuel availability. Returns up to 5 results."""
    data = get_data()
    matches = [r for r in data if query.lower() in
               f"{r.get('stationName')} {r.get('province')}".lower()]

    if not matches:
        return f"No reports found for: {query}"

    output = f"Found {len(matches)} reports (showing top 5):\n"
    for r in matches[:5]:
        output += (f"- {r.get('stationName')} ({r.get('province')}): "
                   f"Diesel: {r.get('diesel')}, B95: {r.get('benzine95')}\n")

    if len(matches) > 5:
        output += f"\n... and {len(matches) - 5} more results. Ask user to narrow the search."
    return output
```

**ทำไม:** AI มี context window จำกัด (เช่น 200K tokens) การส่ง raw data 1000 records กลับไปจะกิน tokens มหาศาล ทำให้แพง ช้า และอาจ error โปรเจคนี้ใช้ `matches[:5]` ถูกต้องแล้ว แต่ต้องไม่ลืมบอกด้วยว่ายังมีผลลัพธ์เพิ่มเติมอีก

---

### ❌ ข้อผิดพลาด 2.2: Return เป็น raw JSON แทน human-readable text

**ปัญหา:** การ return raw JSON ทำให้ AI ต้องแปลง format เอง ซึ่งอาจแปลงผิด หรือเสียแรงในการ parse

**ตัวอย่าง:**
```python
# ❌ แย่ — return raw JSON object ยาวๆ
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    matches = [r for r in data if query.lower() in str(r).lower()]
    return json.dumps(matches[:5], ensure_ascii=False, indent=2)
    # Output: [{"stationName": "PTT สาขา...", "brandId": "ptt", "province": "...",
    #           "district": "...", "diesel": "available", "benzine91": "available",
    #           "benzine95": "out", "e20": null, "lpg": null,
    #           "confidence": 0.85, "createdAt": "2025-01-15T10:30:00Z"}, ...]
```

**✅ แก้ไข:**
```python
# ✅ ดี — return เป็นข้อความที่อ่านง่าย เลือกแค่ field ที่สำคัญ
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    matches = [r for r in data if query.lower() in
               f"{r.get('stationName')} {r.get('province')} {r.get('district')}".lower()]

    if not matches:
        return f"No reports found for: {query}"

    output = f"Found {len(matches)} reports:\n"
    for r in matches[:5]:
        output += (f"- {r.get('stationName')} ({r.get('province')}): "
                   f"Diesel: {r.get('diesel')}, B95: {r.get('benzine95')}\n")
    return output
```

**ทำไม:** MCP tool ควร return ข้อความที่ AI สามารถส่งต่อให้ผู้ใช้ได้เลย โดยไม่ต้อง parse JSON ซ้ำ ซึ่งโปรเจคนี้ทำถูกต้องแล้วใน `mcp_server_modern.py` — เป็นตัวอย่างที่ดี

---

### ❌ ข้อผิดพลาด 2.3: ไม่มีข้อความเมื่อไม่พบข้อมูล

**ปัญหา:** ถ้า tool return string ว่าง `""` หรือ empty list `[]` เมื่อไม่พบข้อมูล AI จะไม่รู้ว่าไม่พบข้อมูล หรือ tool มีปัญหา อาจ hallucinate คำตอบขึ้นมาเอง

**ตัวอย่าง:**
```python
# ❌ แย่ — return ว่างเปล่าเมื่อไม่เจอ
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    matches = [r for r in data if query.lower() in str(r).lower()]
    if not matches:
        return ""  # AI ไม่รู้ว่าไม่เจอ หรือ tool พัง
```

**✅ แก้ไข:**
```python
# ✅ ดี — บอกชัดเจนว่าไม่พบข้อมูล พร้อมแนะนำสิ่งที่ควรทำ
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    matches = [r for r in data if query.lower() in
               f"{r.get('stationName')} {r.get('province')} {r.get('district')}".lower()]
    if not matches:
        return (f"No reports found for: '{query}'. "
                f"Try searching by province name (e.g., 'กรุงเทพ') "
                f"or station name (e.g., 'PTT').")
```

**ทำไม:** AI ต้องรู้สถานะชัดเจน — "ไม่พบข้อมูล" ต่างจาก "tool error" ต่างจาก "ข้อมูลว่าง" ข้อความที่ชัดเจนช่วยให้ AI ตอบผู้ใช้ได้ถูกต้องแทนที่จะ hallucinate โปรเจคนี้ทำถูกแล้วด้วย `return f"No reports found for: {query}"`

---

### ❌ ข้อผิดพลาด 2.4: Return ข้อมูลที่ AI ไม่จำเป็นต้องรู้

**ปัญหา:** การ return internal IDs, raw timestamps, หรือ metadata ที่ผู้ใช้ไม่สนใจ ทำให้ AI สับสน และกิน token โดยไม่จำเป็น

**ตัวอย่าง:**
```python
# ❌ แย่ — ส่ง internal data ที่ไม่จำเป็นทั้งหมดกลับไป
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    matches = [r for r in data if query.lower() in str(r).lower()]
    output = ""
    for r in matches[:5]:
        output += (f"- {r.get('stationName')} | brandId: {r.get('brandId')} | "
                   f"province: {r.get('province')} | district: {r.get('district')} | "
                   f"diesel: {r.get('diesel')} | benzine91: {r.get('benzine91')} | "
                   f"benzine95: {r.get('benzine95')} | e20: {r.get('e20')} | "
                   f"lpg: {r.get('lpg')} | confidence: {r.get('confidence')} | "
                   f"createdAt: {r.get('createdAt')}\n")
    return output
```

**✅ แก้ไข:**
```python
# ✅ ดี — เลือก return แค่สิ่งที่ผู้ใช้ต้องการ
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    matches = [r for r in data if query.lower() in
               f"{r.get('stationName')} {r.get('province')} {r.get('district')}".lower()]

    if not matches:
        return f"No reports found for: {query}"

    output = f"Found {len(matches)} reports:\n"
    for r in matches[:5]:
        # เลือกแค่ field ที่ผู้ใช้สนใจ: ชื่อปั๊ม, จังหวัด, สถานะน้ำมัน
        output += (f"- {r.get('stationName')} ({r.get('province')}): "
                   f"Diesel: {r.get('diesel')}, B95: {r.get('benzine95')}\n")
    return output
```

**ทำไม:** AI ไม่ต้องรู้ `brandId` หรือ `createdAt` เพื่อตอบคำถามผู้ใช้ ยิ่งส่งข้อมูลไม่จำเป็นมาก AI ยิ่งเสี่ยงหลงประเด็น ควรเลือก return แค่ field ที่ตอบคำถามของผู้ใช้ได้

---

## 3. Error Handling ที่ขาดหาย

MCP Server ต้องทำงาน 24/7 — ถ้า error handling ไม่ดี server จะ crash และ AI จะตอบผู้ใช้ไม่ได้

---

### ❌ ข้อผิดพลาด 3.1: ไม่ catch exception — server crash

**ปัญหา:** ถ้า tool function throw exception ที่ไม่ได้ catch ไว้ MCP server อาจ crash ทั้ง process ทำให้ AI ใช้งาน tool ไม่ได้เลย

**ตัวอย่าง:**
```python
# ❌ แย่ — ถ้า JSON parse fail, file read fail, หรือ key ไม่มี จะ crash ทันที
@mcp.tool()
def search_fuel_status(query: str) -> str:
    with open(DATA_PATH, 'r') as f:
        for line in f:
            report = json.loads(line)  # ถ้า line ไม่ใช่ valid JSON → crash!
            if query in report['stationName']:  # ถ้าไม่มี key → KeyError crash!
                pass
```

**✅ แก้ไข:**
```python
# ✅ ดี — catch exception ทุกระดับ, return error message แทน crash
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search for fuel availability in Thailand by station name, province, or district."""
    try:
        data = get_data()
        matches = []
        for r in data:
            # ใช้ .get() แทน direct access เพื่อป้องกัน KeyError
            search_all = f"{r.get('stationName', '')} {r.get('province', '')} {r.get('district', '')}".lower()
            if query.lower() in search_all:
                matches.append(r)

        if not matches:
            return f"No reports found for: {query}"

        output = f"Found {len(matches)} reports:\n"
        for r in matches[:5]:
            output += (f"- {r.get('stationName')} ({r.get('province')}): "
                       f"Diesel: {r.get('diesel')}, B95: {r.get('benzine95')}\n")
        return output
    except Exception as e:
        return f"Error searching fuel status: {str(e)}"
```

**ทำไม:** MCP server ทำงานเป็น long-running process ถ้า crash ต้อง restart ทำให้ AI ใช้งานไม่ได้ การ catch exception และ return error message ช่วยให้ server ยังทำงานต่อได้ โค้ดปัจจุบันใน `get_data()` ใช้ `except: continue` ซึ่งช่วยป้องกัน JSON parse error ได้ แต่ควรใช้ `except json.JSONDecodeError` แทน bare `except` เพื่อไม่ซ่อน bug อื่นๆ

---

### ❌ ข้อผิดพลาด 3.2: ไม่ตรวจว่าไฟล์ข้อมูลมีอยู่จริง

**ปัญหา:** ถ้า data file ยังไม่ถูกสร้าง (เช่น `process_radar.py` ยังไม่ได้รัน) tool จะ crash เมื่อพยายามอ่านไฟล์

**ตัวอย่าง:**
```python
# ❌ แย่ — ไม่เช็คว่าไฟล์มีอยู่
DATA_PATH = "/app/data/radar_clean.jsonl"

def get_data():
    results = []
    with open(DATA_PATH, 'r', encoding='utf-8') as f:  # FileNotFoundError!
        for line in f:
            results.append(json.loads(line))
    return results
```

**✅ แก้ไข:**
```python
# ✅ ดี — เช็คว่าไฟล์มีอยู่ก่อน, return list ว่างถ้าไม่มี
DATA_PATH = "/app/data/radar_clean.jsonl"

def get_data():
    results = []
    if not os.path.exists(DATA_PATH):
        return results  # return empty list แทน crash
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return results
```

โปรเจคนี้ทำถูกแล้วใน `mcp_server_modern.py` โดยใช้ `if os.path.exists(DATA_PATH)` และในเวอร์ชัน `mcp_server.py` ก็ return ข้อความ `"Data file not found. Please run process_radar.py first."` ซึ่งดีกว่าเพราะบอก AI ถึงสาเหตุ

**ทำไม:** ใน Docker container ไฟล์ข้อมูลอาจยังไม่มีตอน server เริ่มทำงาน เพราะ `data-updater` service อาจยังไม่ได้รัน ต้อง handle กรณีนี้อย่าง graceful

---

### ❌ ข้อผิดพลาด 3.3: ไม่ validate input parameter

**ปัญหา:** ถ้าผู้ใช้ (หรือ AI) ส่ง input ที่ไม่ถูกต้อง เช่น string ว่าง, None, หรือค่าที่ยาวเกินไป tool อาจทำงานผิดพลาดหรือ return ผลลัพธ์ที่ไม่มีความหมาย

**ตัวอย่าง:**
```python
# ❌ แย่ — ไม่ validate input เลย
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    matches = []
    for r in data:
        # query = "" จะ match ทุก record!
        if query.lower() in f"{r.get('stationName')} {r.get('province')}".lower():
            matches.append(r)
    # ...
```

**✅ แก้ไข:**
```python
# ✅ ดี — validate input ก่อนทำงาน
@mcp.tool()
def search_fuel_status(query: str) -> str:
    """Search for fuel availability in Thailand by station name, province, or district."""
    # Validate input
    if not query or not query.strip():
        return "Please provide a search query (e.g., province name, station name, or district)."

    query = query.strip()

    if len(query) < 2:
        return "Search query is too short. Please provide at least 2 characters."

    data = get_data()
    matches = []
    for r in data:
        search_all = f"{r.get('stationName', '')} {r.get('province', '')} {r.get('district', '')}".lower()
        if query.lower() in search_all:
            matches.append(r)

    if not matches:
        return f"No reports found for: {query}"

    output = f"Found {len(matches)} reports:\n"
    for r in matches[:5]:
        output += (f"- {r.get('stationName')} ({r.get('province')}): "
                   f"Diesel: {r.get('diesel')}, B95: {r.get('benzine95')}\n")
    return output
```

**ทำไม:** Input ว่าง `""` จะ match กับทุก string ใน Python (`"" in "anything"` เป็น `True`) ทำให้ return ข้อมูลทั้งหมด ซึ่งเปลืองและไม่มีประโยชน์ การ validate ช่วยป้องกันพฤติกรรมไม่พึงประสงค์

---

## 4. Data Pipeline ที่มีปัญหา

Data pipeline (`process_radar.py`) คือส่วนที่ดึงข้อมูลจาก API มาทำความสะอาดก่อนให้ MCP server ใช้ ถ้า pipeline มีปัญหา ข้อมูลที่ AI ใช้ก็จะไม่ดี

---

### ❌ ข้อผิดพลาด 4.1: ไม่กรอง Confidence Score — ข้อมูลไม่น่าเชื่อถือ

**ปัญหา:** ข้อมูลจาก crowd-sourcing (เช่น Thai Pump Radar) มี confidence score บ่งบอกความน่าเชื่อถือ ถ้าไม่กรอง ข้อมูลที่ confidence ต่ำ (เช่น report จากคนเดียวที่ไม่มีใครยืนยัน) ก็จะปนอยู่ในผลลัพธ์

**ตัวอย่าง:**
```python
# ❌ แย่ — ใช้ข้อมูลทั้งหมดโดยไม่กรอง confidence
def process_data(data):
    reports = data.get('reports', [])
    df = pd.DataFrame(reports)
    # ไม่มีการกรอง confidence เลย!
    return df
```

**✅ แก้ไข:**
```python
# ✅ ดี — กรอง confidence >= 0.3 ก่อนใช้ข้อมูล (ตามที่โปรเจคนี้ทำอยู่แล้ว)
def process_data(data):
    if not data:
        return None

    reports = data.get('reports', [])
    if not reports:
        print("No reports found in data.")
        return None

    df = pd.DataFrame(reports)

    # กรอง low-confidence reports ออก
    initial_count = len(df)
    df = df[df['confidence'] >= 0.3].copy()
    print(f"Filtered {initial_count - len(df)} low-confidence reports. Remaining: {len(df)}")

    return df
```

**ทำไม:** AI-Ready data ต้องมีคุณภาพ ถ้า AI ได้ข้อมูลที่ confidence ต่ำ มันจะตอบผู้ใช้ด้วยข้อมูลที่ไม่น่าเชื่อถือ ซึ่งเป็นเรื่องอันตราย โดยเฉพาะข้อมูลน้ำมันที่คนจะใช้ตัดสินใจเดินทาง โปรเจคนี้ใช้ threshold `>= 0.3` ใน `process_radar.py` ซึ่งเป็น practice ที่ดี

---

### ❌ ข้อผิดพลาด 4.2: ไม่จัดการ null/None values

**ปัญหา:** ข้อมูลจาก API จริงมักมี field ที่เป็น null เช่น สถานีที่ไม่มี LPG จะไม่มีค่า `lpg` ถ้าไม่จัดการ จะเกิด error หรือแสดง "None" ให้ผู้ใช้เห็น

**ตัวอย่าง:**
```python
# ❌ แย่ — ไม่จัดการ None ทำให้ output แสดง "None"
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    for r in data:
        if query.lower() in r.get('stationName').lower():  # None.lower() → AttributeError!
            output += f"Diesel: {r['diesel']}, LPG: {r['lpg']}\n"  # อาจแสดง "LPG: None"
```

**✅ แก้ไข:**
```python
# ✅ ดี — ใช้ .get() กับ default value, จัดการ None ก่อนแสดงผล
@mcp.tool()
def search_fuel_status(query: str) -> str:
    data = get_data()
    for r in data:
        station = r.get('stationName', '')
        province = r.get('province', '')

        if query.lower() in f"{station} {province}".lower():
            diesel = r.get('diesel', 'unknown')
            b95 = r.get('benzine95', 'unknown')
            output += f"- {station} ({province}): Diesel: {diesel}, B95: {b95}\n"
```

**ทำไม:** ข้อมูลจาก Thai Pump Radar มี fields หลายตัวที่อาจเป็น null เช่น `e20`, `lpg` (ไม่ใช่ทุกปั๊มจะมีทุกชนิดน้ำมัน) การใช้ `.get('field', 'default')` เป็น pattern พื้นฐานที่ต้องทำเสมอ โปรเจคนี้ใช้ `.get()` ถูกต้องแล้ว แต่ยังขาด default value ในบางจุด

---

### ❌ ข้อผิดพลาด 4.3: Hardcode file paths

**ปัญหา:** การ hardcode path เช่น `/home/user/data/radar.jsonl` ทำให้โค้ดทำงานได้แค่บนเครื่องเดียว ไม่สามารถ deploy ไป Docker หรือเครื่องอื่นได้

**ตัวอย่าง:**
```python
# ❌ แย่ — hardcode path สำหรับเครื่อง dev
DATA_PATH = "/home/somchai/projects/fuel-radar/data/radar_clean.jsonl"

# ❌ แย่อีกแบบ — ใช้ relative path ที่ขึ้นกับ working directory
DATA_PATH = "data/radar_clean.jsonl"
# ถ้ารันจาก directory อื่น จะหาไฟล์ไม่เจอ!
```

**✅ แก้ไข:**
```python
# ✅ วิธีที่ 1 — ใช้ environment variable (ดีที่สุดสำหรับ Docker)
DATA_PATH = os.environ.get("DATA_PATH", "/app/data/radar_clean.jsonl")

# ✅ วิธีที่ 2 — ใช้ path relative to script location (ดีสำหรับ local dev)
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'radar_clean.jsonl')

# ✅ วิธีที่ 3 — ใช้ค่าคงที่ที่ตรงกับ Docker volume mount (ตามที่โปรเจคนี้ทำ)
DATA_PATH = "/app/data/radar_clean.jsonl"
# docker-compose.yml: volumes: - ./data:/app/data
```

**ทำไม:** โปรเจคนี้มีสอง version:
- `mcp_server_modern.py` ใช้ `"/app/data/radar_clean.jsonl"` ซึ่ง match กับ Docker volume mount — ใช้ได้ดีใน container
- `mcp_server.py` ใช้ `os.path.join(os.path.dirname(__file__), '..')` ซึ่งยืดหยุ่นกว่าสำหรับ local dev

วิธีที่ดีที่สุดคือใช้ environment variable เพราะเปลี่ยนได้โดยไม่ต้องแก้โค้ด

---

## 5. Docker & Deployment

---

### ❌ ข้อผิดพลาด 5.1: ลืม rebuild หลังแก้โค้ด

**ปัญหา:** Docker image ถูก build ตอนรัน `docker compose build` ครั้งแรก ถ้าแก้โค้ดแล้วรัน `docker compose up` โดยไม่ build ใหม่ จะได้โค้ดเก่า

**ตัวอย่าง:**
```bash
# ❌ แย่ — แก้โค้ดแล้วรัน up โดยไม่ build ใหม่
vim pipeline/mcp_server_modern.py   # แก้โค้ด
docker compose up -d                 # ยังใช้ image เก่า! โค้ดที่แก้ไม่มีผล!
```

**✅ แก้ไข:**
```bash
# ✅ ดี — build ใหม่ทุกครั้งที่แก้โค้ด
docker compose up -d --build

# หรือแยกคำสั่ง
docker compose build --no-cache
docker compose up -d
```

**ทำไม:** Docker ใช้ layer caching ถ้าไม่บอกให้ build ใหม่ มันจะใช้ image เก่า ทำให้เสียเวลา debug ว่า "ทำไมแก้โค้ดแล้วไม่เปลี่ยน" ใช้ `--build` flag เสมอเมื่อแก้ไขโค้ด

---

### ❌ ข้อผิดพลาด 5.2: Port conflict

**ปัญหา:** ถ้ามี service อื่นใช้ port 3000 อยู่แล้ว (เช่น Node.js app อื่น) Docker container จะ start ไม่ได้

**ตัวอย่าง:**
```yaml
# ❌ แย่ — hardcode port โดยไม่คิดว่าอาจ conflict
services:
  mcp-server:
    ports:
      - "3000:3000"
  # ถ้า port 3000 ถูกใช้อยู่ → Error: port is already allocated
```

**✅ แก้ไข:**
```yaml
# ✅ วิธีที่ 1 — ใช้ environment variable สำหรับ port
services:
  mcp-server:
    ports:
      - "${MCP_PORT:-3000}:3000"
    # รัน: MCP_PORT=3001 docker compose up -d

# ✅ วิธีที่ 2 — ตรวจสอบ port ก่อน start
# bash: lsof -i :3000  หรือ  ss -tlnp | grep 3000
```

**ทำไม:** ในเครื่อง dev มักมี service หลายตัวรันพร้อมกัน port conflict เป็นปัญหาที่พบบ่อยมาก ควรออกแบบให้เปลี่ยน port ได้ง่ายผ่าน environment variable

---

### ❌ ข้อผิดพลาด 5.3: ไม่ mount volume ทำให้ข้อมูลหาย

**ปัญหา:** ถ้าไม่ mount volume ข้อมูลที่ `process_radar.py` สร้างจะอยู่แค่ใน container ของ `data-updater` แต่ `mcp-server` container จะเห็นไฟล์ว่าง และเมื่อ container ถูก recreate ข้อมูลจะหายหมด

**ตัวอย่าง:**
```yaml
# ❌ แย่ — ไม่มี volume mount ข้อมูลอยู่แค่ใน container
services:
  mcp-server:
    build: .
    ports:
      - "3000:3000"
    # ไม่มี volumes! ข้อมูลจะหายเมื่อ container ถูก recreate

  data-updater:
    build: .
    command: ["python", "pipeline/process_radar.py"]
    # ไม่มี volumes! ข้อมูลที่ process จะอยู่แค่ใน container นี้
    # mcp-server จะอ่านไม่เห็น!
```

**✅ แก้ไข:**
```yaml
# ✅ ดี — mount volume เดียวกันให้ทั้งสอง services (ตามที่โปรเจคนี้ทำ)
services:
  mcp-server:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/data    # mount host ./data → container /app/data

  data-updater:
    build: .
    volumes:
      - ./data:/app/data    # mount volume เดียวกัน!
    command: ["python", "pipeline/process_radar.py"]
```

**ทำไม:** โปรเจคนี้มี 2 containers ที่ต้อง share ข้อมูลกัน:
1. `data-updater` — รัน `process_radar.py` เพื่อดึงข้อมูลจาก API และเขียนไฟล์ `radar_clean.jsonl`
2. `mcp-server` — อ่านไฟล์ `radar_clean.jsonl` เพื่อตอบคำถาม

ถ้าไม่ mount volume เดียวกัน (`./data:/app/data`) ให้ทั้งสอง services ข้อมูลจะไม่เชื่อมกัน `docker-compose.yml` ของโปรเจคนี้ทำถูกต้องแล้ว

---

## สรุป Checklist

| หมวด | ตรวจสอบ | สำคัญ |
|------|---------|-------|
| **Tool Description** | เขียนเป็น English, บอก "Use this when...", ไม่ซ้ำกัน | สูงมาก |
| **Return Value** | จำกัดจำนวน records, human-readable, มี empty state message | สูงมาก |
| **Error Handling** | catch exception, เช็คไฟล์, validate input | สูง |
| **Data Pipeline** | กรอง confidence, จัดการ null, ไม่ hardcode path | สูง |
| **Docker** | rebuild หลังแก้โค้ด, เช็ค port, mount volume | ปานกลาง |

> **กฏทอง:** MCP Tool ที่ดีคือ tool ที่ AI เข้าใจว่าเมื่อไหร่ควรเรียก, ส่งค่าอะไรเข้าไป, และได้ผลลัพธ์ที่ส่งต่อให้ผู้ใช้ได้เลย
