"""
Text Preprocessing Module
Cleans and normalizes banking chatbot utterances
"""

import re
import pandas as pd
import numpy as np
from typing import List, Dict
import json
import os
from sklearn.model_selection import train_test_split


class TextPreprocessor:
    def __init__(self):
        # Banking-specific terms to preserve
        self.banking_terms = [
            'atm', 'pin', 'cvv', 'iban', 'swift', 'neft', 'rtgs',
            'pkr', 'usd', 'eur', 'gbp', 'account', 'balance', 'transaction'
        ]
        
        # Currency symbols to preserve
        self.currency_pattern = r'(PKR|Rs\.?|₨|\$|€|£)\s*\d+'
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text while preserving banking terms
        
        Args:
            text: Raw input text
            
        Returns:
            str: Cleaned text
        """
        if pd.isna(text):
            return ""
        
        # Convert to string and lowercase
        text = str(text).lower().strip()
        
        # Preserve currency amounts (mark them temporarily)
        currency_matches = re.findall(self.currency_pattern, text, re.IGNORECASE)
        for i, match in enumerate(currency_matches):
            text = text.replace(match, f'__CURRENCY_{i}__', 1)
        
        # Remove special characters but keep spaces, numbers, and banking terms
        text = re.sub(r'[^a-z0-9\s_]', ' ', text)
        
        # Restore currency markers
        for i, match in enumerate(currency_matches):
            text = text.replace(f'__currency_{i}__', match.lower())
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def normalize_currency(self, text: str) -> str:
        """
        Normalize currency representations
        
        Args:
            text: Input text with currency
            
        Returns:
            str: Text with normalized currency
        """
        # Normalize PKR variations
        text = re.sub(r'rs\.?\s*(\d+)', r'pkr \1', text, flags=re.IGNORECASE)
        text = re.sub(r'₨\s*(\d+)', r'pkr \1', text)
        
        # Normalize dollar signs
        text = re.sub(r'\$\s*(\d+)', r'usd \1', text)
        
        # Remove commas from numbers
        text = re.sub(r'(\d+),(\d+)', r'\1\2', text)
        
        return text
    
    def preprocess_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess entire dataset
        
        Args:
            df: Raw dataset
            
        Returns:
            pd.DataFrame: Preprocessed dataset
        """
        print("\n🔧 Preprocessing dataset...")
        
        df_processed = df.copy()
        
        # Determine the text column (might be 'instruction', 'utterance', or 'text')
        text_column = None
        for col in ['instruction', 'utterance', 'text', 'query']:
            if col in df.columns:
                text_column = col
                break
        
        if text_column is None:
            raise ValueError("Could not find text column in dataset")
        
        print(f"   Text column detected: '{text_column}'")
        
        # Clean text
        print("   Cleaning text...")
        df_processed['cleaned_text'] = df_processed[text_column].apply(self.clean_text)
        
        # Normalize currency
        print("   Normalizing currency...")
        df_processed['cleaned_text'] = df_processed['cleaned_text'].apply(self.normalize_currency)
        
        # Remove empty samples
        initial_count = len(df_processed)
        df_processed = df_processed[df_processed['cleaned_text'].str.len() > 0]
        removed_count = initial_count - len(df_processed)
        
        if removed_count > 0:
            print(f"   Removed {removed_count} empty samples")
        
        # Ensure intent column exists
        if 'intent' not in df_processed.columns and 'category' in df_processed.columns:
            df_processed['intent'] = df_processed['category']
        
        print(f"✅ Preprocessing complete: {len(df_processed)} samples")
        
        return df_processed
    
    def create_intent_mapping(self, df: pd.DataFrame, output_path: str = 'data') -> Dict:
        """
        Create intent to ID mapping
        
        Args:
            df: Preprocessed dataset
            output_path: Path to save mapping
            
        Returns:
            Dict: Intent mapping
        """
        print("\n🗺️  Creating intent mapping...")
        
        # Get unique intents
        unique_intents = sorted(df['intent'].unique())
        
        # Create mapping
        intent_to_id = {intent: idx for idx, intent in enumerate(unique_intents)}
        id_to_intent = {idx: intent for intent, idx in intent_to_id.items()}
        
        mapping = {
            'intent_to_id': intent_to_id,
            'id_to_intent': id_to_intent,
            'num_intents': len(unique_intents)
        }
        
        # Save mapping
        os.makedirs(output_path, exist_ok=True)
        mapping_file = os.path.join(output_path, 'intent_mapping.json')
        
        with open(mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print(f"✅ Intent mapping saved to {mapping_file}")
        print(f"   Total intents: {len(unique_intents)}")
        
        # Print first 10 intents
        print("\n🎯 Intent Mapping (first 10):")
        for intent, idx in list(intent_to_id.items())[:10]:
            print(f"   {idx}: {intent}")
        
        return mapping
    
    def create_splits(self, df: pd.DataFrame, 
                     train_size: float = 0.7,
                     val_size: float = 0.15,
                     test_size: float = 0.15,
                     random_state: int = 42) -> Dict[str, pd.DataFrame]:
        """
        Create stratified train/val/test splits
        
        Args:
            df: Preprocessed dataset
            train_size: Training set proportion
            val_size: Validation set proportion
            test_size: Test set proportion
            random_state: Random seed for reproducibility
            
        Returns:
            Dict: Dictionary with train, val, test DataFrames
        """
        print("\n✂️  Creating data splits...")
        
        # Verify proportions sum to 1
        assert abs(train_size + val_size + test_size - 1.0) < 0.01, "Splits must sum to 1"
        
        # First split: separate test set
        train_val, test = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df['intent']
        )
        
        # Second split: separate validation from training
        val_proportion = val_size / (train_size + val_size)
        train, val = train_test_split(
            train_val,
            test_size=val_proportion,
            random_state=random_state,
            stratify=train_val['intent']
        )
        
        splits = {
            'train': train,
            'val': val,
            'test': test
        }
        
        # Print statistics
        print(f"✅ Splits created:")
        print(f"   Training:   {len(train):5d} samples ({len(train)/len(df)*100:.1f}%)")
        print(f"   Validation: {len(val):5d} samples ({len(val)/len(df)*100:.1f}%)")
        print(f"   Test:       {len(test):5d} samples ({len(test)/len(df)*100:.1f}%)")
        
        return splits
    
    def save_splits(self, splits: Dict[str, pd.DataFrame], output_path: str = 'data/processed'):
        """
        Save train/val/test splits to CSV files
        
        Args:
            splits: Dictionary with train, val, test DataFrames
            output_path: Path to save files
        """
        print(f"\n💾 Saving splits to {output_path}...")
        
        os.makedirs(output_path, exist_ok=True)
        
        for split_name, split_df in splits.items():
            file_path = os.path.join(output_path, f'{split_name}.csv')
            split_df.to_csv(file_path, index=False)
            print(f"   ✅ Saved {split_name}.csv ({len(split_df)} samples)")
        
        print("✅ All splits saved successfully!")


