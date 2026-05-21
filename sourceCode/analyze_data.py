import os
import csv
import datetime

# Taipei timezone offset is UTC+8
TAIPEI_OFFSET = datetime.timedelta(hours=8)

def convert_to_taipei_time(timestamp_val):
    try:
        ts = int(timestamp_val)
        if ts <= 0: return None
        
        # Determine if it's seconds, milliseconds, or nanoseconds
        ts_str = str(ts)
        if len(ts_str) >= 19: # Nanoseconds
            ts = ts / 1_000_000_000
        elif len(ts_str) >= 13: # Milliseconds
            ts = ts / 1_000
        
        dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
        taipei_dt = dt + TAIPEI_OFFSET
        return taipei_dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, OSError):
        return None

def analyze_csv(file_path):
    count = 0
    min_ts = float('inf')
    max_ts = float('-inf')
    
    # Common timestamp column names based on PDF and manual check
    time_cols = ['time', 'timestamp', 'createtime', 'initialtime', 'ctime', 'pkstarttime', 'start_time', 'updatetime']
    time_col_idx = -1
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers:
                return 0, None, None
            
            # Find the best time column (case-insensitive)
            header_lower = [h.lower() for h in headers]
            for col in time_cols:
                if col in header_lower:
                    time_col_idx = header_lower.index(col)
                    break
            
            for row in reader:
                if not any(row): continue # Skip empty rows
                count += 1
                if time_col_idx != -1 and time_col_idx < len(row):
                    try:
                        val = row[time_col_idx]
                        if val:
                            ts_val = int(val)
                            if ts_val > 0:
                                if ts_val < min_ts: min_ts = ts_val
                                if ts_val > max_ts: max_ts = ts_val
                    except ValueError:
                        pass
    except Exception:
        return -1, None, None

    start_time = convert_to_taipei_time(min_ts) if min_ts != float('inf') else "N/A"
    end_time = convert_to_taipei_time(max_ts) if max_ts != float('-inf') else "N/A"
    
    return count, start_time, end_time

csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
# Sort alphabetically for consistent output
csv_files.sort()

results_with_data = []
results_empty = []

for file in csv_files:
    if file == 'analyze_data.py': continue
    count, start, end = analyze_csv(file)
    if count > 0:
        results_with_data.append({
            'file': file,
            'count': count,
            'start': start,
            'end': end
        })
    elif count == 0:
        results_empty.append(file)

with open('analysis_report.md', 'w', encoding='utf-8') as f:
    f.write("### 資料數量 > 0 的資料\n\n")
    for res in results_with_data:
        f.write(f"- **檔案名稱**: {res['file']}\n")
        f.write(f"  - 資料數量: {res['count']}\n")
        f.write(f"  - 時間範圍: {res['start']} 至 {res['end']}\n")
    
    f.write("\n### 資料數量 = 0 的資料\n\n")
    for file in results_empty:
        f.write(f"- {file}\n")

print("Analysis complete. Report generated in analysis_report.md")
