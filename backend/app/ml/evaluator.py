"""
Model Evaluation Module
Evaluates intent classification model performance
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    f1_score,
    precision_score,
    recall_score,
    accuracy_score
)
from tensorflow import keras


class ModelEvaluator:
    def __init__(self, models_path: str = 'data/models',
                 data_path: str = 'data/processed'):
        """
        Initialize Model Evaluator
        
        Args:
            models_path: Path to saved models
            data_path: Path to processed data
        """
        self.models_path = models_path
        self.data_path = data_path
        
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        
    def load_artifacts(self):
        """Load trained model and preprocessors"""
        print("\n📂 Loading trained artifacts...")
        
        # Load model
        model_path = os.path.join(self.models_path, 'intent_classifier.h5')
        self.model = keras.models.load_model(model_path)
        print(f"   ✅ Model loaded from {model_path}")
        
        # Load vectorizer
        vectorizer_path = os.path.join(self.models_path, 'vectorizer.pkl')
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        print(f"   ✅ Vectorizer loaded")
        
        # Load label encoder
        label_encoder_path = os.path.join(self.models_path, 'label_encoder.pkl')
        with open(label_encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)
        print(f"   ✅ Label encoder loaded")
        
        print(f"\n   Number of classes: {len(self.label_encoder.classes_)}")
    
    def load_test_data(self):
        """Load test dataset"""
        test_path = os.path.join(self.data_path, 'test.csv')
        test_df = pd.read_csv(test_path)
        
        print(f"\n📊 Test dataset loaded: {len(test_df)} samples")
        
        return test_df
    
    def evaluate_on_test_set(self, test_df: pd.DataFrame):
        """
        Evaluate model on test set
        
        Args:
            test_df: Test dataframe
            
        Returns:
            dict: Evaluation metrics
        """
        print("\n🔍 Evaluating on test set...")
        
        # Transform features
        X_test = self.vectorizer.transform(test_df['cleaned_text']).toarray()
        y_true = self.label_encoder.transform(test_df['intent'])
        
        # Make predictions
        y_pred_proba = self.model.predict(X_test, verbose=0)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        f1 = f1_score(y_true, y_pred, average='weighted')
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'num_samples': len(test_df)
        }
        
        print("\n📈 Overall Metrics:")
        print(f"   Accuracy:  {accuracy:.4f}")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall:    {recall:.4f}")
        print(f"   F1-Score:  {f1:.4f}")
        
        return metrics, y_true, y_pred, y_pred_proba
    
    def generate_classification_report(self, y_true, y_pred):
        """
        Generate detailed classification report
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            str: Classification report
        """
        print("\n📋 Generating classification report...")
        
        report = classification_report(
            y_true, 
            y_pred, 
            target_names=self.label_encoder.classes_,
            digits=4
        )
        
        print("\n" + "=" * 70)
        print("CLASSIFICATION REPORT")
        print("=" * 70)
        print(report)
        
        # Save report
        report_path = os.path.join(self.models_path, 'classification_report.txt')
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"✅ Report saved to {report_path}")
        
        return report
    
    def generate_confusion_matrix(self, y_true, y_pred, save_plot: bool = True):
        """
        Generate and plot confusion matrix
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            save_plot: Whether to save the plot
            
        Returns:
            np.ndarray: Confusion matrix
        """
        print("\n🔲 Generating confusion matrix...")
        
        cm = confusion_matrix(y_true, y_pred)
        
        # Plot confusion matrix
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d', 
            cmap='Blues',
            xticklabels=self.label_encoder.classes_,
            yticklabels=self.label_encoder.classes_,
            cbar_kws={'label': 'Count'}
        )
        plt.title('Confusion Matrix - Intent Classification', fontsize=16, fontweight='bold')
        plt.xlabel('Predicted Intent', fontsize=12)
        plt.ylabel('True Intent', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if save_plot:
            plot_path = os.path.join(self.models_path, 'confusion_matrix.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"✅ Confusion matrix saved to {plot_path}")
        
        plt.close()
        
        return cm
    
    def calculate_per_class_f1(self, y_true, y_pred):
        """
        Calculate F1 score for each class
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            dict: Per-class F1 scores
        """
        print("\n📊 Calculating per-class F1 scores...")
        
        f1_scores = f1_score(y_true, y_pred, average=None)
        
        per_class_f1 = {}
        for idx, intent in enumerate(self.label_encoder.classes_):
            per_class_f1[intent] = f1_scores[idx]
        
        # Sort by F1 score
        sorted_f1 = sorted(per_class_f1.items(), key=lambda x: x[1], reverse=True)
        
        print("\n🎯 Per-Class F1 Scores (Top 10):")
        for intent, score in sorted_f1[:10]:
            print(f"   {intent:30s} {score:.4f}")
        
        print("\n⚠️  Lowest F1 Scores (Bottom 5):")
        for intent, score in sorted_f1[-5:]:
            print(f"   {intent:30s} {score:.4f}")
        
        # Save to JSON
        f1_path = os.path.join(self.models_path, 'per_class_f1_scores.json')
        with open(f1_path, 'w') as f:
            json.dump(per_class_f1, f, indent=2)
        
        print(f"\n✅ Per-class F1 scores saved to {f1_path}")
        
        return per_class_f1
    
    def test_inference_speed(self, num_samples: int = 100):
        """
        Test model inference speed
        
        Args:
            num_samples: Number of samples to test
            
        Returns:
            dict: Speed metrics
        """
        print(f"\n⚡ Testing inference speed ({num_samples} samples)...")
        
        # Load some test samples
        test_df = self.load_test_data()
        sample_texts = test_df['cleaned_text'].head(num_samples).tolist()
        
        # Measure vectorization + prediction time
        times = []
        
        for text in sample_texts:
            start = time.time()
            
            # Vectorize
            X = self.vectorizer.transform([text]).toarray()
            
            # Predict
            pred = self.model.predict(X, verbose=0)
            
            end = time.time()
            times.append((end - start) * 1000)  # Convert to milliseconds
        
        avg_time = np.mean(times)
        max_time = np.max(times)
        min_time = np.min(times)
        
        speed_metrics = {
            'avg_inference_time_ms': avg_time,
            'max_inference_time_ms': max_time,
            'min_inference_time_ms': min_time,
            'num_samples_tested': num_samples,
            'meets_requirement': avg_time < 100  # Target: <100ms
        }
        
        print(f"\n⏱️  Inference Speed Results:")
        print(f"   Average: {avg_time:.2f} ms")
        print(f"   Maximum: {max_time:.2f} ms")
        print(f"   Minimum: {min_time:.2f} ms")
        
        status = "✅ PASS" if speed_metrics['meets_requirement'] else "❌ FAIL"
        print(f"\n   Target (<100ms): {status}")
        
        # Save speed metrics
        speed_path = os.path.join(self.models_path, 'inference_speed.json')
        with open(speed_path, 'w') as f:
            json.dump(speed_metrics, f, indent=2)
        
        return speed_metrics
    
    def plot_training_history(self, history_path: str = None):
        """
        Plot training history if available
        
        Args:
            history_path: Path to saved history JSON
        """
        if history_path and os.path.exists(history_path):
            with open(history_path, 'r') as f:
                history = json.load(f)
            
            fig, axes = plt.subplots(1, 2, figsize=(15, 5))
            
            # Plot accuracy
            axes[0].plot(history['accuracy'], label='Training Accuracy')
            axes[0].plot(history['val_accuracy'], label='Validation Accuracy')
            axes[0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
            axes[0].set_xlabel('Epoch')
            axes[0].set_ylabel('Accuracy')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            # Plot loss
            axes[1].plot(history['loss'], label='Training Loss')
            axes[1].plot(history['val_loss'], label='Validation Loss')
            axes[1].set_title('Model Loss', fontsize=14, fontweight='bold')
            axes[1].set_xlabel('Epoch')
            axes[1].set_ylabel('Loss')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            plot_path = os.path.join(self.models_path, 'training_history.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"✅ Training history plot saved to {plot_path}")
            
            plt.close()
    
    def generate_evaluation_report(self):
        """Generate comprehensive evaluation report"""
        report_path = os.path.join(self.models_path, 'evaluation_summary.json')
        
        # This will be populated during evaluation
        print(f"\n📝 Evaluation report will be saved to {report_path}")


def main():
    """
    Main evaluation pipeline
    """
    print("=" * 70)
    print(" " * 15 + "MODEL EVALUATION & TESTING")
    print("=" * 70)
    
    # Initialize evaluator
    evaluator = ModelEvaluator()
    
    # Load artifacts
    evaluator.load_artifacts()
    
    # Load test data
    test_df = evaluator.load_test_data()
    
    # Evaluate on test set
    metrics, y_true, y_pred, y_pred_proba = evaluator.evaluate_on_test_set(test_df)
    
    # Generate classification report
    report = evaluator.generate_classification_report(y_true, y_pred)
    
    # Generate confusion matrix
    cm = evaluator.generate_confusion_matrix(y_true, y_pred, save_plot=True)
    
    # Calculate per-class F1 scores
    per_class_f1 = evaluator.calculate_per_class_f1(y_true, y_pred)
    
    # Test inference speed
    speed_metrics = evaluator.test_inference_speed(num_samples=100)
    
    # Final Summary
    print("\n" + "=" * 70)
    print(" " * 20 + "EVALUATION SUMMARY")
    print("=" * 70)
    
    print(f"\n✅ Overall Performance:")
    print(f"   Accuracy:  {metrics['accuracy']:.4f}")
    print(f"   Precision: {metrics['precision']:.4f}")
    print(f"   Recall:    {metrics['recall']:.4f}")
    print(f"   F1-Score:  {metrics['f1_score']:.4f}")
    
    print(f"\n⚡ Inference Speed:")
    print(f"   Average: {speed_metrics['avg_inference_time_ms']:.2f} ms")
    print(f"   Target:  <100 ms")
    print(f"   Status:  {'✅ PASS' if speed_metrics['meets_requirement'] else '❌ FAIL'}")
    
    print(f"\n🎯 Success Criteria:")
    f1_pass = "✅" if metrics['f1_score'] >= 0.85 else "⚠️"
    speed_pass = "✅" if speed_metrics['meets_requirement'] else "⚠️"
    
    print(f"   {f1_pass} F1-Score > 0.85: {metrics['f1_score']:.4f}")
    print(f"   {speed_pass} Inference < 100ms: {speed_metrics['avg_inference_time_ms']:.2f} ms")
    
    print(f"\n📁 Generated Files:")
    print(f"   ✅ classification_report.txt")
    print(f"   ✅ confusion_matrix.png")
    print(f"   ✅ per_class_f1_scores.json")
    print(f"   ✅ inference_speed.json")
    
    print("\n" + "=" * 70)
    print(" " * 20 + "EVALUATION COMPLETE! ✅")
    print("=" * 70 + "\n")
    
    return evaluator, metrics


if __name__ == "__main__":
    evaluator, metrics = main()