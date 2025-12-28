// Learn Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize learn page functionality
    initAlphabetGrid();
    initVideoPlayer();
    initProgressTracker();
    initPracticeModal();
    initFloatingHands();
    initEventListeners();
    
    // Quiz is initialized in quiz.js
});

// Alphabet data with tips and difficulty
const alphabetData = {
    'A': { difficulty: 'easy', tips: ['Thumb placed on the side of the hand', 'Fingers together and straight'] },
    'B': { difficulty: 'easy', tips: ['Fingers together and straight', 'Thumb across palm'] },
    'C': { difficulty: 'easy', tips: ['Form a C shape with your hand', 'Thumb and fingers curved naturally'] },
    'D': { difficulty: 'medium', tips: ['Index finger pointing up', 'Other fingers curled into fist'] },
    'E': { difficulty: 'medium', tips: ['Fingers curled into fist', 'Thumb across fingers'] },
    'F': { difficulty: 'medium', tips: ['Index finger and thumb touching', 'Other fingers extended'] },
    'G': { difficulty: 'medium', tips: ['Index finger pointing to side', 'Thumb across palm'] },
    'H': { difficulty: 'hard', tips: ['Index and middle finger extended', 'Pointing to side'] },
    'I': { difficulty: 'easy', tips: ['Pinky finger extended', 'Other fingers curled'] },
    'J': { difficulty: 'hard', tips: ['Pinky finger extended', 'Draw a J in the air'] },
    'K': { difficulty: 'medium', tips: ['Index and middle finger extended', 'Thumb between them'] },
    'L': { difficulty: 'easy', tips: ['Index finger and thumb extended', 'Form an L shape'] },
    'M': { difficulty: 'hard', tips: ['Thumb under three fingers', 'Fingers slightly curled'] },
    'N': { difficulty: 'hard', tips: ['Thumb under two fingers', 'Fingers slightly curled'] },
    'O': { difficulty: 'easy', tips: ['Form an O shape', 'All fingers touching thumb'] },
    'P': { difficulty: 'hard', tips: ['Index finger and thumb forming P', 'Other fingers curled'] },
    'Q': { difficulty: 'hard', tips: ['Index finger and thumb pointing down', 'Form a Q shape'] },
    'R': { difficulty: 'medium', tips: ['Index and middle finger crossed', 'Other fingers curled'] },
    'S': { difficulty: 'easy', tips: ['Make a fist', 'Thumb across fingers'] },
    'T': { difficulty: 'medium', tips: ['Thumb between index and middle finger', 'Other fingers curled'] },
    'U': { difficulty: 'easy', tips: ['Index and middle finger extended', 'Fingers together'] },
    'V': { difficulty: 'easy', tips: ['Index and middle finger extended', 'Fingers separated'] },
    'W': { difficulty: 'medium', tips: ['Index, middle, and ring finger extended', 'Thumb across pinky'] },
    'X': { difficulty: 'medium', tips: ['Index finger bent', 'Other fingers curled'] },
    'Y': { difficulty: 'easy', tips: ['Thumb and pinky extended', 'Other fingers curled'] },
    'Z': { difficulty: 'hard', tips: ['Index finger drawing a Z', 'Other fingers curled'] }
};

let learnedLetters = new Set();
let currentLetter = null;
let practiceTimer = null;

function initAlphabetGrid() {
    const grid = document.getElementById('alphabetGrid');
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    
    grid.innerHTML = '';
    
    alphabet.split('').forEach(letter => {
        const button = document.createElement('button');
        button.className = 'letter-btn';
        if (learnedLetters.has(letter)) {
            button.classList.add('learned');
        }
        button.textContent = letter;
        
        // Add tooltip
        const tooltip = document.createElement('div');
        tooltip.className = 'letter-tooltip';
        tooltip.textContent = `Tap to Learn ${letter}`;
        button.appendChild(tooltip);
        
        button.addEventListener('click', () => selectLetter(letter));
        grid.appendChild(button);
    });
}

function initVideoPlayer() {
    window.videoPlayer = document.getElementById('aslVideo');
    window.videoPlaceholder = document.getElementById('videoPlaceholder');
    
    // Initialize video event listeners
    setupVideoEvents();
}

function setupVideoEvents() {
    // Handle when video metadata is loaded
    window.videoPlayer.addEventListener('loadedmetadata', function() {
        console.log('Video metadata loaded');
    });
    
    // Handle when video can play
    window.videoPlayer.addEventListener('canplay', function() {
        console.log('Video can start playing');
        // Show video and hide placeholder when video is ready
        window.videoPlaceholder.style.display = 'none';
        window.videoPlayer.style.display = 'block';
    });
    
    // Handle video errors
    window.videoPlayer.addEventListener('error', function(e) {
        console.error('Video error:', e);
        console.error('Video error details:', window.videoPlayer.error);
        showVideoError();
    });
    
    // Handle when video starts playing
    window.videoPlayer.addEventListener('playing', function() {
        console.log('Video started playing');
    });
    
    // Handle when video is waiting for data
    window.videoPlayer.addEventListener('waiting', function() {
        console.log('Video waiting for data');
    });
}

