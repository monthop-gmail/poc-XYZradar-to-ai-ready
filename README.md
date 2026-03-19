# 🚀 จากข้อมูลสาธารณะ (Open Data) สู่ความพร้อมทาง AI (AI-Ready)

โปรเจกต์นี้เป็นตัวอย่างการยกระดับการเปิดเผยข้อมูลสาธารณะตามโมเดล **5+1 Star Open Data** โดยเปลี่ยนข้อมูลจากเว็บไซต์รายงานสถานะน้ำมันให้พร้อมสำหรับการใช้งานกับ AI/ML และ RAG (Retrieval-Augmented Generation)

## 📋 ภาพรวมโครงการ (Project Overview)

เรานำแนวคิดจากการทำ Workshop การเปิดเผยข้อมูลภาครัฐมาประยุกต์ใช้กับข้อมูลจริง เพื่อแสดงให้ทีมงานเห็นว่าข้อมูลที่ "เปิด" เฉยๆ กับข้อมูลที่ "เปิดและพร้อมใช้สำหรับ AI" นั้นต่างกันอย่างไร

### 🌟 บันได 5+1 ขั้นสู่ AI-Ready
ศึกษาโมเดลความละเอียดของข้อมูลได้ที่:
👉 [โมเดลข้อมูลเปิด 5+1 ดาว (research/open_data_model.md)](./research/open_data_model.md)

---

## 🔍 กรณีศึกษา: Thai Pump Radar

เราได้วิเคราะห์ข้อมูลรายงานน้ำมันจากชุมชนของ [thaipumpradar.com](https://thaipumpradar.com/) เพื่อนำมาสาธิตกระบวนการยกระดับข้อมูล

### 1. การวิเคราะห์ข้อมูล (Research & Analysis)
- วิเคราะห์โครงสร้าง API และจุดเด่นของข้อมูล เช่น ค่า Confidence Score
- 👉 [บทวิเคราะห์ Thai Pump Radar (research/thaipumpradar_analysis_th.md)](./research/thaipumpradar_analysis_th.md)

### 2. การจัดการข้อมูล (Data Pipeline)
- สคริปต์ [pipeline/process_radar.py](./pipeline/process_radar.py) สำหรับดึงข้อมูลและคลีนข้อมูล
- การจัดเก็บข้อมูลในรูปแบบ **Parquet** (สำหรับ Analytics) และ **JSONL** (สำหรับ AI)
- การจัดทำ [pipeline/datacard.md](./pipeline/datacard.md) เพื่อกำกับชุดข้อมูล

### 3. การแสดงผลด้วย AI (Demonstration)
- ทดสอบการวิเคราะห์ข้อมูลเชิงลึกและการสืบค้นด้วยภาษาธรรมชาติ (Mock RAG)
- 👉 [สรุปผลการรัน AI Demo (demo/demonstration_results.md)](./demo/demonstration_results.md)
- 👉 [โค้ดสาธิตการใช้ AI (demo/demonstrate_ai.py)](./demo/demonstrate_ai.py)

---

## 🛠️ วิธีการใช้งาน (Getting Started)

### การเตรียมความพร้อม
```bash
pip install pandas pyarrow requests
```

### การรันระบบ (Pipeline)
```bash
python pipeline/process_radar.py
```
*ระบบจะสร้างไฟล์ `data/radar_clean.jsonl` และ `data/radar_clean.parquet` ที่พร้อมใช้งาน*

### การรันเดโม AI
```bash
python demo/demonstrate_ai.py
```

---

## 🎯 สรุปสิ่งที่ทีมงานจะได้รับ
- **เข้าใจมาตรฐานใหม่:** เห็นภาพชัดเจนว่า AI-Ready Data มีองค์ประกอบอย่างไร (Level 6)
- **ลดระยะเวลา:** มีต้นแบบโค้ด (Pipeline) ที่สามารถนำไปปรับใช้กับแหล่งข้อมูลอื่นได้ทันที
- **เพิ่มมูลค่าข้อมูล:** เปลี่ยนจาก "ข้อมูลดิบ" ให้กลายเป็น "ฐานความรู้" (Knowledge Base) สำหรับ AI Agent

---
*จัดทำขึ้นเพื่อสาธิตการเปลี่ยนผ่านข้อมูลสาธารณะสู่ยุค AI อย่างเป็นรูปธรรม*
