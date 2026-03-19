# ✅ AI-Ready Data Audit Checklist
*คู่มือการตรวจสอบความพร้อมของข้อมูลสำหรับ AI (Level 6 Open Data)*

---

## 1. คุณภาพและความสะอาด (Data Quality)
- [ ] **Data Cleaning:** ข้อมูลมีการกำจัดค่าซ้ำ (De-duplication) และจัดการค่าว่าง (Null Handling) แล้วหรือยัง?
- [ ] **Validation Score:** มีการคำนวณค่าความเชื่อมั่น (Confidence Score) หรือเกณฑ์การตรวจสอบคุณภาพหรือไม่?
- [ ] **Normalization:** ข้อมูลที่เป็นหมวดหมู่ (Categorical) มีการจัดรูปแบบให้เป็นมาตรฐานเดียวกันหรือยัง? (เช่น ชื่อจังหวัด, ประเภทน้ำมัน)
- [ ] **Temporal Accuracy:** ข้อมูลมีการบันทึก Timestamp ที่ชัดเจนเพื่อระบุความสดใหม่หรือไม่?

## 2. รูปแบบไฟล์และการเข้าถึง (Formats & Access)
- [ ] **Analytics Format:** มีไฟล์ **Parquet** สำหรับการคำนวณเชิงสถิติ (Analytical Processing) หรือไม่?
- [ ] **AI/RAG Format:** มีไฟล์ **JSONL** หรือ **Markdown** ที่ออกแบบมาเพื่อการทำ Embedding/Retrieval หรือไม่?
- [ ] **Small Chunks:** ข้อมูลถูกแบ่งเป็นชิ้นเล็กๆ (Chunking) ที่สื่อความหมายสมบูรณ์ในตัวเองหรือไม่?

## 3. คำอธิบายข้อมูล (Documentation / Data Card)
- [ ] **Dataset Description:** มีเอกสารระบุที่มา (Source) และวัตถุประสงค์ของข้อมูลหรือไม่?
- [ ] **Schema Definition:** มีการระบุความหมายของแต่ละ Field ชัดเจนหรือไม่?
- [ ] **Cleaning Process:** มีการบันทึกขั้นตอนการแปรรูปข้อมูล (Lineage) ไว้ใน Data Card หรือไม่?
- [ ] **Usage Limitations:** มีการระบุข้อจำกัดหรือ Bias ที่ AI ควรระวังหรือไม่?

## 4. การเชื่อมต่อกับ AI (Interface / MCP)
- [ ] **Standard Protocol:** มีการรองรับ **Model Context Protocol (MCP)** หรือ API มาตรฐานหรือไม่?
- [ ] **Transport Standard:** ใช้การเชื่อมต่อแบบ **Streamable HTTP (/mcp)** บนพอร์ตที่เป็นมาตรฐานหรือไม่?
- [ ] **Tool Definition:** มีการนิยาม Function/Tool ที่ AI สามารถเรียกใช้ได้ชัดเจน (Description, Parameters) หรือไม่?

## 5. ความยั่งยืนและจริยธรรม (Sustainability & Ethics)
- [ ] **Automated Pipeline:** กระบวนการอัปเดตข้อมูลเป็นแบบอัตโนมัติ (Automated) หรือไม่?
- [ ] **Privacy (PII):** มีการตรวจสอบและนำข้อมูลส่วนบุคคลที่ระบุตัวตนได้ออกไปแล้วหรือยัง?
- [ ] **License:** มีการระบุสัญญาอนุญาตการใช้งานข้อมูลที่ชัดเจนหรือไม่?

---
> [!IMPORTANT]
> **เป้าหมาย:** "ข้อมูลที่ดี ไม่ใช่แค่ข้อมูลที่เปิด แต่คือข้อมูลที่ AI สามารถนำไปใช้สร้างความฉลาดได้ทันทีโดยไม่ต้องถามซ้ำ"
