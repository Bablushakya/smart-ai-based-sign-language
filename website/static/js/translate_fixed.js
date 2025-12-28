// ULTRA OPTIMIZED ASL TRANSLATOR - MAXIMUM PERFORMANCE & ROBUST ERROR HANDLING
class ASLTranslator {
    constructor() {
        // Core state - OPTIMIZED
        this.isTranslating = false;
        this.videoStream = null;
        this.isCameraInitialized = false;
        this.cameraRetryCount = 0;
        this.maxCameraRetries = 3;
        
        // Elements - CACHED
        this.videoElement = null;
        this.outputCanvas = null;
        this.keypointCanvas = null;
        this.ctx = null;
        this.keypointCtx = null;
        
        // Performance settings - ENHANCED
        this.confidenceThreshold = 0.75;
        this.smoothingFrames = 4;
        this.targetFPS = 30;
        this.frameInterval = 1000 / this.targetFPS;
        this.lastFrameTime = 0;
        
        // Processing state - OPTIMIZED
        this.processingFrame = false;
        this.animationFrameId = null;
        this.consecutiveErrors = 0;
        this.maxConsecutiveErrors = 5;
        this.currentFrameController = null;
        
        // Prediction state - ENHANCED ACCURACY
        this.predictionHistory = [];
        this.lastValidPrediction = null;
        this.stabilityCounter = 0;
        this.minStabilityFrames = 2;
        
        // Performance tracking
        this.frameCount = 0;
        this.fps = 0;
        this.processingTimes = [];
        this.averageProcessingTime = 0;
        
        // Keypoints state
        this.currentLandmarks = [];
        this.handDetected = false;
        
        // Pre-calculated connections for MediaPipe
        this.handConnections = [
            [0,1],[1,2],[2,3],[3,4], [0,5],[5,6],[6,7],[7,8],
            [0,9],[9,10],[10,11],[11,12], [0,13],[13,14],[14,15],[15,16],
            [0,17],[17,18],[18,19],[19,20], [5,9],[9,13],[13,17]
        ];
        
        console.log('🚀 Initializing Ultra Optimized ASL Translator...');
        this.init();
    }

    async init() {
        try {
            await this.initializeElements();
            this.setupEventListeners();
            this.setupCanvas();
            await this.initializeCamera();
            console.log('✅ Ultra Optimized ASL Translator initialized');
        } catch (error) {
            console.error('❌ Initialization failed:', error);
            this.showError('Failed to initialize translator: ' + error.message);
        }
    }

    async initializeElements() {
        // Cache all elements with null checks
        const elements = {
            'webcamVideo': 'videoElement',
            'outputCanvas': 'outputCanvas', 
            'keypointCanvas': 'keypointCanvas',
            'startBtn': 'startBtn',
            'stopBtn': 'stopBtn',
            'statusIndicator': 'statusIndicator',
            'textOutput': 'textOutput',
            'gestureName': 'gestureName',
            'confidenceBadge': 'confidenceBadge',
            'handsCount': 'handsCount',
            'fpsCounter': 'fpsCounter',
            'processingTime': 'processingTimeElement',
            'currentSignName': 'currentSignName',
            'currentSignConfidence': 'currentSignConfidence'
        };

        for (const [id, property] of Object.entries(elements)) {
            this[property] = document.getElementById(id);
            if (!this[property] && id !== 'startBtn' && id !== 'stopBtn') {
                console.warn(`⚠️ Element with id '${id}' not found`);
            }
        }

        // Modal elements
        this.permissionModal = document.getElementById('permissionModal');
        this.enableCameraBtn = document.getElementById('enableCameraBtn');
        this.cancelCameraBtn = document.getElementById('cancelCameraBtn');
        this.cameraErrorModal = document.getElementById('cameraErrorModal');
        this.retryCameraBtn = document.getElementById('retryCameraBtn');
        this.loadingSpinner = document.getElementById('loadingSpinner');

        console.log('✅ All elements cached');
    }

