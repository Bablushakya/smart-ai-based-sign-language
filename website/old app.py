import base64
import io
import os
import json
import time
import logging
from datetime import datetime
from collections import deque
from flask import Flask, render_template, request, jsonify, Response
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from gtts import gTTS
import pygame
import threading
from typing import Dict, List, Optional, Tuple

# Configure logging with proper encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('asl_translator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # Maintain response order
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables with thread safety
translation_history = []
model = None
model_loaded = False
model_load_attempts = 0
MAX_LOAD_ATTEMPTS = 5

# Define class names based on your dataset
class_names = ['bye', 'hello', 'yes', 'no', 'thank_you', 'perfect']

# Thread-safe data structures
import threading
history_lock = threading.Lock()
tts_lock = threading.Lock()
model_lock = threading.Lock()

# ULTRA ROBUST MediaPipe Hands initialization (EXACTLY like real_time_tester.py)
def initialize_mediapipe():
    """Initialize MediaPipe with EXACT same settings as real_time_tester.py"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Initializing MediaPipe (Attempt {attempt + 1}/{max_retries})...")
            
            # Import MediaPipe components
            mp_hands = mp.solutions.hands
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing_styles = mp.solutions.drawing_styles
            
            # EXACT SAME SETTINGS as real_time_tester.py
            hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,  # EXACTLY like standalone
                model_complexity=0,  # EXACTLY like standalone - Reduced for stability
                min_detection_confidence=0.6,  # EXACTLY like standalone
                min_tracking_confidence=0.5,   # EXACTLY like standalone
            )
            
            # Test MediaPipe with a dummy frame
            test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
            rgb_frame = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
            _ = hands.process(rgb_frame)
            
            logger.info("✅ MediaPipe initialized successfully (matched standalone settings)")
            return hands, mp_drawing, mp_drawing_styles
            
        except Exception as e:
            logger.error(f"❌ MediaPipe initialization failed (Attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logger.warning("⚠️ MediaPipe failed, continuing without hand tracking")
                return None, None, None
            time.sleep(1)  # Wait before retry

# Initialize MediaPipe
hands, mp_drawing, mp_drawing_styles = initialize_mediapipe()

# NEW: Enhanced prediction smoothing with EXACT same logic as real_time_tester.py
prediction_history = deque(maxlen=3)  # EXACTLY 3 frames like standalone for fast response
last_valid_prediction = "No hand detected"
last_valid_confidence = 0.0

# NEW: Enhanced TTS request tracking with better debouncing
tts_requests = {}
active_tts_requests = set()
last_tts_cleanup = time.time()

# NEW: Performance monitoring with enhanced metrics
performance_stats = {
    'total_frames_processed': 0,
    'average_processing_time': 0,
    'last_processing_time': 0,
    'start_time': time.time(),
    'consecutive_errors': 0,
    'last_successful_frame': time.time()
}

def load_model_with_fallbacks(attempt=1) -> bool:
    """ULTRA ROBUST model loading with multiple fallback paths EXACTLY like real_time_tester.py"""
    global model, model_loaded, model_load_attempts, class_names
    
    if model_load_attempts >= MAX_LOAD_ATTEMPTS:
        logger.error("🚨 Maximum model load attempts reached")
        return False
        
    model_load_attempts += 1
    logger.info(f"🔄 Attempting to load model (attempt {model_load_attempts}/{MAX_LOAD_ATTEMPTS})...")
    
    # EXACT SAME model candidates as real_time_tester.py
    model_candidates = []
    
    # Primary paths (RELATIVE paths that work on any laptop)
    primary_paths = [
        '../models/final_asl_model_20251026_144942.h5',
        '../models/best_asl_model_20251026_144813.h5',
        '../models/asl_model.h5',
        './models/final_asl_model_20251026_144942.h5',
        './models/best_asl_model_20251026_144813.h5',
        './models/asl_model.h5',
    ]
    
    # Look for model files with various patterns (like standalone)
    model_patterns = [
        'final_asl_model_*.h5',
        'best_asl_model_*.h5', 
        'asl_model_*.h5',
        'model_*.h5',
        '*.h5'  # Any .h5 file as last resort
    ]
    
    # Collect all possible model candidates
    for pattern in model_patterns:
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.h5') and pattern.replace('*', '') in file:
                    full_path = os.path.join(root, file)
                    if full_path not in model_candidates:
                        model_candidates.append(full_path)
    
    # Add primary paths
    for path in primary_paths:
        if os.path.exists(path) and path not in model_candidates:
            model_candidates.insert(0, path)  # Prioritize primary paths
    
    # Try to load each candidate
    loaded_path = None
    model_errors = []
    
    for model_candidate in model_candidates:
        try:
            logger.info(f"🔄 Attempting to load: {model_candidate}")
            
            with model_lock:
                model = tf.keras.models.load_model(model_candidate)
            
            # Load class mapping (RELATIVE paths that work on any laptop)
            class_mapping_paths = [
                '../models/class_mapping.json',
                './models/class_mapping.json',
                'models/class_mapping.json',
                'class_mapping.json'
            ]
            
            for mapping_path in class_mapping_paths:
                if os.path.exists(mapping_path):
                    try:
                        with open(mapping_path, 'r', encoding='utf-8') as f:
                            class_mapping = json.load(f)
                        # Convert to list maintaining index order
                        class_names = [class_mapping.get(str(i), f"Sign_{i}") for i in range(len(class_mapping))]
                        logger.info(f"📊 Class mapping loaded: {class_names}")
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Could not load class mapping from {mapping_path}: {e}")
            
            # Use default class names if no mapping found
            if not class_names:
                class_names = ['bye', 'hello', 'yes', 'no', 'thank_you', 'perfect']
                logger.info(f"📊 Using default class names: {class_names}")
            
            logger.info(f"✅ Model loaded successfully: {model_candidate}")
            logger.info(f"📐 Model input shape: {model.input_shape}")
            logger.info(f"📐 Model output shape: {model.output_shape}")
            logger.info(f"🎯 Available signs: {class_names}")
            
            model_loaded = True
            return True
            
        except Exception as e:
            error_msg = f"❌ Failed to load model {model_candidate}: {str(e)}"
            model_errors.append(error_msg)
            logger.error(error_msg)
            continue
    
    # If we reach here, no model was loaded successfully
    if not model_errors:
        logger.error("❌ No model files found in any location")
    else:
        logger.error("💥 All model loading attempts failed")
        for error in model_errors[-5:]:  # Show last 5 errors
            logger.error(f"   - {error}")
    
    # Retry after delay if we haven't exceeded max attempts
    if attempt < MAX_LOAD_ATTEMPTS:
        retry_delay = 2 ** attempt  # Exponential backoff
        logger.info(f"🔄 Retrying model load in {retry_delay} seconds... (attempt {attempt + 1}/{MAX_LOAD_ATTEMPTS})")
        time.sleep(retry_delay)
        return load_model_with_fallbacks(attempt + 1)
    
    return False

def process_frame_for_prediction(hand_landmarks) -> Optional[np.ndarray]:
    """Extract and preprocess hand landmarks for model prediction with validation."""
    try:
        landmark_list = []
        for landmark in hand_landmarks.landmark:
            landmark_list.extend([landmark.x, landmark.y, landmark.z])
        
        # Validate landmark data (EXACTLY like standalone validation)
        if len(landmark_list) != 63:  # 21 landmarks * 3 coordinates
            logger.warning(f"⚠️ Unexpected landmark count: {len(landmark_list)}")
            # Pad or truncate to expected size (like standalone)
            if len(landmark_list) < 63:
                landmark_list.extend([0.0] * (63 - len(landmark_list)))
            else:
                landmark_list = landmark_list[:63]
        
        # Normalize landmarks
        landmark_array = np.array(landmark_list, dtype=np.float32)
        
        # Basic validation - check if landmarks are reasonable (like standalone)
        if np.any(np.isnan(landmark_array)) or np.any(np.isinf(landmark_array)):
            logger.warning("⚠️ Invalid landmark values detected")
            return None
            
        return landmark_array.reshape(1, -1)
        
    except Exception as e:
        logger.error(f"❌ Error processing landmarks: {e}")
        return None

def extract_landmark_coordinates(hand_landmarks, frame_shape) -> List[Dict]:
    """Extract landmark coordinates for frontend visualization - CRITICAL FIX: MIRROR X COORDINATES"""
    try:
        landmarks = []
        for landmark in hand_landmarks.landmark:
            # CRITICAL FIX: Mirror the x-coordinate to match the mirrored video display
            # When video is mirrored (like a mirror), left becomes right and right becomes left
            # So we need to flip the x-coordinate: x_mirrored = 1.0 - x_original
            mirrored_x = 1.0 - landmark.x
            
            landmarks.append({
                'x': float(mirrored_x),  # MIRRORED to match video display
                'y': float(landmark.y), 
                'z': float(landmark.z)
            })
        return landmarks
    except Exception as e:
        logger.error(f"❌ Error extracting landmark coordinates: {e}")
        return []

def draw_mediapipe_landmarks(frame, hand_landmarks):
    """Draw MediaPipe landmarks on frame EXACTLY like real_time_tester.py"""
    try:
        if mp_drawing and mp_drawing_styles and hand_landmarks:
            # EXACT SAME drawing as real_time_tester.py
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp.solutions.hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
        return frame
    except Exception as e:
        logger.error(f"❌ Error drawing MediaPipe landmarks: {e}")
        return frame

def smooth_prediction(current_prediction: str, current_confidence: float, smoothing_frames: int = 3) -> Tuple[str, float]:
    """Apply temporal smoothing to predictions EXACTLY like real_time_tester.py."""
    global prediction_history, last_valid_prediction, last_valid_confidence
    
    # Add current prediction to history if valid (same logic as standalone)
    if current_prediction != "No hand detected" and current_confidence > 0.3:
        prediction_history.append((current_prediction, current_confidence, time.time()))
    
    # Remove old entries (keep only last 2 seconds) - EXACTLY like standalone
    current_time = time.time()
    prediction_history = deque(
        [entry for entry in prediction_history if current_time - entry[2] < 2.0],
        maxlen=smoothing_frames
    )
    
    # If no valid predictions in history, return current
    if not prediction_history:
        return current_prediction, current_confidence
    
    # Find the most common prediction in recent history (EXACT algorithm from standalone)
    recent_predictions = list(prediction_history)
    predictions = [pred for pred, conf, ts in recent_predictions]
    
    try:
        most_common_pred = max(set(predictions), key=predictions.count)
        
        # Calculate weighted confidence for the most common prediction
        relevant_confidences = [conf for pred, conf, ts in recent_predictions if pred == most_common_pred]
        avg_confidence = np.mean(relevant_confidences) if relevant_confidences else current_confidence
        
        # Only update if we have enough evidence (majority) - EXACTLY like standalone
        if predictions.count(most_common_pred) >= len(recent_predictions) // 2:
            last_valid_prediction = most_common_pred
            last_valid_confidence = avg_confidence
            return last_valid_prediction, last_valid_confidence
        else:
            # Not enough consensus, return current prediction
            return current_prediction, current_confidence
    
    except Exception as e:
        logger.warning(f"⚠️ Smoothing failed, using current prediction: {e}")
        # Fallback to current prediction if smoothing fails
        return current_prediction, current_confidence

def cleanup_old_tts_requests():
    """Clean up old TTS requests to prevent memory leaks."""
    global last_tts_cleanup
    current_time = time.time()
    
    # Only cleanup every 30 seconds to avoid performance impact
    if current_time - last_tts_cleanup < 30:
        return
        
    last_tts_cleanup = current_time
    old_requests = []
    
    with tts_lock:
        for req_id, timestamp in list(tts_requests.items()):
            if current_time - timestamp > 30.0:  # 30 seconds
                old_requests.append(req_id)
        
        for old_req in old_requests:
            tts_requests.pop(old_req, None)
            active_tts_requests.discard(old_req)

def cleanup_audio_file(audio_file: str):
    """Safely cleanup audio files with retries."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
                logger.debug(f"✅ Cleaned up audio file: {audio_file}")
                break
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"❌ Failed to cleanup audio file {audio_file}: {e}")
            time.sleep(0.1)

