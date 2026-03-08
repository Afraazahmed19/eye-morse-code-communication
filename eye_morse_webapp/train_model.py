# train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
import math
import numpy as np

CSV = 'blink_data.csv'
MODEL_OUT_DIR = 'models'
MODEL_OUT = os.path.join(MODEL_OUT_DIR, 'blink_classifier.pkl')
SCALER_OUT = os.path.join(MODEL_OUT_DIR, 'scaler.pkl')
os.makedirs(MODEL_OUT_DIR, exist_ok=True)

# Load CSV
if not os.path.exists(CSV):
    raise FileNotFoundError(f"Training data file '{CSV}' not found. Please run recorder.py first to collect data.")

df = pd.read_csv(CSV)

# ---- Fix common issues ----
# Drop any empty rows
df = df.dropna(how='any')

# Remove duplicate header rows (if accidentally recorded again)
df = df[df['duration'] != 'duration']  # Remove header rows

# Convert numeric columns to float safely
for col in ['duration', 'avg_ear', 'min_ear', 'time_gap']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Drop any rows that still have NaN values after conversion
df = df.dropna(subset=['duration', 'avg_ear', 'min_ear', 'time_gap', 'label'])

# Remove invalid labels
valid_labels = ['dot', 'dash', 'morse_backspace', 'letter_backspace', 'space', 'enter']
df = df[df['label'].isin(valid_labels)]

# Add engineered features for better accuracy
df['ear_range'] = df['avg_ear'] - df['min_ear']  # Range of EAR during blink
df['duration_normalized'] = df['duration'] / (df['duration'].max() + 1e-6)  # Normalized duration
df['blink_intensity'] = df['min_ear'] / (df['avg_ear'] + 1e-6)  # Intensity of blink

print(f"\n📊 Dataset Statistics:")
print(f"Total samples: {len(df)}")
print(f"Labels distribution:")
print(df['label'].value_counts())

# Define features and labels
feature_cols = ['duration', 'avg_ear', 'min_ear', 'time_gap', 'ear_range', 'duration_normalized', 'blink_intensity']
X = df[feature_cols]
y = df['label']

# Robust train/test split for small datasets:
n_samples = len(df)
n_classes = y.nunique()

if n_samples < n_classes * 3:
    print(f"⚠️ Warning: Very small dataset ({n_samples} samples, {n_classes} classes)")
    print("Recommended: Collect at least 30-50 samples per class for better accuracy")

if n_samples < 2:
    raise RuntimeError(f"Not enough samples to train (found {n_samples})")

desired_frac = 0.25
desired_test = max(1, int(math.ceil(n_samples * desired_frac)))
desired_test = min(desired_test, n_samples - 1)

if desired_test < n_classes:
    print(f"Warning: too few samples for stratified split. Falling back to non-stratified split.")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=desired_test, random_state=42, stratify=None
    )
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=desired_test, random_state=42, stratify=y
    )

# Scale features for better performance
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train multiple models and choose the best
print("\n🔄 Training models...")

# Model 1: Random Forest
rf_clf = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    class_weight='balanced'  # Handle class imbalance
)
rf_clf.fit(X_train_scaled, y_train)
rf_preds = rf_clf.predict(X_test_scaled)
rf_accuracy = accuracy_score(y_test, rf_preds)

# Model 2: Gradient Boosting
gb_clf = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
gb_clf.fit(X_train_scaled, y_train)
gb_preds = gb_clf.predict(X_test_scaled)
gb_accuracy = accuracy_score(y_test, gb_preds)

# Choose best model
if rf_accuracy >= gb_accuracy:
    clf = rf_clf
    model_type = "Random Forest"
    print(f"✅ Selected Random Forest (Accuracy: {rf_accuracy:.3f})")
else:
    clf = gb_clf
    model_type = "Gradient Boosting"
    print(f"✅ Selected Gradient Boosting (Accuracy: {gb_accuracy:.3f})")

# Cross-validation score
cv_scores = cross_val_score(clf, X_train_scaled, y_train, cv=min(5, len(X_train)//n_classes), scoring='accuracy')
print(f"📈 Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

# Evaluate on test set
preds = clf.predict(X_test_scaled)
accuracy = accuracy_score(y_test, preds)

print("\n" + "="*60)
print("📋 Classification Report:")
print("="*60)
print(classification_report(y_test, preds, zero_division=0))

print("\n📊 Confusion Matrix:")
print(confusion_matrix(y_test, preds))

print(f"\n🎯 Test Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")

# Feature importance
if hasattr(clf, 'feature_importances_'):
    print("\n🔍 Feature Importance:")
    importances = clf.feature_importances_
    indices = np.argsort(importances)[::-1]
    for i in range(len(feature_cols)):
        print(f"  {feature_cols[indices[i]]}: {importances[indices[i]]:.3f}")

# Save model and scaler
joblib.dump(clf, MODEL_OUT)
joblib.dump(scaler, SCALER_OUT)
print(f"\n✅ Model saved to {MODEL_OUT}")
print(f"✅ Scaler saved to {SCALER_OUT}")
print(f"\n💡 Tip: To improve accuracy, collect more training data with recorder.py")
print(f"   Aim for at least 30-50 samples per class (dot, dash, morse_backspace, etc.)")
