import torch
import torch.nn as nn
from typing import List

class YelpClassifier(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int,
        hidden_sizes: List[int],
        num_classes: int = 5,
        dropout_rate: float = 0.3
    ):
        super(YelpClassifier, self).__init__()
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        
        # LSTM layer
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_sizes[0],
            batch_first=True,
            bidirectional=True
        )
        
        # Fully connected layers
        layers = []
        prev_size = hidden_sizes[0] * 2  # * 2 for bidirectional
        
        for hidden_size in hidden_sizes[1:]:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_size = hidden_size
        
        # Output layer
        layers.append(nn.Linear(prev_size, num_classes))
        
        self.classifier = nn.Sequential(*layers)
        
    def forward(self, input_ids, attention_mask):
        # Embed input tokens
        embedded = self.embedding(input_ids)
        
        # Apply attention mask
        embedded = embedded * attention_mask.unsqueeze(-1)
        
        # Pass through LSTM
        lstm_out, _ = self.lstm(embedded)
        
        # Global max pooling
        pooled = torch.max(lstm_out, dim=1)[0]
        
        # Pass through classifier
        logits = self.classifier(pooled)
        
        return logits 