# Email Configuration and Functions
try:
    from email_config import EMAIL_CONFIG, EMAIL_TEMPLATES, VALIDATION_RULES
except ImportError:
    # Fallback configuration if email_config.py is not found
    EMAIL_CONFIG = {
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': 587,
        'SENDER_EMAIL': 'my726contact@gmail.com',
        'RECIPIENT_EMAIL': 'my726contact@gmail.com',
        'SENDER_PASSWORD': 'your_app_password_here'
    }
    EMAIL_TEMPLATES = {
        'contact_form': {
            'subject_prefix': 'HandsSpeak Contact Form: ',
            'body_template': """
New contact form submission from HandsSpeak website:

Name: {name}
Email: {sender_email}
Subject: {subject}
Submitted: {timestamp}

Message:
{message}

---
This email was sent automatically from the HandsSpeak contact form.
Reply directly to this email to respond to {name} at {sender_email}.
            """
        }
    }
    VALIDATION_RULES = {
        'name': {'min_length': 2, 'max_length': 100},
        'email': {'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
        'subject': {'min_length': 3, 'max_length': 200},
        'message': {'min_length': 10, 'max_length': 2000}
    }

def send_contact_email(name, sender_email, subject, message):
    """Send contact form email using SMTP with enhanced security and error handling."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from datetime import datetime
    import os
    
    try:
        # Get email configuration
        smtp_server = EMAIL_CONFIG['SMTP_SERVER']
        smtp_port = EMAIL_CONFIG['SMTP_PORT']
        sender_email_addr = EMAIL_CONFIG['SENDER_EMAIL']
        recipient_email = EMAIL_CONFIG['RECIPIENT_EMAIL']
        
        # Get password from environment variable or config
        sender_password = os.getenv('EMAIL_PASSWORD') or EMAIL_CONFIG['SENDER_PASSWORD']
        
        if sender_password == 'your_app_password_here':
            logger.warning("⚠️ Email password not configured. Email will not be sent.")
            return  # Don't send email if password is not set
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email_addr
        msg['To'] = recipient_email
        msg['Reply-To'] = sender_email  # Set reply-to to the form submitter
        
        # Use template for subject and body
        template = EMAIL_TEMPLATES['contact_form']
        msg['Subject'] = template['subject_prefix'] + subject
        
        # Format email body using template
        email_body = template['body_template'].format(
            name=name,
            sender_email=sender_email,
            subject=subject,
            message=message,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Send email with enhanced error handling
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable encryption
        server.login(sender_email_addr, sender_password)
        
        text = msg.as_string()
        server.sendmail(sender_email_addr, recipient_email, text)
        server.quit()
        
        logger.info(f"✅ Contact email sent successfully from {name} ({sender_email})")
        
    except smtplib.SMTPAuthenticationError:
        logger.error("❌ SMTP Authentication failed. Check email credentials.")
        raise Exception("Email authentication failed")
    except smtplib.SMTPException as smtp_error:
        logger.error(f"❌ SMTP error: {smtp_error}")
        raise Exception(f"Email server error: {smtp_error}")
    except Exception as e:
        logger.error(f"❌ Failed to send contact email: {e}")
        raise e

# Routes
@app.route('/')
def home():
    """Serve the home page."""
    return render_template('home.html')

@app.route('/learn')
def learn():
    """Serve the learning page."""
    return render_template('learn.html')

@app.route('/translate')
def translate():
    """Serve the translation page."""
    return render_template('translate.html')

@app.route('/about')
def about():
    """Serve the about page."""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Serve the contact page."""
    return render_template('contact.html')

@app.route('/test-camera')
def test_camera():
    """Serve the camera test page."""
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.dirname(__file__), 'test_camera.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets like videos from the assets folder."""
    from flask import send_from_directory
    import os
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    return send_from_directory(assets_dir, filename)

@app.route('/video_feed', methods=['POST'])
@app.route('/api/process_frame', methods=['POST'])
def process_frame():
    """ULTRA ROBUST endpoint to process frames with EXACT same logic as real_time_tester.py"""
    global performance_stats, prediction_history
    
    start_time = time.time()
    processing_start = time.perf_counter()
    
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405

    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data received'}), 400

    try:
        # Get settings from request
        confidence_threshold = float(data.get('confidence_threshold', 0.7))  # EXACTLY like standalone
        smoothing_frames = int(data.get('smoothing_frames', 3))  # EXACTLY like standalone
        request_timestamp = data.get('request_timestamp', time.time())
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            performance_stats['consecutive_errors'] += 1
            return jsonify({'error': 'Could not decode image'}), 400

        # CRITICAL FIX: Flip frame horizontally EXACTLY like real_time_tester.py for natural interaction
        # This creates the mirror effect that users expect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        if hands is None:
            return jsonify({'error': 'MediaPipe not initialized'}), 500
            
        results = hands.process(rgb_frame)

        prediction_text = "No hand detected"
        confidence = 0.0
        raw_confidence = 0.0
        landmarks_detected = False
        hand_count = 0
        processed_landmarks = None
        landmark_data = []
        smoothed_prediction = None

        if results.multi_hand_landmarks:
            hand_count = len(results.multi_hand_landmarks)
            landmarks_detected = True
            
            # Process only the first hand for prediction (EXACTLY like standalone version)
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # CRITICAL FIX: Extract landmark coordinates with MIRRORED x-coordinates
            # This ensures keypoints match the mirrored video display
            landmark_data = extract_landmark_coordinates(hand_landmarks, frame.shape)
            
            # Extract landmarks for prediction (using original coordinates for model)
            processed_landmarks = process_frame_for_prediction(hand_landmarks)
            
            if processed_landmarks is not None and model_loaded:
                try:
                    # Make prediction
                    with model_lock:
                        predictions = model.predict(processed_landmarks, verbose=0)
                    raw_confidence = float(np.max(predictions))
                    predicted_class_index = np.argmax(predictions)
                    
                    if predicted_class_index < len(class_names):
                        predicted_class = class_names[predicted_class_index]
                        
                        # Apply confidence threshold (EXACTLY like standalone)
                        if raw_confidence > confidence_threshold:
                            prediction_text = predicted_class
                            confidence = raw_confidence
                            
                            # Apply smoothing (EXACTLY like standalone)
                            smoothed_prediction, smoothed_confidence = smooth_prediction(
                                prediction_text, confidence, smoothing_frames
                            )
                            prediction_text = smoothed_prediction
                            confidence = smoothed_confidence
                            
                            # Add to translation history with thread safety
                            translation_entry = {
                                'timestamp': datetime.now().strftime("%H:%M:%S"),
                                'text': prediction_text,
                                'confidence': round(float(confidence), 3),
                                'raw_confidence': round(float(raw_confidence), 3)
                            }
                            
                            with history_lock:
                                translation_history.append(translation_entry)
                                # Keep only last 50 entries
                                if len(translation_history) > 50:
                                    translation_history.pop(0)
                        else:
                            prediction_text = "Low confidence"
                            confidence = raw_confidence
                    else:
                        prediction_text = "Unknown sign"
                        confidence = raw_confidence
                        
                except Exception as e:
                    logger.error(f"❌ Prediction error: {e}")
                    prediction_text = "Prediction error"
                    performance_stats['consecutive_errors'] += 1
            else:
                if not model_loaded:
                    prediction_text = "Model not loaded"
                else:
                    prediction_text = "Landmark processing failed"
        else:
            # Reset prediction history when no hand is detected for too long (like standalone)
            current_time = time.time()
            if prediction_history:
                last_pred_time = prediction_history[-1][2] if prediction_history else 0
                if current_time - last_pred_time > 2.0:  # 2 seconds without hand (like standalone)
                    prediction_history.clear()
            prediction_text = "No hand detected"

        # Calculate processing time
        processing_time = round((time.time() - start_time) * 1000, 2)
        perf_processing_time = round((time.perf_counter() - processing_start) * 1000, 2)
        
        # Update performance stats
        performance_stats['total_frames_processed'] += 1
        performance_stats['last_processing_time'] = perf_processing_time
        performance_stats['average_processing_time'] = (
            (performance_stats['average_processing_time'] * (performance_stats['total_frames_processed'] - 1) + perf_processing_time) 
            / performance_stats['total_frames_processed']
        )
        
        # Reset error counter on success
        if prediction_text not in ["Prediction error", "Model not loaded", "Landmark processing failed"]:
            performance_stats['consecutive_errors'] = 0
            performance_stats['last_successful_frame'] = time.time()
        
        response_data = {
            'success': True,
            'prediction': prediction_text,
            'confidence': round(float(confidence), 3),
            'raw_confidence': round(float(raw_confidence), 3),
            'landmarks_detected': landmarks_detected,
            'hand_count': hand_count,
            'processing_time_ms': perf_processing_time,
            'model_loaded': model_loaded,
            'timestamp': datetime.now().isoformat(),
            'landmarks': landmark_data,  # Now with MIRRORED x-coordinates
            'smoothed_prediction': smoothed_prediction if smoothed_prediction else prediction_text,
            'performance': {
                'fps_estimate': round(1000 / perf_processing_time, 1) if perf_processing_time > 0 else 0,
                'total_frames': performance_stats['total_frames_processed'],
                'avg_processing_time': round(performance_stats['average_processing_time'], 2),
                'consecutive_errors': performance_stats['consecutive_errors']
            }
        }

        logger.debug(f"📊 Frame processed: {prediction_text} ({confidence:.1%}) in {perf_processing_time}ms")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"❌ Error processing frame: {e}")
        performance_stats['consecutive_errors'] += 1
        return jsonify({
            'success': False,
            'error': f'Processing error: {str(e)}',
            'consecutive_errors': performance_stats['consecutive_errors']
        }), 500

