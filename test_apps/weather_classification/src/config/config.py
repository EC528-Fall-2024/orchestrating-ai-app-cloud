from dataclasses import dataclass, field
from typing import List

@dataclass
class ModelConfig:
    hidden_sizes: list = field(default_factory=lambda: [64, 32])
    dropout_rate: float = 0.2
    
@dataclass
class TrainingConfig:
    num_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    random_seed: int = 0 