import pandas as pd
import joblib
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import json
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np # لإدارة الاحتماليات بشكل أفضل

# --- تنزيل بيانات NLTK الضرورية (لبيئة GitHub Actions) ---
# سيتم تشغيلها في بيئة GitHub Actions
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    print("Downloading NLTK data for NLP pipeline...")
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    print("Done downloading NLTK data.")

# --- تعريف دالة معالجة النصوص (مطابقة لما في مشروع NLP الأصلي) ---
lemmatizer = WordNetLemmatizer()
# تأكد أن هذه الكلمات المتوقفة تتناسب مع لغة مراجعاتك (إنجليزية/عربية)
stop_words_set = set(stopwords.words('english')) 

def preprocess_text(text):
    # تحويل النص إلى حروف صغيرة
    text = text.lower()
    # إزالة علامات الترقيم والأرقام والأحرف غير الأبجدية
    # ملاحظة: إذا كانت المراجعات باللغة العربية، فهذا السطر يحتاج تعديل ليسمح بالحروف العربية
    text = re.sub(r'[^a-z\s]', '', text) 
    # تقسيم النص إلى كلمات
    tokens = text.split()
    # إزالة الكلمات المتوقفة
    tokens = [word for word in tokens if word not in stop_words_set]
    # Lemmatization
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    # دمج الكلمات مرة أخرى
    cleaned_text = ' '.join(tokens)
    return cleaned_text

# تعريف مسار ملف المراجعات الوهمية (المصدر الذي سنقرأ منه)
REVIEWS_FILE_PATH = 'data/customer_reviews_sample.csv'

# --- الدالة الرئيسية للبايبلاين ---
def run_nlp_pipeline():
    """
    هذه الدالة الرئيسية لخط أنابيب تحليل المراجعات الآلي.
    تقرأ المراجعات من ملف CSV، تنظفها، تحللها باستخدام موديل NLP،
    وتخزن النتائج في Firestore.
    """
    print("--- [START] NLP Reviews Pipeline ---")

    # --- 1. تهيئة اتصال Firebase ---
    try:
        # نحصل على بيانات الاعتماد من متغير بيئة (Environment Variable) يتم تعيينه بواسطة GitHub Actions.
        # تأكد من أن السر FIREBASE_KEY_JSON موجود في GitHub Secrets
        key_json_str = os.environ.get("FIREBASE_KEY_JSON")
        if not key_json_str:
            raise ValueError("FIREBASE_KEY_JSON environment variable not set. Cannot connect to Firebase.")
        
        key_dict = json.loads(key_json_str)
        cred = credentials.Certificate(key_dict)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ [1/5] تم الاتصال بـ Firestore بنجاح.")
    except Exception as e:
        print(f"❌ [خطأ] لم يتم الاتصال بـ Firebase: {e}")
        return

    # --- 2. تحميل موديل تحليل المشاعر و Vectorizer ---
    # هذه الموديلات يجب أن تكون موجودة في مجلد 'models' في جذر مشروع Car_Rental_Dashboard
    try:
        vectorizer_path = 'models/tfidf_vectorizer.joblib'
        sentiment_model_path = 'models/sentiment_classifier_model.joblib'

        if not os.path.exists(vectorizer_path):
            raise FileNotFoundError(f"Vectorizer model not found at {vectorizer_path}")
        if not os.path.exists(sentiment_model_path):
            raise FileNotFoundError(f"Sentiment model not found at {sentiment_model_path}")

        vectorizer = joblib.load(vectorizer_path)
        sentiment_model = joblib.load(sentiment_model_path)
        print("✅ [2/5] تم تحميل موديل NLP و Vectorizer بنجاح.")
    except Exception as e:
        print(f"❌ [خطأ] لم يتم تحميل موديل NLP أو Vectorizer: {e}")
        return

    # --- 3. قراءة المراجعات من ملف CSV ---
    try:
        if not os.path.exists(REVIEWS_FILE_PATH):
            raise FileNotFoundError(f"Reviews file '{REVIEWS_FILE_PATH}' not found. Please create it.")
        
        reviews_df = pd.read_csv(REVIEWS_FILE_PATH)
        print("✅ [3/5] تم قراءة المراجعات من ملف CSV بنجاح.")
    except Exception as e:
        print(f"❌ [خطأ] لم يتم قراءة ملف المراجعات CSV: {e}")
        return

    # --- 4. معالجة وتحليل المراجعات ---
    print("✅ [4/5] بدء معالجة وتحليل المراجعات...")
    
    # تطبيق دالة المعالجة المسبقة
    reviews_df['cleaned_review'] = reviews_df['review_text'].apply(preprocess_text)
    
    # تحويل النصوص المعالجة إلى ميزات رقمية
    # يجب أن تكون أعمدة الميزات مطابقة لما تدرب عليه الموديل
    vectorized_reviews = vectorizer.transform(reviews_df['cleaned_review'])
    
    # إجراء التنبؤ بالمشاعر
    predictions = sentiment_model.predict(vectorized_reviews)
    probabilities = sentiment_model.predict_proba(vectorized_reviews)
    
    sentiment_labels = ['سلبية', 'محايدة', 'إيجابية'] # يجب أن تتطابق مع ترتيب الفئات في بياناتك
    reviews_df['predicted_sentiment'] = [sentiment_labels[p] for p in predictions]
    reviews_df['sentiment_proba_negative'] = np.round(probabilities[:, 0], 4)
    reviews_df['sentiment_proba_neutral'] = np.round(probabilities[:, 1], 4)
    reviews_df['sentiment_proba_positive'] = np.round(probabilities[:, 2], 4)

    # --- 5. تخزين النتائج في Firestore ---
    print("✅ [5/5] بدء تخزين النتائج في Firestore...")
    collection_name = "customer_reviews_analysis"
    
    # حفظ كل تحليل مراجعة كمستند منفصل
    for index, row in reviews_df.iterrows():
        doc_id = f"review_{row['review_id']}" # استخدام review_id كمعرف للمستند
        data_to_save = {
            'review_id': row['review_id'],
            'review_text': row['review_text'],
            'rating': int(row['rating']), # تحويل التقييم إلى عدد صحيح
            'source': row['source'],
            'predicted_sentiment': row['predicted_sentiment'],
            'sentiment_proba_positive': float(row['sentiment_proba_positive']),
            'sentiment_proba_negative': float(row['sentiment_proba_negative']),
            'sentiment_proba_neutral': float(row['sentiment_proba_neutral']),
            'analysis_run_at': datetime.datetime.now()
        }
        db.collection(collection_name).document(doc_id).set(data_to_save)
        time.sleep(0.05) # لإعطاء Firestore وقتًا لمعالجة الطلبات
    
    print("\n--- [نجاح] انتهى عمل خط أنابيب تحليل المراجعات ---")
    print(f"راجع مجموعة '{collection_name}' في لوحة تحكم Firebase Console.")


# هذا السطر يجعل السكريبت قابلاً للتشغيل من سطر الأوامر
if __name__ == "__main__":
    run_nlp_pipeline()

