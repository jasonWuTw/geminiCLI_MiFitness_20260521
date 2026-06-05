# 安靜心率 (RHR) 趨勢儀表板

## 專案簡介

本專案是一個個人健康數據儀表板，從小米運動健康 App（MiFitness）匯出的 CSV 資料中，提取**安靜心率 (Resting Heart Rate, RHR)** 數據，並以互動式圖表與 AI 健康建議的方式呈現。

---

## 資料來源

- **來源 App：** 小米運動健康 (MiFitness)
- **資料位置：** `/Users/wuzhongxiong/Documents/geminiCLI/geminiCLI_MiFitness_20260521/data/`
- **關鍵 CSV 檔：** `20260521_6499811869_MiFitness_hlth_center_fitness_data.csv`
- **資料格式：** CSV，包含 `Uid`, `Sid`, `Key`, `Time`, `Value`, `UpdateTime` 欄位；`Value` 欄位為 JSON 格式字串
- **時區：** 台北時區 (UTC+8)

### 安靜心率資料概況

| 項目 | 內容 |
|---|---|
| 總筆數 | 140 筆 |
| 記錄頻率 | 每日一筆 (08:00:00 CST) |
| 最早紀錄 | 2023-11-15 |
| 最晚紀錄 | 2026-05-20 |
| 整體資料範圍 | 2023-10-27 ~ 2026-05-21 |

---

## 專案結構

```
20260604/
├── app.py                  # Flask 後端伺服器（提供 API）
├── analyze_data.py         # 獨立資料分析腳本（探索用）
├── generate_dashboard.py   # 資料提取腳本（探索用）
├── templates/
│   └── index.html          # 儀表板前端頁面
├── README.md               # 本說明文件
├── SPEC.md                 # 程式規格說明
└── Prompt.md               # 原始提示詞紀錄
```

---

## 環境需求

- Python 3.x
- pip 套件：`flask`, `pytz`

---

## 安裝與啟動

### 1. 安裝套件

```bash
pip3 install flask pytz
```

### 2. 啟動伺服器

```bash
cd /Users/wuzhongxiong/Documents/geminiCLI/geminiCLI_MiFitness_20260521/20260604
python3 app.py
```

### 3. 開啟瀏覽器

前往 👉 **http://127.0.0.1:5000**

---

## 功能說明

1. **安靜心率趨勢圖**：預設顯示最近 30 筆 RHR 資料的折線圖
2. **年份選擇**：可從下拉選單選擇 2023、2024、2025、2026 等年份
3. **月曆式日期選擇器**：可自訂日期範圍；沒有 RHR 資料的日期呈現灰色且無法選取
4. **無資料提示**：若所選期間無資料，顯示「沒有安靜心率」
5. **AI 健康建議**：根據選定期間的 RHR 數據，由專家團隊邏輯給出文字分析建議
6. **醫療免責聲明**：頁面頂部顯示醒目的警語提示

---

## 警語

> ⚠️ 本儀表板與 AI 分析僅供個人健康趨勢參考，**並非醫療診斷**。如有任何身體不適或疑慮，請諮詢專業醫師。
