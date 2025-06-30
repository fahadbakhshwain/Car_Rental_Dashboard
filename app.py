import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="لوحة تحكم حلول الذكاء الاصطناعي", layout="wide")

st.title("📊 لوحة تحكم حلول الذكاء الاصطناعي المتكاملة")

st.markdown("مرحباً بك في لوحة تحكم الذكاء الاصطناعي. 👇 اختر القسم لعرض نتائجه:")

# --- الأقسام ---
section = st.sidebar.selectbox("🧭 اختر القسم لعرضه:", [
    "الرؤية العامة للمؤشرات",
    "توقع الطلب",
    "توقع مغادرة العملاء",
    "تحليل المشاعر من التعليقات",
    "محرك التسعير الديناميكي"
])

# --- الرؤية العامة ---
if section == "الرؤية العامة للمؤشرات":
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي الإيرادات الشهرية", "1.2M ريال", "↑ 5%")
    col2.metric("معدل إشغال الأسطول", "85%", "↑ 2%")
    col3.metric("معدل مغادرة العملاء", "3.5%", "↓ 0.5% (تحسن)")
    col4.metric("رضا العملاء", "4.7/5", "↑ 0.1")

    st.subheader("🔎 نظرة عامة على أقسام الحلول الذكية:")
    st.markdown("""
    1. **توقع الطلب**: يعرض حالة الطقس والعوامل المؤثرة على تأجير السيارات.
    2. **مغادرة العملاء**: يظهر تحليل العملاء المتوقع مغادرتهم.
    3. **تحليل المشاعر**: يستعرض تعليقات العملاء وتحليل رضاهم.
    4. **محرك التسعير**: يقترح أسعار ديناميكية حسب الفروع والطلب.
    """)

# --- توقع الطلب ---
elif section == "توقع الطلب":
    st.subheader("🌤️ توقعات الطقس لتأثيرها على الطلب")

    try:
        df_weather = pd.read_csv("data/forecast_results/weather_forecast.csv")
        st.dataframe(df_weather)
    except Exception as e:
        st.error(f"تعذر تحميل ملف الطقس: {e}")

# --- مغادرة العملاء ---
elif section == "توقع مغادرة العملاء":
    st.subheader("👥 تحليل العملاء المتوقع مغادرتهم")

    try:
        df_churn = pd.read_csv("data/predictions/churn_predictions.csv")
        st.write("عرض كامل للبيانات:")
        st.dataframe(df_churn)

        if 'will_churn' in df_churn.columns:
            churned = df_churn[df_churn['will_churn'] == 1]
            st.subheader("العملاء المتوقع مغادرتهم:")
            st.dataframe(churned)
        else:
            st.warning("⚠️ العمود 'will_churn' غير موجود في البيانات.")
    except Exception as e:
        st.error(f"تعذر تحميل ملف مغادرة العملاء: {e}")

# --- تحليل المشاعر ---
elif section == "تحليل المشاعر من التعليقات":
    st.subheader("💬 تحليل مشاعر العملاء من التعليقات")

    try:
        df_sentiment = pd.read_csv("data/sentiment_results/sentiment_analysis_results.csv")
        st.dataframe(df_sentiment)
    except Exception as e:
        st.error(f"تعذر تحميل ملف تحليل المشاعر: {e}")

# --- محرك التسعير ---
elif section == "محرك التسعير الديناميكي":
    st.subheader("💲 محرك التسعير الديناميكي لتأجير السيارات")

    try:
        df_prices = pd.read_csv("data/pricing_results/optimal_prices.csv")

        col1, col2 = st.columns(2)
        with col1:
            car_category = st.selectbox("فئة السيارة", df_prices['car_category'].unique())
            branch = st.selectbox("الفرع", df_prices['rental_branch'].unique())
        with col2:
            day = st.selectbox("اليوم", df_prices['day_of_week'].unique())

        st.markdown("اضغط الزر أدناه للحصول على السعر المقترح:")
        if st.button("🎯 اقتراح السعر الأمثل"):
            result = df_prices[
                (df_prices['car_category'] == car_category) &
                (df_prices['rental_branch'] == branch) &
                (df_prices['day_of_week'] == day)
            ]
            if not result.empty:
                price = result['suggested_price'].iloc[0]
                st.success(f"💰 السعر المقترح هو: {price:.2f} ريال/يوم")
            else:
                st.warning("⚠️ لم يتم العثور على نتيجة لهذه الاختيارات.")

        st.dataframe(df_prices.head())
    except Exception as e:
        st.error(f"تعذر تحميل ملف الأسعار: {e}")


