import torch
from src.models.classifier import YelpClassifier
from src.data.dataset import YelpDataset
from src.training.trainer import ReviewPredictor
from src.config.config import ModelConfig, TrainingConfig
import pandas as pd
import sys
from datetime import datetime

class OutputLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

def main():
    # Store original stdout
    original_stdout = sys.stdout
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f'training_log_{timestamp}.txt'
    sys.stdout = OutputLogger(log_filename)
    
    try:
        # Load configurations
        model_config = ModelConfig()
        training_config = TrainingConfig()
        
        # Set random seed
        torch.manual_seed(training_config.random_seed)
        
        # Initialize dataset with actual paths to CSV files
        dataset = YelpDataset(
            train_path='train.csv',  # Update with your actual train file path
            test_path='test.csv'     # Update with your actual test file path
        )
        train_dataloader, test_dataloader = dataset.load_and_preprocess(
            batch_size=training_config.batch_size
        )
        
        # Initialize model
        model = YelpClassifier(
            vocab_size=dataset.vocab_size,
            embedding_dim=model_config.embedding_dim,
            hidden_sizes=model_config.hidden_sizes,
            num_classes=5,  # Yelp has 5 classes
            dropout_rate=model_config.dropout_rate
        )
        
        # Initialize predictor
        predictor = ReviewPredictor(model)
        
        # Train model
        history = predictor.train(
            train_dataloader,
            test_dataloader,
            num_epochs=training_config.num_epochs,
            learning_rate=training_config.learning_rate
        )
        
        # Plot training history
        predictor.plot_training_history()
        
        # Evaluate model
        accuracy, report = predictor.evaluate(test_dataloader)
        print(f'\nTest Accuracy: {accuracy:.4f}')
        print("\nClassification Report:")
        print(pd.DataFrame(report).transpose())
        
        # Make sample predictions
        sample_texts = [
            "The food was amazing and the service was excellent!",
            "Decent place but nothing special.",
            "Terrible experience, would not recommend.",
        ]
        predictions, probabilities = predictor.predict(sample_texts, dataset.word_to_idx)
        
        print("\nSample Predictions:")
        for i, (text, pred, probs) in enumerate(zip(sample_texts, predictions, probabilities)):
            print(f"\nSample {i+1}:")
            print(f"Text: {text}")
            print(f"Predicted Rating: {pred + 1} stars")
            print("Class Probabilities:")
            for stars, prob in enumerate(probs, 1):
                print(f"  {stars} stars: {prob:.4f}")
        
    finally:
        # Close and restore stdout
        if isinstance(sys.stdout, OutputLogger):
            sys.stdout.close()
        sys.stdout = original_stdout

if __name__ == "__main__":
    main()
