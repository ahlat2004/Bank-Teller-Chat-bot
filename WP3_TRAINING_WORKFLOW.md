# Bank Teller Chatbot - WP3 Training Workflow

## Overview
This document outlines the complete workflow for training the intent classification model using Google Colab.

---

## Workflow Steps

### Phase 1: Local Preparation ✅

**Status:** COMPLETE

Files prepared:
- ✅ `data/processed/train.csv` - 17,881 training samples
- ✅ `data/processed/val.csv` - 3,832 validation samples
- ✅ `data/processed/test.csv` - 3,832 test samples
- ✅ `data/intent_mapping.json` - 26 intent categories
- ✅ `colab_training_script.py` - Ready for Colab execution
- ✅ `backend/app/ml/load_trained_model.py` - Local inference engine

---

### Phase 2: Colab Training (Instructions)

#### Step 1: Create Colab Notebook
1. Go to https://colab.research.google.com/
2. Create a new notebook
3. Copy entire content from `colab_training_script.py`

#### Step 2: Upload Data to Colab
When the script prompts "Running: files.upload()":
1. Click the upload button
2. Select and upload:
   - `data/processed/train.csv`
   - `data/processed/val.csv`
   - `data/processed/test.csv`
   - `data/intent_mapping.json`

#### Step 3: Run Training
1. Execute all cells in the notebook
2. Monitor progress (typically 10-20 minutes)
3. Model will automatically evaluate on test set

#### Step 4: Download Artifacts
When training completes:
1. Download `trained_models.zip` (automatic)
2. Extract the zip file locally

---

### Phase 3: Local Model Loading

#### Step 1: Extract Downloaded Models
```bash
# Extract trained_models.zip to data/models/
Extract-Archive -Path "trained_models.zip" -DestinationPath "e:\AI Project\bank-teller-chatbot\data\models" -Force
```

#### Step 2: Verify Model Files
Check that `data/models/` contains:
- ✅ `intent_classifier.h5` - Main trained model
- ✅ `vectorizer.pkl` - TF-IDF vectorizer
- ✅ `label_encoder.pkl` - Intent label encoder
- ✅ `best_model.h5` - Best checkpoint
- ✅ `training_history.json` - Training metrics
- ✅ `classification_report.txt` - Detailed metrics
- ✅ `confusion_matrix.png` - Visualization
- ✅ `per_class_f1_scores.json` - Per-intent scores

#### Step 3: Test Local Inference
```powershell
cd "e:\AI Project\bank-teller-chatbot"
C:\Users\talha\AppData\Local\Programs\Python\Python310\python.exe backend\app\ml\load_trained_model.py
```

Expected output:
```
TEST PREDICTIONS:
1. Query: "How can I check my account balance?"
   Intent: balance_inquiry
   Confidence: 0.9823
   Top 3 Predictions:
      1. balance_inquiry         (0.9823)
      2. account_update          (0.0123)
      3. account_opening         (0.0054)
```

---

## Expected Outcomes

### Training Performance Targets
- **F1-Score Target:** > 0.85 ✓
- **Accuracy Target:** > 0.85 ✓
- **Inference Speed:** < 100ms ✓

### Generated Artifacts
1. **Models:**
   - `intent_classifier.h5` - Production model
   - `best_model.h5` - Best checkpoint

2. **Preprocessing:**
   - `vectorizer.pkl` - TF-IDF vectorizer
   - `label_encoder.pkl` - Intent encoder

3. **Evaluation:**
   - `classification_report.txt` - Per-class metrics
   - `confusion_matrix.png` - Visualization
   - `per_class_f1_scores.json` - Intent-level F1 scores
   - `training_history.json` - Loss/accuracy curves

4. **Metadata:**
   - `training_history.json` - All training metrics

---

## Integration with FastAPI Backend

Once models are loaded, they can be integrated into `backend/app/api/`:

```python
from ml.load_trained_model import IntentClassifierInference

# Initialize once at startup
classifier = IntentClassifierInference(models_path='data/models')
classifier.load_artifacts()

# Use in API endpoints
@app.post("/api/predict-intent")
async def predict_intent(query: str):
    result = classifier.predict(query)
    return result
```

---

## Troubleshooting

### Issue: TensorFlow not found in Colab
**Solution:** The script handles this automatically with `import tensorflow`

### Issue: Model too large to download
**Solution:** The zip file is ~500MB, which is within Colab's download limits

### Issue: Local inference fails
**Solution:** 
1. Verify all model files exist in `data/models/`
2. Check Python 3.10 is being used
3. Ensure TensorFlow 2.15.0 is installed

### Issue: Poor F1 score (< 0.85)
**Solution:** In Colab, increase epochs to 100 and adjust batch_size to 16

---

## Files Summary

### Local Scripts
- `colab_training_script.py` - Complete Colab training notebook
- `backend/app/ml/load_trained_model.py` - Local inference engine
- `backend/app/ml/model_architecture.py` - Model definition
- `backend/app/ml/train_intent_classifier.py` - Training utilities
- `backend/app/ml/evaluator.py` - Evaluation utilities

### Data Files
- `data/processed/train.csv` - Training data (17,881 samples)
- `data/processed/val.csv` - Validation data (3,832 samples)
- `data/processed/test.csv` - Test data (3,832 samples)
- `data/intent_mapping.json` - Intent categories (26 intents)

### Trained Models (After Colab)
- `data/models/intent_classifier.h5` - Main model
- `data/models/vectorizer.pkl` - TF-IDF vectorizer
- `data/models/label_encoder.pkl` - Label encoder
- `data/models/best_model.h5` - Best checkpoint
- `data/models/training_history.json` - Metrics
- `data/models/classification_report.txt` - Detailed report
- `data/models/confusion_matrix.png` - Visualization
- `data/models/per_class_f1_scores.json` - Per-class scores

---

## Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| WP2 | Dataset Acquisition & Preprocessing | ✅ Complete | Done |
| WP3-Phase1 | Local Preparation | ✅ Complete | Done |
| WP3-Phase2 | Colab Training | ⏳ Pending | Ready to start |
| WP3-Phase3 | Model Loading & Integration | ⏳ Pending | After Colab |
| WP4 | Entity Extraction | 🔜 Next | After WP3 |

---

## Next Steps

1. **Copy Colab Script:** Copy content from `colab_training_script.py`
2. **Go to Colab:** https://colab.research.google.com/
3. **Create Notebook:** New notebook in Colab
4. **Paste Code:** Paste the script content
5. **Upload Data:** When prompted, upload the 4 CSV files
6. **Run Training:** Execute the notebook (10-20 minutes)
7. **Download:** Save the trained_models.zip
8. **Extract:** Extract to `data/models/` locally
9. **Test:** Run `load_trained_model.py` to verify

---

## Support

For issues or questions, refer to:
- `backend/app/ml/model_architecture.py` - Model structure details
- `backend/app/ml/train_intent_classifier.py` - Training utilities
- `backend/app/ml/evaluator.py` - Evaluation metrics
