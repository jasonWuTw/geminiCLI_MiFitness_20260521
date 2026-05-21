import csv
import json
import datetime
import os

# Taipei timezone offset is UTC+8
TAIPEI_OFFSET = datetime.timedelta(hours=8)

START_2026 = int(datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc).timestamp())

def get_taipei_date(ts):
    dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc) + TAIPEI_OFFSET
    return dt.strftime('%Y-%m-%d')

daily_data = {} # date -> {steps: 0, calories: 0, distance: 0, hr_avg: [], spo2_avg: [], stress_avg: [], sleep_duration: 0}
sport_counts = {} # type -> count

# Process fitness data
fitness_file = '20260521_6499811869_MiFitness_hlth_center_fitness_data.csv'
if os.path.exists(fitness_file):
    with open(fitness_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = int(row['Time'])
            if ts < START_2026: continue
            
            date = get_taipei_date(ts)
            if date not in daily_data:
                daily_data[date] = {
                    'steps': 0, 'calories': 0, 'distance': 0, 
                    'hr_vals': [], 'spo2_vals': [], 'stress_vals': [], 'sleep_duration': 0
                }
            
            try:
                val_json = json.loads(row['Value'])
                key = row['Key']
                if key == 'steps':
                    daily_data[date]['steps'] += val_json.get('steps', 0)
                    daily_data[date]['distance'] += val_json.get('distance', 0)
                elif key == 'calories':
                    daily_data[date]['calories'] += val_json.get('calories', 0)
                elif key == 'single_heart_rate':
                    daily_data[date]['hr_vals'].append(val_json.get('bpm', 0))
                elif key == 'spo2':
                    daily_data[date]['spo2_vals'].append(val_json.get('spo2', 0))
                elif key == 'sleep':
                    daily_data[date]['sleep_duration'] += val_json.get('duration', 0)
            except:
                pass

# Process aggregated data for stress
agg_file = '20260521_6499811869_MiFitness_hlth_center_aggregated_fitness_data.csv'
if os.path.exists(agg_file):
    with open(agg_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = int(row['Time'])
            if ts < START_2026: continue
            date = get_taipei_date(ts)
            if date not in daily_data: continue
            
            try:
                val_json = json.loads(row['Value'])
                if row['Key'] == 'stress':
                    daily_data[date]['stress_vals'].append(val_json.get('avg_stress', 0))
            except:
                pass

# Process sport records
sport_file = '20260521_6499811869_MiFitness_hlth_center_sport_record.csv'
if os.path.exists(sport_file):
    with open(sport_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = int(row['Time'])
            if ts < START_2026: continue
            category = row['Category']
            sport_counts[category] = sport_counts.get(category, 0) + 1

# Format daily data for JS
sorted_dates = sorted(daily_data.keys())
formatted_daily = []
for d in sorted_dates:
    day = daily_data[d]
    avg_hr = round(sum(day['hr_vals']) / len(day['hr_vals'])) if day['hr_vals'] else 0
    avg_spo2 = round(sum(day['spo2_vals']) / len(day['spo2_vals'])) if day['spo2_vals'] else 0
    avg_stress = round(sum(day['stress_vals']) / len(day['stress_vals'])) if day['stress_vals'] else 0
    
    formatted_daily.append({
        'date': d,
        'steps': round(day['steps']),
        'calories': round(day['calories'], 2),
        'distance': round(day['distance'] / 1000, 2), # km
        'hr': avg_hr,
        'spo2': avg_spo2,
        'stress': avg_stress,
        'sleep': round(day['sleep_duration'] / 60, 2) # hours
    })

# Output as a JS file
with open('data.js', 'w', encoding='utf-8') as f:
    f.write(f"const dailyData = {json.dumps(formatted_daily, indent=2)};\n")
    f.write(f"const sportData = {json.dumps(sport_counts, indent=2)};\n")

print("Data processed and saved to data.js")
