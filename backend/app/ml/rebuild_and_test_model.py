"""
Rebuild model architecture and load weights from trained H5 file
This bypasses the Keras batch_shape compatibility issue
"""

import os
import pickle
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers, models
from sklearn.preprocessing import LabelEncoder


def build_model(num_classes: int, input_dim: int):
    """Build the neural network model architecture"""
    
    model = models.Sequential([
        layers.Dense(256, activation='relu', input_shape=(input_dim,)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def main():
    print("\n" + "=" * 80)
    print(" " * 20 + "REBUILDING MODEL FROM WEIGHTS")
    print("=" * 80)
    
    models_path = 'data/models'
    
    # Load vectorizer to get input dimension
    print("\n[*] Loading vectorizer...")
    with open(f"{models_path}/vectorizer.pkl", 'rb') as f:
        vectorizer = pickle.load(f)
    input_dim = vectorizer.get_feature_names_out().shape[0]
    print(f"   [OK] Input dimension: {input_dim}")
    
    # Load label encoder to get number of classes
    print("\n[*] Loading label encoder...")
    with open(f"{models_path}/label_encoder.pkl", 'rb') as f:
        label_encoder = pickle.load(f)
    num_classes = len(label_encoder.classes_)
    print(f"   [OK] Number of classes: {num_classes}")
    
    # Build fresh model
    print("\n[*] Building model architecture...")
    model = build_model(num_classes, input_dim)
    model.summary()
    
    # Load weights from trained model
    print("\n[*] Loading weights from trained model...")
    weight_paths = [
        f"{models_path}/best_model.h5",
        f"{models_path}/intent_classifier.h5"
    ]
    
    loaded = False
    for weight_path in weight_paths:
        if os.path.exists(weight_path):
            try:
                # Try loading weights only (not the full model)
                model.load_weights(weight_path)
                print(f"   [OK] Weights loaded from {os.path.basename(weight_path)}")
                loaded = True
                break
            except Exception as e:
                print(f"   [!] Could not load weights from {weight_path}: {e}")
    
    if not loaded:
        print("   [ERROR] Could not load weights from any model file!")
        return None
    
    # Test inference
    print("\n" + "=" * 80)
    print("TESTING INFERENCE")
    print("=" * 80)
    
    test_queries = [
        "How can I check my account balance?",
        "I want to transfer money to another account",
        "Can I apply for a credit card?",
        "What are the interest rates for savings accounts?",
        "How do I report a fraudulent transaction?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        # Vectorize
        X = vectorizer.transform([query]).toarray()
        
        # Predict
        proba = model.predict(X, verbose=0)[0]
        pred_idx = np.argmax(proba)
        pred_intent = label_encoder.classes_[pred_idx]
        confidence = float(proba[pred_idx])
        
        # Top 3
        top_indices = np.argsort(proba)[-3:][::-1]
        
        print(f"\n{i}. Query: \"{query}\"")
        print(f"   Intent: {pred_intent} ({confidence:.4f})")
        print(f"   Top 3:")
        for j, idx in enumerate(top_indices, 1):
            print(f"      {j}. {label_encoder.classes_[idx]:30s} ({proba[idx]:.4f})")
    
    print("\n" + "=" * 80)
    print(" " * 25 + "MODEL REBUILT SUCCESSFULLY [OK]")
    print("=" * 80)
    
    # Save the rebuilt model
    print("\n[*] Saving rebuilt model...")
    model.save(f"{models_path}/intent_classifier_rebuilt.h5")
    print(f"   [OK] Saved to: {models_path}/intent_classifier_rebuilt.h5")
    
    return model


if __name__ == "__main__":
    model = main()
