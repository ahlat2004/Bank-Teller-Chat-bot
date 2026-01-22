"""
WP2 Complete Runner Script
Executes all WP2 tasks in sequence
Place this in: backend/app/ml/run_wp2.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.data_loader import DatasetLoader
from ml.preprocessor import TextPreprocessor
import pandas as pd


def run_wp2():
    """
    Complete WP2 execution pipeline
    """
    print("=" * 70)
    print(" " * 15 + "BANK TELLER CHATBOT - WP2")
    print(" " * 10 + "Dataset Acquisition & Preprocessing")
    print("=" * 70)
    
    try:
        # Initialize components
        loader = DatasetLoader(raw_data_path='data/raw')
        preprocessor = TextPreprocessor()
        
        # TASK 1: Download Dataset
        print("\n📥 TASK 1: Downloading Dataset")
        print("-" * 70)
        df_raw = loader.download_dataset()
        
        # TASK 2: Data Exploration
        print("\n📊 TASK 2: Data Exploration")
        print("-" * 70)
        stats = loader.analyze_dataset(df_raw)
        
        # TASK 3: Text Preprocessing
        print("\n🔧 TASK 3: Text Preprocessing")
        print("-" * 70)
        df_processed = preprocessor.preprocess_dataset(df_raw)
        
        # Show preprocessing examples
        print("\n📝 Preprocessing Examples:")
        print("-" * 70)
        text_col = 'instruction' if 'instruction' in df_raw.columns else 'utterance'
        
        for i in range(min(3, len(df_processed))):
            print(f"\nExample {i+1}:")
            print(f"  Original:  {df_raw.iloc[i][text_col]}")
            print(f"  Cleaned:   {df_processed.iloc[i]['cleaned_text']}")
            print(f"  Intent:    {df_processed.iloc[i]['intent']}")
        
        # TASK 4: Create Intent Mapping
        print("\n🗺️  TASK 4: Creating Intent Mapping")
        print("-" * 70)
        intent_mapping = preprocessor.create_intent_mapping(df_processed, output_path='data')
        
        # TASK 5: Create Data Splits
        print("\n✂️  TASK 5: Creating Train/Val/Test Splits")
        print("-" * 70)
        splits = preprocessor.create_splits(
            df_processed,
            train_size=0.70,
            val_size=0.15,
            test_size=0.15,
            random_state=42
        )
        
        # Verify stratification
        print("\n📊 Verifying Stratification (Top 5 Intents):")
        print("-" * 70)
        top_intents = df_processed['intent'].value_counts().head(5).index
        
        for intent in top_intents:
            train_count = (splits['train']['intent'] == intent).sum()
            val_count = (splits['val']['intent'] == intent).sum()
            test_count = (splits['test']['intent'] == intent).sum()
            total = train_count + val_count + test_count
            
            print(f"\n  Intent: {intent}")
            print(f"    Train: {train_count:4d} ({train_count/total*100:5.1f}%)")
            print(f"    Val:   {val_count:4d} ({val_count/total*100:5.1f}%)")
            print(f"    Test:  {test_count:4d} ({test_count/total*100:5.1f}%)")
        
        # TASK 6: Save Splits
        print("\n💾 TASK 6: Saving Data Splits")
        print("-" * 70)
        preprocessor.save_splits(splits, output_path='data/processed')
        
        # Final Summary
        print("\n" + "=" * 70)
        print(" " * 25 + "WP2 COMPLETE! ✅")
        print("=" * 70)
        
        print("\n📊 FINAL STATISTICS:")
        print("-" * 70)
        print(f"  Total Raw Samples:       {len(df_raw):6,d}")
        print(f"  Processed Samples:       {len(df_processed):6,d}")
        print(f"  Unique Intents:          {intent_mapping['num_intents']:6d}")
        print(f"  Training Samples:        {len(splits['train']):6,d} (70.0%)")
        print(f"  Validation Samples:      {len(splits['val']):6,d} (15.0%)")
        print(f"  Test Samples:            {len(splits['test']):6,d} (15.0%)")
        
        print("\n📁 FILES CREATED:")
        print("-" * 70)
        files_created = [
            "data/raw/banking_dataset_raw.csv",
            "data/raw/data_analysis_report.json",
            "data/processed/train.csv",
            "data/processed/val.csv",
            "data/processed/test.csv",
            "data/intent_mapping.json"
        ]
        
        for file in files_created:
            exists = "✅" if os.path.exists(file) else "❌"
            size = os.path.getsize(file) / 1024 if os.path.exists(file) else 0
            print(f"  {exists} {file} ({size:.1f} KB)")
        
        print("\n🎯 INTENT MAPPING PREVIEW:")
        print("-" * 70)
        print(f"  Total Intents: {len(intent_mapping['intent_to_id'])}")
        print("\n  Sample Intents:")
        for i, (intent, idx) in enumerate(list(intent_mapping['intent_to_id'].items())[:10]):
            print(f"    [{idx:2d}] {intent}")
        
        if len(intent_mapping['intent_to_id']) > 10:
            print(f"    ... and {len(intent_mapping['intent_to_id']) - 10} more")
        
        print("\n🚀 NEXT STEPS:")
        print("-" * 70)
        print("  1. Review data/intent_mapping.json for intent categories")
        print("  2. Check data/processed/ folder for train/val/test splits")
        print("  3. Proceed to WP3: Intent Classification Model Training")
        print("  4. Expected model performance target: F1 > 0.85")
        
        print("\n" + "=" * 70)
        print(" " * 20 + "WP2 Successfully Completed!")
        print("=" * 70 + "\n")
        
        return {
            'raw_data': df_raw,
            'processed_data': df_processed,
            'intent_mapping': intent_mapping,
            'splits': splits,
            'stats': stats
        }
        
    except Exception as e:
        print(f"\n❌ ERROR in WP2 execution:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = run_wp2()
    
    if result:
        print("✅ WP2 completed successfully!")
        print(f"   You can now proceed to WP3")
    else:
        print("❌ WP2 failed. Please check the errors above.")