function initProgressTracker() {
    const progressDots = document.querySelector('.progress-dots');
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    
    progressDots.innerHTML = '';
    
    alphabet.split('').forEach(letter => {
        const dot = document.createElement('div');
        dot.className = 'progress-dot';
        if (learnedLetters.has(letter)) {
            dot.classList.add('learned');
        }
        progressDots.appendChild(dot);
    });
    
    updateProgress();
}

function initPracticeModal() {
    window.practiceModal = document.getElementById('practiceModal');
    window.modalClose = document.getElementById('modalClose');
    window.practiceSuccess = document.getElementById('practiceSuccess');
    window.practiceRetry = document.getElementById('practiceRetry');
    
    modalClose.addEventListener('click', closePracticeModal);
    practiceSuccess.addEventListener('click', markLetterAsLearned);
    practiceRetry.addEventListener('click', restartPractice);
}

function initFloatingHands() {
    // Floating hands are already in the HTML with CSS animations
}

function initEventListeners() {
    // Replay button
    document.getElementById('replayBtn').addEventListener('click', replayVideo);
    
    // Fullscreen button
    document.getElementById('fullscreenBtn').addEventListener('click', toggleFullscreen);
    
    // Quiz button is handled by ASLQuiz class
    
    // Video ended event
    window.videoPlayer.addEventListener('ended', onVideoEnded);
    
    // Close modal when clicking outside
    window.practiceModal.addEventListener('click', function(event) {
        if (event.target === window.practiceModal) {
            closePracticeModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            if (window.practiceModal.classList.contains('active')) {
                closePracticeModal();
            }
            if (window.aslQuiz && window.aslQuiz.isQuizActive) {
                window.aslQuiz.cancelQuiz();
            }
        }
    });
    
    // Size controls
    document.getElementById('increaseSize').addEventListener('click', increaseButtonSize);
    document.getElementById('decreaseSize').addEventListener('click', decreaseButtonSize);
}

function selectLetter(letter) {
    currentLetter = letter;
    
    // Update active button
    document.querySelectorAll('.letter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent === letter) {
            btn.classList.add('active');
        }
    });
    
    // Show loading state first
    showLoadingState(letter);
    
    // Load and play video
    loadVideo(letter);
    
    // Update info card
    updateInfoCard(letter);
    
    // Update current letter display
    document.getElementById('currentLetter').textContent = letter;
    
    // Add subtle animation
    animateLetterSelection(letter);
    
    // Announce to screen readers
    const announcement = document.getElementById('screenReaderAnnouncements');
    announcement.textContent = `Selected letter ${letter}. Loading American Sign Language demonstration.`;
}

function showLoadingState(letter) {
    window.videoPlaceholder.innerHTML = `
        <i class="fas fa-spinner fa-spin placeholder-icon" aria-hidden="true"></i>
        <h3>Loading ${letter} Sign...</h3>
        <p>Please wait while the video loads</p>
    `;
    window.videoPlaceholder.style.display = 'flex';
    window.videoPlayer.style.display = 'none';
}

function showVideoError() {
    window.videoPlaceholder.innerHTML = `
        <i class="fas fa-exclamation-triangle placeholder-icon" aria-hidden="true"></i>
        <h3>Video Not Available</h3>
        <p>Could not load video for letter ${currentLetter}</p>
        <small>Please check if the video file exists at: /assets/videos/alphabet/${currentLetter}.mp4</small>
    `;
    window.videoPlaceholder.style.display = 'flex';
    window.videoPlayer.style.display = 'none';
}

function loadVideo(letter) {
    const videoPath = `/assets/videos/alphabet/${letter}.mp4`;
    console.log('Attempting to load video:', videoPath);
    
    // Reset video player
    window.videoPlayer.pause();
    window.videoPlayer.currentTime = 0;
    
    // Clear any previous error state
    window.videoPlayer.removeAttribute('src');
    window.videoPlayer.load();
    
    // Set the new source
    window.videoPlayer.src = videoPath;
    
    // Set preload to auto to ensure video loads
    window.videoPlayer.preload = 'auto';
    
    // Load the video
    window.videoPlayer.load();
    
    // Try to play the video after a short delay to ensure it's loaded
    setTimeout(() => {
        const playPromise = window.videoPlayer.play();
        
        if (playPromise !== undefined) {
            playPromise.then(() => {
                // Video played successfully
                console.log('Video autoplay started successfully');
            }).catch(error => {
                // Autoplay was prevented - this is normal in many browsers
                console.log('Autoplay prevented (normal behavior):', error);
                // Show play button to user
                showPlayButton();
            });
        }
    }, 500);
}

