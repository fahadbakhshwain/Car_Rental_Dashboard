# 🚗 Car Rental AI Dashboard

A smart, multi-page Streamlit dashboard that empowers car rental companies to make proactive, data-driven decisions using predictive models and real-time insights.

## 🔍 Overview

This project simulates a real-world **Business Intelligence Command Center** for a car rental company. It integrates four machine learning models into a centralized dashboard that supports strategic decisions across demand forecasting, customer retention, pricing optimization, and sentiment analysis.

---

## 🧠 Dashboard Modules

### 1. 🔮 Demand Forecasting
- Predicts how many cars will be needed at each hour and location.
- Input variables: Hour of day, weather conditions, seasonality.
- **Business Value:** Optimizes fleet distribution and reduces customer loss due to unavailability.

### 2. ⚠️ Customer Churn Prediction
- Predicts whether a customer is likely to leave based on tenure, contract type, and other features.
- **Business Value:** Enables early intervention and personalized offers to improve loyalty.

### 3. 💬 Sentiment Analysis
- Analyzes customer reviews to detect dominant sentiment and topics (e.g., cleanliness, speed).
- **Business Value:** Helps management react faster to service issues and improve brand perception.

### 4. 💰 Dynamic Pricing Engine
- Suggests real-time car rental prices based on day, hour, demand, and competition level.
- **Business Value:** Increases revenue during peak hours and improves occupancy during slow times.

---

## 📊 Tools & Technologies

- **Language:** Python
- **Framework:** Streamlit (multi-page setup)
- **Models:** Logistic Regression, Decision Trees, Sentiment Analysis (TF-IDF + ML), Regression
- **Visualization:** Matplotlib, Seaborn
- **Data:** Synthetic business-like datasets (fleet usage, customer reviews, pricing history)

---

## 🏁 Getting Started

To run the app locally:

```bash
git clone https://github.com/fahadbakhshwain/Car_Rental_Dashboard.git
cd Car_Rental_Dashboard
pip install -r requirements.txt
streamlit run Home.py
