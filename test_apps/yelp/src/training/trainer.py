import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import re

class ReviewPredictor:
    def __init__(self, model: nn.Module):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Initializing ReviewPredictor with device: {self.device}")
        self.model = model.to(self.device)
        self.history = {'loss': [], 'val_loss': [], 'accuracy': [], 'val_accuracy': []}
        print("Model moved to device and history initialized")
        
    def train(
        self,
        train_dataloader: DataLoader,
        val_dataloader: DataLoader,
        num_epochs: int = 10,
        learning_rate: float = 0.001
    ) -> Dict[str, List[float]]:
        print(f"\nStarting training with {num_epochs} epochs")
        print(f"Training batches: {len(train_dataloader)}, Validation batches: {len(val_dataloader)}")
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        
        for epoch in range(num_epochs):
            # Training phase
            self.model.train()
            total_loss = 0
            correct = 0
            total = 0
            
            print(f"\nEpoch [{epoch+1}/{num_epochs}]")
            for batch_idx, batch in enumerate(train_dataloader):
                if batch_idx % 10 == 0:  # Print progress every 10 batches
                    print(f"  Processing batch {batch_idx}/{len(train_dataloader)}", end='\r')
                
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(input_ids, attention_mask)
                loss = criterion(outputs, labels)
                
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
            
            avg_train_loss = total_loss / len(train_dataloader)
            train_accuracy = correct / total
            
            # Validation phase
            print("\nRunning validation...", end='\r')
            val_loss, val_accuracy = self._validate(val_dataloader, criterion)
            
            # Store metrics
            self.history['loss'].append(avg_train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['accuracy'].append(train_accuracy)
            self.history['val_accuracy'].append(val_accuracy)
            
            print(f'\nEpoch [{epoch+1}/{num_epochs}], '
                  f'Loss: {avg_train_loss:.4f}, '
                  f'Accuracy: {train_accuracy:.4f}, '
                  f'Val Loss: {val_loss:.4f}, '
                  f'Val Accuracy: {val_accuracy:.4f}')
        
        return self.history
    
    def _validate(self, val_dataloader: DataLoader, criterion: nn.Module) -> Tuple[float, float]:
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in val_dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask)
                loss = criterion(outputs, labels)
                
                total_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        return total_loss / len(val_dataloader), correct / total
    
    def evaluate(self, test_dataloader: DataLoader) -> Tuple[float, Dict]:
        self.model.eval()
        all_predictions = []
        all_labels = []
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in test_dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask)
                _, predicted = torch.max(outputs.data, 1)
                
                all_predictions.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = correct / total
        report = classification_report(
            all_labels,
            all_predictions,
            labels=[0, 1, 2, 3, 4],
            target_names=['1 star', '2 stars', '3 stars', '4 stars', '5 stars'],
            output_dict=True
        )
        
        # Plot confusion matrix
        cm = confusion_matrix(all_labels, all_predictions)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig('confusion_matrix.png')
        plt.close()
        
        return accuracy, report
    
    def predict(self, texts: List[str], word_to_idx: dict) -> Tuple[np.ndarray, np.ndarray]:
        self.model.eval()
        
        # Tokenize texts
        max_length = 512
        input_ids = []
        attention_masks = []
        
        for text in texts:
            # Simple tokenization
            words = text.lower()
            words = re.sub(r'[^\w\s]', '', words)
            words = words.split()
            
            # Convert to indices with padding/truncation
            indices = [word_to_idx.get(word, word_to_idx['<UNK>']) for word in words[:max_length]]
            indices = indices + [word_to_idx['<PAD>']] * (max_length - len(indices))
            
            # Create attention mask
            attention_mask = [1] * min(len(words), max_length) + [0] * (max_length - min(len(words), max_length))
            
            input_ids.append(indices)
            attention_masks.append(attention_mask)
        
        input_ids = torch.tensor(input_ids, dtype=torch.long).to(self.device)
        attention_mask = torch.tensor(attention_masks, dtype=torch.float).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask)
            probabilities = torch.softmax(outputs, dim=1)
            predictions = torch.argmax(outputs, dim=1)
        
        return predictions.cpu().numpy(), probabilities.cpu().numpy()

    def plot_training_history(self):
        plt.figure(figsize=(12, 4))
        
        # Plot loss
        plt.subplot(1, 2, 1)
        plt.plot(self.history['loss'], label='Training Loss')
        plt.plot(self.history['val_loss'], label='Validation Loss')
        plt.title('Training History - Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Plot accuracy
        plt.subplot(1, 2, 2)
        plt.plot(self.history['accuracy'], label='Training Accuracy')
        plt.plot(self.history['val_accuracy'], label='Validation Accuracy')
        plt.title('Training History - Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('training_history.png')
        plt.close() 