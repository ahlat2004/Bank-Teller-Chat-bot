"""
Neural Network Model Architecture
Defines the intent classification model structure
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import numpy as np


class IntentClassifierModel:
    def __init__(self, input_dim: int, num_classes: int, model_name: str = "intent_classifier"):
        """
        Initialize Intent Classification Model
        
        Args:
            input_dim: Input feature dimension (TF-IDF vector size)
            num_classes: Number of intent classes
            model_name: Model identifier
        """
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.model_name = model_name
        self.model = None
        
    def build_model(self) -> keras.Model:
        """
        Build neural network architecture
        
        Architecture:
        Input → Dense(256, relu) → Dropout(0.3)
              → Dense(128, relu) → Dropout(0.3)
              → Dense(num_intents, softmax)
        
        Returns:
            keras.Model: Compiled model
        """
        print("\n🏗️  Building Neural Network Architecture...")
        
        model = models.Sequential([
            # Input layer
            layers.Input(shape=(self.input_dim,)),
            
            # First hidden layer
            layers.Dense(256, activation='relu', name='dense_1'),
            layers.BatchNormalization(),
            layers.Dropout(0.3, name='dropout_1'),
            
            # Second hidden layer
            layers.Dense(128, activation='relu', name='dense_2'),
            layers.BatchNormalization(),
            layers.Dropout(0.3, name='dropout_2'),
            
            # Output layer
            layers.Dense(self.num_classes, activation='softmax', name='output')
        ], name=self.model_name)
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("✅ Model built successfully!")
        print("\n📊 Model Summary:")
        model.summary()
        
        self.model = model
        return model
    
    def get_callbacks(self, checkpoint_path: str) -> list:
        """
        Get training callbacks
        
        Args:
            checkpoint_path: Path to save best model
            
        Returns:
            list: List of callbacks
        """
        callbacks = [
            # Early stopping
            EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Model checkpoint
            ModelCheckpoint(
                filepath=checkpoint_path,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            
            # Learning rate reduction
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=0.00001,
                verbose=1
            )
        ]
        
        return callbacks
    
    def train(self, X_train, y_train, X_val, y_val, 
              epochs: int = 50, 
              batch_size: int = 32,
              checkpoint_path: str = 'data/models/best_model.h5') -> dict:
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels (one-hot encoded)
            X_val: Validation features
            y_val: Validation labels (one-hot encoded)
            epochs: Maximum number of epochs
            batch_size: Batch size
            checkpoint_path: Path to save best model
            
        Returns:
            dict: Training history
        """
        print("\n🚀 Starting Model Training...")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Validation samples: {len(X_val)}")
        print(f"   Epochs: {epochs}")
        print(f"   Batch size: {batch_size}")
        
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        # Get callbacks
        callbacks = self.get_callbacks(checkpoint_path)
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        print("\n✅ Training Complete!")
        
        return history.history
    
    def save_model(self, filepath: str):
        """
        Save trained model
        
        Args:
            filepath: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        self.model.save(filepath)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load trained model
        
        Args:
            filepath: Path to load model from
        """
        self.model = keras.models.load_model(filepath)
        print(f"✅ Model loaded from {filepath}")
        
        return self.model
    
    def predict(self, X, return_probabilities: bool = False):
        """
        Make predictions
        
        Args:
            X: Input features
            return_probabilities: Whether to return probabilities
            
        Returns:
            Predictions (class indices or probabilities)
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call build_model() or load_model() first.")
        
        predictions = self.model.predict(X, verbose=0)
        
        if return_probabilities:
            return predictions
        else:
            return np.argmax(predictions, axis=1)


def create_lstm_model(input_dim: int, num_classes: int, max_length: int = 50) -> keras.Model:
    """
    Alternative LSTM-based model architecture
    (Optional - for sequence-based input)
    
    Args:
        input_dim: Vocabulary size
        num_classes: Number of intent classes
        max_length: Maximum sequence length
        
    Returns:
        keras.Model: Compiled LSTM model
    """
    model = models.Sequential([
        layers.Input(shape=(max_length,)),
        layers.Embedding(input_dim=input_dim, output_dim=128),
        layers.LSTM(128, return_sequences=True),
        layers.Dropout(0.3),
        layers.LSTM(64),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax')
    ], name='lstm_intent_classifier')
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


if __name__ == "__main__":
    # Test model creation
    print("Testing model architecture...")
    
    # Create model with dummy parameters
    classifier = IntentClassifierModel(input_dim=5000, num_classes=27)
    model = classifier.build_model()
    
    print("\n✅ Model architecture test successful!")