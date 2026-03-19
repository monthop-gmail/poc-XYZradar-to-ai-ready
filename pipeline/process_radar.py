import requests
import pandas as pd
import json
import os

def fetch_radar_data(limit=100):
    url = f"https://thaipumpradar.com/api/reports/feed?limit={limit}"
    print(f"Fetching data from {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def process_data(data):
    if not data:
        return None
    
    # Extract reports
    reports = data.get('reports', [])
    if not reports:
        print("No reports found in data.")
        return None

    # Load into DataFrame
    df = pd.DataFrame(reports)
    
    # 1. Validation: Filter by confidence >= 0.3
    initial_count = len(df)
    df = df[df['confidence'] >= 0.3].copy()
    print(f"Filtered {initial_count - len(df)} low-confidence reports. Remaining: {len(df)}")

    # 2. Cleaning: Normalize fields
    # Keep only relevant fields for AI-Ready dataset
    fields = [
        'stationName', 'brandId', 'province', 'district', 
        'diesel', 'benzine91', 'benzine95', 'e20', 'lpg', 
        'confidence', 'createdAt'
    ]
    df = df[[f for f in fields if f in df.columns]]
    
    return df

def save_ai_ready(df, base_path):
    # Save as JSONL (AI/RAG friendly)
    jsonl_path = os.path.join(base_path, 'radar_clean.jsonl')
    df.to_json(jsonl_path, orient='records', lines=True, force_ascii=False)
    print(f"Saved AI-Ready JSONL to {jsonl_path}")

    # Save as Parquet (Analytics friendly)
    parquet_path = os.path.join(base_path, 'radar_clean.parquet')
    df.to_parquet(parquet_path, index=False)
    print(f"Saved AI-Ready Parquet to {parquet_path}")

if __name__ == "__main__":
    raw_data = fetch_radar_data(100)
    clean_df = process_data(raw_data)
    
    if clean_df is not None:
        save_ai_ready(clean_df, ".")
        print("\n--- Data Summary ---")
        # Avoid printing Thai characters to console to prevent UnicodeEncodeError
        print(f"Total processed reports: {len(clean_df)}")
        print(f"Columns: {list(clean_df.columns)}")
    else:
        print("Process failed.")
