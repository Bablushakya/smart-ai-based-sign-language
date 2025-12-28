import tensorflow as tf

class AdvancedASLModel:
    def __init__(self, num_classes=6, input_shape=63):
        self.num_classes = num_classes
        self.input_shape = input_shape
    
    def create_landmark_model(self):
        """Create optimized neural network for landmark data"""
        model = tf.keras.Sequential([
            # Input layer
            tf.keras.layers.Dense(128, activation='relu', input_shape=(self.input_shape,)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            
            # Hidden layers (reduced size for faster training)
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),
            
            # Output layer
            tf.keras.layers.Dense(self.num_classes, activation='softmax')
        ])
        
        return model
    
    def create_simple_model(self):
        """Even simpler model for quick testing"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(self.input_shape,)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(self.num_classes, activation='softmax')
        ])
        return model