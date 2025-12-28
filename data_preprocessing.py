import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
import tensorflow as tf
import mediapipe as mp
import json

class DataPreprocessor:
    def __init__(self):
        self.signs = ['bye', 'hello', 'yes', 'no', 'thank_you', 'perfect']
        self.img_height = 224
        self.img_width = 224
        self.mp_hands = mp.solutions.hands
        
    def load_landmarks_data(self, max_samples_per_class=1000):
        """Load preprocessed MediaPipe landmarks with memory limit"""
        X_landmarks = []
        y_landmarks = []
        
        for label, sign in enumerate(self.signs):
            landmark_dir = f"dataset/processed/{sign}/landmarks"
            if not os.path.exists(landmark_dir):
                print(f"⚠️  No landmarks found for {sign}, skipping...")
                continue
                
            landmark_files = [f for f in os.listdir(landmark_dir) if f.endswith('.npy')]
            # Use only first max_samples_per_class to prevent memory issues
            landmark_files = landmark_files[:max_samples_per_class]
            
            print(f"📁 Loading {len(landmark_files)} landmark files for {sign}")
            
            for lmk_file in landmark_files:
                lmk_path = os.path.join(landmark_dir, lmk_file)
                landmarks = np.load(lmk_path)
                
                if landmarks.shape[0] == 63:  # 21 landmarks * 3 coordinates
                    X_landmarks.append(landmarks)
                    y_landmarks.append(label)
        
        if not X_landmarks:
            raise ValueError("❌ No landmark data found! Please collect data first.")
        
        return np.array(X_landmarks), np.array(y_landmarks)
    
    def extract_landmarks_from_raw_batches(self, max_images_per_class=500):
        """Extract landmarks from raw images in batches to save memory"""
        landmarks_list = []
        labels_list = []
        
        with self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        ) as hands:
            
            for label, sign in enumerate(self.signs):
                sign_dir = f"dataset/raw/{sign}"
                if not os.path.exists(sign_dir):
                    print(f"⚠️  No raw images found for {sign}, skipping...")
                    continue
                    
                image_files = [f for f in os.listdir(sign_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                image_files = image_files[:max_images_per_class]  # Limit images per class
                
                print(f"🖼️  Processing {len(image_files)} raw images for {sign} in batches...")
                
                for img_file in image_files:
                    img_path = os.path.join(sign_dir, img_file)
                    img = cv2.imread(img_path)
                    
                    if img is not None:
                        # Resize image
                        img = cv2.resize(img, (self.img_height, self.img_width))
                        
                        # Convert BGR to RGB
                        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        
                        # Process with MediaPipe
                        results = hands.process(rgb_img)
                        
                        if results.multi_hand_landmarks:
                            landmarks = []
                            for landmark in results.multi_hand_landmarks[0].landmark:
                                landmarks.extend([landmark.x, landmark.y, landmark.z])
                            landmarks_list.append(np.array(landmarks))
                            labels_list.append(label)
        
        return np.array(landmarks_list), np.array(labels_list)
    
    def prepare_data(self, use_landmarks=True, use_images=False, max_samples=1000):
        """Prepare final dataset for training with memory limits"""
        X_final = []
        y_final = []
        
        if use_landmarks:
            print("📊 Loading pre-collected landmarks...")
            X_landmarks, y_landmarks = self.load_landmarks_data(max_samples_per_class=max_samples)
            X_final.append(X_landmarks)
            y_final.append(y_landmarks)
            print(f"✅ Loaded {len(X_landmarks)} landmark samples")
        
        if use_images:
            print("🖼️  Extracting landmarks from raw images...")
            X_img_landmarks, y_img = self.extract_landmarks_from_raw_batches(max_images_per_class=max_samples//2)
            if len(X_img_landmarks) > 0:
                X_final.append(X_img_landmarks)
                y_final.append(y_img)
                print(f"✅ Extracted {len(X_img_landmarks)} landmarks from raw images")
        
        if not X_final:
            raise ValueError("❌ No data found! Please collect data first.")
        
        # Combine all data
        X_combined = np.vstack(X_final)
        y_combined = np.hstack(y_final)
        
        # Remove any samples with all-zero landmarks
        valid_mask = ~np.all(X_combined == 0, axis=1)
        X_combined = X_combined[valid_mask]
        y_combined = y_combined[valid_mask]
        
        print(f"📈 Final dataset shape: {X_combined.shape}")
        print(f"🎯 Class distribution: {np.bincount(y_combined)}")
        
        return X_combined, y_combined