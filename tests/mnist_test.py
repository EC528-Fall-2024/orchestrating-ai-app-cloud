import tensorflow as tf
import numpy as np
import time
import os
import sys
import gc
import random
from datetime import datetime

def display_predictions(model, x_test, y_test, num_samples=5):
    # Get random sample indices
    indices = random.sample(range(len(x_test)), num_samples)
    
    # Get predictions
    samples = x_test[indices]
    true_labels = y_test[indices]
    predictions = model.predict(samples, verbose=0)
    predicted_labels = np.argmax(predictions, axis=1)
    
    print("\nSample Classifications:")
    print("-" * 50)
    
    for i in range(num_samples):
        # Convert the image to ASCII art
        img = samples[i].reshape(28, 28)
        ascii_img = []
        for row in img:
            ascii_row = ''
            for pixel in row:
                if pixel < 0.2:
                    ascii_row += '  '
                elif pixel < 0.4:
                    ascii_row += '..'
                elif pixel < 0.6:
                    ascii_row += '**'
                elif pixel < 0.8:
                    ascii_row += '##'
                else:
                    ascii_row += '@@'
            ascii_img.append(ascii_row)
        
        print(f"\nSample {i + 1}:")
        print("Image:")
        for row in ascii_img:
            print(row)
            
        print(f"True Label: {true_labels[i]}")
        print(f"Predicted Label: {predicted_labels[i]}")
        print(f"Confidence: {predictions[i][predicted_labels[i]]:.2%}")
        print("-" * 50)

def test_mnist_deployment():
    # Create a log file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'mnist_test_log_{timestamp}.txt'
    
    # Redirect stdout to both file and console
    class Logger(object):
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, 'w')

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
            self.log.flush()

        def flush(self):
            self.terminal.flush()
            self.log.flush()

    sys.stdout = Logger(log_file)
    
    try:
        # Suppress TensorFlow logging except for errors
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        
        # Check for GPU availability
        print("\nHardware Configuration:")
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"Found {len(gpus)} GPU(s):")
            for gpu in gpus:
                print(f"  - {gpu.device_type}: {gpu.name}")
        else:
            print("No GPU found, running on CPU")
        
        # Load MNIST dataset
        print("\nLoading MNIST dataset...")
        try:
            (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
        except Exception as e:
            print(f"Error loading MNIST dataset: {e}")
            return None, None, None
        
        # Normalize and reshape the test data
        x_test = x_test.astype('float32') / 255.0
        x_test = x_test.reshape((-1, 28, 28, 1))
        
        # Create a simple CNN model
        print("\nCreating model...")
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(28, 28, 1)),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(64, 3, activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Performance testing
        print("\nRunning performance tests...")
        
        # Test batch inference time
        batch_size = 32
        test_batch = x_test[:batch_size]
        
        # Warmup
        print("Performing warmup prediction...")
        model.predict(test_batch, verbose=0)
        
        # Time batch prediction
        print("Testing batch inference...")
        start_time = time.time()
        predictions = model.predict(test_batch, verbose=0)
        batch_time = time.time() - start_time
        
        # Test single image inference time
        single_image = x_test[0:1]
        
        # Time single prediction
        print("Testing single image inference...")
        start_time = time.time()
        single_prediction = model.predict(single_image, verbose=0)
        single_time = time.time() - start_time
        
        # Print results
        print("\nPerformance Results:")
        print(f"Model Summary:")
        model.summary()
        print(f"\nBatch Size: {batch_size}")
        print(f"Batch Inference Time: {batch_time:.4f} seconds")
        print(f"Single Image Inference Time: {single_time:.4f} seconds")
        print(f"Images Per Second (batch): {batch_size/batch_time:.2f}")
        
        # Model size calculation
        def get_size_of_dtype(dtype):
            dtype_str = str(dtype)
            if 'float32' in dtype_str:
                return 4
            elif 'float64' in dtype_str:
                return 8
            elif 'float16' in dtype_str:
                return 2
            elif 'int32' in dtype_str:
                return 4
            elif 'int64' in dtype_str:
                return 8
            else:
                return 4
        
        try:
            model_size = sum(np.prod(v.shape) * get_size_of_dtype(v.dtype) 
                           for v in model.trainable_variables) / (1024 * 1024)
            print(f"\nApproximate Model Size: {model_size:.2f} MB")
        except Exception as e:
            print(f"\nError calculating model size: {e}")
        
        # Display some sample predictions
        display_predictions(model, x_test, y_test)
        
        return model, x_test, y_test
        
    except Exception as e:
        print(f"\nAn error occurred during testing: {e}")
        return None, None, None
        
    finally:
        # Add to existing cleanup
        sys.stdout = sys.__stdout__  # Restore original stdout
        gc.collect()
        if gpus:
            tf.keras.backend.clear_session()

if __name__ == "__main__":
    try:
        model, x_test, y_test = test_mnist_deployment()
        if model is None:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)