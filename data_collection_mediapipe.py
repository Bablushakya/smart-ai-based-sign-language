import cv2
import os
import numpy as np
import mediapipe as mp
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def create_mediapipe_directories():
    base_dir = "dataset/processed"
    signs = ['bye', 'hello', 'yes', 'no', 'thank_you', 'perfect']
    
    for sign in signs:
        # Create directories for images and landmarks
        img_dir = os.path.join(base_dir, sign, "images")
        landmark_dir = os.path.join(base_dir, sign, "landmarks")
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(landmark_dir, exist_ok=True)
        print(f"Created directories for: {sign}")
    
    return signs

def count_existing_mediapipe_images(sign):
    img_dir = f"dataset/processed/{sign}/images"
    if os.path.exists(img_dir):
        return len([f for f in os.listdir(img_dir) if f.endswith('.jpg')])
    return 0

def extract_hand_region(frame, hand_landmarks, padding=20):
    """Extract hand region from frame based on landmarks"""
    h, w = frame.shape[:2]
    
    # Get landmark coordinates
    x_coords = [landmark.x * w for landmark in hand_landmarks.landmark]
    y_coords = [landmark.y * h for landmark in hand_landmarks.landmark]
    
    # Calculate bounding box
    x_min, x_max = int(min(x_coords)) - padding, int(max(x_coords)) + padding
    y_min, y_max = int(min(y_coords)) - padding, int(max(y_coords)) + padding
    
    # Ensure coordinates are within frame bounds
    x_min, y_min = max(0, x_min), max(0, y_min)
    x_max, y_max = min(w, x_max), min(h, y_max)
    
    # Extract hand region
    hand_roi = frame[y_min:y_max, x_min:x_max]
    
    return hand_roi, (x_min, y_min, x_max, y_max)

def main():
    signs = create_mediapipe_directories()
    
    # Initialize MediaPipe Hands with higher confidence for better detection
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    current_sign_index = 0
    image_count = count_existing_mediapipe_images(signs[current_sign_index])
    total_images_per_sign = 1500
    
    print("=== ASL Data Collection - MediaPipe ===")
    print("Instructions:")
    print("1. Hand will be automatically detected")
    print("2. Press 'c' to capture when hand is visible")
    print("3. Press 'n' for next sign")
    print("4. Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break
        
        # Flip frame for mirror view
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = hands.process(rgb_frame)
        
        current_sign = signs[current_sign_index]
        status_text = f"Sign: {current_sign} | MediaPipe Images: {image_count}/{total_images_per_sign}"
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'c' to capture (when hand detected)", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        hand_detected = False
        hand_roi = None
        
        if results.multi_hand_landmarks:
            hand_detected = True
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks on frame
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Extract hand region
                hand_roi, bbox = extract_hand_region(frame, hand_landmarks)
                
                # Draw bounding box
                x_min, y_min, x_max, y_max = bbox
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(frame, "Hand Detected", (x_min, y_min-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Display hand detection status
        if hand_detected:
            status_color = (0, 255, 0)
            status_msg = "Hand Detected - Ready to Capture"
        else:
            status_color = (0, 0, 255)
            status_msg = "No Hand Detected"
        
        cv2.putText(frame, status_msg, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        cv2.imshow('ASL Data Collection - MediaPipe', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c') and hand_detected and image_count < total_images_per_sign:
            # Save MediaPipe processed image
            img_filename = f"dataset/processed/{current_sign}/images/{current_sign}_mediapipe_{image_count:04d}.jpg"
            cv2.imwrite(img_filename, frame)
            
            # Save landmark data
            if results.multi_hand_landmarks:
                landmarks = []
                for landmark in results.multi_hand_landmarks[0].landmark:
                    landmarks.extend([landmark.x, landmark.y, landmark.z])
                
                landmark_filename = f"dataset/processed/{current_sign}/landmarks/{current_sign}_landmarks_{image_count:04d}.npy"
                np.save(landmark_filename, np.array(landmarks))
            
            image_count += 1
            print(f"Captured MediaPipe data: {img_filename}")
            
        elif key == ord('n'):  # Next sign
            current_sign_index = (current_sign_index + 1) % len(signs)
            image_count = count_existing_mediapipe_images(signs[current_sign_index])
            print(f"Switched to: {signs[current_sign_index]}")
            
        elif key == ord('q'):  # Quit
            break
    
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("MediaPipe data collection completed!")

if __name__ == "__main__":
    main()