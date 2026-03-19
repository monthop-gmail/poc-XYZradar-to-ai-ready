import pandas as pd
import json

def run_demo():
    results = []
    results.append("# AI Demonstration Results: Thai Pump Radar\n")
    
    # 1. Analysis Demo
    df = pd.read_parquet('radar_clean.parquet')
    results.append("## 📊 1. ตัวอย่างการวิเคราะห์ข้อมูล (Data Analysis)")
    results.append(f"จำนวนข้อมูลทั้งหมดที่ประมวลผล: **{len(df)} รายการ**\n")
    
    out_counts = df[df['diesel'] == 'out']['province'].value_counts()
    results.append("### จังหวัดที่มีรายงาน 'ดีเซลหมด' สูงสุด:")
    if not out_counts.empty:
        for prov, count in out_counts.head(5).items():
            results.append(f"- {prov}: {count} รายการ")
    else:
        results.append("- ไม่พบรายงานดีเซลหมดในชุดข้อมูลนี้")
    
    # 2. Mock RAG Demo
    results.append("\n## 🤖 2. ตัวอย่างการสืบค้นสำหรับ AI (Mock RAG)")
    
    queries = ["กรุงเทพ", "ปตท", "สระบุรี"]
    for query in queries:
        results.append(f"\n**คำถามผู้ใช้ (Query):** \"{query}\"")
        matches = []
        with open('radar_clean.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                report = json.loads(line)
                if any(query.lower() in str(report.get(k, '')).lower() for k in ['stationName', 'province', 'district']):
                    matches.append(report)
        
        results.append(f"**ผลลัพธ์การสืบค้น:** พบ {len(matches)} รายการที่เกี่ยวข้อง")
        for i, res in enumerate(matches[:2]):
            results.append(f"{i+1}. **{res.get('stationName')}** ({res.get('province')}/{res.get('district')})")
            results.append(f"   - สถานะน้ำมัน: ดีเซล ({res.get('diesel')}), เบนซิน 95 ({res.get('benzine95')})")

    # Write to file
    with open('demonstration_results.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(results))
    print("Demonstration results saved to demonstration_results.md")

if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"Error in demonstration: {e}")
