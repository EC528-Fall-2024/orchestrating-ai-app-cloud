import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Optional
import numpy as np

class WeatherDataset:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.scaler = StandardScaler()
        self.feature_names = None
        self.raw_data = None
        
    def load_and_preprocess(self) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        # Load data
        self.raw_data = pd.read_csv(self.data_path)
        
        # Store feature names
        self.feature_names = self.raw_data.drop(['Rain'], axis=1).columns.tolist()
        
        # Prepare features and target
        X = self.raw_data.drop(['Rain'], axis=1).values
        y = (self.raw_data['Rain'] == 'rain').astype(int).values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train_scaled)
        y_train_tensor = torch.FloatTensor(y_train)
        X_test_tensor = torch.FloatTensor(X_test_scaled)
        y_test_tensor = torch.FloatTensor(y_test)
        
        return X_train_tensor, X_test_tensor, y_train_tensor, y_test_tensor
    
    def get_feature_names(self) -> Optional[list[str]]:
        return self.feature_names
    
    def get_raw_data(self) -> Optional[pd.DataFrame]:
        return self.raw_data 