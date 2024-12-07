import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

class RainPredictor:
    def __init__(self, model: nn.Module, scaler: StandardScaler):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.scaler = scaler
        self.history = {'loss': [], 'val_loss': []}
        print(f"Using device: {self.device}")
        
    def train(
        self,
        X_train: torch.Tensor,
        y_train: torch.Tensor,
        X_val: torch.Tensor,
        y_val: torch.Tensor,
        num_epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001
    ) -> Dict[str, List[float]]:
        # Move data to device
        X_train = X_train.to(self.device)
        y_train = y_train.to(self.device)
        X_val = X_val.to(self.device)
        y_val = y_val.to(self.device)

        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        n_batches = len(X_train) // batch_size
        
        for epoch in range(num_epochs):
            # Training phase
            self.model.train()
            total_loss = 0
            
            for i in range(n_batches):
                start_idx = i * batch_size
                end_idx = start_idx + batch_size
                
                batch_X = X_train[start_idx:end_idx]
                batch_y = y_train[start_idx:end_idx]
                
                outputs = self.model(batch_X)
                loss = criterion(outputs.squeeze(), batch_y)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_train_loss = total_loss / n_batches
            self.history['loss'].append(avg_train_loss)
            
            # Validation phase
            val_loss = self._validate(X_val, y_val, criterion)
            self.history['val_loss'].append(val_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{num_epochs}], '
                      f'Train Loss: {avg_train_loss:.4f}, '
                      f'Val Loss: {val_loss:.4f}')
        
        return self.history
    
    def _validate(self, X_val: torch.Tensor, y_val: torch.Tensor, criterion: nn.Module) -> float:
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X_val)
            val_loss = criterion(outputs.squeeze(), y_val).item()
        return val_loss
    
    def evaluate(self, X_test: torch.Tensor, y_test: torch.Tensor) -> Tuple[float, Dict]:
        X_test = X_test.to(self.device)
        y_test = y_test.to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            test_outputs = self.model(X_test)
            predicted = (test_outputs.squeeze() >= 0.5).float()
            accuracy = (predicted == y_test).float().mean()
            
            # Move tensors to CPU for numpy conversion
            y_pred = predicted.cpu().numpy()
            y_true = y_test.cpu().numpy()
            report = classification_report(y_true, y_pred, output_dict=True)
            
            # Generate confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            
            # Plot confusion matrix
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title('Confusion Matrix')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            plt.savefig('confusion_matrix.png')
            plt.close()
            
        return accuracy.item(), report
    
    def predict(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        scaled_features = self.scaler.transform(features)
        features_tensor = torch.FloatTensor(scaled_features).to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(features_tensor)
            predictions = (outputs.squeeze() >= 0.5).float()
            probabilities = outputs.squeeze()
        
        return predictions.cpu().numpy(), probabilities.cpu().numpy()

    def plot_training_history(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.history['loss'], label='Training Loss')
        plt.plot(self.history['val_loss'], label='Validation Loss')
        plt.title('Training History')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig('training_history.png')
        plt.close() 