import os
import csv
import json
from datetime import datetime
import pytz
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

TAIPEI_TZ = pytz.timezone('Asia/Taipei')
DATA_DIR = '/Users/wuzhongxiong/Documents/geminiCLI/geminiCLI_MiFitness_20260521/data'
CSV_FILE = '20260521_6499811869_MiFitness_hlth_center_fitness_data.csv'

rhr_data = {}

def load_data():
    global rhr_data
    rhr_data = {}
    rhr_keywords = ['resting_heart_rate', 'rhr', 'resting_hr', 'resting heart rate']
    filepath = os.path.join(DATA_DIR, CSV_FILE)
    
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t = int(row.get('Time', 0))
                key = row.get('Key', '').lower()
                val_str = row.get('Value', '{}')
                val = json.loads(val_str)
            except:
                continue
                
            if t > 3000000000:
                t = t // 1000
                
            if any(k in key for k in rhr_keywords) and 'bpm' in val:
                dt = datetime.fromtimestamp(t, TAIPEI_TZ)
                date_str = dt.strftime('%Y-%m-%d')
                rhr_data[date_str] = val['bpm']

load_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/available_dates')
def available_dates():
    return jsonify(list(rhr_data.keys()))

@app.route('/api/rhr')
def get_rhr():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    limit = request.args.get('limit', type=int)
    
    filtered_data = []
    
    # Sort data by date
    sorted_dates = sorted(rhr_data.keys())
    
    for date in sorted_dates:
        if start_date and date < start_date:
            continue
        if end_date and date > end_date:
            continue
        filtered_data.append({'date': date, 'bpm': rhr_data[date]})
        
    if limit and not start_date and not end_date:
        filtered_data = filtered_data[-limit:]
        
    return jsonify(filtered_data)

@app.route('/api/analysis', methods=['POST'])
def analysis():
    data = request.json.get('data', [])
    if not data:
        return jsonify({'message': '沒有安靜心率'})
    
    bpms = [item['bpm'] for item in data]
    avg_bpm = sum(bpms) / len(bpms)
    min_bpm = min(bpms)
    max_bpm = max(bpms)
    
    # Simple expert analysis logic
    advice = f"在這段期間內，您的平均安靜心率為 **{avg_bpm:.1f} bpm** (最低 {min_bpm} bpm, 最高 {max_bpm} bpm)。"
    
    if avg_bpm < 60:
        advice += " 您的安靜心率偏低，這在經常運動的運動員中很常見，代表心肺功能良好。但若伴隨頭暈或疲倦，建議尋求專業諮詢。"
    elif avg_bpm <= 75:
        advice += " 您的安靜心率處於非常健康的理想範圍內，請繼續保持良好的作息與運動習慣！"
    elif avg_bpm <= 85:
        advice += " 您的安靜心率落在正常範圍的正常偏高區間。適度的有氧運動與壓力管理有助於進一步改善心肺健康。"
    else:
        advice += " 您的安靜心率偏高。可能與近期壓力較大、睡眠不足、缺乏運動或飲食習慣有關。建議多加留意休息，若持續偏高請諮詢醫師。"
        
    return jsonify({'advice': advice})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
