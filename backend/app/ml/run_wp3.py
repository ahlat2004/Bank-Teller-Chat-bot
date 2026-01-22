"""
WP3 Complete Runner Script
Executes all WP3 tasks: Training + Evaluation
Place this in: backend/app/ml/run_wp3.py
"""

import sys
import os
import json
import pickle

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.train_intent_classifier import IntentClassifierTrainer
from ml.evaluator import ModelEvaluator
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for plotting


def save_training_history(history: dict, filepath: str):
    """Save training history to JSON"""
    with open(filepath, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"✅ Training history saved to {filepath}")


def run_wp3():
    """
    Complete WP3 execution pipeline
    """
    print("=" * 80)
    print(" " * 20 + "BANK TELLER CHATBOT - WP3")
    print(" " * 15 + "Intent Classification Model Training")
    print("=" * 80)
    
    try:
        # ========== PHASE 1: MODEL TRAINING ==========
        print("\n" + "🔷" * 40)
        print(" " * 28 + "PHASE 1: TRAINING")
        print("🔷" * 40)
        
        trainer = IntentClassifierTrainer(
            data_path='data/processed',
            models_path='data/models'
        )
        
        # TASK 1: Load Intent Mapping
        print("\n📋 TASK 1: Loading Intent Mapping")
        print("-" * 80)
        intent_mapping = trainer.load_intent_mapping()
        
        print(f"\nIntent Categories ({intent_mapping['num_intents']} total):")
        for i, (intent, idx) in enumerate(list(intent_mapping['intent_to_id'].items())[:10]):
            print(f"  [{idx:2d}] {intent}")
        if intent_mapping['num_intents'] > 10:
            print(f"  ... and {intent_mapping['num_intents'] - 10} more intents")
        
        # TASK 2: Load Data
        print("\n📂 TASK 2: Loading Datasets")
        print("-" * 80)
        train_df, val_df, test_df = trainer.load_data()
        
        # TASK 3: Build TF-IDF Vectorizer
        print("\n🔢 TASK 3: Building TF-IDF Vectorizer")
        print("-" * 80)
        trainer.build_tfidf_vectorizer(train_df, max_features=5000)
        
        # Show sample vocabulary
        vocab_sample = list(trainer.vectorizer.vocabulary_.items())[:15]
        print("\nSample Vocabulary (first 15 terms):")
        for term, idx in vocab_sample:
            print(f"  '{term}': {idx}")
        
        # TASK 4: Prepare Features
        print("\n🔄 TASK 4: Preparing Features")
        print("-" * 80)
        X_train, y_train, X_val, y_val, X_test, y_test = trainer.prepare_features(
            train_df, val_df, test_df
        )
        
        print(f"\nFeature Matrix Shapes:")
        print(f"  X_train: {X_train.shape} (samples × features)")
        print(f"  X_val:   {X_val.shape}")
        print(f"  X_test:  {X_test.shape}")
        print(f"\nLabel Matrix Shapes:")
        print(f"  y_train: {y_train.shape} (samples × classes)")
        print(f"  y_val:   {y_val.shape}")
        print(f"  y_test:  {y_test.shape}")
        
        # TASK 5: Train Model
        print("\n🎯 TASK 5: Training Neural Network")
        print("-" * 80)
        print("⚠️  This may take 5-15 minutes depending on your hardware...")
        print("    Progress will be shown below:\n")
        
        history = trainer.train_model(
            X_train, y_train,
            X_val, y_val,
            epochs=50,
            batch_size=32
        )
        
        # TASK 6: Save Artifacts
        print("\n💾 TASK 6: Saving Trained Artifacts")
        print("-" * 80)
        trainer.save_artifacts()
        
        # Save training history
        history_path = os.path.join('data/models', 'training_history.json')
        save_training_history(history, history_path)
        
        # Get top features analysis
        print("\n🔍 TASK 7: Analyzing Top Features")
        print("-" * 80)
        top_features = trainer.get_top_features_per_intent(top_n=5)
        
        print("\n📊 Top 5 Keywords per Intent (Sample):")
        for i, (intent, features) in enumerate(list(top_features.items())[:5]):
            print(f"\n  Intent: {intent}")
            print(f"    Keywords: {', '.join(features)}")
        
        # ========== PHASE 2: MODEL EVALUATION ==========
        print("\n\n" + "🔶" * 40)
        print(" " * 27 + "PHASE 2: EVALUATION")
        print("🔶" * 40)
        
        evaluator = ModelEvaluator(
            models_path='data/models',
            data_path='data/processed'
        )
        
        # TASK 8: Load Artifacts for Evaluation
        print("\n📂 TASK 8: Loading Trained Artifacts")
        print("-" * 80)
        evaluator.load_artifacts()
        
        # TASK 9: Load Test Data
        print("\n📊 TASK 9: Loading Test Dataset")
        print("-" * 80)
        test_df_eval = evaluator.load_test_data()
        
        # TASK 10: Evaluate on Test Set
        print("\n🔍 TASK 10: Evaluating on Test Set")
        print("-" * 80)
        metrics, y_true, y_pred, y_pred_proba = evaluator.evaluate_on_test_set(test_df_eval)
        
        # TASK 11: Generate Classification Report
        print("\n📋 TASK 11: Generating Classification Report")
        print("-" * 80)
        report = evaluator.generate_classification_report(y_true, y_pred)
        
        # TASK 12: Generate Confusion Matrix
        print("\n🔲 TASK 12: Generating Confusion Matrix")
        print("-" * 80)
        cm = evaluator.generate_confusion_matrix(y_true, y_pred, save_plot=True)
        
        # TASK 13: Calculate Per-Class F1 Scores
        print("\n📊 TASK 13: Calculating Per-Class F1 Scores")
        print("-" * 80)
        per_class_f1 = evaluator.calculate_per_class_f1(y_true, y_pred)
        
        # TASK 14: Test Inference Speed
        print("\n⚡ TASK 14: Testing Inference Speed")
        print("-" * 80)
        speed_metrics = evaluator.test_inference_speed(num_samples=100)
        
        # ========== FINAL SUMMARY ==========
        print("\n\n" + "=" * 80)
        print(" " * 30 + "WP3 COMPLETE! ✅")
        print("=" * 80)
        
        print("\n📊 PERFORMANCE METRICS:")
        print("-" * 80)
        print(f"  Accuracy:           {metrics['accuracy']:.4f}")
        print(f"  Precision:          {metrics['precision']:.4f}")
        print(f"  Recall:             {metrics['recall']:.4f}")
        print(f"  F1-Score:           {metrics['f1_score']:.4f}")
        print(f"  Test Samples:       {metrics['num_samples']:,}")
        
        print("\n⚡ INFERENCE SPEED:")
        print("-" * 80)
        print(f"  Average Time:       {speed_metrics['avg_inference_time_ms']:.2f} ms")
        print(f"  Maximum Time:       {speed_metrics['max_inference_time_ms']:.2f} ms")
        print(f"  Minimum Time:       {speed_metrics['min_inference_time_ms']:.2f} ms")
        print(f"  Target:             < 100 ms")
        
        print("\n🎯 SUCCESS CRITERIA:")
        print("-" * 80)
        
        f1_target = 0.85
        speed_target = 100
        
        f1_pass = metrics['f1_score'] >= f1_target
        speed_pass = speed_metrics['avg_inference_time_ms'] < speed_target
        
        f1_status = "✅ PASS" if f1_pass else "⚠️  FAIL"
        speed_status = "✅ PASS" if speed_pass else "⚠️  FAIL"
        
        print(f"  {f1_status} F1-Score > {f1_target}: {metrics['f1_score']:.4f}")
        print(f"  {speed_status} Inference < {speed_target}ms: {speed_metrics['avg_inference_time_ms']:.2f} ms")
        
        overall_pass = f1_pass and speed_pass
        overall_status = "✅ ALL CRITERIA MET" if overall_pass else "⚠️  SOME CRITERIA NOT MET"
        print(f"\n  Overall: {overall_status}")
        
        print("\n📁 ARTIFACTS CREATED:")
        print("-" * 80)
        
        artifacts = [
            ("data/models/intent_classifier.h5", "Trained Neural Network"),
            ("data/models/vectorizer.pkl", "TF-IDF Vectorizer"),
            ("data/models/label_encoder.pkl", "Label Encoder"),
            ("data/models/best_model.h5", "Best Model Checkpoint"),
            ("data/models/training_history.json", "Training History"),
            ("data/models/classification_report.txt", "Classification Report"),
            ("data/models/confusion_matrix.png", "Confusion Matrix Plot"),
            ("data/models/per_class_f1_scores.json", "Per-Class F1 Scores"),
            ("data/models/inference_speed.json", "Inference Speed Metrics")
        ]
        
        for filepath, description in artifacts:
            exists = "✅" if os.path.exists(filepath) else "❌"
            size = ""
            if os.path.exists(filepath):
                size_kb = os.path.getsize(filepath) / 1024
                if size_kb < 1024:
                    size = f"({size_kb:.1f} KB)"
                else:
                    size = f"({size_kb/1024:.1f} MB)"
            print(f"  {exists} {description:30s} {size}")
            print(f"      → {filepath}")
        
        print("\n🚀 NEXT STEPS:")
        print("-" * 80)
        print("  1. ✅ Review confusion_matrix.png for misclassification patterns")
        print("  2. ✅ Check classification_report.txt for detailed per-class metrics")
        print("  3. ✅ Verify per_class_f1_scores.json for intent-specific performance")
        print("  4. 🔜 Proceed to WP4: Entity Extraction System")
        print("  5. 🔜 The trained model is ready for integration with FastAPI backend")
        
        print("\n💡 MODEL INTEGRATION:")
        print("-" * 80)
        print("  The following files will be loaded by the FastAPI backend:")
        print("    • intent_classifier.h5   → Neural network for intent prediction")
        print("    • vectorizer.pkl         → Text-to-vector transformation")
        print("    • label_encoder.pkl      → Intent ID to intent name mapping")
        
        print("\n" + "=" * 80)
        print(" " * 25 + "WP3 Successfully Completed!")
        print("=" * 80 + "\n")
        
        return {
            'trainer': trainer,
            'evaluator': evaluator,
            'metrics': metrics,
            'speed_metrics': speed_metrics,
            'history': history,
            'intent_mapping': intent_mapping
        }
        
    except Exception as e:
        print(f"\n❌ ERROR in WP3 execution:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n🚀 Starting WP3: Intent Classification Model Training\n")
    
    result = run_wp3()
    
    if result:
        print("\n✅ WP3 completed successfully!")
        print("   Ready to proceed to WP4: Entity Extraction System")
    else:
        print("\n❌ WP3 failed. Please check the errors above.")
        print("   Common issues:")
        print("     • Missing WP2 outputs (run WP2 first)")
        print("     • Insufficient memory (reduce batch_size in train_intent_classifier.py)")
        print("     • TensorFlow/Keras installation issues")