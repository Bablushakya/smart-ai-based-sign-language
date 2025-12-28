// Home Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize website opening animation first
    initWebsiteOpener();
    
    // Initialize floating hands for all sections
    initSectionFloatingHands();
});

// Website Opening Animation - Pull String Version
function initWebsiteOpener() {
    const websiteOpener = document.getElementById('websiteOpener');
    const pullString = document.querySelector('.pull-string');
    const mainContent = document.getElementById('mainContent');
    const body = document.body;

    if (!websiteOpener || !pullString) return;

    // Add loading class to body
    body.classList.add('website-loading');

    let isPulled = false;

    // Add click event to pull string
    pullString.addEventListener('click', function() {
        if (isPulled) return;
        isPulled = true;

        // Add pulled class to trigger CSS animations
        this.classList.add('pulled');

        // Hide the "Pull to Start" text
        const handleText = this.querySelector('.handle-text');
        if (handleText) {
            handleText.style.opacity = '0';
        }

        // After animation completes, hide opener and show main content
        setTimeout(() => {
            websiteOpener.classList.add('hidden');
            
            // Show main content with fade-in effect
            if (mainContent) {
                mainContent.style.opacity = '0';
                mainContent.style.display = 'block';
                
                setTimeout(() => {
                    mainContent.style.transition = 'opacity 1s ease-in-out';
                    mainContent.style.opacity = '1';
                }, 100);
            }

            // Remove loading class
            body.classList.remove('website-loading');

            // Initialize all other functionality after animation
            initParallax();
            initScrollAnimations();
            initFAQ();
            initParticleBackground();
            initMetricCounters();
            initSmoothScrolling();
            initButtonEffects();
            initGlobalFloatingHands();

            // Remove opener from DOM after transition
            setTimeout(() => {
                if (websiteOpener.parentNode) {
                    websiteOpener.parentNode.removeChild(websiteOpener);
                }
            }, 1000);

        }, 1500); // Match the CSS animation duration

    });

    // Auto-pull after 8 seconds if user doesn't interact
    setTimeout(() => {
        if (!isPulled) {
            pullString.click();
        }
    }, 8000);
}

// Section Floating Hands System
function initSectionFloatingHands() {
    const sections = [
        '.hero',
        '.purpose', 
        '.features',
        '.testimonials',
        '.future-goals',
        '.faq'
    ];

    sections.forEach(sectionSelector => {
        const section = document.querySelector(sectionSelector);
        if (!section) return;

        // Create hands container for this section
        const handsContainer = document.createElement('div');
        handsContainer.className = 'section-hands';
        section.appendChild(handsContainer);

        // Add floating hands to this section
        createSectionHands(handsContainer, sectionSelector);
    });
}

function createSectionHands(container, sectionClass) {
    const handCount = 4; // Reduced for performance
    const handEmojis = ['👋', '🤟', '✋', '🤙', '🖐️', '👍', '👌', '🤞'];
    
    for (let i = 0; i < handCount; i++) {
        setTimeout(() => {
            const hand = document.createElement('div');
            hand.className = `section-hand hand-${i + 1}`;
            
            // Random position within section
            const left = Math.random() * 80 + 10; // 10% to 90%
            const top = Math.random() * 80 + 10;
            const delay = Math.random() * 5; // Stagger animations
            
            hand.style.left = `${left}%`;
            hand.style.top = `${top}%`;
            hand.style.animationDelay = `${delay}s`;
            
            // Random emoji
            const randomEmoji = handEmojis[Math.floor(Math.random() * handEmojis.length)];
            hand.textContent = randomEmoji;
            
            container.appendChild(hand);
        }, i * 500); // Stagger creation
    }
}

// Global Floating Hands (for entire page)
function initGlobalFloatingHands() {
    const floatingHandsContainer = document.getElementById('floatingHands');
    if (!floatingHandsContainer) return;

    const handCount = 8;
    const handEmojis = ['👋', '🤟', '✋', '🤙', '🖐️', '👍', '👌', '🤞'];

    for (let i = 0; i < handCount; i++) {
        createFloatingHand(floatingHandsContainer, handEmojis, i);
    }
}

function createFloatingHand(container, emojis, index) {
    const hand = document.createElement('div');
    hand.className = 'floating-hand';
    
    // Random starting position
    const startLeft = Math.random() * 100;
    const startDelay = Math.random() * 5;
    const duration = 6 + Math.random() * 4; // 6-10 seconds
    const emoji = emojis[index % emojis.length];
    
    hand.style.left = `${startLeft}%`;
    hand.style.animationDelay = `${startDelay}s`;
    hand.style.animationDuration = `${duration}s`;
    hand.textContent = emoji;
    
    container.appendChild(hand);

    // Remove hand after animation and create new one
    setTimeout(() => {
        if (hand.parentNode) {
            hand.parentNode.removeChild(hand);
        }
        // Create new hand after a delay
        setTimeout(() => {
            createFloatingHand(container, emojis, index);
        }, 1000);
    }, (duration + startDelay) * 1000);
}

