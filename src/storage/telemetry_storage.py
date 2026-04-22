"""
Telemetry Storage Module - Handles CSV storage without interfering with existing telemetry
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List


class TelemetryStorage:
    """
    Separate utility for storing telemetry data to CSV
    Does not modify existing telemetry generation
    """
    
    def __init__(self, csv_path: str = "data/telemetry.csv"):
        self.csv_path = csv_path
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    def save_telemetry(self, device_id: str, device_name: str, 
                       baseline: float, current: float, 
                       is_anomaly: bool = False):
        """
        Save single telemetry record to CSV (append mode only)
        """
        df = pd.DataFrame([{
            'timestamp': datetime.now().isoformat(),
            'device_id': device_id,
            'device_name': device_name,
            'baseline_traffic': round(baseline, 2),
            'current_traffic': round(current, 2),
            'is_anomaly': is_anomaly
        }])
        
        if os.path.exists(self.csv_path):
            existing = pd.read_csv(self.csv_path)
            df = pd.concat([existing, df], ignore_index=True)
        
        df.to_csv(self.csv_path, index=False)
    
    def save_batch(self, telemetry_data: Dict[str, Dict]):
        """
        Save batch of telemetry records
        """
        records = []
        for device_id, data in telemetry_data.items():
            records.append({
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'device_id': device_id,
                'device_name': data.get('device_name', 'unknown'),
                'baseline_traffic': data.get('baseline', 0),
                'current_traffic': data.get('current', 0),
                'is_anomaly': data.get('is_anomaly', False)
            })
        
        if records:
            df = pd.DataFrame(records)
            if os.path.exists(self.csv_path):
                existing = pd.read_csv(self.csv_path)
                df = pd.concat([existing, df], ignore_index=True)
            df.to_csv(self.csv_path, index=False)
    
    def get_telemetry_history(self, limit: int = 100) -> pd.DataFrame:
        """
        Retrieve telemetry history
        """
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path)
            return df.tail(limit)
        return pd.DataFrame()
    
    def get_device_history(self, device_id: str, limit: int = 50) -> pd.DataFrame:
        """
        Retrieve history for specific device
        """
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path)
            device_df = df[df['device_id'] == device_id]
            return device_df.tail(limit)
        return pd.DataFrame()