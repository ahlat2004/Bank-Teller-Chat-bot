"""
Bank Teller Chatbot - WP3 Training Script for Google Colab
This script handles:
1. Dataset upload/loading
2. Model training
3. Artifact saving
4. Download preparation

Instructions for Colab:
1. Upload this script to Colab
2. Upload data/processed/ folder contents (train.csv, val.csv, test.csv)
3. Upload data/intent_mapping.json
4. Run all cells
5. Download the generated models/ folder
"""

import os
import sys
import json
import pickle
import pandas as pd
import numpy as np
import time
from google.colab import files
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    f1_score,
    precision_score,
    recall_score,
    accuracy_score
)
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 80)
print(" " * 20 + "BANK TELLER CHATBOT - WP3 TRAINING")
print(" " * 15 + "Google Colab Training Environment")
print("=" * 80)

# ============================================================================
# STEP 1: SETUP AND UPLOAD DATA
# ============================================================================
print("\n📂 STEP 1: Setting up directories...")

# Create working directories
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/models', exist_ok=True)

print("✅ Directories created")

print("\n📥 STEP 1B: Upload training data files")
print("   Please upload:")
print("   - train.csv")
print("   - val.csv")
print("   - test.csv")
print("   - intent_mapping.json")
print("\n   Running: files.upload()")

uploaded = files.upload()
print(f"✅ Uploaded {len(uploaded)} files")

# ============================================================================
# STEP 2: LOAD DATA AND INTENT MAPPING
# ============================================================================
print("\n📋 STEP 2: Loading data...")

try:
    train_df = pd.read_csv('train.csv')
    val_df = pd.read_csv('val.csv')
    test_df = pd.read_csv('test.csv')
    
    with open('intent_mapping.json', 'r') as f:
        intent_mapping = json.load(f)
    
    print(f"✅ Training samples:   {len(train_df)}")
    print(f"✅ Validation samples: {len(val_df)}")
    print(f"✅ Test samples:       {len(test_df)}")
    print(f"✅ Intent categories:  {intent_mapping['num_intents']}")
    
except Exception as e:
    print(f"❌ Error loading data: {e}")
    raise

# ============================================================================
# STEP 3: BUILD TF-IDF VECTORIZER
# ============================================================================
print("\n🔢 STEP 3: Building TF-IDF Vectorizer...")

vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.8,
    sublinear_tf=True
)

vectorizer.fit(train_df['cleaned_text'])
print(f"✅ Vectorizer fitted")
print(f"   Vocabulary size: {len(vectorizer.vocabulary_)}")

# ============================================================================
# STEP 4: PREPARE FEATURES
# ============================================================================
print("\n🔄 STEP 4: Preparing features...")

X_train = vectorizer.transform(train_df['cleaned_text']).toarray()
X_val = vectorizer.transform(val_df['cleaned_text']).toarray()
X_test = vectorizer.transform(test_df['cleaned_text']).toarray()

label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(train_df['intent'])
y_val_encoded = label_encoder.transform(val_df['intent'])
y_test_encoded = label_encoder.transform(test_df['intent'])

y_train = to_categorical(y_train_encoded)
y_val = to_categorical(y_val_encoded)
y_test = to_categorical(y_test_encoded)

print(f"✅ Feature matrices created:")
print(f"   X_train: {X_train.shape}")
print(f"   X_val:   {X_val.shape}")
print(f"   X_test:  {X_test.shape}")
print(f"   Classes: {len(label_encoder.classes_)}")

# ============================================================================
# STEP 5: BUILD MODEL ARCHITECTURE
# ============================================================================
print("\n🏗️  STEP 5: Building Neural Network...")

input_dim = X_train.shape[1]
num_classes = y_train.shape[1]

model = models.Sequential([
    layers.Input(shape=(input_dim,)),
    layers.Dense(256, activation='relu', name='dense_1'),
    layers.BatchNormalization(),
    layers.Dropout(0.3, name='dropout_1'),
    layers.Dense(128, activation='relu', name='dense_2'),
    layers.BatchNormalization(),
    layers.Dropout(0.3, name='dropout_2'),
    layers.Dense(num_classes, activation='softmax', name='output')
], name='bank_teller_intent_classifier')

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("✅ Model compiled successfully!")
model.summary()

# ============================================================================
# STEP 6: TRAIN MODEL
# ============================================================================
print("\n🎯 STEP 6: Training Model...")
print("   This may take 10-20 minutes depending on Colab GPU availability")

callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    ),
    ModelCheckpoint(
        filepath='data/models/best_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=0.00001,
        verbose=1
    )
]

start_time = time.time()

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

training_time = time.time() - start_time
print(f"\n✅ Training completed in {training_time/60:.2f} minutes")

