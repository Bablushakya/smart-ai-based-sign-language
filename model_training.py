import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import json
from datetime import datetime
import gc

# Import our custom modules
from data_preprocessing import DataPreprocessor
from model_architecture import AdvancedASLModel

class AdvancedModelTrainer:
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.model_creator = AdvancedASLModel()
        self.history = None
        
    def create_callbacks(self):
        """Create advanced callbacks for training"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        callbacks = [
            # Early stopping to prevent overfitting
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Reduce learning rate when plateau
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=8,
                min_lr=1e-7,
                verbose=1
            ),
            
            # Model checkpoint
            tf.keras.callbacks.ModelCheckpoint(
                filepath=f'models/best_asl_model_{timestamp}.h5',
                monitor='val_accuracy',
                save_best_only=True,
                mode='max',
                verbose=1
            )
        ]
        
        return callbacks
    
    def calculate_class_weights(self, y_train):
        """Calculate class weights for imbalanced data"""
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        return dict(enumerate(class_weights))
    
    def create_memory_efficient_model(self):
        """Create a simpler model to prevent memory issues"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(63,)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Dense(6, activation='softmax')
        ])
        
        return model
    
    def train_advanced_model(self):
        """Train the advanced ASL model with memory efficiency"""
        print("🚀 Starting ASL Model Training (Memory Efficient Version)")
        print("⚠️  Using reduced dataset size to prevent memory errors")
        
        # Load data - ONLY USE LANDMARKS (much more memory efficient)
        X, y = self.preprocessor.prepare_data(use_landmarks=True, use_images=False)
        
        print(f"📊 Dataset loaded: {X.shape[0]} samples, {X.shape[1]} features")
        print(f"📈 Class distribution: {np.bincount(y)}")
        
        # Convert to categorical
        y_categorical = tf.keras.utils.to_categorical(y, num_classes=6)
        
        # Split data with smaller test size
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y_categorical, test_size=0.2, random_state=42, stratify=y
        )
        
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=np.argmax(y_temp, axis=1)
        )
        
        print(f"🎯 Training set: {X_train.shape[0]} samples")
        print(f"🔍 Validation set: {X_val.shape[0]} samples")
        print(f"🧪 Test set: {X_test.shape[0]} samples")
        
        # Clear memory
        del X, y, X_temp, y_temp
        gc.collect()
        
        # Calculate class weights
        class_weights = self.calculate_class_weights(np.argmax(y_train, axis=1))
        print("⚖️ Class weights:", class_weights)
        
        # Create and compile model (simpler version)
        model = self.create_memory_efficient_model()
        
        # Use simpler optimizer
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
        
        # FIX: Use proper metric names, not strings
        model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=[
                'accuracy',
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall')
            ]
        )
        
        print("🧠 Model architecture:")
        model.summary()
        
        # Train with smaller batch size
        print("🚀 Starting training...")
        self.history = model.fit(
            X_train, y_train,
            epochs=100,  # Reduced epochs
            batch_size=16,  # Smaller batch size for memory
            validation_data=(X_val, y_val),
            callbacks=self.create_callbacks(),
            class_weight=class_weights,
            verbose=1
        )
        
        # Evaluate model
        print("📊 Evaluating model...")
        test_loss, test_accuracy, test_precision, test_recall = model.evaluate(X_test, y_test, verbose=0)
        
        print(f"\n🎉 Final Test Results:")
        print(f"✅ Accuracy: {test_accuracy:.4f}")
        print(f"🎯 Precision: {test_precision:.4f}")
        print(f"🔍 Recall: {test_recall:.4f}")
        
        # Save final model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_model_path = f'models/final_asl_model_{timestamp}.h5'
        model.save(final_model_path)
        print(f"💾 Final model saved to: {final_model_path}")
        
        # Save class labels
        class_mapping = {i: sign for i, sign in enumerate(self.preprocessor.signs)}
        with open('models/class_mapping.json', 'w') as f:
            json.dump(class_mapping, f, indent=4)
        
        return model, test_accuracy
    
    def plot_training_history(self):
        """Plot training history"""
        if self.history is None:
            print("No training history available. Train model first.")
            return
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot accuracy
        ax1.plot(self.history.history['accuracy'], label='Training Accuracy', linewidth=2)
        ax1.plot(self.history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
        ax1.set_title('Model Accuracy', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Accuracy', fontsize=12)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Plot loss
        ax2.plot(self.history.history['loss'], label='Training Loss', linewidth=2)
        ax2.plot(self.history.history['val_loss'], label='Validation Loss', linewidth=2)
        ax2.set_title('Model Loss', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Epoch', fontsize=12)
        ax2.set_ylabel('Loss', fontsize=12)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('models/training_history.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    try:
        # Train model
        trainer = AdvancedModelTrainer()
        model, accuracy = trainer.train_advanced_model()
        
        # Plot training history
        trainer.plot_training_history()
        
        print(f"\n🎉 Training completed with {accuracy:.2%} accuracy!")
        print("\n📝 Next steps:")
        print("1. Check the models/ directory for saved models")
        print("2. Run model_evaluation.py for detailed analysis")
        print("3. Use real_time_tester.py to test the model")
        print("4. If accuracy is low, collect more diverse data")
        
    except MemoryError as e:
        print(f"💥 Memory error: {e}")
        print("🔧 Try these solutions:")
        print("   - Reduce batch size in model_training.py")
        print("   - Use only landmarks (set use_images=False)")
        print("   - Collect less data per class")
        print("   - Close other applications to free up RAM")
        
    except Exception as e:
        print(f"💥 Error during training: {e}")
        print("🔧 Check your data and try again")

if __name__ == "__main__":
    main()