# Fix for model_trainer.py - convert to numpy arrays for XGBoost

with open('services/model_trainer.py', 'r') as f:
    lines = f.readlines()

# Find and replace the prepare methods
output = []
skip_until = None

for i, line in enumerate(lines):
    if skip_until and i < skip_until:
        continue
    
    if 'def _prepare_match_result_data' in line:
        # Replace entire method
        output.append(line)  # Keep def line
        output.append('''        """Prepare data for match result model"""
        
        df = df.copy()
        
        # Create target based on venue
        def map_result(row):
            if row['venue'] == 'Home':
                return {'W': 0, 'D': 1, 'L': 2}[row['result']]
            else:  # Away
                return {'W': 2, 'D': 1, 'L': 0}[row['result']]
        
        y = df.apply(map_result, axis=1)
        
        # Get features
        available_features = [col for col in feature_columns if col in df.columns]
        X = df[available_features].fillna(0)
        
        # Convert to numpy arrays
        return X.values, y.values
''')
        # Skip until next method
        for j in range(i+1, len(lines)):
            if lines[j].strip().startswith('def '):
                skip_until = j
                break
    
    elif 'def _prepare_goals_data' in line:
        output.append(line)
        output.append('''        """Prepare data for goals Over/Under model"""
        
        df = df.copy()
        total_goals = df['goals_for'] + df['goals_against']
        y = (total_goals > threshold).astype(int)
        
        available_features = [col for col in feature_columns if col in df.columns]
        X = df[available_features].fillna(0)
        
        # Convert to numpy arrays
        return X.values, y.values
''')
        for j in range(i+1, len(lines)):
            if lines[j].strip().startswith('def '):
                skip_until = j
                break
    
    elif 'def _prepare_btts_data' in line:
        output.append(line)
        output.append('''        """Prepare data for BTTS model"""
        
        df = df.copy()
        y = ((df['goals_for'] > 0) & (df['goals_against'] > 0)).astype(int)
        
        available_features = [col for col in feature_columns if col in df.columns]
        X = df[available_features].fillna(0)
        
        # Convert to numpy arrays
        return X.values, y.values
''')
        for j in range(i+1, len(lines)):
            if lines[j].strip().startswith('def '):
                skip_until = j
                break
    else:
        if not skip_until or i >= skip_until:
            output.append(line)
            skip_until = None

with open('services/model_trainer.py', 'w') as f:
    f.writelines(output)

print("Fixed! Converted DataFrame to numpy arrays for XGBoost.")
