import pandas as pd
import numpy as np
import joblib
import os # أضفنا هذا الاستيراد للتعامل مع المسارات
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE

def run_churn_pipeline():
    print("--- Starting Churn Model Pipeline ---")

    # Define paths
    file_path = 'data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv'
    model_save_path = 'models/churn_classifier_model.joblib'
    
    # تعريف مسار ملف التنبؤات الناتج
    predictions_output_dir = "data/predictions"
    predictions_output_file = os.path.join(predictions_output_dir, "churn_predictions.csv")
    
    # التأكد من وجود مجلد المخرجات
    os.makedirs(predictions_output_dir, exist_ok=True)


    # --- Step 1: Load the Dataset ---
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Dataset loaded successfully from {file_path}! Shape: {df.shape}")
    except FileNotFoundError:
        print(f"❌ Error: Dataset not found at {file_path}. Please ensure the file is in the correct path.")
        return # Stop execution if file not found

    # --- Step 2: Handle Missing Values and Data Types ---
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['TotalCharges'].fillna(0, inplace=True)
    df_processed = df.drop('customerID', axis=1)
    df_processed['Churn'] = df_processed['Churn'].apply(lambda x: 1 if x == 'Yes' else 0)
    categorical_cols = df_processed.select_dtypes(include='object').columns
    df_processed = pd.get_dummies(df_processed, columns=categorical_cols, drop_first=True)
    print(f"✅ Data preprocessing completed. New shape: {df_processed.shape}")

    # --- Step 3: Separate Features (X) and Target (y) ---
    X = df_processed.drop('Churn', axis=1)
    y = df_processed['Churn']
    print("✅ Features and Target separated.")

    # --- Step 4: Split Data into Training and Testing Sets ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"✅ Data split into training ({X_train.shape[0]} samples) and testing ({X_test.shape[0]} samples).")

    # --- Step 5: Handle Class Imbalance using SMOTE ---
    print("Applying SMOTE to balance training data...")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"✅ Training data resampled.")

    # --- Step 6: Train the Random Forest Classifier ---
    print("Training the Random Forest Classifier on resampled data...")
    rf_smote_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
    rf_smote_model.fit(X_train_resampled, y_train_resampled)
    print("✅ Model trained successfully!")

    # --- Step 7: Save the Trained Model ---
    joblib.dump(rf_smote_model, model_save_path)
    print(f"✅ Churn model saved successfully to {model_save_path}!")

    # --- Step 8: Make Predictions and Save Results to CSV ---
    print(f"Making predictions on test data and saving to {predictions_output_file}...")
    y_pred = rf_smote_model.predict(X_test)
    y_proba = rf_smote_model.predict_proba(X_test)[:, 1] # احتمالية الخروج

    # إنشاء DataFrame لنتائج التنبؤات
    results_df = X_test.copy()
    results_df['Actual_Churn'] = y_test
    results_df['Predicted_Churn'] = y_pred
    results_df['Churn_Probability'] = y_proba
    
    # إضافة عمود 'Risk_Category' بناءً على احتمالية الخروج
    # يمكنك تعديل هذه العتبات بناءً على تحليلك للموديل
    def get_risk_category(prob):
        if prob >= 0.7:
            return "High Risk (Action Needed)"
        elif prob >= 0.4:
            return "Medium Risk (Monitor)"
        else:
            return "Low Risk (Stable)"
            
    results_df['Risk_Category'] = results_df['Churn_Probability'].apply(get_risk_category)

    # حفظ النتائج في ملف CSV
    results_df.to_csv(predictions_output_file, index=False)
    print(f"✅ Churn predictions saved successfully to {predictions_output_file}!")


    print("--- Churn Model Pipeline Completed ---")

if __name__ == "__main__":
    run_churn_pipeline()