function showPlayButton() {
    window.videoPlaceholder.innerHTML = `
        <i class="fas fa-hand-pointer placeholder-icon" aria-hidden="true"></i>
        <h3>Ready to Learn ${currentLetter}</h3>
        <p>Click the play button to start the video</p>
        <button class="control-btn play-video-btn" onclick="playCurrentVideo()" style="margin-top: 1rem; pointer-events: all;">
            <i class="fas fa-play" aria-hidden="true"></i> Play Video
        </button>
    `;
    window.videoPlaceholder.style.display = 'flex';
    window.videoPlayer.style.display = 'block';
}

function playCurrentVideo() {
    if (window.videoPlayer.src) {
        window.videoPlayer.play().then(() => {
            window.videoPlaceholder.style.display = 'none';
        }).catch(error => {
            console.error('Error playing video:', error);
            showVideoError();
        });
    }
}

function updateInfoCard(letter) {
    const data = alphabetData[letter];
    
    document.getElementById('letterName').textContent = `Letter ${letter}`;
    document.getElementById('practiceTime').textContent = '0min';
    document.getElementById('masteredStatus').textContent = learnedLetters.has(letter) ? 'Yes' : 'No';
    
    // Update difficulty badge
    const difficultyBadge = document.querySelector('.difficulty-badge');
    difficultyBadge.textContent = data.difficulty.charAt(0).toUpperCase() + data.difficulty.slice(1);
    difficultyBadge.className = `difficulty-badge ${data.difficulty}`;
    
    // Update tips
    const tipsList = document.getElementById('tipsList');
    tipsList.innerHTML = '';
    data.tips.forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        tipsList.appendChild(li);
    });
}

function replayVideo() {
    if (window.videoPlayer.src) {
        window.videoPlayer.currentTime = 0;
        window.videoPlayer.play().catch(error => {
            console.log('Replay prevented:', error);
            // If replay fails, show the play button
            showPlayButton();
        });
    }
}

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        if (window.videoPlayer.requestFullscreen) {
            window.videoPlayer.requestFullscreen();
        } else if (window.videoPlayer.webkitRequestFullscreen) {
            window.videoPlayer.webkitRequestFullscreen();
        } else if (window.videoPlayer.msRequestFullscreen) {
            window.videoPlayer.msRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
}

function onVideoEnded() {
    // Auto-show practice modal when video ends
    if (currentLetter && !learnedLetters.has(currentLetter)) {
        setTimeout(() => {
            showPracticeModal(currentLetter);
        }, 1000);
    }
}

function showPracticeModal(letter) {
    document.getElementById('practiceLetter').textContent = letter;
    document.getElementById('practiceInstruction').textContent = `Make the sign for letter ${letter} with your hand`;
    
    startPracticeTimer();
    window.practiceModal.classList.add('active');
    
    // Prevent background scrolling
    document.body.style.overflow = 'hidden';
}

function closePracticeModal() {
    window.practiceModal.classList.remove('active');
    stopPracticeTimer();
    
    // Restore background scrolling
    document.body.style.overflow = '';
}

function startPracticeTimer() {
    let timeLeft = 10;
    const timerElement = document.getElementById('practiceTimer');
    timerElement.textContent = `${timeLeft}s`;
    
    practiceTimer = setInterval(() => {
        timeLeft--;
        timerElement.textContent = `${timeLeft}s`;
        
        if (timeLeft <= 0) {
            stopPracticeTimer();
            closePracticeModal();
        }
    }, 1000);
}

function stopPracticeTimer() {
    if (practiceTimer) {
        clearInterval(practiceTimer);
        practiceTimer = null;
    }
}

function markLetterAsLearned() {
    if (currentLetter) {
        learnedLetters.add(currentLetter);
        updateProgress();
        closePracticeModal();
        
        // Show celebration
        showCelebration();
    }
}

function restartPractice() {
    stopPracticeTimer();
    startPracticeTimer();
    replayVideo();
}

