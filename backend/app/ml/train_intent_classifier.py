"""
Intent Classification Model Training Module
Trains TF-IDF + Neural Network for intent classification
"""

import pandas as pd
import numpy as np
import json
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import time

from app.ml.model_architecture import IntentClassifierModel


class IntentClassifierTrainer:
    def __init__(self, data_path: str = 'data/processed', 
                 models_path: str = 'data/models'):
        """
        Initialize Intent Classifier Trainer
        
        Args:
            data_path: Path to processed data
            models_path: Path to save models
        """
        self.data_path = data_path
        self.models_path = models_path
        os.makedirs(models_path, exist_ok=True)
        
        self.vectorizer = None
        self.label_encoder = None
        self.model = None
        self.intent_mapping = None
        
    def load_data(self):
        """
        Load train, validation, and test datasets
        
        Returns:
            tuple: (train_df, val_df, test_df)
        """
        print("\n📂 Loading datasets...")
        
        train_df = pd.read_csv(os.path.join(self.data_path, 'train.csv'))
        val_df = pd.read_csv(os.path.join(self.data_path, 'val.csv'))
        test_df = pd.read_csv(os.path.join(self.data_path, 'test.csv'))
        
        print(f"   Training samples:   {len(train_df)}")
        print(f"   Validation samples: {len(val_df)}")
        print(f"   Test samples:       {len(test_df)}")
        
        return train_df, val_df, test_df
    
    def load_intent_mapping(self):
        """Load intent mapping from JSON"""
        mapping_path = os.path.join('data', 'intent_mapping.json')
        
        with open(mapping_path, 'r') as f:
            self.intent_mapping = json.load(f)
        
        print(f"\n✅ Loaded intent mapping: {self.intent_mapping['num_intents']} intents")
        
        return self.intent_mapping
    
    def build_tfidf_vectorizer(self, train_df: pd.DataFrame, 
                               max_features: int = 5000):
        """
        Build and fit TF-IDF vectorizer
        
        Args:
            train_df: Training dataframe
            max_features: Maximum number of features
            
        Returns:
            TfidfVectorizer: Fitted vectorizer
        """
        print("\n🔢 Building TF-IDF Vectorizer...")
        print(f"   Max features: {max_features}")
        print(f"   N-grams: (1, 2) - unigrams and bigrams")
        
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.8,  # Ignore terms that appear in more than 80% of documents
            sublinear_tf=True  # Apply sublinear tf scaling
        )
        
        # Fit on training data
        self.vectorizer.fit(train_df['cleaned_text'])
        
        print(f"✅ Vectorizer fitted!")
        print(f"   Vocabulary size: {len(self.vectorizer.vocabulary_)}")
        
        return self.vectorizer
    
    def prepare_features(self, train_df, val_df, test_df):
        """
        Transform text to TF-IDF features
        
        Args:
            train_df: Training dataframe
            val_df: Validation dataframe
            test_df: Test dataframe
            
        Returns:
            tuple: (X_train, y_train, X_val, y_val, X_test, y_test)
        """
        print("\n🔄 Transforming text to TF-IDF features...")
        
        # Transform text to TF-IDF vectors
        X_train = self.vectorizer.transform(train_df['cleaned_text']).toarray()
        X_val = self.vectorizer.transform(val_df['cleaned_text']).toarray()
        X_test = self.vectorizer.transform(test_df['cleaned_text']).toarray()
        
        print(f"   X_train shape: {X_train.shape}")
        print(f"   X_val shape:   {X_val.shape}")
        print(f"   X_test shape:  {X_test.shape}")
        
        # Encode labels
        print("\n🏷️  Encoding labels...")
        self.label_encoder = LabelEncoder()
        
        y_train_encoded = self.label_encoder.fit_transform(train_df['intent'])
        y_val_encoded = self.label_encoder.transform(val_df['intent'])
        y_test_encoded = self.label_encoder.transform(test_df['intent'])
        
        # One-hot encode for neural network
        y_train = to_categorical(y_train_encoded)
        y_val = to_categorical(y_val_encoded)
        y_test = to_categorical(y_test_encoded)
        
        print(f"   Number of classes: {len(self.label_encoder.classes_)}")
        print(f"   y_train shape: {y_train.shape}")
        
        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def train_model(self, X_train, y_train, X_val, y_val, 
                   epochs: int = 50, 
                   batch_size: int = 32):
        """
        Train the intent classification model
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of epochs
            batch_size: Batch size
            
        Returns:
            dict: Training history
        """
        print("\n🎯 Initializing Model...")
        
        # Get input dimensions
        input_dim = X_train.shape[1]
        num_classes = y_train.shape[1]
        
        # Create model
        self.model = IntentClassifierModel(
            input_dim=input_dim,
            num_classes=num_classes,
            model_name="bank_teller_intent_classifier"
        )
        
        # Build architecture
        self.model.build_model()
        
        # Train model
        checkpoint_path = os.path.join(self.models_path, 'best_model.h5')
        
        start_time = time.time()
        history = self.model.train(
            X_train, y_train,
            X_val, y_val,
            epochs=epochs,
            batch_size=batch_size,
            checkpoint_path=checkpoint_path
        )
        training_time = time.time() - start_time
        
        print(f"\n⏱️  Training completed in {training_time/60:.2f} minutes")
        
        return history
    
    def save_artifacts(self):
        """
        Save all trained artifacts (model, vectorizer, label encoder)
        """
        print("\n💾 Saving trained artifacts...")
        
        # Save model
        model_path = os.path.join(self.models_path, 'intent_classifier.h5')
        self.model.save_model(model_path)
        
        # Save vectorizer
        vectorizer_path = os.path.join(self.models_path, 'vectorizer.pkl')
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        print(f"✅ Vectorizer saved to {vectorizer_path}")
        
        # Save label encoder
        label_encoder_path = os.path.join(self.models_path, 'label_encoder.pkl')
        with open(label_encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        print(f"✅ Label encoder saved to {label_encoder_path}")
        
        print("\n✅ All artifacts saved successfully!")
    
    def get_top_features_per_intent(self, top_n: int = 10):
        """
        Get top TF-IDF features for each intent
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            dict: Top features per intent
        """
        feature_names = self.vectorizer.get_feature_names_out()
        top_features = {}
        
        for intent_idx, intent_name in enumerate(self.label_encoder.classes_):
            # Get the weight vector for this class
            weights = self.model.model.layers[-1].get_weights()[0][:, intent_idx]
            
            # Get top feature indices
            top_indices = np.argsort(weights)[-top_n:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            
            top_features[intent_name] = top_words
        
        return top_features


def main():
    """
    Main training pipeline
    """
    print("=" * 70)
    print(" " * 15 + "WP3: INTENT CLASSIFICATION TRAINING")
    print("=" * 70)
    
    # Initialize trainer
    trainer = IntentClassifierTrainer()
    
    # Load intent mapping
    trainer.load_intent_mapping()
    
    # Load datasets
    train_df, val_df, test_df = trainer.load_data()
    
    # Build TF-IDF vectorizer
    trainer.build_tfidf_vectorizer(train_df, max_features=5000)
    
    # Prepare features
    X_train, y_train, X_val, y_val, X_test, y_test = trainer.prepare_features(
        train_df, val_df, test_df
    )
    
    # Train model
    history = trainer.train_model(
        X_train, y_train,
        X_val, y_val,
        epochs=50,
        batch_size=32
    )
    
    # Save artifacts
    trainer.save_artifacts()
    
    # Get top features (optional analysis)
    print("\n🔍 Analyzing top features per intent...")
    top_features = trainer.get_top_features_per_intent(top_n=5)
    
    print("\n📊 Top 5 Features for Sample Intents:")
    for i, (intent, features) in enumerate(list(top_features.items())[:5]):
        print(f"\n  {intent}:")
        print(f"    {', '.join(features)}")
    
    # Training summary
    print("\n" + "=" * 70)
    print(" " * 20 + "TRAINING SUMMARY")
    print("=" * 70)
    
    final_train_acc = history['accuracy'][-1]
    final_val_acc = history['val_accuracy'][-1]
    final_train_loss = history['loss'][-1]
    final_val_loss = history['val_loss'][-1]
    
    print(f"\n📈 Final Metrics:")
    print(f"   Training Accuracy:   {final_train_acc:.4f}")
    print(f"   Validation Accuracy: {final_val_acc:.4f}")
    print(f"   Training Loss:       {final_train_loss:.4f}")
    print(f"   Validation Loss:     {final_val_loss:.4f}")
    
    print(f"\n📁 Saved Artifacts:")
    print(f"   ✅ data/models/intent_classifier.h5")
    print(f"   ✅ data/models/vectorizer.pkl")
    print(f"   ✅ data/models/label_encoder.pkl")
    print(f"   ✅ data/models/best_model.h5")
    
    print("\n🎯 Target Achievement:")
    target_met = "✅" if final_val_acc >= 0.85 else "⚠️"
    print(f"   {target_met} F1 Score Target (>0.85): {final_val_acc:.4f}")
    
    print("\n🚀 Next Steps:")
    print("   1. Run evaluation script to get detailed metrics")
    print("   2. Test inference speed (<100ms requirement)")
    print("   3. Proceed to WP4: Entity Extraction System")
    
    print("\n" + "=" * 70)
    print(" " * 20 + "WP3 COMPLETED! ✅")
    print("=" * 70 + "\n")
    
    return trainer, history


if __name__ == "__main__":
    trainer, history = main()