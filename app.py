import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# --- Page Configuration ---
st.set_page_config(
    page_title="لوحة تحكم الذكاء الاصطناعي المتكاملة لتأجير السيارات", # تم تحديث العنوان
    page_icon="🧠",
    layout="wide" # استخدام layout "wide" للاستفادة من المساحة للرسوم البيانية
)

# --- Sidebar Navigation ---
st.sidebar.title("قائمة حلول الذكاء الاصطناعي")
section = st.sidebar.selectbox(
    "🧭 الرجاء اختيار قسم لوحة التحكم",
    [
        "لوحة البيانات العامة للمديرين",
        "توقع الطلب",
        "محرك التسعير الديناميكي",
        "تحليل رضا العملاء والمشاعر",
        "توقع مغادرة العملاء"
    ]
)

# ---------- Loaders ----------
@st.cache_data # استخدام هذه لتخزين البيانات مؤقتًا لتحسين الأداء
def load_csv(path):
    if not os.path.exists(path):
        st.warning(f"⚠️ ملف البيانات غير موجود: {path}", icon="⚠️")
        return pd.DataFrame() # إرجاع DataFrame فارغ إذا لم يتم العثور على الملف
    try:
        df = pd.read_csv(path)
        # محاولة تحويل عمود التاريخ إذا كان موجودًا
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                st.warning(f"تحذير: لا يمكن تحويل عمود 'timestamp' إلى تاريخ: {e}")
        return df
    except Exception as e:
        st.error(f"❌ خطأ في تحميل ملف البيانات من {path}: {e}", icon="❌")
        return pd.DataFrame()

# Set plot style
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 10, 'axes.labelsize': 10, 'xtick.labelsize': 8, 'ytick.labelsize': 8})


# ------------------------------------------------
# قسم 1 - لوحة المدير العامة (إضافة رسوم بيانية ملخصة إذا توفرت البيانات)
# ------------------------------------------------
if section == "لوحة البيانات العامة للمديرين":
    st.title("📊 لوحة تحكم حلول الذكاء الاصطناعي المتكاملة")
    st.markdown("مرحبًا بك في لوحة تحكم الذكاء الاصطناعي المتكاملة لتأجير السيارات.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي الإيرادات التقديرية", "1.2M ريال", "↑ 5% عن الشهر الماضي")
    col2.metric("معدل إشغال الأسطول", "85%", "↑ 2% عن الأسبوع الماضي")
    col3.metric("معدل مغادرة العملاء", "3.5%", "↓ -0.5% (تحسن)")
    col4.metric("متوسط رضا العملاء", "4.7/5", "↑ 0.1")

    st.markdown("### نظرة عامة على أقسام الحلول الذكية:")
    st.markdown("""
    1. **قسم "توقع الطلب"**: يعرض التوقعات اليومية للطقس ومدى تأثيرها على الطلب.
    2. **قسم "محرك التسعير الديناميكي"**: يقترح أسعار مثالية حسب الفروع والأيام.
    3. **قسم "تحليل المشاعر"**: يستعرض نتائج تحليل تعليقات العملاء (إيجابية/سلبية).
    4. **قسم "توقع مغادرة العملاء"**: يعرض العملاء المتوقع مغادرتهم قريبًا.
    """)

    # --- رسوم بيانية ملخصة عامة (أمثلة - تحتاج لبيانات مجمعة حقيقية) ---
    st.subheader("ملخص أداء الموديلات (أمثلة مرئية)")
    
    # تحميل بعض البيانات للملخص (للتجربة، يمكن تحسينها لاحقا ببيانات مجمعة)
    df_churn_pred = load_csv("data/predictions/churn_predictions.csv")
    df_sentiment_res = load_csv("data/sentiment_results/sentiment_analysis_results.csv")
    
    # توزيع توقعات مغادرة العملاء
    if not df_churn_pred.empty and 'Predicted_Churn' in df_churn_pred.columns:
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        sns.countplot(x='Predicted_Churn', data=df_churn_pred, ax=ax1, palette='viridis')
        ax1.set_title('توزيع توقعات مغادرة العملاء')
        ax1.set_xlabel('توقع المغادرة')
        ax1.set_ylabel('عدد العملاء')
        ax1.set_xticklabels(['مستقر', 'مغادر متوقع'])
        st.pyplot(fig1)
        plt.close(fig1)
    
    # توزيع مشاعر العملاء
    if not df_sentiment_res.empty and 'sentiment' in df_sentiment_res.columns:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.countplot(x='sentiment', data=df_sentiment_res, ax=ax2, palette='coolwarm')
        ax2.set_title('توزيع مشاعر العملاء')
        ax2.set_xlabel('المشاعر')
        ax2.set_ylabel('عدد التعليقات')
        st.pyplot(fig2)
        plt.close(fig2)


