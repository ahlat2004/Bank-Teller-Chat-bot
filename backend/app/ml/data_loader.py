"""
Dataset Acquisition Module
Downloads and loads the Bitext banking dataset from HuggingFace
"""

from datasets import load_dataset
import pandas as pd
import os
import json
from typing import Dict, Tuple

class DatasetLoader:
    def __init__(self, raw_data_path: str = 'data/raw'):
        self.raw_data_path = raw_data_path
        os.makedirs(raw_data_path, exist_ok=True)
    
    def download_dataset(self) -> pd.DataFrame:
        """
        Download Bitext banking dataset from HuggingFace using parquet
        
        Returns:
            pd.DataFrame: Raw dataset
        """
        print("📥 Downloading dataset from HuggingFace...")
        
        try:
            # Download using pandas read_parquet with HuggingFace link
            parquet_url = "hf://datasets/bitext/Bitext-retail-banking-llm-chatbot-training-dataset/bitext-retail-banking-llm-chatbot-training-dataset.parquet"
            df = pd.read_parquet(parquet_url)
            
            # Save raw data
            raw_file = os.path.join(self.raw_data_path, 'banking_dataset_raw.csv')
            df.to_csv(raw_file, index=False)
            
            print(f"✅ Dataset downloaded successfully!")
            print(f"   Total samples: {len(df)}")
            print(f"   Columns: {df.columns.tolist()}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error downloading dataset: {e}")
            raise
    
    def load_raw_dataset(self) -> pd.DataFrame:
        """
        Load previously downloaded raw dataset
        
        Returns:
            pd.DataFrame: Raw dataset
        """
        raw_file = os.path.join(self.raw_data_path, 'banking_dataset_raw.csv')
        
        if not os.path.exists(raw_file):
            print("⚠️  Raw dataset not found. Downloading...")
            return self.download_dataset()
        
        print(f"📂 Loading raw dataset from {raw_file}")
        df = pd.read_csv(raw_file)
        print(f"✅ Loaded {len(df)} samples")
        
        return df
    
    def analyze_dataset(self, df: pd.DataFrame) -> Dict:
        """
        Analyze dataset statistics
        
        Args:
            df: Raw dataset
            
        Returns:
            Dict: Analysis statistics
        """
        print("\n📊 Dataset Analysis:")
        print("=" * 50)
        
        # Basic stats
        stats = {
            'total_samples': len(df),
            'columns': df.columns.tolist(),
            'intent_distribution': df['intent'].value_counts().to_dict() if 'intent' in df.columns else {},
            'unique_intents': df['intent'].nunique() if 'intent' in df.columns else 0,
            'avg_utterance_length': df['instruction'].apply(len).mean() if 'instruction' in df.columns else 0,
            'missing_values': df.isnull().sum().to_dict()
        }
        
        # Print analysis
        print(f"Total Samples: {stats['total_samples']}")
        print(f"Unique Intents: {stats['unique_intents']}")
        print(f"Average Utterance Length: {stats['avg_utterance_length']:.2f} characters")
        
        print("\n🎯 Intent Distribution (Top 10):")
        intent_counts = df['intent'].value_counts().head(10) if 'intent' in df.columns else []
        for intent, count in intent_counts.items():
            print(f"  {intent}: {count} samples")
        
        print("\n⚠️  Missing Values:")
        for col, count in stats['missing_values'].items():
            if count > 0:
                print(f"  {col}: {count} missing")
        
        # Save analysis report
        analysis_file = os.path.join(self.raw_data_path, 'data_analysis_report.json')
        with open(analysis_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n💾 Analysis saved to {analysis_file}")
        
        return stats


def main():
    """Main execution function"""
    loader = DatasetLoader()
    
    # Download or load dataset
    df = loader.download_dataset()
    
    # Analyze dataset
    stats = loader.analyze_dataset(df)
    
    print("\n✅ WP2 Step 1: Dataset Acquisition Complete!")
    print("\nFirst 3 samples:")
    print(df.head(3))
    
    return df, stats


if __name__ == "__main__":
    df, stats = main()