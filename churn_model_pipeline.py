import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE # للتأكد من تثبيتها: pip install imbalanced-learn

def run_churn_pipeline():
    print("--- Starting Churn Model Pipeline ---")

    # --- Step 1: Load the Dataset ---
    file_path = 'data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv'
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Dataset loaded successfully from {file_path}! Shape: {df.shape}")
    except FileNotFoundError:
        print(f"❌ Error: Dataset not found at {file_path}. Please ensure the file is in the correct path.")
        return # Stop execution if file not found

    # --- Step 2: Handle Missing Values and Data Types ---
    # Convert 'TotalCharges' to numeric, coercing errors to NaN
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    # Fill missing 'TotalCharges' with 0 (for new customers with tenure=0)
    df['TotalCharges'].fillna(0, inplace=True)
    print("✅ TotalCharges handled.")

    # Drop customerID as it's just an identifier
    df_processed = df.drop('customerID', axis=1)
    print("✅ customerID dropped.")

    # --- Step 3: Convert Categorical Features to Numerical (One-Hot Encoding) ---
    # Convert 'Churn' target variable to numerical (Yes=1, No=0)
    df_processed['Churn'] = df_processed['Churn'].apply(lambda x: 1 if x == 'Yes' else 0)
    
    # Apply one-hot encoding to all other categorical columns
    categorical_cols = df_processed.select_dtypes(include='object').columns
    df_processed = pd.get_dummies(df_processed, columns=categorical_cols, drop_first=True)
    print(f"✅ Categorical features encoded. New shape: {df_processed.shape}")

    # --- Step 4: Separate Features (X) and Target (y) ---
    X = df_processed.drop('Churn', axis=1)
    y = df_processed['Churn']
    print("✅ Features and Target separated.")

    # --- Step 5: Split Data into Training and Testing Sets ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"✅ Data split into training ({X_train.shape[0]} samples) and testing ({X_test.shape[0]} samples).")

    # --- Step 6: Handle Class Imbalance using SMOTE (Recommended for Churn) ---
    print("Applying SMOTE to balance training data...")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"✅ Training data resampled. Original Churn distribution: {y_train.value_counts().tolist()}")
    print(f"   Resampled Churn distribution: {y_train_resampled.value_counts().tolist()}")

    # --- Step 7: Train the Random Forest Classifier ---
    print("Training the Random Forest Classifier on resampled data...")
    rf_smote_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced') # يمكن استخدام class_weight هنا أيضاً
    rf_smote_model.fit(X_train_resampled, y_train_resampled)
    print("✅ Model trained successfully!")

    # --- Step 8: Evaluate the Model (Optional in Pipeline, mainly for reports) ---
    y_pred = rf_smote_model.predict(X_test)
    print("\n--- Model Performance Report ---")
    print(classification_report(y_test, y_pred, target_names=['Did Not Churn', 'Churned']))
    print("✅ Model evaluated.")

    # --- Step 9: Save the Trained Model ---
    model_save_path = 'models/churn_classifier_model.joblib'
    joblib.dump(rf_smote_model, model_save_path)
    print(f"✅ Churn model saved successfully to {model_save_path}!")

    print("--- Churn Model Pipeline Completed ---")

if __name__ == "__main__":
    run_churn_pipeline()