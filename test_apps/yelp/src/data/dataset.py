import torch
from torch.utils.data import Dataset, DataLoader
from typing import Tuple, Optional
import numpy as np
import pandas as pd
from collections import Counter
import re

class YelpDataset:
    def __init__(self, train_path: str, test_path: str, max_vocab_size: int = 50000):
        self.train_path = train_path
        self.test_path = test_path
        self.max_vocab_size = max_vocab_size
        self.word_to_idx = None
        self.vocab_size = None
        
    def build_vocabulary(self, texts):
        # Tokenize and count words
        word_counts = Counter()
        for text in texts:
            words = self._tokenize(text)
            word_counts.update(words)
        
        # Create vocabulary with most common words
        vocab_words = ['<PAD>', '<UNK>'] + [word for word, _ in word_counts.most_common(self.max_vocab_size - 2)]
        self.word_to_idx = {word: idx for idx, word in enumerate(vocab_words)}
        self.vocab_size = len(self.word_to_idx)
    
    def _tokenize(self, text):
        # Simple tokenization
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.split()

    def load_and_preprocess(self, batch_size: int = 64) -> Tuple[DataLoader, DataLoader]:
        # Load CSV files
        train_df = pd.read_csv(self.train_path)
        test_df = pd.read_csv(self.test_path)
        
        # Take a smaller subset of the data for faster training
        train_df = train_df.sample(n=min(1000, len(train_df)), random_state=42)
        test_df = test_df.sample(n=min(200, len(test_df)), random_state=42)
        print(f"Using {len(train_df)} training samples and {len(test_df)} test samples")
        
        # Build vocabulary from training data
        if self.word_to_idx is None:
            self.build_vocabulary(train_df['text'])
        
        # Create torch datasets
        train_dataset = YelpReviewDataset(
            train_df,
            self.word_to_idx,
            max_length=128
        )
        
        test_dataset = YelpReviewDataset(
            test_df,
            self.word_to_idx,
            max_length=128
        )
        
        # Create dataloaders
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0
        )
        
        test_dataloader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )
        
        return train_dataloader, test_dataloader

class YelpReviewDataset(Dataset):
    def __init__(self, dataframe: pd.DataFrame, word_to_idx: dict, max_length: int = 512):
        self.dataframe = dataframe
        self.word_to_idx = word_to_idx
        self.max_length = max_length
        
        # Clean the labels before processing
        self.dataframe = self.dataframe[self.dataframe['label'].between(1, 5)].reset_index(drop=True)
    
    def _tokenize_and_encode(self, text):
        # Tokenize
        words = text.lower()
        words = re.sub(r'[^\w\s]', '', words)
        words = words.split()
        
        # Convert to indices with padding/truncation
        indices = [self.word_to_idx.get(word, self.word_to_idx['<UNK>']) for word in words[:self.max_length]]
        indices = indices + [self.word_to_idx['<PAD>']] * (self.max_length - len(indices))
        
        # Create attention mask
        attention_mask = [1] * min(len(words), self.max_length) + [0] * (self.max_length - min(len(words), self.max_length))
        
        return indices, attention_mask
    
    def __len__(self):
        return len(self.dataframe)
    
    def __getitem__(self, idx):
        row = self.dataframe.iloc[idx]
        text = row['text']
        rating = row['label']
        label = max(min(rating, 5), 1) - 1
        
        # Tokenize and encode text
        indices, attention_mask = self._tokenize_and_encode(text)
        
        return {
            'input_ids': torch.tensor(indices, dtype=torch.long),
            'attention_mask': torch.tensor(attention_mask, dtype=torch.float),
            'label': torch.tensor(label, dtype=torch.long)
        } 