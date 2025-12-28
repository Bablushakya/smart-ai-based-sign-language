// Contact Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    const successModal = document.getElementById('successModal');
    const modalClose = document.getElementById('modalClose');

    // Form submission with EmailJS
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(contactForm);
        
        // Prepare template parameters matching EmailJS template variables
        const templateParams = {
            from_name: formData.get('name'),
            from_email: formData.get('email'),
            subject: formData.get('subject'),
            message: formData.get('message')
        };

        // Show loading state
        const submitBtn = contactForm.querySelector('.submit-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        submitBtn.disabled = true;

        // Send email using EmailJS
        emailjs.send('service_9hcjo9n', 'template_p0qw1qn', templateParams)
            .then(function(response) {
                console.log('SUCCESS!', response.status, response.text);
                
                // Show success modal
                successModal.classList.add('active');
                
                // Reset form
                contactForm.reset();
                
                // Reset button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, function(error) {
                console.error('FAILED...', error);
                
                // Show error message
                alert('Failed to send message. Please try again or contact us directly at hello@signspeak.com');
                
                // Reset button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
    });

    // Close modal
    modalClose.addEventListener('click', function() {
        successModal.classList.remove('active');
    });

    // Close modal when clicking outside
    successModal.addEventListener('click', function(e) {
        if (e.target === successModal) {
            successModal.classList.remove('active');
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && successModal.classList.contains('active')) {
            successModal.classList.remove('active');
        }
    });

    // Add smooth animations to info cards
    const infoCards = document.querySelectorAll('.info-card');
    infoCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // 3D Mouse Interaction for Video Container
    init3DVideoEffect();
});

function init3DVideoEffect() {
    const videoContainer = document.querySelector('.video-container-3d');
    
    if (!videoContainer) return;

    // 3D tilt effect on mouse move
    videoContainer.addEventListener('mousemove', function(e) {
        const rect = videoContainer.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        videoContainer.style.transform = `
            perspective(1000px)
            rotateX(${rotateX}deg)
            rotateY(${rotateY}deg)
            translateY(-5px)
            scale3d(1.02, 1.02, 1.02)
        `;
    });

    // Reset on mouse leave
    videoContainer.addEventListener('mouseleave', function() {
        videoContainer.style.transform = `
            perspective(1000px)
            rotateX(0deg)
            rotateY(0deg)
            translateY(0)
            scale3d(1, 1, 1)
        `;
    });

    // Add parallax effect to overlay
    videoContainer.addEventListener('mousemove', function(e) {
        const overlay = videoContainer.querySelector('.video-overlay');
        if (!overlay) return;

        const rect = videoContainer.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const moveX = (x - rect.width / 2) / 20;
        const moveY = (y - rect.height / 2) / 20;
        
        overlay.style.transform = `translate(${moveX}px, ${moveY}px)`;
    });

    // Ensure video plays
    const video = videoContainer.querySelector('video');
    if (video) {
        video.play().catch(e => console.log('Video autoplay prevented:', e));
    }
}
