# 🤖 AI Business Anomaly Detection

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-orange?logo=pandas)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-red?logo=scikitlearn)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-green)
![Status](https://img.shields.io/badge/Project-Completed-brightgreen)

---

## 📌 Project Overview

AI Business Anomaly Detection is a Machine Learning project that identifies unusual business transactions using the **Isolation Forest Algorithm**.

The project performs complete data analysis, including data loading, data cleaning, exploratory data analysis (EDA), visualization, anomaly detection, and exporting processed datasets.

---

## 🎯 Objectives

- Load raw business transaction data
- Clean and preprocess the dataset
- Perform Exploratory Data Analysis (EDA)
- Generate business insights using visualizations
- Detect anomalous transactions using Machine Learning
- Export cleaned data and detected anomalies

---

# 📂 Project Structure

```text
AI-Business-Anomaly-Detection/
│
├── data/
│   ├── raw/
│   │   └── business_data.csv
│   │
│   └── processed/
│       ├── cleaned_data.csv
│       └── anomalies.csv
│
├── reports/
│   ├── sales_by_region.png
│   └── profit_by_category.png
│
├── src/
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── eda.py
│   ├── visualization.py
│   ├── anomaly_detection.py
│   └── main.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-Learn

---

# 🧠 Machine Learning Algorithm

### Isolation Forest

Isolation Forest is an unsupervised machine learning algorithm designed for anomaly detection.

The model isolates unusual observations by creating random decision trees. Transactions requiring fewer splits are considered anomalies.

---

# 📊 Exploratory Data Analysis

The project performs:

- Dataset Shape
- Data Types
- Missing Values Analysis
- Duplicate Detection
- Summary Statistics
- Category Distribution
- Regional Sales Analysis
- Profit Analysis

---

# 📈 Visualizations

Generated graphs include:

- Sales by Region
- Profit by Category

All visualizations are automatically saved inside the **reports/** directory.

---

# 🚨 Anomaly Detection

Features used:

- Sales
- Profit
- Quantity
- Discount

Model:

```python
IsolationForest(
    contamination=0.02,
    random_state=42
)
```

Output:

- Total anomalies detected
- anomalies.csv

---

# 📁 Output Files

## Processed Data

- cleaned_data.csv
- anomalies.csv

## Reports

- sales_by_region.png
- profit_by_category.png

---

# ▶️ Installation

Clone the repository

```bash
git clone https://github.com/theshubham1508-alt/AI-Business-Anomaly-Detection.git
```

Move into project directory

```bash
cd AI-Business-Anomaly-Detection
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Project

```bash
python src/main.py
```

---

# 📌 Sample Output

```
Dataset Loaded Successfully

Rows : 9994

Columns : 21

Data Cleaning Completed Successfully

Graphs Saved Successfully

Total Anomalies Found : 200

Anomalies Saved Successfully
```

---

# 🚀 Future Improvements

- Interactive Dashboard using Streamlit
- Power BI Dashboard
- Real-Time Business Monitoring
- Model Comparison (LOF, One-Class SVM)
- Email Alert System
- Cloud Deployment

---

# 👨‍💻 Author

**Shubham**

B.Tech Computer Science Engineering

Interested in:

- Data Analytics
- Machine Learning
- Business Intelligence
- Data Science

---

# ⭐ If you found this project useful, consider giving it a Star.