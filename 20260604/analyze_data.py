import os
import csv
from datetime import datetime
import pytz
import json

taipei_tz = pytz.timezone('Asia/Taipei')

data_dir = '/Users/wuzhongxiong/Documents/geminiCLI/geminiCLI_MiFitness_20260521/data'

rhr_records = []
rhr_keywords = ['resting_heart_rate', 'rhr', 'resting_hr', 'resting heart rate']

def check_file(filename):
    filepath = os.path.join(data_dir, filename)
    if not filepath.endswith('.csv'):
        return
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            return
            
        time_idx = None
        for i, h in enumerate(headers):
            if h.lower() in ['time', 'start_time', 'endtime']:
                time_idx = i
                break
        
        key_idx = None
        for i, h in enumerate(headers):
            if h.lower() in ['key', 'type', 'name', 'tag']:
                key_idx = i
                break
                
        val_idx = None
        for i, h in enumerate(headers):
            if h.lower() in ['value', 'data']:
                val_idx = i
                break

        if time_idx is None:
            return
            
        for row in reader:
            if len(row) <= time_idx:
                continue
            t_str = row[time_idx]
            try:
                t = int(t_str)
                if t > 3000000000:
                    t = t // 1000
                if t > 0:
                    if key_idx is not None and len(row) > key_idx:
                        val_key = row[key_idx].lower()
                        if any(k in val_key for k in rhr_keywords):
                            value_data = row[val_idx] if val_idx is not None and len(row) > val_idx else ""
                            rhr_records.append({
                                'time': t,
                                'key': val_key,
                                'value': value_data,
                                'file': filename
                            })
                            
            except ValueError:
                pass

for f in os.listdir(data_dir):
    check_file(f)

# Sort by time
rhr_records.sort(key=lambda x: x['time'])

print(f"Total RHR records found: {len(rhr_records)}")

if len(rhr_records) > 0:
    print("\nFirst 10 RHR records:")
    for i in range(min(10, len(rhr_records))):
        rec = rhr_records[i]
        dt = datetime.fromtimestamp(rec['time'], taipei_tz)
        print(f"{i+1}. Time: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')} | File: {rec['file']} | Key: {rec['key']} | Value: {rec['value']}")
        
    if len(rhr_records) > 1:
        diffs = [rhr_records[i]['time'] - rhr_records[i-1]['time'] for i in range(1, len(rhr_records))]
        avg_diff = sum(diffs) / len(diffs)
        print(f"\nAverage interval between records: {avg_diff} seconds ({avg_diff/3600:.2f} hours or {avg_diff/86400:.2f} days)")
