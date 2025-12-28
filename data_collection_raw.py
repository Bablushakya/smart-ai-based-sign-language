import cv2
import os
import time

# Create dataset directories
def create_directories():
    base_dir = "dataset/raw"
    signs = ['bye', 'hello', 'yes', 'no', 'thank_you', 'perfect']
    
    for sign in signs:
        sign_dir = os.path.join(base_dir, sign)
        os.makedirs(sign_dir, exist_ok=True)
        print(f"Created directory: {sign_dir}")
    
    return signs

def count_existing_images(sign):
    sign_dir = f"dataset/raw/{sign}"
    if os.path.exists(sign_dir):
        return len([f for f in os.listdir(sign_dir) if f.endswith('.jpg')])
    return 0

def main():
    signs = create_directories()
    cap = cv2.VideoCapture(0)
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    current_sign_index = 0
    image_count = count_existing_images(signs[current_sign_index])
    total_images_per_sign = 1500  # Target 1500 images per sign
    
    print("=== ASL Data Collection - Raw Images ===")
    print("Instructions:")
    print("1. Press 'c' to capture image")
    print("2. Press 'n' for next sign")
    print("3. Press 'p' for previous sign")
    print("4. Press 'q' to quit")
    print("5. Make sure hand is clearly visible")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break
        
        # Display current sign and count
        current_sign = signs[current_sign_index]
        status_text = f"Sign: {current_sign} | Images: {image_count}/{total_images_per_sign}"
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'c' to capture, 'n' for next, 'q' to quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw hand bounding box guide
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        box_size = 300
        x1 = center_x - box_size // 2
        y1 = center_y - box_size // 2
        x2 = center_x + box_size // 2
        y2 = center_y + box_size // 2
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "Place hand here", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow('ASL Data Collection - Raw Images', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):  # Capture image
            if image_count < total_images_per_sign:
                # Crop to hand region
                hand_roi = frame[y1:y2, x1:x2]
                
                # Save image
                filename = f"dataset/raw/{current_sign}/{current_sign}_{image_count:04d}.jpg"
                cv2.imwrite(filename, hand_roi)
                image_count += 1
                print(f"Captured: {filename}")
            else:
                print(f"Reached target for {current_sign}")
                
        elif key == ord('n'):  # Next sign
            current_sign_index = (current_sign_index + 1) % len(signs)
            image_count = count_existing_images(signs[current_sign_index])
            print(f"Switched to: {signs[current_sign_index]}")
            
        elif key == ord('p'):  # Previous sign
            current_sign_index = (current_sign_index - 1) % len(signs)
            image_count = count_existing_images(signs[current_sign_index])
            print(f"Switched to: {signs[current_sign_index]}")
            
        elif key == ord('q'):  # Quit
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Data collection completed!")

if __name__ == "__main__":
    main()