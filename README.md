# 📊 Smart Data Analyzer

A powerful and user-friendly **Streamlit** application for analyzing and visualizing your data with **interactive charts**, **filtering**, and **PDF report generation**.

---

## 🚀 Features

- 📂 Upload **Excel** (`.xlsx`) or **CSV** files  
- 🧰 Interactive **data filtering**  
- 📊 Multiple chart types: `Bar`, `Line`, `Pie`, `Scatter`, `Histogram`  
- 🧾 Generate and download **PDF reports**  
- 🔍 View **top 20 rows** or full dataset  
- 🧪 Built-in **sample dataset** for quick testing  

---

## 📁 Project Structure

### 📄 `app.py`
The main **Streamlit application** file containing:
- 📂 File upload and validation  
- 🎯 Filtering logic and UI  
- 📊 Chart visualization using Plotly  
- 🧾 PDF generation with `fpdf`  
- 🖥️ User interface layout  

### 📊 `data/coffee_sales_full.xlsx`
Sample dataset for demo:
- ☕ Coffee sales data  
- 🗓️ Dates, products, and sales figures  
- 🧹 Clean and structured format  

### 🧠 `utils/insights.py`
Helper module with:
- 📈 Analysis and insights generation  
- 📊 Statistical functions  
- 🧼 Data preprocessing utilities  
- 🧩 Extendable for custom logic  

### 📦 `requirements :`
List of Python dependencies:
- `streamlit` – Web UI framework  
- `pandas` – Data manipulation  
- `plotly` – Charting library  
- `fpdf` – PDF report generator  
- `openpyxl` – Excel file support  

### 🛠️ `Command-Run Project :`
streamlit run app.py

Quick commands to get started and run the app.

---

## ⚙️ Installation & Usage

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ankitpoddar07/smart_data-analyzer.git
cd smart_data-analyzer