# ============================================================================
# STEP 7: SAVE TRAINED ARTIFACTS
# ============================================================================
print("\n💾 STEP 7: Saving Trained Artifacts...")

os.makedirs('data/models', exist_ok=True)

# Save main model
model.save('data/models/intent_classifier.h5')
print("✅ Model saved")

# Save vectorizer
with open('data/models/vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
print("✅ Vectorizer saved")

# Save label encoder
with open('data/models/label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)
print("✅ Label encoder saved")

# Save training history
with open('data/models/training_history.json', 'w') as f:
    json.dump(history.history, f, indent=2)
print("✅ Training history saved")

# ============================================================================
# STEP 8: EVALUATE MODEL
# ============================================================================
print("\n🔍 STEP 8: Evaluating Model on Test Set...")

y_pred_proba = model.predict(X_test, verbose=0)
y_pred = np.argmax(y_pred_proba, axis=1)

accuracy = accuracy_score(y_test_encoded, y_pred)
precision = precision_score(y_test_encoded, y_pred, average='weighted')
recall = recall_score(y_test_encoded, y_pred, average='weighted')
f1 = f1_score(y_test_encoded, y_pred, average='weighted')

print(f"\n📈 Test Set Metrics:")
print(f"   Accuracy:  {accuracy:.4f}")
print(f"   Precision: {precision:.4f}")
print(f"   Recall:    {recall:.4f}")
print(f"   F1-Score:  {f1:.4f}")

# ============================================================================
# STEP 9: GENERATE CLASSIFICATION REPORT
# ============================================================================
print("\n📋 STEP 9: Generating Classification Report...")

report = classification_report(
    y_test_encoded,
    y_pred,
    target_names=label_encoder.classes_,
    digits=4
)

with open('data/models/classification_report.txt', 'w') as f:
    f.write(report)

print(report)

# ============================================================================
# STEP 10: GENERATE CONFUSION MATRIX
# ============================================================================
print("\n🔲 STEP 10: Generating Confusion Matrix...")

cm = confusion_matrix(y_test_encoded, y_pred)

plt.figure(figsize=(12, 10))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_,
    cbar_kws={'label': 'Count'}
)
plt.title('Confusion Matrix - Intent Classification', fontsize=16, fontweight='bold')
plt.xlabel('Predicted Intent', fontsize=12)
plt.ylabel('True Intent', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('data/models/confusion_matrix.png', dpi=150, bbox_inches='tight')
print("✅ Confusion matrix saved")
plt.close()

# ============================================================================
# STEP 11: CALCULATE PER-CLASS F1 SCORES
# ============================================================================
print("\n📊 STEP 11: Calculating Per-Class F1 Scores...")

f1_scores = f1_score(y_test_encoded, y_pred, average=None)
per_class_f1 = {}

for idx, intent in enumerate(label_encoder.classes_):
    per_class_f1[intent] = float(f1_scores[idx])

with open('data/models/per_class_f1_scores.json', 'w') as f:
    json.dump(per_class_f1, f, indent=2)

print("✅ Per-class F1 scores saved")

# ============================================================================
# STEP 12: FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print(" " * 30 + "TRAINING COMPLETE! ✅")
print("=" * 80)

print("\n📊 FINAL RESULTS:")
print("-" * 80)
print(f"  Overall Accuracy:   {accuracy:.4f}")
print(f"  Overall F1-Score:   {f1:.4f}")
print(f"  Training Time:      {training_time/60:.2f} minutes")

print("\n✅ SUCCESS CRITERIA:")
f1_pass = "✅ PASS" if f1 >= 0.85 else "⚠️  FAIL"
print(f"  {f1_pass} F1-Score > 0.85: {f1:.4f}")

print("\n📁 ARTIFACTS TO DOWNLOAD:")
print("-" * 80)
print("  ✅ data/models/intent_classifier.h5")
print("  ✅ data/models/vectorizer.pkl")
print("  ✅ data/models/label_encoder.pkl")
print("  ✅ data/models/best_model.h5")
print("  ✅ data/models/training_history.json")
print("  ✅ data/models/classification_report.txt")
print("  ✅ data/models/confusion_matrix.png")
print("  ✅ data/models/per_class_f1_scores.json")

# ============================================================================
# STEP 13: DOWNLOAD ARTIFACTS
# ============================================================================
print("\n📥 STEP 13: Preparing files for download...")

# Create a zip file with all artifacts
import shutil
shutil.make_archive('trained_models', 'zip', 'data/models')
print("✅ Created trained_models.zip")

print("\n📥 Running: files.download('trained_models.zip')")
files.download('trained_models.zip')

print("\n" + "=" * 80)
print(" " * 15 + "Download 'trained_models.zip' and extract to local system")
print(" " * 20 + "Then proceed to Step: LOAD TRAINED MODEL")
print("=" * 80 + "\n")
