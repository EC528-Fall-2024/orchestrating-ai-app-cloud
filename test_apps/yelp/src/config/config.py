from dataclasses import dataclass, field
from typing import List

@dataclass
class ModelConfig:
    embedding_dim: int = 100
    hidden_sizes: list = field(default_factory=lambda: [256, 128])
    dropout_rate: float = 0.3
    max_sequence_length: int = 512  # Maximum length of input text
    
@dataclass
class TrainingConfig:
    num_epochs: int = 10
    batch_size: int = 64
    learning_rate: float = 0.001
    random_seed: int = 42 