# 🌱 Farmer Irrigation Decision Support System using NASA POWER Data

## 📌 Project Overview
This project is a **farmer-friendly irrigation decision support system** that uses **NASA POWER climatic data** to analyze rainfall and evapotranspiration trends and provide **actionable irrigation guidance**.

Instead of raw climate numbers, the system translates data into:
- Clear stress levels
- Simple alerts
- Irrigation risk percentages

The goal is to help farmers **understand climate data and act accordingly**.

---

## 🎯 Objectives
- Fetch real-time and historical climate data from NASA POWER
- Compute a scientifically defined **Irrigation Deficit Index (IDI)**
- Categorize irrigation need into **three understandable levels**
- Estimate irrigation risk using a trained Machine Learning model
- Provide an interactive, farmer-friendly web dashboard

---

## 🧠 Methodology

### 1️⃣ Data Source
- **NASA POWER API**
- Daily data:
  - Rainfall (PRECTOTCORR)
  - Evapotranspiration (EVPTRNS)
- Regions: Mandya, Raichur, Tumakuru, Anantapur, Warangal
- Years: 2019 – 2024

---

### 2️⃣ Irrigation Deficit Index (IDI)
The Irrigation Deficit Index represents cumulative water stress.

\[
IDI_7 = \sum_{i=1}^{7} (ET_i - Rainfall_i)
\]

- Negative IDI → Rainfall surplus
- Positive IDI → Water deficit

---

### 3️⃣ Irrigation Decision Logic (Rule-Based)

| IDI₇ Value | Stress Level | Recommendation |
|-----------|-------------|----------------|
| ≤ 0 | Surplus | No irrigation |
| 0 – 15 | Low | No irrigation |
| 15 – 30 | Moderate | Monitor irrigation |
| ≥ 30 | High | Irrigation required |

This ensures **explainability and trust** for farmers.

---

### 4️⃣ Machine Learning Model
- Model: **Random Forest Classifier**
- Inputs:
  - Rainfall
  - Evapotranspiration
- Output:
  - Probability of irrigation requirement (risk %)

> ML is used as a **decision-support tool**, not as the primary trigger.

---

### 5️⃣ Dataset Generation & Training
- Auto-generated ~10,900 samples using NASA POWER
- Labels created using IDI thresholds (weak supervision)
- Class imbalance handled using `class_weight="balanced"`
- Target leakage avoided

---

## 🖥️ System Architecture

1. User selects farm location & date range  
2. NASA POWER data is fetched  
3. IDI is computed  
4. Rule-based irrigation level is determined  
5. ML model estimates irrigation risk  
6. Results are visualized on the dashboard  

---

## 📊 Features
- Interactive map-based farm selection
- Seasonal irrigation analysis
- Farmer-friendly alert banners
- Risk percentage (0–100%)
- Time-series visualizations
- Supports negative IDI (rainfall surplus)

---

## 🛠️ Technologies Used
- Python
- Streamlit
- Pandas, NumPy
- Scikit-learn
- Plotly
- NASA POWER API

---

## ▶️ How to Run the Project

```bash
pip install -r requirements.txt
streamlit run app.py