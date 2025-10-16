import re

with open('services/predictor.py', 'r') as f:
    content = f.read()

# Find and replace the _generate_features method completely
pattern = r'def _generate_features\(self.*?return X'
replacement = '''def _generate_features(self, match_data: pd.DataFrame) -> np.ndarray:
        """Generate features for the match"""
        
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            with_features = self.feature_engineer.generate_features(match_data)
        
        # Get last row
        match_features = with_features.iloc[-1]
        
        # Get expected features from model
        metadata = self.model_manager.get_model_metadata('match_result')
        if metadata and 'feature_names' in metadata:
            expected_features = metadata['feature_names']
            
            # Build feature array matching trained model EXACTLY
            X_list = []
            for feat in expected_features:
                val = match_features.get(feat, 0)
                X_list.append(0 if pd.isna(val) else float(val))
            
            X = np.array(X_list).reshape(1, -1)
        else:
            # Fallback
            feature_names = self.feature_engineer.get_feature_names()
            X = match_features[feature_names].values.reshape(1, -1)
            X = np.nan_to_num(X, 0)
        
        return X'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('services/predictor.py', 'w') as f:
    f.write(content)

print("✓ Fixed predictor.py to handle feature mismatch")
