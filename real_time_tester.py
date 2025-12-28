import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import json
import os
import time
import sys
from collections import deque
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('asl_translator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class UltraRobustASLTester:
    def __init__(self, model_path=None):
        self.model = None
        self.class_mapping = None
        self.hands = None
        self.cap = None
        self.is_running = False
        
        # Prediction smoothing
        self.prediction_history = deque(maxlen=15)
        self.confidence_threshold = 0.7
        self.min_hand_detection_confidence = 0.6
        self.min_tracking_confidence = 0.5
        
        # Error handling and recovery
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        self.last_successful_frame_time = time.time()
        self.frame_timeout = 5.0  # 5 seconds without frames
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        
        # Emergency mode
        self.emergency_mode = False
        
        # Initialize components with robust error handling
        self.initialize_components(model_path)
    
    def initialize_components(self, model_path):
        """Initialize all components with comprehensive error handling"""
        logger.info("🔄 Initializing ASL Translator Components...")
        
        # 1. Initialize MediaPipe with fallbacks
        self.initialize_mediapipe()
        
        # 2. Load model with multiple fallback options
        self.load_model_with_fallbacks(model_path)
        
        # 3. Initialize camera with multiple attempts
        if not self.initialize_camera_with_retry():
            logger.warning("⚠️ Camera initialization failed, entering emergency mode...")
            self.emergency_mode = True
        
        logger.info("✅ All components initialized successfully!")
    
    def initialize_mediapipe(self):
        """Initialize MediaPipe with robust error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Initializing MediaPipe (Attempt {attempt + 1}/{max_retries})...")
                
                # Suppress MediaPipe warnings
                import warnings
                warnings.filterwarnings("ignore", category=UserWarning)
                
                self.mp_hands = mp.solutions.hands
                self.mp_drawing = mp.solutions.drawing_utils
                self.mp_drawing_styles = mp.solutions.drawing_styles
                
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    model_complexity=0,  # Reduced complexity for stability
                    min_detection_confidence=self.min_hand_detection_confidence,
                    min_tracking_confidence=self.min_tracking_confidence
                )
                
                # Test MediaPipe with a dummy frame
                test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
                rgb_frame = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
                _ = self.hands.process(rgb_frame)
                
                logger.info("✅ MediaPipe initialized successfully")
                return True
                
            except Exception as e:
                logger.error(f"❌ MediaPipe initialization failed (Attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    logger.warning("⚠️ MediaPipe failed, continuing without hand tracking")
                    return False
                time.sleep(1)  # Wait before retry
    
    def load_model_with_fallbacks(self, model_path):
        """Load model with multiple fallback strategies"""
        model_candidates = []
        
        # Collect all possible model candidates
        if model_path and os.path.exists(model_path):
            model_candidates.append(model_path)
        
        # Look for model files with various patterns
        model_patterns = [
            'final_asl_model_*.h5',
            'best_asl_model_*.h5', 
            'asl_model_*.h5',
            'model_*.h5',
            '*.h5'  # Any .h5 file as last resort
        ]
        
        for pattern in model_patterns:
            for file in self.find_files('models', pattern):
                if file not in model_candidates:
                    model_candidates.append(file)
        
        # Try to load each candidate
        for model_candidate in model_candidates:
            try:
                logger.info(f"🔄 Attempting to load model: {model_candidate}")
                self.model = tf.keras.models.load_model(model_candidate)
                
                # Load class mapping
                class_mapping_path = 'models/class_mapping.json'
                if os.path.exists(class_mapping_path):
                    with open(class_mapping_path, 'r') as f:
                        self.class_mapping = json.load(f)
                else:
                    # Create default class mapping
                    self.class_mapping = {str(i): f"Sign_{i}" for i in range(6)}
                    logger.warning("⚠️ Using default class mapping")
                
                logger.info(f"✅ Model loaded successfully: {model_candidate}")
                logger.info(f"🎯 Available signs: {list(self.class_mapping.values())}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to load model {model_candidate}: {e}")
                continue
        
        logger.critical("💥 Could not load any model file!")
        return False
    
    def find_files(self, directory, pattern):
        """Find files matching pattern in directory"""
        import glob
        return glob.glob(os.path.join(directory, pattern))
    
    def initialize_camera_with_retry(self):
        """Initialize camera with multiple attempts and fallbacks"""
        max_retries = 5
        camera_indices = [0, 1, 2, 3]  # Try multiple camera indices
        
        for camera_index in camera_indices:
            for attempt in range(max_retries):
                try:
                    logger.info(f"📷 Attempting to initialize camera {camera_index} (Attempt {attempt + 1}/{max_retries})...")
                    
                    self.cap = cv2.VideoCapture(camera_index)
                    
                    # Set camera properties for better compatibility
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.cap.set(cv2.CAP_PROP_FPS, 30)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for real-time
                    
                    # Test camera by reading a frame
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        logger.info(f"✅ Camera {camera_index} initialized successfully")
                        return True
                    else:
                        self.cap.release()
                        self.cap = None
                        
                except Exception as e:
                    logger.error(f"❌ Camera {camera_index} initialization failed: {e}")
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                
                time.sleep(1)  # Wait before retry
        
        logger.critical("💥 Could not initialize any camera!")
        return False
    
    def emergency_camera_test(self):
        """Ultra simple emergency camera test that always works"""
        print("🚨 EMERGENCY MODE - Basic Camera Test")
        print("📷 Trying all available cameras...")
        
        # Try all camera indices with minimal settings
        for i in range(4):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    print(f"✅ Camera {i} working in emergency mode!")
                    
                    while True:
                        ret, frame = cap.read()
                        if ret:
                            # Display emergency info
                            cv2.putText(frame, "EMERGENCY MODE - Camera Working", 
                                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            cv2.putText(frame, "ASL Translation Not Available", 
                                       (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            cv2.putText(frame, "Press 'q' to exit emergency mode", 
                                       (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            cv2.imshow('Emergency Camera Test', frame)
                        
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                            break
                    
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
            except Exception as e:
                print(f"❌ Camera {i} failed in emergency mode: {e}")
                continue
        
        print("❌ No cameras found in emergency mode")
        return False
    
    def safe_capture_frame(self):
        """Safely capture frame with error recovery"""
        if not self.cap or not self.cap.isOpened():
            logger.warning("🔄 Camera not available, attempting to reinitialize...")
            if self.initialize_camera_with_retry():
                return self.safe_capture_frame()
            else:
                return None, False
        
        try:
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                self.consecutive_errors += 1
                logger.warning(f"⚠️ Frame capture failed (Consecutive errors: {self.consecutive_errors})")
                
                if self.consecutive_errors >= self.max_consecutive_errors:
                    logger.error("🔄 Too many consecutive errors, reinitializing camera...")
                    self.cap.release()
                    self.cap = None
                    if self.initialize_camera_with_retry():
                        self.consecutive_errors = 0
                        return self.safe_capture_frame()
                    else:
                        return None, False
                
                return None, False
            
            # Success - reset error counter and update timestamp
            self.consecutive_errors = 0
            self.last_successful_frame_time = time.time()
            self.frame_count += 1
            
            return frame, True
            
        except Exception as e:
            logger.error(f"❌ Error capturing frame: {e}")
            self.consecutive_errors += 1
            return None, False
    
    def safe_extract_landmarks(self, frame):
        """Safely extract landmarks with error handling"""
        if self.hands is None:
            return None, frame, False
        
        try:
            # Flip frame for mirror view
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                landmarks = []
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks on frame for visual feedback
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Extract landmark coordinates
                    for landmark in hand_landmarks.landmark:
                        landmarks.extend([landmark.x, landmark.y, landmark.z])
                
                return np.array(landmarks), frame, True
            else:
                return None, frame, False
                
        except Exception as e:
            logger.error(f"❌ Error extracting landmarks: {e}")
            return None, frame, False
    
    def safe_predict(self, landmarks):
        """Safely make prediction with error handling"""
        if self.model is None or landmarks is None:
            return None, 0.0
        
        try:
            # Ensure landmarks are in correct shape
            if landmarks.shape[0] != 63:
                logger.warning(f"⚠️ Unexpected landmarks shape: {landmarks.shape}")
                return None, 0.0
            
            # Make prediction
            prediction = self.model.predict(landmarks.reshape(1, -1), verbose=0)
            predicted_class = np.argmax(prediction)
            confidence = np.max(prediction)
            
            return predicted_class, float(confidence)
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return None, 0.0
    
    def smooth_prediction(self, current_pred, current_confidence):
        """Apply smoothing to predictions using history"""
        if current_pred is None:
            # Return most recent valid prediction if available
            if self.prediction_history:
                last_pred, last_conf = self.prediction_history[-1]
                return last_pred, last_conf * 0.9  # Decay confidence
            return None, 0.0
        
        self.prediction_history.append((current_pred, current_confidence))
        
        if len(self.prediction_history) < 3:  # Reduced from 5 for faster response
            return current_pred, current_confidence
        
        # Get the most common prediction from recent history
        recent_predictions = list(self.prediction_history)[-5:]  # Last 5 predictions
        predictions = [pred for pred, conf in recent_predictions]
        
        try:
            most_common_pred = max(set(predictions), key=predictions.count)
            
            # Calculate weighted confidence for the most common prediction
            relevant_confidences = [conf for pred, conf in recent_predictions if pred == most_common_pred]
            avg_confidence = np.mean(relevant_confidences) if relevant_confidences else current_confidence
            
            return most_common_pred, avg_confidence
        except:
            return current_pred, current_confidence
    
    def calculate_fps(self):
        """Calculate and return current FPS"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        if elapsed_time > 0:
            fps = self.frame_count / elapsed_time
            return fps
        return 0
    
    def draw_ui_elements(self, frame, sign_name, confidence, hand_detected, fps):
        """Draw all UI elements on the frame"""
        try:
            # Draw hand detection status
            status_color = (0, 255, 0) if hand_detected else (0, 0, 255)
            status_text = "Hand Detected" if hand_detected else "Show Hand in Frame"
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Draw prediction if available
            if sign_name and confidence >= self.confidence_threshold:
                # Display prediction with confidence
                text = f"{sign_name} ({confidence:.1%})"
                color = (0, 255, 0)  # Green for high confidence
                
                # Add background for better text visibility
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
                text_x, text_y = 10, 70
                cv2.rectangle(frame, (text_x, text_y - text_size[1] - 10), 
                             (text_x + text_size[0] + 10, text_y + 10), (0, 0, 0), -1)
                
                cv2.putText(frame, text, (text_x, text_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
                
                # Add confidence bar
                bar_width = 300
                bar_height = 20
                bar_x, bar_y = 10, 100
                filled_width = int(bar_width * confidence)
                
                cv2.rectangle(frame, (bar_x, bar_y), 
                             (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
                cv2.rectangle(frame, (bar_x, bar_y), 
                             (bar_x + filled_width, bar_y + bar_height), color, -1)
                cv2.putText(frame, "Confidence", (bar_x, bar_y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            elif sign_name:
                text = f"Low confidence: {confidence:.1%}"
                cv2.putText(frame, text, (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)  # Orange for medium confidence
            
            # Draw FPS
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(frame, fps_text, (frame.shape[1] - 120, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw instructions
            instructions = [
                "Press 'q' to quit",
                "Press 'c' to clear history", 
                "Press 'r' to restart camera",
                "Press 'd' to toggle debug",
                "Press 'e' for emergency mode"
            ]
            
            for i, instruction in enumerate(instructions):
                y_pos = frame.shape[0] - 30 - (i * 25)
                cv2.putText(frame, instruction, (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw hand bounding box guide
            height, width = frame.shape[:2]
            center_x, center_y = width // 2, height // 2
            box_size = 250
            x1 = center_x - box_size // 2
            y1 = center_y - box_size // 2
            x2 = center_x + box_size // 2
            y2 = center_y + box_size // 2
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Place hand here", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        except Exception as e:
            logger.error(f"❌ Error drawing UI: {e}")
    
    def run_test(self):
        """Main method to run the ASL detection"""
        if self.emergency_mode:
            logger.warning("🚨 Starting in emergency mode - basic camera only")
            self.run_emergency_mode()
            return
            
        if not self.cap or not self.model:
            logger.critical("💥 Cannot start - essential components missing")
            print("🔧 Attempting emergency mode...")
            self.emergency_camera_test()
            return
        
        self.is_running = True
        self.frame_count = 0
        self.start_time = time.time()
        
        logger.info("🚀 Starting real-time ASL detection...")
        print("\n" + "="*50)
        print("🤟 ASL Real-Time Translator - Ultra Robust Version")
        print("="*50)
        print("📝 Instructions:")
        print("   - Show ASL signs in the green box")
        print("   - Ensure good lighting on your hand")
        print("   - Keep your hand steady and visible")
        print("   - Press 'q' to quit")
        print("   - Press 'c' to clear prediction history") 
        print("   - Press 'r' to restart camera if needed")
        print("   - Press 'd' to toggle debug mode")
        print("   - Press 'e' for emergency camera test")
        print("="*50 + "\n")
        
        debug_mode = False
        
        while self.is_running:
            try:
                # Check for frame timeout
                if time.time() - self.last_successful_frame_time > self.frame_timeout:
                    logger.warning("🔄 Frame timeout detected, attempting camera restart...")
                    self.cap.release()
                    self.cap = None
                    if not self.initialize_camera_with_retry():
                        logger.error("💥 Failed to restart camera, switching to emergency mode...")
                        self.run_emergency_mode()
                        break
                
                # Capture frame safely
                frame, success = self.safe_capture_frame()
                if not success:
                    # Display error message on black frame
                    error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(error_frame, "Camera Error - Attempting to reconnect...", 
                               (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(error_frame, "Press 'e' for emergency mode", 
                               (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow('ASL Real-Time Translator', error_frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('e'):
                        self.run_emergency_mode()
                        break
                    if key == ord('q'):
                        break
                        
                    time.sleep(0.5)
                    continue
                
                # Extract landmarks safely
                landmarks, processed_frame, hand_detected = self.safe_extract_landmarks(frame)
                
                # Make prediction if landmarks available
                sign_name = None
                confidence = 0.0
                
                if hand_detected and landmarks is not None:
                    predicted_class, raw_confidence = self.safe_predict(landmarks)
                    
                    if predicted_class is not None:
                        # Apply smoothing
                        smooth_pred, smooth_confidence = self.smooth_prediction(predicted_class, raw_confidence)
                        
                        if smooth_pred is not None and str(smooth_pred) in self.class_mapping:
                            sign_name = self.class_mapping[str(smooth_pred)]
                            confidence = smooth_confidence
                
                # Calculate FPS
                fps = self.calculate_fps()
                
                # Draw UI elements
                self.draw_ui_elements(processed_frame, sign_name, confidence, hand_detected, fps)
                
                # Display frame
                cv2.imshow('ASL Real-Time Translator', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("👋 Quit requested by user")
                    break
                elif key == ord('c'):
                    self.prediction_history.clear()
                    logger.info("🗑️ Prediction history cleared!")
                elif key == ord('r'):
                    logger.info("🔄 Camera restart requested...")
                    self.cap.release()
                    self.cap = None
                    if self.initialize_camera_with_retry():
                        logger.info("✅ Camera restarted successfully")
                    else:
                        logger.error("❌ Camera restart failed")
                elif key == ord('d'):
                    debug_mode = not debug_mode
                    status = "enabled" if debug_mode else "disabled"
                    logger.info(f"🔧 Debug mode {status}")
                elif key == ord('e'):
                    logger.info("🚨 Emergency mode requested...")
                    self.run_emergency_mode()
                    break
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {e}")
                # Try to continue despite errors
                try:
                    error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(error_frame, f"Error: {str(e)[:50]}...", 
                               (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(error_frame, "Press any key to continue...", 
                               (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow('ASL Real-Time Translator', error_frame)
                    cv2.waitKey(2000)  # Wait 2 seconds
                except:
                    pass
        
        self.cleanup()
        logger.info("✅ Real-time testing completed!")
    
    def run_emergency_mode(self):
        """Run emergency camera-only mode"""
        logger.info("🚨 Entering emergency mode - basic camera test")
        
        # Try to initialize any camera
        emergency_cap = None
        for i in range(4):
            try:
                emergency_cap = cv2.VideoCapture(i)
                if emergency_cap.isOpened():
                    logger.info(f"✅ Emergency camera {i} initialized")
                    break
                else:
                    emergency_cap = None
            except:
                emergency_cap = None
        
        if emergency_cap is None:
            logger.error("💥 No cameras available in emergency mode")
            print("❌ No cameras detected in emergency mode")
            print("🔧 Please check:")
            print("   - Camera connection")
            print("   - Camera drivers")
            print("   - Other applications using camera")
            input("Press Enter to exit...")
            return
        
        print("\n" + "="*50)
        print("🚨 EMERGENCY MODE - Basic Camera Test")
        print("="*50)
        print("📷 Camera is working!")
        print("🤟 ASL translation not available in emergency mode")
        print("⏹️  Press 'q' to exit emergency mode")
        print("="*50 + "\n")
        
        while True:
            try:
                ret, frame = emergency_cap.read()
                if ret:
                    # Display emergency info
                    cv2.putText(frame, "EMERGENCY MODE - Camera Working", 
                               (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, "ASL Translation Not Available", 
                               (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(frame, "Press 'q' to exit emergency mode", 
                               (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Emergency Camera Test', frame)
                else:
                    # Show error frame
                    error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(error_frame, "Emergency Camera Error", 
                               (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow('Emergency Camera Test', error_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                    
            except Exception as e:
                logger.error(f"❌ Emergency mode error: {e}")
                break
        
        if emergency_cap:
            emergency_cap.release()
        cv2.destroyAllWindows()
        logger.info("✅ Emergency mode completed")
    
    def cleanup(self):
        """Clean up resources safely"""
        self.is_running = False
        
        logger.info("🧹 Cleaning up resources...")
        
        try:
            if self.cap and self.cap.isOpened():
                self.cap.release()
                logger.info("✅ Camera released")
        except Exception as e:
            logger.error(f"❌ Error releasing camera: {e}")
        
        try:
            if self.hands:
                self.hands.close()
                logger.info("✅ MediaPipe resources released")
        except Exception as e:
            logger.error(f"❌ Error closing MediaPipe: {e}")
        
        try:
            cv2.destroyAllWindows()
            # Also destroy any specific windows that might remain
            for i in range(10):  # Try to close multiple windows
                cv2.waitKey(1)
            logger.info("✅ OpenCV windows closed")
        except Exception as e:
            logger.error(f"❌ Error closing windows: {e}")

def main():
    """Main function with comprehensive error handling"""
    tester = None
    
    try:
        print("🚀 Starting Ultra Robust ASL Translator...")
        print("📝 This version includes advanced error recovery and fallback mechanisms")
        print("🛡️  Designed to work reliably during presentations\n")
        
        # Create tester instance
        tester = UltraRobustASLTester()
        
        # Run the tester
        tester.run_test()
        
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"💥 Critical error in main: {e}")
        print("🔧 Attempting emergency cleanup...")
    finally:
        # Ensure cleanup happens no matter what
        if tester:
            tester.cleanup()
        print("👋 Program ended")

if __name__ == "__main__":
    main()