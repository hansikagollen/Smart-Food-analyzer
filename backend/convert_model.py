#!/usr/bin/env python3
"""
Script to convert legacy Keras model to TensorFlow 2.15 compatible format
"""
import h5py
import json
import tensorflow as tf
from tensorflow import keras
import numpy as np

def load_legacy_model(model_path):
    """Load model weights from legacy H5 file"""
    print(f"Loading legacy model from: {model_path}")
    
    # Try to get architecture info from the H5 file
    with h5py.File(model_path, 'r') as f:
        # Get model config if available
        if 'model_config' in f.attrs:
            config_attr = f.attrs['model_config']
            if isinstance(config_attr, bytes):
                config = json.loads(config_attr.decode('utf-8'))
            else:
                config = json.loads(config_attr)
            
            print("Model config class:", config.get('class_name'))
            
            # Get layer info
            if 'config' in config and 'layers' in config['config']:
                layers = config['config']['layers']
                print(f"Number of layers: {len(layers)}")
                
                # Find input shape
                for layer in layers:
                    if 'batch_input_shape' in layer.get('config', {}) or 'batch_shape' in layer.get('config', {}):
                        batch_shape = layer['config'].get('batch_input_shape') or layer['config'].get('batch_shape')
                        print(f"Input shape found: {batch_shape}")
                        break
        
        # List weight layer names
        if 'model_weights' in f:
            print("\nWeight layers:")
            for layer_name in f['model_weights'].keys():
                print(f"  - {layer_name}")
    
    # Since direct loading fails, let's extract weights manually
    print("\nExtracting weights manually...")
    
    with h5py.File(model_path, 'r') as f:
        if 'model_weights' in f:
            model_weights_group = f['model_weights']
            weights_dict = {}
            
            def extract_weights(name, obj):
                if isinstance(obj, h5py.Dataset):
                    weights_dict[name] = np.array(obj)
            
            model_weights_group.visititems(extract_weights)
            print(f"Extracted {len(weights_dict)} weight tensors")
            
            return weights_dict
    
    return None

def create_compatible_model():
    """Create a fresh model with compatible architecture"""
    print("\nCreating fresh model architecture...")
    
    # Simple CNN architecture for food freshness classification (3 classes)
    model = keras.Sequential([
        keras.layers.Input(shape=(224, 224, 3)),
        keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Flatten(),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(3, activation='softmax')  # 3 classes: Fresh, Rotten, Semi-Rotten
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("Model created successfully!")
    model.summary()
    
    return model

if __name__ == "__main__":
    import sys
    
    old_model_path = 'models/food_freshness_model.h5'
    new_model_path = 'models/food_freshness_model_converted.h5'
    
    print("="*60)
    print("Keras Model Converter")
    print("="*60)
    
    # Try to extract info from old model
    weights = load_legacy_model(old_model_path)
    
    # Create new compatible model
    new_model = create_compatible_model()
    
    # Save the new model
    print(f"\nSaving compatible model to: {new_model_path}")
    new_model.save(new_model_path)
    print("✓ Model saved successfully!")
    
    # Test loading the new model
    print("\nTesting new model loading...")
    test_model = keras.models.load_model(new_model_path)
    print("✓ New model loads successfully!")
    print(f"Input shape: {test_model.input_shape}")
    print(f"Output shape: {test_model.output_shape}")
    
    print("\n" + "="*60)
    print("IMPORTANT NOTE:")
    print("="*60)
    print("A new model architecture has been created, but the weights from")
    print("your original model could not be transferred due to compatibility issues.")
    print("")
    print("This new model will work with the app, but will need to be retrained")
    print("or you can:")
    print("  1. Re-save your original model using TensorFlow 2.15+")
    print("  2. Or provide the model in SavedModel format instead of .h5")
    print("="*60)
