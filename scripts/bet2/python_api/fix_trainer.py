# Quick fix for model_trainer.py
import re

with open('services/model_trainer.py', 'r') as f:
    content = f.read()

# Fix the _prepare_match_result_data method
old_code = '''        # Get features
        X = df[feature_columns].fillna(0)
        
        return X, y'''

new_code = '''        # Get features - only use columns that exist
        available_features = [col for col in feature_columns if col in df.columns]
        X = df[available_features].copy()
        X = X.fillna(0).astype('float64')
        
        return X, y'''

content = content.replace(old_code, new_code)

# Also fix _prepare_goals_data
old_goals = '''        X = df[feature_columns].fillna(0)
        
        return X, y'''

new_goals = '''        available_features = [col for col in feature_columns if col in df.columns]
        X = df[available_features].copy()
        X = X.fillna(0).astype('float64')
        
        return X, y'''

content = content.replace(old_goals, new_goals)

# Also fix _prepare_btts_data  
old_btts = '''        X = df[feature_columns].fillna(0)
        
        return X, y'''

new_btts = '''        available_features = [col for col in feature_columns if col in df.columns]
        X = df[available_features].copy()
        X = X.fillna(0).astype('float64')
        
        return X, y'''

# Only replace if not already replaced
if 'available_features' not in content:
    content = content.replace(old_btts, new_btts)

with open('services/model_trainer.py', 'w') as f:
    f.write(content)

print("Fixed model_trainer.py!")