def main():
    """Main execution function for WP2"""
    from data_loader import DatasetLoader
    
    print("=" * 60)
    print("WP2: DATASET ACQUISITION & PREPROCESSING")
    print("=" * 60)
    
    # Step 1: Load dataset
    loader = DatasetLoader()
    df_raw = loader.load_raw_dataset()
    stats = loader.analyze_dataset(df_raw)
    
    # Step 2: Preprocess
    preprocessor = TextPreprocessor()
    df_processed = preprocessor.preprocess_dataset(df_raw)
    
    # Step 3: Create intent mapping
    intent_mapping = preprocessor.create_intent_mapping(df_processed)
    
    # Step 4: Create splits
    splits = preprocessor.create_splits(df_processed)
    
    # Step 5: Save splits
    preprocessor.save_splits(splits)
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ WP2 COMPLETE!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   Raw samples:        {len(df_raw)}")
    print(f"   Processed samples:  {len(df_processed)}")
    print(f"   Unique intents:     {intent_mapping['num_intents']}")
    print(f"   Training samples:   {len(splits['train'])}")
    print(f"   Validation samples: {len(splits['val'])}")
    print(f"   Test samples:       {len(splits['test'])}")
    
    print("\n📁 Files Created:")
    print("   ✅ data/raw/banking_dataset_raw.csv")
    print("   ✅ data/raw/data_analysis_report.json")
    print("   ✅ data/processed/train.csv")
    print("   ✅ data/processed/val.csv")
    print("   ✅ data/processed/test.csv")
    print("   ✅ data/intent_mapping.json")
    
    print("\n🚀 Ready for WP3: Intent Classification Model Training!")
    
    return df_processed, intent_mapping, splits


if __name__ == "__main__":
    df_processed, intent_mapping, splits = main()