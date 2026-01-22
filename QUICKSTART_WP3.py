"""
QUICK START - WP3 Training Workflow

This is a step-by-step checklist for the complete training process.
"""

# ============================================================================
# STEP 1: VERIFY LOCAL DATA ✅ (ALREADY DONE)
# ============================================================================
"""
Check that these files exist:
✅ data/processed/train.csv (17,881 samples)
✅ data/processed/val.csv (3,832 samples)
✅ data/processed/test.csv (3,832 samples)
✅ data/intent_mapping.json (26 intents)

Command to verify:
"""

import os

files_to_check = [
    "data/processed/train.csv",
    "data/processed/val.csv",
    "data/processed/test.csv",
    "data/intent_mapping.json"
]

print("📋 Checking data files...")
for file in files_to_check:
    exists = os.path.exists(file)
    size = os.path.getsize(file) / (1024*1024) if exists else 0
    status = "✅" if exists else "❌"
    print(f"   {status} {file} ({size:.2f} MB)")

# ============================================================================
# STEP 2: COLAB TRAINING
# ============================================================================
"""
Instructions:
1. Open: https://colab.research.google.com/
2. Create new notebook
3. Copy all content from: colab_training_script.py
4. Run the notebook step by step
5. When prompted, upload the 4 CSV files
6. Wait for training (10-20 minutes)
7. Download trained_models.zip

Expected output:
  ✅ Accuracy: ~0.90+
  ✅ F1-Score: ~0.90+ (target: >0.85)
  ✅ Training time: 10-20 minutes
"""

# ============================================================================
# STEP 3: EXTRACT AND LOAD MODELS LOCALLY
# ============================================================================
"""
After downloading trained_models.zip:

1. Extract to data/models/:
   Extract-Archive -Path "trained_models.zip" -DestinationPath "data/models" -Force

2. Verify files in data/models/:
   - intent_classifier.h5 ✅
   - vectorizer.pkl ✅
   - label_encoder.pkl ✅
   - best_model.h5 ✅
   - training_history.json ✅
   - classification_report.txt ✅
   - confusion_matrix.png ✅
   - per_class_f1_scores.json ✅

3. Test local inference:
   C:\Users\talha\AppData\Local\Programs\Python\Python310\python.exe backend\app\ml\load_trained_model.py

Expected output:
  TEST PREDICTIONS:
  1. Query: "How can I check my account balance?"
     Intent: balance_inquiry
     Confidence: 0.9823
"""

# ============================================================================
# STEP 4: VERIFY TRAINING METRICS
# ============================================================================
"""
Check training results:

1. Open data/models/classification_report.txt
   - Should show F1-scores for each intent
   - Target: Average F1 > 0.85

2. View data/models/confusion_matrix.png
   - Should show most predictions on diagonal
   - Few misclassifications

3. Check data/models/per_class_f1_scores.json
   - All intents should have F1 > 0.80

Example good metrics:
{
  "activate_card": 0.95,
  "find_branch": 0.92,
  "check_recent_transactions": 0.88,
  ...
  "block_card": 0.91
}
"""

# ============================================================================
# STEP 5: INTEGRATION READY ✅
# ============================================================================
"""
Once loaded, the model is ready for:

1. FastAPI Integration:
   from ml.load_trained_model import IntentClassifierInference
   classifier = IntentClassifierInference()
   classifier.load_artifacts()
   result = classifier.predict("user input text")

2. Features available:
   - Single prediction: classifier.predict(text)
   - Batch prediction: classifier.predict_batch(texts)
   - Confidence scores: result['confidence']
   - Top predictions: result['top_predictions']

3. Next phase (WP4):
   - Entity Extraction System
   - Dialog Management
   - Full backend integration
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================
"""
Problem: Colab training is slow
Solution: Use GPU in Colab (Runtime > Change runtime type > GPU)

Problem: Downloaded file is too large
Solution: The zip is ~500MB, normal for trained models

Problem: Local inference fails
Solution: 
  1. Verify Python 3.10 is active
  2. Verify TensorFlow 2.15.0: 
     python -c "import tensorflow; print(tensorflow.__version__)"
  3. Verify all model files exist in data/models/

Problem: F1-score is low (< 0.85)
Solution: 
  1. In Colab, increase epochs to 100
  2. Reduce batch_size to 16
  3. Retrain and download again

Problem: Model predictions are random/poor
Solution:
  1. Verify label_encoder.pkl loaded correctly
  2. Verify vectorizer.pkl loaded correctly
  3. Check that test data matches training data format
"""

# ============================================================================
# TIMELINE
# ============================================================================
"""
WP3 Timeline:

Phase 1 (Local Prep):     ✅ Complete
  - Data preparation:     ✅ 25,545 samples
  - Split creation:       ✅ Train/Val/Test
  - Scripts creation:     ✅ Ready

Phase 2 (Colab Training):  ⏳ Ready to start
  - Upload data:          10 minutes
  - Training:             10-20 minutes (depending on GPU)
  - Download:             5-10 minutes
  
Phase 3 (Local Loading):   ⏳ After Colab
  - Extract models:       2 minutes
  - Test inference:       1 minute
  - Integration ready:    Immediate

Total time: ~30-50 minutes (mostly Colab training)
"""

print("\n" + "=" * 80)
print(" " * 25 + "WP3 READY TO START")
print("=" * 80)
print("\n📋 Next action:")
print("   1. Go to: https://colab.research.google.com/")
print("   2. Create new notebook")
print("   3. Copy content from: colab_training_script.py")
print("   4. Run and follow prompts")
print("\n" + "=" * 80)