function updateProgress() {
    const progress = (learnedLetters.size / 26) * 100;
    const progressFill = document.getElementById('progressFill');
    const progressCount = document.querySelector('.progress-count');
    const progressDots = document.querySelectorAll('.progress-dot');
    
    // Animate progress bar
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }
    if (progressCount) {
        progressCount.textContent = `${learnedLetters.size}/26`;
    }
    
    // Update progress dots
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    alphabet.split('').forEach((letter, index) => {
        if (progressDots[index]) {
            if (learnedLetters.has(letter)) {
                progressDots[index].classList.add('learned');
            } else {
                progressDots[index].classList.remove('learned');
            }
        }
    });
    
    // Update alphabet buttons
    document.querySelectorAll('.letter-btn').forEach(btn => {
        if (learnedLetters.has(btn.textContent)) {
            btn.classList.add('learned');
        } else {
            btn.classList.remove('learned');
        }
    });
}

function showCelebration() {
    // Create celebration elements
    const celebration = document.createElement('div');
    celebration.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 4rem;
        z-index: 1001;
        pointer-events: none;
    `;
    
    const emojis = ['🎉', '👏', '🤟', '✅', '⭐'];
    emojis.forEach((emoji, index) => {
        const element = document.createElement('div');
        element.textContent = emoji;
        element.style.cssText = `
            position: absolute;
            font-size: 3rem;
            animation: celebrate 1s ease-out forwards;
            animation-delay: ${index * 0.2}s;
        `;
        
        celebration.appendChild(element);
    });
    
    // Add CSS for celebration animation if not already added
    if (!document.querySelector('#celebration-style')) {
        const style = document.createElement('style');
        style.id = 'celebration-style';
        style.textContent = `
            @keyframes celebrate {
                0% {
                    transform: translate(0, 0) scale(0);
                    opacity: 0;
                }
                50% {
                    opacity: 1;
                }
                100% {
                    transform: translate(${Math.random() * 200 - 100}px, ${Math.random() * 200 - 100}px) scale(1);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(celebration);
    
    // Remove after animation
    setTimeout(() => {
        if (celebration.parentNode) {
            document.body.removeChild(celebration);
        }
    }, 2000);
}

function animateLetterSelection(letter) {
    const button = Array.from(document.querySelectorAll('.letter-btn'))
        .find(btn => btn.textContent === letter);
    
    if (button) {
        button.style.animation = 'none';
        setTimeout(() => {
            button.style.animation = 'pulse 0.5s ease';
        }, 10);
    }
}

// Button size controls
function increaseButtonSize() {
    const buttons = document.querySelectorAll('.letter-btn');
    buttons.forEach(btn => {
        const currentSize = parseInt(getComputedStyle(btn).fontSize) || 16;
        btn.style.fontSize = `${Math.min(currentSize + 2, 24)}px`;
        btn.style.padding = `${Math.min(currentSize + 4, 28)}px ${Math.min(currentSize + 8, 32)}px`;
    });
}

function decreaseButtonSize() {
    const buttons = document.querySelectorAll('.letter-btn');
    buttons.forEach(btn => {
        const currentSize = parseInt(getComputedStyle(btn).fontSize) || 16;
        btn.style.fontSize = `${Math.max(currentSize - 2, 12)}px`;
        btn.style.padding = `${Math.max(currentSize - 4, 16)}px ${Math.max(currentSize - 8, 20)}px`;
    });
}

// Keyboard navigation
document.addEventListener('keydown', function(event) {
    const key = event.key.toUpperCase();
    if (alphabetData[key] && (!window.aslQuiz || !window.aslQuiz.isQuizActive)) {
        selectLetter(key);
    }
});

// Initialize with first letter
setTimeout(() => {
    // Pre-load first letter video but don't autoplay
    const videoPath = '/assets/videos/alphabet/A.mp4';
    window.videoPlayer.src = videoPath;
    window.videoPlayer.load();
}, 1000);

// Make playCurrentVideo function available globally
window.playCurrentVideo = playCurrentVideo;

// Test function - can be called from browser console
window.testQuiz = function() {
    console.log('🧪 Testing quiz...');
    console.log('window.aslQuiz exists:', !!window.aslQuiz);
    if (window.aslQuiz) {
        console.log('Calling startQuiz()...');
        window.aslQuiz.startQuiz();
    } else {
        console.error('window.aslQuiz is not defined!');
    }
};

// Also expose quiz for debugging
window.debugQuiz = function() {
    console.log('Quiz Debug Info:');
    console.log('- window.aslQuiz:', window.aslQuiz);
    console.log('- Quiz button:', document.getElementById('quizBtn'));
    console.log('- Quiz modal:', document.getElementById('quizModal'));
    console.log('- Quiz result modal:', document.getElementById('quizResultModal'));
};

console.log('📚 Learn.js loaded successfully');
console.log('💡 You can test the quiz by typing: testQuiz() in the console');
console.log('💡 Debug quiz info by typing: debugQuiz() in the console');
