import numpy as np
import tensorflow as tf
import json
from data_preprocessing import DataPreprocessor

def quick_model_test():
    """Quick test to verify model performance"""
    print("🧪 Running Quick Model Test...")
    
    # Load the latest model
    import os
    model_files = [f for f in os.listdir('models') if f.startswith('final_asl_model') and f.endswith('.h5')]
    if not model_files:
        print("❌ No final model found!")
        return
    
    model_path = os.path.join('models', model_files[-1])
    model = tf.keras.models.load_model(model_path)
    print(f"✅ Loaded model: {model_path}")
    
    # Load class mapping
    with open('models/class_mapping.json', 'r') as f:
        class_mapping = json.load(f)
    
    # Load a small test set
    preprocessor = DataPreprocessor()
    X, y = preprocessor.prepare_data(use_landmarks=True, use_images=False, max_samples=100)
    
    # Make predictions
    predictions = model.predict(X, verbose=0)
    predicted_classes = np.argmax(predictions, axis=1)
    
    # Calculate accuracy
    accuracy = np.mean(predicted_classes == y)
    
    print(f"🎯 Test Accuracy: {accuracy:.4f}")
    print(f"📊 Test Samples: {len(y)}")
    
    # Show some example predictions
    print("\n🔍 Sample Predictions:")
    for i in range(min(5, len(y))):
        true_sign = class_mapping[str(y[i])]
        pred_sign = class_mapping[str(predicted_classes[i])]
        confidence = np.max(predictions[i])
        status = "✅" if true_sign == pred_sign else "❌"
        print(f"   {status} True: {true_sign:10} | Pred: {pred_sign:10} | Conf: {confidence:.4f}")

if __name__ == "__main__":
    quick_model_test()