// Parallax Effect
function initParallax() {
    const heroBg = document.querySelector('.hero-background');
    const testimonialBg = document.querySelector('.testimonials-background');
    
    if (!heroBg && !testimonialBg) return;
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        if (heroBg) {
            heroBg.style.transform = `translateY(${rate}px)`;
        }
        
        if (testimonialBg) {
            testimonialBg.style.transform = `translateY(${rate * 0.3}px)`;
        }
    });
}

// Scroll Animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                // If it's a metric counter, trigger the count animation
                if (entry.target.classList.contains('metric-number')) {
                    const target = parseInt(entry.target.getAttribute('data-count'));
                    const suffix = entry.target.textContent.includes('%') ? '%' : '';
                    animateCounter(entry.target, target, suffix);
                }
            }
        });
    }, observerOptions);

    // Observe all elements with data-aos attribute
    document.querySelectorAll('[data-aos]').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// FAQ Accordion
function initFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    if (faqItems.length === 0) return;
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', () => {
            // Close all other items
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle current item
            item.classList.toggle('active');
        });
    });
}

// Particle Background for Future Goals Section
function initParticleBackground() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;
    
    // Set canvas size
    function setCanvasSize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    // Particle class
    class Particle {
        constructor() {
            this.reset();
        }
        
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 20 + 10;
            this.speedX = Math.random() * 0.5 - 0.25;
            this.speedY = Math.random() * 0.5 - 0.25;
            this.opacity = Math.random() * 0.3 + 0.1;
            this.wobble = Math.random() * Math.PI * 2;
            this.wobbleSpeed = Math.random() * 0.02 + 0.01;
        }
        
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.wobble += this.wobbleSpeed;
            
            // Add slight wobble
            this.x += Math.sin(this.wobble) * 0.3;
            this.y += Math.cos(this.wobble) * 0.3;
            
            // Reset if out of bounds
            if (this.x < -50 || this.x > canvas.width + 50 || 
                this.y < -50 || this.y > canvas.height + 50) {
                this.reset();
            }
        }
        
        draw() {
            ctx.save();
            ctx.globalAlpha = this.opacity;
            ctx.translate(this.x, this.y);
            
            // Draw hand shape (simplified)
            ctx.fillStyle = '#C49A6C';
            ctx.beginPath();
            
            // Palm
            ctx.arc(0, 0, this.size * 0.3, 0, Math.PI * 2);
            
            // Fingers (simplified)
            for (let i = 0; i < 4; i++) {
                ctx.rect(
                    -this.size * 0.2 + i * this.size * 0.15,
                    -this.size * 0.4,
                    this.size * 0.1,
                    this.size * 0.3
                );
            }
            
            // Thumb
            ctx.rect(
                -this.size * 0.35,
                -this.size * 0.1,
                this.size * 0.3,
                this.size * 0.1
            );
            
            ctx.fill();
            ctx.restore();
        }
    }
    
    // Initialize particles
    function initParticles() {
        particles = [];
        const particleCount = Math.min(15, Math.floor(canvas.width * canvas.height / 20000));
        
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        animationId = requestAnimationFrame(animate);
    }
    
    // Handle resize
    function handleResize() {
        setCanvasSize();
        initParticles();
    }
    
    // Start
    setCanvasSize();
    initParticles();
    animate();
    
    // Add resize listener with debounce
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 250);
    });
    
    // Cleanup function
    return () => {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        window.removeEventListener('resize', handleResize);
    };
}

// Metric Counters
function initMetricCounters() {
    const metricNumbers = document.querySelectorAll('.metric-number[data-count]');
    
    if (metricNumbers.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const metric = entry.target;
                const target = parseInt(metric.getAttribute('data-count'));
                const suffix = metric.textContent.includes('%') ? '%' : '';
                animateCounter(metric, target, suffix);
                observer.unobserve(metric);
            }
        });
    }, { threshold: 0.5 });
    
    metricNumbers.forEach(metric => observer.observe(metric));
}

function animateCounter(element, target, suffix) {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current) + suffix;
    }, 40);
}

// Smooth Scrolling
function initSmoothScrolling() {
    const scrollLinks = document.querySelectorAll('a[href^="#"]');
    
    if (scrollLinks.length === 0) return;
    
    scrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Button hover effects
function initButtonEffects() {
    const buttons = document.querySelectorAll('.btn');
    
    if (buttons.length === 0) return;
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
            this.style.boxShadow = '0 10px 25px rgba(196, 154, 108, 0.3)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
        
        // Add click effect
        button.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(0) scale(0.98)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
    });
}

// Error handling for images
function handleImageErrors() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            console.warn('Image failed to load:', this.src);
            // Don't hide the image, just log the error
        });
    });
}

// Initialize image error handling
handleImageErrors();

// Performance optimization: Throttle scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Export functions for potential use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initWebsiteOpener,
        initSectionFloatingHands,
        initGlobalFloatingHands,
        initParallax,
        initScrollAnimations,
        initFAQ,
        initParticleBackground,
        initMetricCounters,
        initSmoothScrolling,
        initButtonEffects
    };
}