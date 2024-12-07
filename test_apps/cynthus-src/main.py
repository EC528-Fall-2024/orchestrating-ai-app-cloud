import torch
from src.models.classifier import RainClassifier
from src.data.dataset import WeatherDataset
from src.training.trainer import RainPredictor
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
        
        # Initialize dataset
        dataset = WeatherDataset('data/weather_forecast_data.csv')
        X_train, X_test, y_train, y_test = dataset.load_and_preprocess()
        
        # Initialize model
        input_size = X_train.shape[1]
        model = RainClassifier(
            input_size=input_size,
            hidden_sizes=model_config.hidden_sizes,
            dropout_rate=model_config.dropout_rate
        )
        
        # Initialize predictor
        predictor = RainPredictor(model, dataset.scaler)
        
        # Train model
        history = predictor.train(
            X_train, y_train,
            X_test, y_test,  # Using test set as validation set for simplicity
            num_epochs=training_config.num_epochs,
            batch_size=training_config.batch_size,
            learning_rate=training_config.learning_rate
        )
        
        # Plot training history
        predictor.plot_training_history()
        
        # Evaluate model
        accuracy, report = predictor.evaluate(X_test, y_test)
        print(f'\nTest Accuracy: {accuracy:.4f}')
        print("\nClassification Report:")
        print(pd.DataFrame(report).transpose())
        
        # Make sample predictions
        sample_data = X_test.numpy()[:5]
        predictions, probabilities = predictor.predict(sample_data)
        actual = y_test[:5].numpy()
        
        print("\nSample Predictions:")
        for i, (pred, prob, true) in enumerate(zip(predictions, probabilities, actual)):
            print(f"Sample {i+1}:")
            print(f"  Predicted: {'Rain' if pred == 1 else 'No Rain'} (Probability: {prob:.4f})")
            print(f"  Actual: {'Rain' if true == 1 else 'No Rain'}")
        
    finally:
        # Close and restore stdout
        if isinstance(sys.stdout, OutputLogger):
            sys.stdout.close()
        sys.stdout = original_stdout

if __name__ == "__main__":
    main()