    setupCanvas() {
        try {
            this.ctx = this.outputCanvas.getContext('2d', { 
                alpha: false,
                desynchronized: true // Performance boost
            });
            this.keypointCtx = this.keypointCanvas.getContext('2d', { 
                alpha: true,
                desynchronized: true
            });
            
            // Pre-configure canvas styles
            this.keypointCtx.lineCap = 'round';
            this.keypointCtx.lineJoin = 'round';
            this.keypointCtx.imageSmoothingEnabled = false;
            
            this.setupCanvasDimensions();
            console.log('✅ Canvas contexts optimized');
        } catch (error) {
            console.error('❌ Canvas setup failed:', error);
            throw new Error('Canvas initialization failed');
        }
    }

    setupEventListeners() {
        // Use passive event listeners for better performance
        const options = { passive: true };
        
        if (this.startBtn) {
            this.startBtn.addEventListener('click', () => this.debouncedStartTranslation());
        }
        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stopTranslation());
        }

        // Modal buttons
        if (this.enableCameraBtn) {
            this.enableCameraBtn.addEventListener('click', () => this.initializeCamera());
        }
        if (this.cancelCameraBtn) {
            this.cancelCameraBtn.addEventListener('click', () => this.hidePermissionModal());
        }
        if (this.retryCameraBtn) {
            this.retryCameraBtn.addEventListener('click', () => this.initializeCamera());
        }

        // Efficient resize handler with throttling
        let resizeTimeout;
        const handleResize = () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => this.setupCanvasDimensions(), 250);
        };
        window.addEventListener('resize', handleResize, options);

        // Handle visibility changes to pause/resume processing
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseProcessing();
            } else {
                this.resumeProcessing();
            }
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => this.cleanup());
        window.addEventListener('pagehide', () => this.cleanup());

        console.log('✅ Optimized event listeners setup');
    }

    // ENHANCED CAMERA INITIALIZATION WITH BETTER ERROR HANDLING
    async initializeCamera() {
        if (this.cameraRetryCount >= this.maxCameraRetries) {
            this.showCameraErrorModal('Camera Error', 'Maximum retry attempts reached. Please refresh the page.');
            return;
        }

        console.log('📷 Starting optimized camera initialization...');
        
        try {
            this.hidePermissionModal();
            this.showLoading('Initializing camera...');

            // Check browser support
            if (!navigator.mediaDevices?.getUserMedia) {
                throw new Error('Camera API not supported in this browser');
            }

            // Stop existing stream
            await this.stopCamera();

            // Setup video element
            this.setupVideoElement();

            // Get camera stream with enhanced constraints
            const stream = await this.getOptimizedCameraStream();
            await this.setupVideoStream(stream);

            // Verify camera is working
            await this.verifyCameraWorking();

            this.isCameraInitialized = true;
            this.cameraRetryCount = 0;
            this.hideLoading();
            this.hideCameraErrorModal();
            
            console.log('✅ Camera initialized successfully');
            this.showSuccess('Camera ready!');
            this.updateStatus('Camera Ready', true);

        } catch (error) {
            this.cameraRetryCount++;
            console.error('❌ Camera initialization failed:', error);
            this.hideLoading();
            this.handleCameraError(error);
        }
    }

    setupVideoElement() {
        // Performance-optimized video setup
        this.videoElement.setAttribute('playsinline', 'true');
        this.videoElement.setAttribute('webkit-playsinline', 'true');
        this.videoElement.setAttribute('muted', 'true');
        this.videoElement.setAttribute('autoplay', 'true');
        this.videoElement.srcObject = null;
    }

    async getOptimizedCameraStream() {
        const constraints = {
            video: {
                width: { ideal: 640, max: 1280 },
                height: { ideal: 480, max: 720 },
                facingMode: 'user',
                frameRate: { ideal: 30, max: 30 },
                aspectRatio: { ideal: 1.7777777778 } // 16:9
            },
            audio: false
        };

        try {
            return await navigator.mediaDevices.getUserMedia(constraints);
        } catch (error) {
            console.warn('Primary constraints failed, trying fallback...');
            // Fallback constraints
            return await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'user' } 
            });
        }
    }

    async setupVideoStream(stream) {
        this.videoStream = stream;
        this.videoElement.srcObject = stream;

        // Add track ended listener for camera disconnection
        stream.getVideoTracks().forEach(track => {
            track.addEventListener('ended', () => {
                console.warn('Camera track ended unexpectedly');
                this.handleCameraDisconnected();
            });
        });

        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                this.videoElement.removeEventListener('loadedmetadata', onLoadedMetadata);
                this.videoElement.removeEventListener('error', onError);
                reject(new Error('Video load timeout after 8 seconds'));
            }, 8000);

            const onLoadedMetadata = () => {
                clearTimeout(timeout);
                this.videoElement.removeEventListener('loadedmetadata', onLoadedMetadata);
                this.videoElement.removeEventListener('error', onError);
                resolve();
            };

            const onError = (error) => {
                clearTimeout(timeout);
                this.videoElement.removeEventListener('loadedmetadata', onLoadedMetadata);
                this.videoElement.removeEventListener('error', onError);
                reject(new Error(`Video element error: ${error.message}`));
            };

            this.videoElement.addEventListener('loadedmetadata', onLoadedMetadata);
            this.videoElement.addEventListener('error', onError);
            
            // If metadata is already loaded, resolve immediately
            if (this.videoElement.readyState >= this.videoElement.HAVE_METADATA) {
                onLoadedMetadata();
            }
        });
    }

    async verifyCameraWorking() {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        if (this.videoElement.videoWidth === 0 || this.videoElement.videoHeight === 0) {
            throw new Error('Camera initialized but not providing video frames');
        }
    }

    handleCameraDisconnected() {
        console.error('Camera disconnected during operation');
        this.isCameraInitialized = false;
        this.stopTranslation();
        this.showError('Camera disconnected. Please check your camera connection.');
        this.updateStatus('Camera Disconnected', false);
    }

    async stopCamera() {
        // Cancel any ongoing frame processing
        if (this.currentFrameController) {
            this.currentFrameController.abort();
            this.currentFrameController = null;
        }

        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => {
                track.stop();
            });
            this.videoStream = null;
        }
        
        if (this.videoElement) {
            this.videoElement.srcObject = null;
        }

        this.clearCanvases();
        this.isCameraInitialized = false;
    }

    // OPTIMIZED FRAME PROCESSING PIPELINE
    debouncedStartTranslation() {
        if (this.isTranslating) return;
        
        // Use requestAnimationFrame for debouncing
        if (this._startDebounce) cancelAnimationFrame(this._startDebounce);
        this._startDebounce = requestAnimationFrame(() => this.startTranslation());
    }

    async startTranslation() {
        if (!this.isCameraInitialized) {
            this.showError('Please enable camera access first');
            this.showPermissionModal();
            return;
        }

        console.log('🚀 Starting optimized translation...');
        this.isTranslating = true;
        this.consecutiveErrors = 0;
        this.predictionHistory = [];
        this.lastValidPrediction = null;
        this.stabilityCounter = 0;
        
        this.updateUI();
        this.updateStatus('Translating...', true);
        
        // Start optimized frame processing
        this.processFramesOptimized();
    }

    stopTranslation() {
        console.log('🛑 Stopping translation...');
        this.isTranslating = false;
        
        // Cancel any ongoing frame request
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
        
        // Abort any in-progress fetch requests
        if (this.currentFrameController) {
            this.currentFrameController.abort();
            this.currentFrameController = null;
        }
        
        this.clearCanvases();
        this.currentLandmarks = [];
        this.handDetected = false;
        
        this.updateUI();
        this.updateStatus('Ready', true);
    }

    pauseProcessing() {
        if (this.isTranslating) {
            console.log('⏸️ Pausing processing due to page visibility');
            this.isTranslating = false;
            if (this.animationFrameId) {
                cancelAnimationFrame(this.animationFrameId);
                this.animationFrameId = null;
            }
        }
    }

    resumeProcessing() {
        if (!this.isTranslating && this.isCameraInitialized) {
            console.log('▶️ Resuming processing');
            this.isTranslating = true;
            this.processFramesOptimized();
        }
    }

    processFramesOptimized() {
        if (!this.isTranslating) return;

        const now = performance.now();
        const elapsed = now - this.lastFrameTime;

        // Frame rate control with adaptive interval
        if (elapsed > this.frameInterval) {
            this.lastFrameTime = now - (elapsed % this.frameInterval);
            
            // Process frame only if not already processing and system is ready
            if (!this.processingFrame && this.isSystemReady()) {
                this.processSingleFrame();
            }
            
            // Update FPS counter
            this.updateFPSCounter(elapsed);
        }

        // Always draw keypoints if available (lightweight operation)
        if (this.handDetected && this.currentLandmarks.length > 0) {
            this.drawOptimizedLandmarks();
        }

        // Schedule next frame with error handling
        try {
            this.animationFrameId = requestAnimationFrame(() => this.processFramesOptimized());
        } catch (error) {
            console.error('Animation frame error:', error);
            this.stopTranslation();
        }
    }

    isSystemReady() {
        return this.isCameraInitialized && 
               this.videoElement.readyState === this.videoElement.HAVE_ENOUGH_DATA &&
               this.videoElement.videoWidth > 0 &&
               this.videoElement.videoHeight > 0;
    }

    updateFPSCounter(elapsed) {
        this.fps = Math.round(1000 / elapsed);
        if (this.fpsCounter) {
            this.fpsCounter.textContent = `${this.fps} FPS`;
            this.fpsCounter.style.color = this.fps > 25 ? '#27ae60' : this.fps > 15 ? '#f39c12' : '#e74c3c';
        }
    }

    async processSingleFrame() {
        if (this.processingFrame || !this.isSystemReady()) return;

        this.processingFrame = true;
        const startTime = performance.now();

        try {
            // Draw video frame efficiently
            this.ctx.drawImage(this.videoElement, 0, 0, this.outputCanvas.width, this.outputCanvas.height);
            
            // Adaptive quality based on performance
            const quality = this.averageProcessingTime > 100 ? 0.5 : 0.7;
            const imageData = this.outputCanvas.toDataURL('image/jpeg', quality);
            
            // Send to backend with abort controller
            this.currentFrameController = new AbortController();
            const timeoutId = setTimeout(() => this.currentFrameController.abort(), 5000);

            const response = await fetch('/api/process_frame', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: imageData,
                    confidence_threshold: this.confidenceThreshold,
                    smoothing_frames: this.smoothingFrames,
                    enable_landmarks: true,
                    request_timestamp: Date.now(),
                    frame_id: this.frameCount++
                }),
                signal: this.currentFrameController.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            // Process the prediction result
            this.processPredictionResult(result);
            
            // Update performance metrics
            this.updatePerformanceMetrics(performance.now() - startTime);

        } catch (error) {
            this.handleProcessingError(error);
        } finally {
            this.processingFrame = false;
            this.currentFrameController = null;
        }
    }

    // ENHANCED PREDICTION PROCESSING WITH BETTER VALIDATION
    processPredictionResult(result) {
        if (!result.success) {
            this.handleNoPrediction();
            return;
        }

        // Update hand detection state
        this.handDetected = result.landmarks_detected && result.landmarks?.length > 0;
        this.currentLandmarks = result.landmarks || [];

        // Enhanced prediction validation
        const isValidPrediction = result.prediction && 
                                result.prediction !== 'No hand detected' && 
                                result.confidence >= this.confidenceThreshold;

        if (isValidPrediction) {
            this.handleValidPrediction(result);
        } else {
            this.handleLowConfidencePrediction(result);
        }

        // Batch UI updates
        this.updateDisplay(result, isValidPrediction);
    }

    handleValidPrediction(result) {
        // Add to prediction history for smoothing
        this.predictionHistory.push({
            prediction: result.prediction,
            confidence: result.confidence,
            timestamp: Date.now()
        });

        // Keep history manageable
        if (this.predictionHistory.length > this.smoothingFrames) {
            this.predictionHistory.shift();
        }

        // Apply temporal smoothing
        const smoothedPrediction = this.applyTemporalSmoothing();
        if (smoothedPrediction) {
            this.stabilityCounter++;
            
            // Only update if prediction is stable
            if (this.stabilityCounter >= this.minStabilityFrames) {
                this.consecutiveErrors = 0;
                this.addToHistory(smoothedPrediction.prediction, smoothedPrediction.confidence);
            }
        } else {
            this.stabilityCounter = 0;
        }
    }

    applyTemporalSmoothing() {
        if (this.predictionHistory.length < 2) return null;

        // Simple majority voting
        const predictions = {};
        this.predictionHistory.forEach(item => {
            predictions[item.prediction] = (predictions[item.prediction] || 0) + 1;
        });

        const mostFrequent = Object.entries(predictions)
            .sort(([,a], [,b]) => b - a)[0];

        if (mostFrequent && mostFrequent[1] >= Math.floor(this.predictionHistory.length / 2)) {
            const confidence = this.predictionHistory
                .filter(item => item.prediction === mostFrequent[0])
                .reduce((sum, item) => sum + item.confidence, 0) / mostFrequent[1];

            return {
                prediction: mostFrequent[0],
                confidence: confidence
            };
        }

        return null;
    }

    handleLowConfidencePrediction(result) {
        this.stabilityCounter = 0;
        this.lastValidPrediction = null;
        
        if (result.prediction === 'No hand detected') {
            this.clearKeypoints();
        }
    }

    handleNoPrediction() {
        this.consecutiveErrors++;
        this.handDetected = false;
        this.clearKeypoints();
        
        if (this.consecutiveErrors >= this.maxConsecutiveErrors) {
            this.showError('Translation issues detected. Please check connection and try again.');
            this.consecutiveErrors = 0;
        }
    }

    // ULTRA OPTIMIZED MEDIAPIPE LANDMARKS RENDERING
    drawOptimizedLandmarks() {
        if (!this.keypointCtx || this.currentLandmarks.length === 0) return;

        const width = this.keypointCanvas.width;
        const height = this.keypointCanvas.height;

        // Clear only the necessary area
        this.keypointCtx.clearRect(0, 0, width, height);

        // Batch draw connections
        this.keypointCtx.strokeStyle = '#00ff00';
        this.keypointCtx.lineWidth = 2;
        this.keypointCtx.globalAlpha = 0.8;

        this.keypointCtx.beginPath();
        for (const [startIdx, endIdx] of this.handConnections) {
            if (startIdx < this.currentLandmarks.length && endIdx < this.currentLandmarks.length) {
                const start = this.currentLandmarks[startIdx];
                const end = this.currentLandmarks[endIdx];
                
                this.keypointCtx.moveTo(start.x * width, start.y * height);
                this.keypointCtx.lineTo(end.x * width, end.y * height);
            }
        }
        this.keypointCtx.stroke();

        // Batch draw landmarks with optimized rendering
        this.keypointCtx.globalAlpha = 1.0;
        for (let i = 0; i < this.currentLandmarks.length; i++) {
            const landmark = this.currentLandmarks[i];
            const x = landmark.x * width;
            const y = landmark.y * height;
            
            this.keypointCtx.fillStyle = this.getLandmarkColor(i);
            
            this.keypointCtx.beginPath();
            this.keypointCtx.arc(x, y, 3, 0, 2 * Math.PI);
            this.keypointCtx.fill();
        }
    }

    getLandmarkColor(index) {
        // Pre-defined color map for different hand parts
        const colorMap = {
            0: '#ff0000',    // Wrist - Red
            1: '#ffff00', 2: '#ffff00', 3: '#ffff00', 4: '#ffff00', // Thumb - Yellow
            5: '#00ffff', 6: '#00ffff', 7: '#00ffff', 8: '#00ffff', // Index - Cyan
            9: '#ff00ff', 10: '#ff00ff', 11: '#ff00ff', 12: '#ff00ff', // Middle - Magenta
            13: '#ffffff', 14: '#ffffff', 15: '#ffffff', 16: '#ffffff', // Ring - White
            17: '#ffa500', 18: '#ffa500', 19: '#ffa500', 20: '#ffa500' // Little - Orange
        };
        return colorMap[index] || '#00ff00';
    }

    // OPTIMIZED DISPLAY UPDATES
    updateDisplay(result, isValidPrediction) {
        // Batch DOM updates in single animation frame
        requestAnimationFrame(() => {
            this.updateTextOutput(result, isValidPrediction);
            this.updateGestureInfo(result, isValidPrediction);
            this.updateVideoOverlay(result, isValidPrediction);
        });
    }

    updateTextOutput(result, isValidPrediction) {
        if (!this.textOutput) return;
        
        if (isValidPrediction) {
            this.textOutput.innerHTML = `<span class="detected-text">${this.escapeHtml(result.prediction)}</span>`;
        } else {
            this.textOutput.innerHTML = '<span class="placeholder">Show a sign to your webcam...</span>';
        }
    }

    updateGestureInfo(result, isValidPrediction) {
        if (this.gestureName) {
            this.gestureName.textContent = result.prediction || '-';
            this.gestureName.style.color = isValidPrediction ? '#27ae60' : '#e74c3c';
        }
        
        if (this.confidenceBadge) {
            const confidence = Math.round((result.confidence || 0) * 100);
            this.confidenceBadge.textContent = `${confidence}%`;
            this.confidenceBadge.className = `detail-value confidence-badge ${this.getConfidenceClass(confidence)}`;
        }

        if (this.handsCount) {
            this.handsCount.textContent = result.hand_count || 0;
            this.handsCount.style.color = (result.hand_count || 0) > 0 ? '#27ae60' : '#e74c3c';
        }
    }

    updateVideoOverlay(result, isValidPrediction) {
        if (this.currentSignName) {
            this.currentSignName.textContent = result.prediction || 'No Sign Detected';
            this.currentSignName.style.color = isValidPrediction ? '#27ae60' : '#e74c3c';
        }

        if (this.currentSignConfidence) {
            const confidence = Math.round((result.confidence || 0) * 100);
            this.currentSignConfidence.textContent = `${confidence}%`;
        }
    }

    // PERFORMANCE OPTIMIZED UTILITIES
    updatePerformanceMetrics(processingTime) {
        this.processingTimes.push(processingTime);
        if (this.processingTimes.length > 10) {
            this.processingTimes.shift();
        }
        
        this.averageProcessingTime = this.processingTimes.reduce((a, b) => a + b, 0) / this.processingTimes.length;

        if (this.processingTimeElement) {
            this.processingTimeElement.textContent = `${Math.round(processingTime)}ms`;
            this.processingTimeElement.style.color = processingTime < 80 ? '#27ae60' : processingTime < 150 ? '#f39c12' : '#e74c3c';
        }
    }

    addToHistory(prediction, confidence) {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;

        const timestamp = new Date().toLocaleTimeString();
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-text">${this.escapeHtml(prediction)}</div>
            <div class="history-meta">
                <span class="history-time">${timestamp}</span>
                <span class="history-confidence">${Math.round(confidence * 100)}%</span>
            </div>
        `;

        // Add to top and limit size for performance
        historyList.insertBefore(historyItem, historyList.firstChild);
        
        const items = historyList.getElementsByClassName('history-item');
        if (items.length > 10) {
            historyList.removeChild(items[items.length - 1]);
        }
    }

    // ERROR HANDLING IMPROVEMENTS
    handleProcessingError(error) {
        this.consecutiveErrors++;
        
        if (error.name === 'AbortError') {
            console.warn('Frame processing aborted (timeout)');
        } else {
            console.error('Frame processing error:', error);
        }
        
        if (this.consecutiveErrors >= 3) {
            this.showError('Processing issues detected. Please try again.');
            this.consecutiveErrors = 0;
        }
    }

    handleCameraError(error) {
        let title = 'Camera Error';
        let message = 'Unable to access camera. ';

        if (error.name === 'NotAllowedError') {
            title = 'Permission Required';
            message = 'Please allow camera access in your browser settings. Click "Enable Camera" to try again.';
            this.showPermissionModal();
        } else if (error.name === 'NotFoundError' || error.name === 'OverconstrainedError') {
            title = 'Camera Not Found';
            message = 'No suitable camera detected. Please check your device has a working camera.';
        } else if (error.name === 'NotReadableError') {
            title = 'Camera Busy';
            message = 'Camera is already in use by another application. Please close other camera apps and try again.';
        } else {
            message += error.message || 'Please try again.';
        }

        this.showCameraErrorModal(title, message);
        this.updateStatus('Camera Error', false);
        
        console.error('Camera error details:', error);
    }

    // UI MANAGEMENT
    updateUI() {
        requestAnimationFrame(() => {
            if (this.startBtn) {
                this.startBtn.disabled = this.isTranslating || !this.isCameraInitialized;
                this.startBtn.innerHTML = this.isTranslating ? 
                    '<i class="fas fa-sync-alt fa-spin"></i> Processing...' : 
                    '<i class="fas fa-play"></i> Start Translation';
            }
            
            if (this.stopBtn) {
                this.stopBtn.disabled = !this.isTranslating;
            }
        });
    }

    updateStatus(message, isActive = false) {
        if (this.statusIndicator) {
            const statusText = this.statusIndicator.querySelector('span');
            const statusDot = this.statusIndicator.querySelector('.status-dot');
            
            if (statusText) statusText.textContent = message;
            if (statusDot) statusDot.style.backgroundColor = isActive ? '#27ae60' : '#e74c3c';
            
            this.statusIndicator.classList.toggle('active', isActive);
        }
    }

    setupCanvasDimensions() {
        if (!this.videoElement?.parentElement) return;

        const container = this.videoElement.parentElement;
        const width = container.clientWidth;
        const height = Math.round(width * 0.75);

        [this.videoElement, this.outputCanvas, this.keypointCanvas].forEach(element => {
            if (element) {
                element.width = width;
                element.height = height;
            }
        });
    }

    clearCanvases() {
        if (this.ctx && this.outputCanvas) {
            this.ctx.clearRect(0, 0, this.outputCanvas.width, this.outputCanvas.height);
        }
        this.clearKeypoints();
    }

    clearKeypoints() {
        if (this.keypointCtx && this.keypointCanvas) {
            this.keypointCtx.clearRect(0, 0, this.keypointCanvas.width, this.keypointCanvas.height);
        }
    }

    getConfidenceClass(confidence) {
        if (confidence >= 80) return 'high-confidence';
        if (confidence >= 60) return 'medium-confidence';
        return 'low-confidence';
    }

    // MODAL MANAGEMENT
    showPermissionModal() {
        if (this.permissionModal) this.permissionModal.style.display = 'flex';
    }

    hidePermissionModal() {
        if (this.permissionModal) this.permissionModal.style.display = 'none';
    }

    showCameraErrorModal(title, message) {
        if (this.cameraErrorModal) {
            const titleElement = this.cameraErrorModal.querySelector('h3');
            const messageElement = document.getElementById('cameraErrorMessage');
            
            if (titleElement) titleElement.textContent = title;
            if (messageElement) messageElement.textContent = message;
            
            this.cameraErrorModal.style.display = 'flex';
        }
    }

    hideCameraErrorModal() {
        if (this.cameraErrorModal) this.cameraErrorModal.style.display = 'none';
    }

    showLoading(message = 'Loading...') {
        if (this.loadingSpinner) {
            this.loadingSpinner.style.display = 'flex';
            const messageElement = this.loadingSpinner.querySelector('p');
            if (messageElement) messageElement.textContent = message;
        }
    }

    hideLoading() {
        if (this.loadingSpinner) this.loadingSpinner.style.display = 'none';
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existing = document.querySelector('.notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${this.escapeHtml(message)}</span>
            </div>
        `;

        document.body.appendChild(notification);
        
        // Animate in
        requestAnimationFrame(() => notification.classList.add('show'));
        
        // Auto remove
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return unsafe;
        return unsafe.replace(/[&<"'>]/g, m => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
        }[m]));
    }

    cleanup() {
        console.log('🧹 Cleaning up ASL Translator...');
        this.stopTranslation();
        this.stopCamera();
        
        // Clean up any pending timeouts or intervals
        if (this._startDebounce) {
            cancelAnimationFrame(this._startDebounce);
        }
    }
}

// Initialize when DOM is ready with error handling
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌟 DOM loaded, initializing Ultra Optimized ASL Translator...');
    
    try {
        window.aslTranslator = new ASLTranslator();
    } catch (error) {
        console.error('💥 Failed to initialize ASL Translator:', error);
        // Show user-friendly error message
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #e74c3c;
            color: white;
            padding: 20px;
            border-radius: 8px;
            z-index: 10000;
            text-align: center;
            max-width: 400px;
        `;
        errorDiv.innerHTML = `
            <h3>Initialization Error</h3>
            <p>Failed to initialize ASL Translator. Please refresh the page.</p>
            <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; background: white; color: #e74c3c; border: none; border-radius: 4px; cursor: pointer;">
                Refresh Page
            </button>
        `;
        document.body.appendChild(errorDiv);
    }
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ASLTranslator;
}