import streamlit as st
import pandas as pd
import numpy as np
import os # أضفنا هذا الاستيراد للتعامل مع المسارات

# --- Page Configuration ---
st.set_page_config(
    page_title="محرك التسعير الديناميكي",
    page_icon="💲",
    layout="centered"
)

# --- App Title and Description ---
st.title('💲 محرك التسعير الديناميكي لتأجير السيارات')
st.write("يقترح هذا التطبيق السعر الأمثل لتأجير السيارات بناءً على الطلب المتوقع والمخزون المتاح وعوامل السوق.")
st.write("---")

# --- Load Optimal Prices Data ---
@st.cache_data # استخدام هذه لتخزين البيانات مؤقتًا لتحسين الأداء
def load_optimal_prices():
    # تأكد أن المسار صحيح لملف المخرجات الذي ينتجه الموديل
    file_path = 'data/pricing_results/optimal_prices.csv'
    if not os.path.exists(file_path):
        st.warning(f"⚠️ ملف بيانات الأسعار المثلى ({file_path}) غير موجود. الرجاء تشغيل بايب لاين الموديل أولاً.", icon="⚠️")
        return pd.DataFrame() # إرجاع DataFrame فارغ إذا لم يتم العثور على الملف
    try:
        df_prices = pd.read_csv(file_path)
        return df_prices
    except Exception as e:
        st.error(f"❌ خطأ في تحميل ملف الأسعار المثلى: {e}", icon="❌")
        return pd.DataFrame()

df_optimal_prices = load_optimal_prices()

if df_optimal_prices.empty:
    st.info("لا توجد بيانات أسعار مثلى حالياً لعرضها. يرجى الانتظار حتى يتم تشغيل الموديل وتحديث البيانات.", icon="ℹ️")
    st.stop() # إيقاف التطبيق هنا إذا لم تكن هناك بيانات


# --- User Input Section ---
st.subheader("توقع الطلب والمخزون")
col1, col2 = st.columns(2)

with col1:
    # سيتم استخدام هذه المدخلات لاحقًا لاختيار السعر من df_optimal_prices
    st.markdown("**الطلبات التالية ستحدد السعر من البيانات المحسوبة:**")
    car_category_input = st.selectbox('فئة السيارة', df_optimal_prices['car_category'].unique())
    rental_branch_input = st.selectbox('الفرع', df_optimal_prices['rental_branch'].unique())

with col2:
    day_of_week_input = st.selectbox('اليوم من الأسبوع', df_optimal_prices['day_of_week'].unique())
    st.write("*(عوامل أخرى مثل الطلب والمخزون يتم حسابها في الموديل)*") # إشارة إلى أن هذه العوامل ليست مباشرة هنا في UI للاختيار

st.subheader("السعر المقترح")
# --- Prediction Logic (now using loaded data) ---
if st.button("اقتراح السعر الأمثل", type="primary"):
    # تصفية بيانات الأسعار المثلى بناءً على اختيار المستخدم
    filtered_price_df = df_optimal_prices[
        (df_optimal_prices['car_category'] == car_category_input) &
        (df_optimal_prices['rental_branch'] == rental_branch_input) &
        (df_optimal_prices['day_of_week'] == day_of_week_input)
    ]

    if not filtered_price_df.empty:
        suggested_price = filtered_price_df['suggested_price'].iloc[0]
        st.success(f"السعر المقترح الأمثل: {suggested_price:.2f} ريال/يوم")
        st.write("*(هذا السعر مستخرج من البيانات التي حسبها موديل التسعير الديناميكي)*")
    else:
        st.warning("لم يتم العثور على سعر مقترح لهذه المجموعة من الخيارات. يرجى التحقق من بيانات الموديل.", icon="⚠️")

# Display a sample of the loaded data (for debugging/verification)
st.subheader("معاينة لبيانات الأسعار المثلى (للتأكد)")
st.dataframe(df_optimal_prices.head())

# ملاحظة عن التنبؤ غير الدقيق للموديلات (التي كانت في app.py القديم) لم تعد ضرورية هنا لأن هذا الجزء يخص التسعير
# ولابد من حذف أي جزء يخص الشك في الموديل لكي لا يؤثر علي الداش بورد
# ستتم معالجة تحديثات الداشبورد من الموديلات الأخرى في خطوات لاحقة

