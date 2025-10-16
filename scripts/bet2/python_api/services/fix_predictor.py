# Fix predictor to handle feature mismatch

with open('predictor.py', 'r') as f:
    content = f.read()

# Replace the _generate_features method
old_method = '''    def _generate_features(self, match_data: pd.DataFrame) -> np.ndarray:
        """Generate features for the match"""
        
        # Generate features for all data
        with_features = self.feature_engineer.generate_features(match_data)
        
        # Get the last row (our match to predict)
        match_features = with_features.iloc[-1]
        
        # Get feature names from engineer
        feature_names = self.feature_engineer.get_feature_names()
        
        # Extract feature values
        X = match_features[feature_names].values.reshape(1, -1)
        
        # Replace NaN with 0
        X = np.nan_to_num(X, 0)
        
        return X'''

new_method = '''    def _generate_features(self, match_data: pd.DataFrame) -> np.ndarray:
        """Generate features for the match"""
        
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            # Generate features for all data
            with_features = self.feature_engineer.generate_features(match_data)
        
        # Get the last row (our match to predict)
        match_features = with_features.iloc[-1]
        
        # Get expected features from model metadata
        metadata = self.model_manager.get_model_metadata('match_result')
        if metadata and 'feature_names' in metadata:
            expected_features = metadata['feature_names']
            
            # Build feature array with exact features expected by model
            X_list = []
            for feat in expected_features:
                if feat in match_features.index:
                    val = match_features[feat]
                    X_list.append(0 if pd.isna(val) else val)
                else:
                    X_list.append(0)  # Missing feature = 0
            
            X = np.array(X_list).reshape(1, -1)
        else:
            # Fallback
            feature_names = self.feature_engineer.get_feature_names()
            X = match_features[feature_names].values.reshape(1, -1)
            X = np.nan_to_num(X, 0)
        
        return X'''

content = content.replace(old_method, new_method)

with open('predictor.py', 'w') as f:
    f.write(content)

print("Fixed predictor.py to handle feature mismatch!")
