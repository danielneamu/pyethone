    def predict_to_json(self, home_team, away_team, output_file=None):
        """
        Predict and save as JSON
        
        Args:
            home_team: Home team
            away_team: Away team
            output_file: Optional file path to save JSON
        
        Returns:
            JSON string
        """
        predictions = self.predict_match(home_team, away_team)
        
        # Convert numpy types to native Python types for JSON serialization
        predictions = self._convert_to_json_serializable(predictions)
        
        json_output = json.dumps(predictions, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_output)
            print(f"Predictions saved to: {output_file}")
        
        return json_output
    
    def _convert_to_json_serializable(self, obj):
        """
        Recursively convert numpy types to native Python types
        
        Args:
            obj: Object to convert (dict, list, numpy type, etc.)
        
        Returns:
            JSON-serializable object
        """
        if isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
