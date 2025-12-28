import os
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import json
from data_preprocessing import DataPreprocessor

class ModelEvaluator:
    def __init__(self, model_path=None):
        if model_path is None:
            # Find the latest model
            if os.path.exists('models'):
                model_files = [f for f in os.listdir('models') if f.startswith('best_asl_model') and f.endswith('.h5')]
                if model_files:
                    model_path = os.path.join('models', sorted(model_files)[-1])
                else:
                    model_files = [f for f in os.listdir('models') if f.startswith('final_asl_model') and f.endswith('.h5')]
                    if model_files:
                        model_path = os.path.join('models', sorted(model_files)[-1])
                    else:
                        raise FileNotFoundError("No trained model found in models directory")
            else:
                raise FileNotFoundError("Models directory does not exist")
        
        self.model = tf.keras.models.load_model(model_path)
        self.preprocessor = DataPreprocessor()
        
        # Load class mapping
        class_mapping_path = 'models/class_mapping.json'
        if os.path.exists(class_mapping_path):
            with open(class_mapping_path, 'r') as f:
                self.class_mapping = json.load(f)
        else:
            # Default class mapping
            self.class_mapping = {str(i): sign for i, sign in enumerate(['bye', 'hello', 'yes', 'no', 'thank_you', 'perfect'])}
    
    def comprehensive_evaluation(self):
        """Perform comprehensive model evaluation"""
        # Load test data
        X, y = self.preprocessor.prepare_data()
        y_categorical = tf.keras.utils.to_categorical(y, num_classes=6)
        
        # Split test data (use the same split as training)
        from sklearn.model_selection import train_test_split
        _, X_test, _, y_test = train_test_split(
            X, y_categorical, test_size=0.15, random_state=42, stratify=y
        )
        
        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true_classes = np.argmax(y_test, axis=1)
        
        # Calculate metrics
        test_accuracy = np.mean(y_pred_classes == y_true_classes)
        
        print(f"Test Accuracy: {test_accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_true_classes, y_pred_classes, 
                                  target_names=[self.class_mapping[str(i)] for i in range(6)]))
        
        # Confusion Matrix
        self.plot_confusion_matrix(y_true_classes, y_pred_classes)
        
        # Confidence analysis
        self.analyze_confidence(y_pred, y_true_classes)
    
    def plot_confusion_matrix(self, y_true, y_pred):
        """Plot detailed confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(10, 8))
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=[self.class_mapping[str(i)] for i in range(6)],
                   yticklabels=[self.class_mapping[str(i)] for i in range(6)])
        
        plt.title('Confusion Matrix - ASL Sign Recognition')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('models/confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print misclassification analysis
        print("\nMisclassification Analysis:")
        for i in range(len(cm)):
            total = np.sum(cm[i])
            correct = cm[i][i]
            incorrect = total - correct
            if incorrect > 0:
                print(f"{self.class_mapping[str(i)]}: {correct}/{total} correct "
                      f"({correct/total:.1%}), {incorrect} misclassified")
    
    def analyze_confidence(self, y_pred_proba, y_true):
        """Analyze prediction confidence"""
        confidence_correct = []
        confidence_incorrect = []
        
        for i, (probs, true_class) in enumerate(zip(y_pred_proba, y_true)):
            pred_class = np.argmax(probs)
            confidence = np.max(probs)
            
            if pred_class == true_class:
                confidence_correct.append(confidence)
            else:
                confidence_incorrect.append(confidence)
        
        print(f"\nConfidence Analysis:")
        print(f"Correct predictions: {len(confidence_correct)} samples")
        if confidence_correct:
            print(f"  Average confidence: {np.mean(confidence_correct):.3f}")
            print(f"  Std confidence: {np.std(confidence_correct):.3f}")
        
        print(f"Incorrect predictions: {len(confidence_incorrect)} samples")
        if confidence_incorrect:
            print(f"  Average confidence: {np.mean(confidence_incorrect):.3f}")
            print(f"  Std confidence: {np.std(confidence_incorrect):.3f}")

if __name__ == "__main__":
    evaluator = ModelEvaluator()
    evaluator.comprehensive_evaluation()