# ------------------------------------------------
# قسم 2 - توقع الطلب (الطقس)
# ------------------------------------------------
elif section == "توقع الطلب":
    st.header("🌤️ توقعات الطقس وتأثيرها على الطلب")

    df_weather = load_csv("data/forecast_results/weather_forecast.csv")

    if df_weather.empty:
        st.warning("لم يتم العثور على بيانات الطقس.")
    else:
        st.dataframe(df_weather)
        latest = df_weather.iloc[-1]
        st.success(f"""آخر تحديث:
        - الموقع: **{latest['location']}**
        - التاريخ: **{latest['timestamp']}**
        - درجة الحرارة: **{latest['temperature_celsius']}°C**
        - الحالة: **{latest['condition']}**
        """)
        
        st.subheader("رسم بياني: درجات الحرارة المتوقعة")
        fig, ax = plt.subplots(figsize=(10, 5))
        # استخدام df_weather['timestamp'] مباشرة من DataFrame (يجب أن يكون قابلاً للتحويل إلى datetime في Pandas)
        ax.plot(df_weather['timestamp'], df_weather['temperature_celsius'], marker='o', linestyle='-', color='skyblue')
        ax.set_title('توقع درجات الحرارة عبر الوقت')
        ax.set_xlabel('التاريخ والوقت')
        ax.set_ylabel('درجة الحرارة (°C)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)


# ------------------------------------------------
# قسم 3 - التسعير الديناميكي
# ------------------------------------------------
elif section == "محرك التسعير الديناميكي":
    st.header("💲 محرك التسعير الديناميكي لتأجير السيارات")
    df_optimal = load_csv("data/pricing_results/optimal_prices.csv")

    if df_optimal.empty:
        st.warning("لا توجد بيانات أسعار مثلى حالياً.")
        st.stop() # إيقاف التطبيق هنا إذا لم تكن هناك بيانات

    col1, col2 = st.columns(2)
    with col1:
        car_category = st.selectbox("فئة السيارة", df_optimal['car_category'].unique())
        branch = st.selectbox("الفرع", df_optimal['rental_branch'].unique())
    with col2:
        day = st.selectbox("اليوم من الأسبوع", df_optimal['day_of_week'].unique()) # تصحيح اسم العمود هنا

    if st.button("اقتراح السعر الأمثل"):
        filt = df_optimal[
            (df_optimal['car_category'] == car_category) &
            (df_optimal['rental_branch'] == branch) &
            (df_optimal['day_of_week'] == day)
        ]
        if not filt.empty:
            suggested_price = filt['suggested_price'].iloc[0]
            st.success(f"السعر المقترح الأمثل: {suggested_price:.2f} ريال/يوم")
            st.write("*(هذا السعر مستخرج من البيانات التي حسبها موديل التسعير الديناميكي)*")
        else:
            st.warning("لم يتم العثور على سعر مقترح لهذه المجموعة من الخيارات. يرجى التحقق من بيانات الموديل.", icon="⚠️")

    st.subheader("رسم بياني: متوسط الأسعار المقترحة")
    
    # متوسط السعر حسب فئة السيارة
    fig_cat, ax_cat = plt.subplots(figsize=(10, 5))
    sns.barplot(x='car_category', y='suggested_price', data=df_optimal, ax=ax_cat, estimator=np.mean, palette='Blues')
    ax_cat.set_title('متوسط السعر المقترح حسب فئة السيارة')
    ax_cat.set_xlabel('فئة السيارة')
    ax_cat.set_ylabel('متوسط السعر المقترح')
    st.pyplot(fig_cat)
    plt.close(fig_cat)

    # متوسط السعر حسب اليوم
    fig_day, ax_day = plt.subplots(figsize=(10, 5))
    sns.barplot(x='day_of_week', y='suggested_price', data=df_optimal, ax=ax_day, estimator=np.mean, palette='Greens')
    ax_day.set_title('متوسط السعر المقترح حسب اليوم من الأسبوع')
    ax_day.set_xlabel('اليوم من الأسبوع')
    ax_day.set_ylabel('متوسط السعر المقترح')
    st.pyplot(fig_day)
    plt.close(fig_day)


# ------------------------------------------------
# قسم 4 - تحليل المشاعر
# ------------------------------------------------
elif section == "تحليل رضا العملاء والمشاعر":
    st.header("🗣️ تحليل مشاعر العملاء من التعليقات")
    df_sentiment = load_csv("data/sentiment_results/sentiment_analysis_results.csv")

    if df_sentiment.empty:
        st.warning("لا توجد بيانات تحليل مشاعر حالياً.")
    else:
        st.dataframe(df_sentiment.head(20)) # عرض أول 20 تعليق
        
        st.subheader("رسم بياني: توزيع المشاعر")
        fig_sent, ax_sent = plt.subplots(figsize=(8, 6))
        sentiment_counts = df_sentiment['sentiment'].value_counts()
        ax_sent.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
        ax_sent.set_title('توزيع المشاعر العامة')
        st.pyplot(fig_sent)
        plt.close(fig_sent)
        
        st.subheader("رسم بياني: توزيع درجات المشاعر")
        fig_score, ax_score = plt.subplots(figsize=(10, 5))
        sns.histplot(df_sentiment['sentiment_score'], kde=True, ax=ax_score, color='purple')
        ax_score.set_title('توزيع درجات المشاعر')
        ax_score.set_xlabel('درجة المشاعر (-1 سلبي جداً إلى 1 إيجابي جداً)')
        ax_score.set_ylabel('العدد')
        st.pyplot(fig_score)
        plt.close(fig_score)


# ------------------------------------------------
# قسم 5 - توقع مغادرة العملاء
# ------------------------------------------------
elif section == "توقع مغادرة العملاء":
    st.header("🚪 العملاء المتوقع مغادرتهم")
    df_churn = load_csv("data/predictions/churn_predictions.csv")

    if df_churn.empty:
        st.warning("لا توجد بيانات حالياً عن مغادرة العملاء.")
    else:
        st.dataframe(df_churn.head(10)) # عرض أول 10 عملاء
        
        # تصحيح الخطأ هنا من 'will_churn' إلى 'Predicted_Churn'
        churned_customers = df_churn[df_churn['Predicted_Churn'] == 1]
        st.info(f"📌 عدد العملاء المتوقع مغادرتهم: **{len(churned_customers)}**")

        st.subheader("رسم بياني: توقعات المغادرة")
        fig_churn_pred, ax_churn_pred = plt.subplots(figsize=(8, 6))
        churn_counts = df_churn['Predicted_Churn'].value_counts()
        ax_churn_pred.pie(churn_counts, labels=['مستقر', 'مغادر متوقع'], autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'salmon'])
        ax_churn_pred.set_title('توزيع العملاء حسب توقع المغادرة')
        st.pyplot(fig_churn_pred)
        plt.close(fig_churn_pred)
        
        st.subheader("رسم بياني: توزيع العملاء حسب فئة المخاطرة")
        if 'Risk_Category' in df_churn.columns:
            fig_risk, ax_risk = plt.subplots(figsize=(10, 6))
            sns.countplot(x='Risk_Category', data=df_churn, ax=ax_risk, order=['Low Risk (Stable)', 'Medium Risk (Monitor)', 'High Risk (Action Needed)'], palette='coolwarm')
            ax_risk.set_title('توزيع العملاء حسب فئة المخاطرة')
            ax_risk.set_xlabel('فئة المخاطرة')
            ax_risk.set_ylabel('العدد')
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig_risk)
            plt.close(fig_risk)
        else:
            st.warning("عمود 'فئة المخاطرة' غير موجود في بيانات توقعات المغادرة.")














