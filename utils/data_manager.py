import pandas as pd
import os
from datetime import datetime

def load_historical_data():
    """
    Load historical crop analysis data
    """
    try:
        if os.path.exists('data/sample_data.csv'):
            return pd.read_csv('data/sample_data.csv')
        return pd.DataFrame(columns=['date', 'ndvi', 'green_ratio', 'stress_level'])
    except Exception as e:
        print(f"Error loading historical data: {e}")
        return pd.DataFrame(columns=['date', 'ndvi', 'green_ratio', 'stress_level'])

def save_analysis_result(result):
    """
    Save new analysis result to CSV
    """
    try:
        df = load_historical_data()
        new_row = pd.DataFrame([result])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        df.to_csv('data/sample_data.csv', index=False)
    except Exception as e:
        print(f"Error saving analysis result: {e}")
