import json
import os
import re

# Load data
with open('cleaned_report_data.json', 'r') as f:
    data_json = f.read()

# Load HTML
with open('Cleaned_Data_Elite_Report.html', 'r', encoding='utf-8') as f:
    html = f.read()

# JS logic for BPM chart
bpm_js = """
    // 0. BPM Trend
    new Chart(document.getElementById('bpmTrendChart'), {
        type: 'line',
        data: {
            labels: data.bpm_trend.labels,
            datasets: [{
                label: '心率 (BPM)',
                data: data.bpm_trend.values,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                fill: true,
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { x: { display: false }, y: { suggestedMin: 50, suggestedMax: 150, title: { display: true, text: 'BPM' } } }
        }
    });
"""

# Perform replacements
# Replace the data block
html = re.sub(r'const data = \{.*?\};', f'const data = {data_json};', html, flags=re.DOTALL)

# Add the JS rendering code if not already present
if '// 0. BPM Trend' not in html:
    html = html.replace('// 1. RR Trend', bpm_js + '\n    // 1. RR Trend')

# Write back
with open('Cleaned_Data_Elite_Report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Update successful!")
