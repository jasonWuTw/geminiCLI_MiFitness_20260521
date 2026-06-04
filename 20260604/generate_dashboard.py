#!/usr/bin/env python3
"""
健康數據提取腳本 - 從 MiFitness CSV 提取所有數據，生成儀表板 HTML
"""
import os, csv, json
from datetime import datetime, timezone, timedelta
import pytz

TAIPEI_TZ = pytz.timezone('Asia/Taipei')
DATA_DIR = '/Users/wuzhongxiong/Documents/geminiCLI/geminiCLI_MiFitness_20260521/data'
OUT_DIR  = '/Users/wuzhongxiong/Documents/geminiCLI/geminiCLI_MiFitness_20260521/20260604'

def ts_to_date(ts):
    """Unix timestamp → 台北時區 YYYY-MM-DD"""
    return datetime.fromtimestamp(ts, TAIPEI_TZ).strftime('%Y-%m-%d')

def safe_json(s):
    try:    return json.loads(s)
    except: return {}

# ── 1. 靜息心率 RHR ──────────────────────────────────────────
rhr = {}   # date -> bpm
agg_hr = {}  # date -> {avg, max, min, avg_rhr}

# ── 2. 每日步數 / 卡路里 ────────────────────────────────────
steps_daily = {}   # date -> {steps, calories, distance}

# ── 3. SpO2 ─────────────────────────────────────────────────
spo2_daily = {}    # date -> {avg, max, min}

# ── 4. 睡眠 ─────────────────────────────────────────────────
sleep_daily = {}   # date -> {score, total_min, deep_min, light_min, rem_min}

# ── 5. 壓力 ─────────────────────────────────────────────────
stress_daily = {}  # date -> {avg, max, min}

# ── 6. 運動紀錄 ─────────────────────────────────────────────
sport_records = [] # list of dicts

print("📂 讀取 fitness_data.csv ...")
fitness_path = os.path.join(DATA_DIR, '20260521_6499811869_MiFitness_hlth_center_fitness_data.csv')
with open(fitness_path, encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            t   = int(row['Time'])
            key = row['Key'].lower()
            val = safe_json(row['Value'])
            date = ts_to_date(t)
        except:
            continue

        if key == 'resting_heart_rate' and 'bpm' in val:
            rhr[date] = val['bpm']

print(f"  ✓ RHR 筆數: {len(rhr)}")

print("📂 讀取 aggregated_fitness_data.csv ...")
agg_path = os.path.join(DATA_DIR, '20260521_6499811869_MiFitness_hlth_center_aggregated_fitness_data.csv')
with open(agg_path, encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            t   = int(row['Time'])
            key = row['Key'].lower()
            val = safe_json(row['Value'])
            date = ts_to_date(t)
        except:
            continue

        if key == 'steps':
            steps_daily[date] = {
                'steps':    val.get('steps', 0),
                'calories': val.get('calories', 0),
                'distance': val.get('distance', 0)
            }
        elif key == 'heart_rate':
            agg_hr[date] = {
                'avg': val.get('avg_hr', 0),
                'max': val.get('max_hr', 0),
                'min': val.get('min_hr', 0),
                'avg_rhr': val.get('avg_rhr', 0)
            }
        elif key == 'spo2':
            spo2_daily[date] = {
                'avg': val.get('avg_spo2', 0),
                'max': val.get('max_spo2', 0),
                'min': val.get('min_spo2', 0)
            }
        elif key == 'sleep':
            sleep_daily[date] = {
                'score':     val.get('sleep_score', 0),
                'total_min': val.get('total_duration', 0),
                'deep_min':  val.get('sleep_deep_duration', 0),
                'light_min': val.get('sleep_light_duration', 0),
                'rem_min':   val.get('sleep_rem_duration', 0)
            }
        elif key == 'stress':
            stress_daily[date] = {
                'avg': val.get('avg_stress', 0),
                'max': val.get('max_stress', 0),
                'min': val.get('min_stress', 0)
            }

print(f"  ✓ Steps: {len(steps_daily)}, HR: {len(agg_hr)}, SpO2: {len(spo2_daily)}, Sleep: {len(sleep_daily)}, Stress: {len(stress_daily)}")

print("📂 讀取 sport_record.csv ...")
sport_path = os.path.join(DATA_DIR, '20260521_6499811869_MiFitness_hlth_center_sport_record.csv')
with open(sport_path, encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            t   = int(row['Time'])
            val = safe_json(row['Value'])
            date = ts_to_date(t)
        except:
            continue
        sport_records.append({
            'date':     date,
            'type':     row.get('Key', ''),
            'category': row.get('Category', ''),
            'duration': val.get('duration', 0),
            'distance': val.get('distance', 0),
            'calories': val.get('calories', 0),
            'avg_hrm':  val.get('avg_hrm', 0),
            'max_hrm':  val.get('max_hrm', 0),
            'steps':    val.get('steps', 0),
        })
sport_records.sort(key=lambda x: x['date'])
print(f"  ✓ 運動紀錄: {len(sport_records)} 筆")

# ── 建立 ALL_DATES 集合，用於月曆灰色標記 ───────────────────
all_data_dates = set(rhr) | set(steps_daily) | set(spo2_daily) | set(sleep_daily) | set(stress_daily)

data_payload = {
    'rhr':          dict(sorted(rhr.items())),
    'steps':        dict(sorted(steps_daily.items())),
    'heart_rate':   dict(sorted(agg_hr.items())),
    'spo2':         dict(sorted(spo2_daily.items())),
    'sleep':        dict(sorted(sleep_daily.items())),
    'stress':       dict(sorted(stress_daily.items())),
    'sport':        sport_records,
    'data_dates':   sorted(all_data_dates),
    'rhr_dates':    sorted(rhr.keys()),
}

# ── 讀取 HTML 模板，嵌入 JSON ────────────────────────────────
template_path = os.path.join(OUT_DIR, 'dashboard_template.html')
out_path      = os.path.join(OUT_DIR, 'health_dashboard.html')

if not os.path.exists(template_path):
    print(f"❌ 找不到模板: {template_path}")
    print("   請先確認 dashboard_template.html 存在")
else:
    with open(template_path, encoding='utf-8') as f:
        html = f.read()

    json_str = json.dumps(data_payload, ensure_ascii=False)
    html = html.replace('/*__DATA_PLACEHOLDER__*/', f'const HEALTH_DATA = {json_str};')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n✅ 儀表板已生成: {out_path}")
