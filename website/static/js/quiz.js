// Simple Quiz System for ASL Learn Page
class ASLQuiz {
    constructor() {
        // Get DOM elements
        this.quizBtn = document.getElementById('quizBtn');
        this.quizModal = document.getElementById('quizModal');
        this.quizResultModal = document.getElementById('quizResultModal');
        this.quizVideo = document.getElementById('quizVideo');
        this.currentQuestionEl = document.getElementById('currentQuestion');
        this.quizScoreEl = document.getElementById('quizScore');
        this.quizProgressFill = document.getElementById('quizProgressFill');
        this.submitAnswerBtn = document.getElementById('submitAnswerBtn');
        
        // Quiz state
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.score = 0;
        this.selectedAnswer = null;
        
        // Setup
        this.init();
    }
    
    init() {
        // Attach event listeners
        if (this.quizBtn) {
            this.quizBtn.addEventListener('click', () => this.start());
        }
        
        document.getElementById('quizCloseBtn')?.addEventListener('click', () => this.cancel());
        document.getElementById('cancelQuizBtn')?.addEventListener('click', () => this.cancel());
        document.getElementById('submitAnswerBtn')?.addEventListener('click', () => this.submitAnswer());
        document.getElementById('closeQuizBtn')?.addEventListener('click', () => this.close());
        
        console.log('Quiz initialized');
    }
    
    start() {
        console.log('Starting quiz...');
        
        // Pause background video
        if (window.videoPlayer) {
            window.videoPlayer.pause();
        }
        
        // Generate 10 random questions
        this.generateQuestions();
        
        // Reset state
        this.currentQuestionIndex = 0;
        this.score = 0;
        this.selectedAnswer = null;
        
        // Show first question
        this.showQuestion();
        
        // Show modal
        this.quizModal.style.display = 'flex';
        
        console.log('Quiz started with', this.questions.length, 'questions');
    }
    
    generateQuestions() {
        // All letters A-Z
        const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
        
        // Shuffle and take 10
        const shuffled = alphabet.sort(() => Math.random() - 0.5);
        const selected = shuffled.slice(0, 10);
        
        // Create questions
        this.questions = selected.map(letter => {
            // Get 3 wrong answers
            const wrong = alphabet.filter(l => l !== letter)
                .sort(() => Math.random() - 0.5)
                .slice(0, 3);
            
            // Mix correct and wrong answers
            const options = [letter, ...wrong].sort(() => Math.random() - 0.5);
            
            return {
                letter: letter,
                videoUrl: `/assets/videos/alphabet/${letter}.mp4`,
                options: options,
                correctAnswer: letter
            };
        });
    }
    
    showQuestion() {
        if (this.currentQuestionIndex >= this.questions.length) {
            this.showResults();
            return;
        }
        
        const question = this.questions[this.currentQuestionIndex];
        
        // Update progress
        this.currentQuestionEl.textContent = this.currentQuestionIndex + 1;
        this.quizScoreEl.textContent = this.score;
        const progress = ((this.currentQuestionIndex + 1) / 10) * 100;
        this.quizProgressFill.style.width = progress + '%';
        
        // Load video
        this.quizVideo.src = question.videoUrl;
        this.quizVideo.load();
        this.quizVideo.play().catch(e => console.log('Autoplay prevented'));
        
        // Create options
        this.renderOptions(question.options);
        
        // Reset submit button
        this.submitAnswerBtn.disabled = true;
        this.selectedAnswer = null;
    }
    
    renderOptions(options) {
        // Remove old options
        const oldOptions = document.querySelector('.quiz-options');
        if (oldOptions) {
            oldOptions.remove();
        }
        
        // Create new options container
        const container = document.createElement('div');
        container.className = 'quiz-options';
        
        // Create option buttons
        options.forEach(option => {
            const btn = document.createElement('button');
            btn.className = 'quiz-option';
            btn.textContent = option;
            btn.onclick = () => this.selectOption(option, btn);
            container.appendChild(btn);
        });
        
        // Insert before cancel button
        const quizContent = document.querySelector('.quiz-content');
        const cancelBtn = document.getElementById('cancelQuizBtn');
        quizContent.insertBefore(container, cancelBtn);
    }
    
    selectOption(option, button) {
        // Remove previous selection
        document.querySelectorAll('.quiz-option').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Mark as selected
        button.classList.add('selected');
        this.selectedAnswer = option;
        
        // Enable submit button
        this.submitAnswerBtn.disabled = false;
    }
    
    submitAnswer() {
        if (!this.selectedAnswer) return;
        
        const question = this.questions[this.currentQuestionIndex];
        const isCorrect = this.selectedAnswer === question.correctAnswer;
        
        // Update score
        if (isCorrect) {
            this.score++;
        }
        
        // Show feedback
        document.querySelectorAll('.quiz-option').forEach(btn => {
            btn.disabled = true;
            if (btn.textContent === question.correctAnswer) {
                btn.classList.add('correct');
            } else if (btn.textContent === this.selectedAnswer && !isCorrect) {
                btn.classList.add('incorrect');
            }
        });
        
        // Move to next question after delay
        setTimeout(() => {
            this.currentQuestionIndex++;
            this.showQuestion();
        }, 1500);
    }
    
    showResults() {
        // Hide quiz modal
        this.quizModal.style.display = 'none';
        
        // Calculate results
        const passed = this.score >= 8;
        const percentage = Math.round((this.score / 10) * 100);
        
        // Update result modal
        document.getElementById('resultTitle').textContent = passed ? 'Congratulations! 🎉' : 'Keep Practicing! 💪';
        document.getElementById('resultMessage').textContent = passed 
            ? 'You have successfully passed the ASL Alphabet Quiz!' 
            : `You got ${this.score}/10. Practice more and try again!`;
        document.getElementById('finalScore').textContent = `${this.score}/10`;
        document.getElementById('resultPercentage').textContent = `${percentage}%`;
        
        // Update animation
        const animation = document.getElementById('resultAnimation');
        animation.innerHTML = passed 
            ? '<i class="fas fa-trophy" style="font-size: 5rem; color: #C49A6C;"></i>'
            : '<i class="fas fa-redo" style="font-size: 5rem; color: #A1887F;"></i>';
        
        // Show result modal
        this.quizResultModal.style.display = 'flex';
    }
    
    cancel() {
        this.quizModal.style.display = 'none';
        this.quizResultModal.style.display = 'none';
        if (this.quizVideo) {
            this.quizVideo.pause();
        }
    }
    
    close() {
        this.quizResultModal.style.display = 'none';
        if (this.quizVideo) {
            this.quizVideo.pause();
        }
    }
}

// Initialize quiz when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.aslQuiz = new ASLQuiz();
    });
} else {
    window.aslQuiz = new ASLQuiz();
}