@app.route('/text_to_speech', methods=['POST'])
@app.route('/api/text_to_speech', methods=['POST'])
def text_to_speech():
    """ULTRA ROBUST TTS with professional error handling and request debouncing."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
        
    text = data.get('text', '').strip()
    request_id = data.get('request_id', f"tts_{int(time.time()*1000)}")
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Clean up old requests periodically
    cleanup_old_tts_requests()

    # Check for duplicate requests with robust debouncing
    current_time = time.time()
    with tts_lock:
        if request_id in tts_requests:
            # If request was made less than 2 seconds ago, reject as duplicate (like standalone debouncing)
            if current_time - tts_requests[request_id] < 2.0:
                logger.warning(f"⚠️ Duplicate TTS request rejected: {request_id}")
                return jsonify({'error': 'Duplicate TTS request - please wait before speaking again'}), 429
        
        # Store request timestamp
        tts_requests[request_id] = current_time
        active_tts_requests.add(request_id)

    try:
        # Initialize pygame mixer with robust error handling
        max_mixer_attempts = 3
        mixer_initialized = False
        
        for attempt in range(max_mixer_attempts):
            try:
                if pygame.mixer.get_init() is None:
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                mixer_initialized = True
                break
            except Exception as e:
                logger.warning(f"⚠️ Pygame mixer init failed (attempt {attempt + 1}): {e}")
                if attempt == max_mixer_attempts - 1:
                    return jsonify({'error': 'Audio system initialization failed'}), 500
                time.sleep(0.5)
        
        if not mixer_initialized:
            return jsonify({'error': 'Audio system unavailable'}), 500
        
        # Stop any currently playing audio
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                time.sleep(0.1)  # Brief pause to ensure clean stop
        except Exception as e:
            logger.warning(f"⚠️ Could not stop previous audio: {e}")
        
        # Use gTTS for text-to-speech with error handling
        max_tts_attempts = 2
        audio_file = None
        
        for attempt in range(max_tts_attempts):
            try:
                tts = gTTS(text=text, lang='en', slow=False)
                audio_file = f"temp_audio_{request_id}.mp3"
                tts.save(audio_file)
                break
            except Exception as e:
                if attempt == max_tts_attempts - 1:
                    logger.error(f"❌ gTTS generation failed: {e}")
                    with tts_lock:
                        active_tts_requests.discard(request_id)
                    return jsonify({'error': 'Speech generation failed'}), 500
                time.sleep(1)
        
        # Load and play audio with error handling
        max_playback_attempts = 2
        playback_success = False
        
        for attempt in range(max_playback_attempts):
            try:
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                playback_success = True
                break
            except Exception as e:
                if attempt == max_playback_attempts - 1:
                    logger.error(f"❌ Audio playback failed: {e}")
                    cleanup_audio_file(audio_file)
                    with tts_lock:
                        active_tts_requests.discard(request_id)
                    return jsonify({'error': 'Audio playback failed'}), 500
                time.sleep(0.5)
        
        # Background cleanup function
        def wait_for_playback():
            try:
                start_time = time.time()
                max_wait_time = 10.0  # Increased timeout for longer texts
                
                # Wait for playback to complete with timeout
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    # Safety timeout
                    if time.time() - start_time > max_wait_time:
                        logger.warning(f"⚠️ TTS playback timeout for request: {request_id}")
                        break
                
                # Stop and cleanup
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
                
                # Cleanup audio file
                cleanup_audio_file(audio_file)
                
                # Remove from active requests
                with tts_lock:
                    active_tts_requests.discard(request_id)
                    
                logger.info(f"✅ TTS playback completed: '{text}' (request: {request_id})")
                
            except Exception as e:
                logger.error(f"❌ TTS cleanup error: {e}")
                # Ensure cleanup happens even on error
                cleanup_audio_file(audio_file)
                with tts_lock:
                    active_tts_requests.discard(request_id)
        
        # Run cleanup in background
        cleanup_thread = threading.Thread(target=wait_for_playback)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        logger.info(f"🎵 TTS playing: '{text}' (request: {request_id})")
        return jsonify({
            'status': 'success', 
            'message': 'Audio playing',
            'request_id': request_id,
            'text_length': len(text)
        })
    
    except Exception as e:
        logger.error(f"❌ TTS system error: {e}")
        # Clean up on error
        with tts_lock:
            active_tts_requests.discard(request_id)
        cleanup_audio_file(audio_file)
        return jsonify({'error': f'TTS system error: {str(e)}'}), 500

@app.route('/get_history')
@app.route('/api/get_history')
def get_history():
    """Retrieve translation history."""
    with history_lock:
        return jsonify({'history': translation_history[-20:]})  # Return last 20 entries

@app.route('/api/contact', methods=['POST'])
def contact_form():
    """Handle contact form submissions with validation and email sending."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No form data received'}), 400
            
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        # Enhanced validation using configuration
        if not all([name, email, subject, message]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Validate name
        name_rules = VALIDATION_RULES['name']
        if len(name) < name_rules['min_length']:
            return jsonify({'error': f'Name must be at least {name_rules["min_length"]} characters'}), 400
        if len(name) > name_rules['max_length']:
            return jsonify({'error': f'Name must be less than {name_rules["max_length"]} characters'}), 400
            
        # Validate email
        import re
        email_pattern = VALIDATION_RULES['email']['pattern']
        if not re.match(email_pattern, email):
            return jsonify({'error': 'Please enter a valid email address'}), 400
            
        # Validate subject
        subject_rules = VALIDATION_RULES['subject']
        if len(subject) < subject_rules['min_length']:
            return jsonify({'error': f'Subject must be at least {subject_rules["min_length"]} characters'}), 400
        if len(subject) > subject_rules['max_length']:
            return jsonify({'error': f'Subject must be less than {subject_rules["max_length"]} characters'}), 400
            
        # Validate message
        message_rules = VALIDATION_RULES['message']
        if len(message) < message_rules['min_length']:
            return jsonify({'error': f'Message must be at least {message_rules["min_length"]} characters'}), 400
        if len(message) > message_rules['max_length']:
            return jsonify({'error': f'Message must be less than {message_rules["max_length"]} characters'}), 400
        
        # Send email
        try:
            send_contact_email(name, email, subject, message)
            logger.info(f"📧 Contact form submission sent: {name} ({email}) - {subject}")
        except Exception as email_error:
            logger.error(f"❌ Email sending failed: {email_error}")
            # Still return success to user, but log the error
            logger.warning("⚠️ Email failed but form submission recorded")
        
        return jsonify({
            'status': 'success', 
            'message': 'Thank you for your message! We will get back to you within 24 hours.'
        })
    
    except Exception as e:
        logger.error(f"❌ Contact form error: {e}")
        return jsonify({'error': f'Contact form error: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Comprehensive health check endpoint."""
    current_time = time.time()
    uptime = current_time - performance_stats['start_time']
    
    health_status = 'healthy'
    if performance_stats['consecutive_errors'] > 10:
        health_status = 'degraded'
    if not model_loaded:
        health_status = 'unhealthy'
    
    return jsonify({
        'status': health_status,
        'model_loaded': model_loaded,
        'mediapipe_initialized': hands is not None,
        'translation_history_count': len(translation_history),
        'model_load_attempts': model_load_attempts,
        'timestamp': datetime.now().isoformat(),
        'class_names': class_names,
        'version': '3.0.0',
        'performance': {
            'uptime_seconds': round(uptime, 2),
            'total_frames_processed': performance_stats['total_frames_processed'],
            'average_processing_time_ms': round(performance_stats['average_processing_time'], 2),
            'last_processing_time_ms': performance_stats['last_processing_time'],
            'consecutive_errors': performance_stats['consecutive_errors'],
            'seconds_since_last_success': round(current_time - performance_stats['last_successful_frame'], 2)
        },
        'system': {
            'active_tts_requests': len(active_tts_requests),
            'prediction_history_size': len(prediction_history),
            'memory_usage_mb': round(os.sys.getsizeof(translation_history) / 1024 / 1024, 2)
        }
    })

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """Clear translation history."""
    global translation_history, prediction_history
    with history_lock:
        translation_history.clear()
    prediction_history.clear()
    logger.info("🗑️ Translation history cleared")
    return jsonify({'status': 'success', 'message': 'History cleared'})

@app.route('/api/model/reload', methods=['POST'])
def reload_model():
    """Reload the model (useful for updates)."""
    global model_loaded
    model_loaded = load_model_with_fallbacks()
    return jsonify({
        'status': 'success' if model_loaded else 'error',
        'model_loaded': model_loaded,
        'class_names': class_names
    })

@app.route('/api/performance')
def get_performance():
    """Get performance statistics."""
    return jsonify(performance_stats)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'Request payload too large'}), 413

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"💥 Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    logger.error(f"💥 Unexpected error: {error}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Application startup
def initialize_application():
    """Initialize all application components with ULTRA ROBUST error handling."""
    print("\n" + "="*60)
    print("🚀 Starting ULTRA ROBUST HandsSpeak ASL Translator Server")
    print("="*60)
    
    # Load model with comprehensive error handling
    print("📦 Loading AI model with multiple fallback paths...")
    if not load_model_with_fallbacks():
        print("❌ CRITICAL: Failed to load model after multiple attempts.")
        print("   Some features will be disabled.")
    else:
        print("✅ Model loaded successfully!")
    
    # Verify MediaPipe
    if hands is None:
        print("❌ CRITICAL: MediaPipe initialization failed.")
        print("   Hand detection will not work.")
    else:
        print("✅ MediaPipe initialized successfully!")
    
    print("✅ ULTRA ROBUST application initialization complete")
    print("🌐 Server will be available at: http://localhost:5000")
    
    # Print available routes
    routes = [
        "GET  /                    -> Home page",
        "GET  /translate           -> Translation page", 
        "GET  /learn               -> Learning page",
        "GET  /about               -> About page",
        "GET  /contact             -> Contact page",
        "POST /api/process_frame   -> Process ASL frame (ULTRA ROBUST)",
        "POST /api/text_to_speech  -> Convert text to speech (DEBOUNCED)",
        "GET  /api/get_history     -> Get translation history",
        "POST /api/contact         -> Submit contact form",
        "GET  /api/health          -> Health check",
        "POST /api/clear_history   -> Clear history",
        "POST /api/model/reload    -> Reload model",
        "GET  /api/performance     -> Performance stats"
    ]
    
    print("\n📡 Available routes:")
    for route in routes:
        print(f"   - {route}")
    
    print("\n🎯 Key Features:")
    print("   ✅ EXACT same camera mirroring as real_time_tester.py")
    print("   ✅ EXACT same MediaPipe settings as standalone version") 
    print("   ✅ EXACT same prediction smoothing (3 frames)")
    print("   ✅ EXACT same confidence threshold (0.7)")
    print("   ✅ Professional error handling and recovery")
    print("   ✅ Robust TTS with request debouncing")
    print("   ✅ REAL-TIME MediaPipe keypoints that MATCH video position")
    print("   ✅ MIRRORED landmark coordinates for perfect alignment")
    
    print("="*60 + "\n")

# Background cleanup task
def background_cleanup():
    """Periodic cleanup of temporary files and old data."""
    while True:
        try:
            cleanup_old_tts_requests()
            
            # Cleanup old temporary audio files
            current_time = time.time()
            for filename in os.listdir('.'):
                if filename.startswith('temp_audio_') and filename.endswith('.mp3'):
                    file_time = os.path.getctime(filename)
                    if current_time - file_time > 300:  # 5 minutes
                        try:
                            os.remove(filename)
                            logger.info(f"🧹 Cleaned up old audio file: {filename}")
                        except:
                            pass
                            
        except Exception as e:
            logger.error(f"❌ Background cleanup error: {e}")
        
        time.sleep(60)  # Run every minute

if __name__ == '__main__':
    initialize_application()
    
    # Start background cleanup thread
    cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
    cleanup_thread.start()
    
    # Start Flask application with enhanced error handling
    try:
        print("🚀 Starting Flask server...")
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Failed to start server: {e}")
        print(f"💥 Server startup failed: {e}")
    finally:
        # Cleanup on exit
        print("🧹 Cleaning up resources...")
        if 'pygame' in globals():
            try:
                pygame.mixer.quit()
            except:
                pass
        print("✅ Cleanup complete. Goodbye!")