"""
Quick test of feature engineering
"""
import sys
sys.path.insert(0, '.')

from services.data_loader import DataLoader
from services.feature_engineering import FeatureEngineer

print("="*80)
print("Testing Feature Engineering")
print("="*80)

# Load data
print("\n1. Loading data...")
loader = DataLoader('premier_league')
df = loader.load_season('2025-2026')
print(f"   Loaded {len(df)} rows, {df.shape[1]} columns")

# Generate features
print("\n2. Generating features...")
engineer = FeatureEngineer(rolling_windows=[3, 5, 10])
df_with_features = engineer.generate_features(df)

print(f"   Original columns: {df.shape[1]}")
print(f"   With features: {df_with_features.shape[1]}")
print(f"   Total features added: {engineer.get_feature_count()}")

print("\n3. Sample features:")
feature_cols = engineer.get_feature_names()[:10]
for feat in feature_cols:
    if feat in df_with_features.columns:
        print(f"   - {feat}")

print("\n" + "="*80)
print("Feature engineering test complete!")
print("="*80)
