// ═══════════════════════════════════════════════════════════
// STUDY QUEST -> Landing Page JavaScript
// Handles animations, scroll effects, and interactivity
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {
  
  // ── Intersection Observer for Scroll Animations ──────────
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, observerOptions);

  // Observe all animate-in elements
  const animatedElements = document.querySelectorAll('.animate-in');
  animatedElements.forEach(el => observer.observe(el));

  // ── Floating Animation Enhancement ───────────────────────
  const floatingElements = document.querySelectorAll('.float-anim');
  floatingElements.forEach((el, index) => {
    // Stagger the animation timing for multiple floating elements
    el.style.animationDelay = `${index * 0.2}s`;
  });

  // ── Smooth Scroll for Anchor Links ───────────────────────
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // ── Hero CTA Button Ripple Effect ────────────────────────
  const ctaButtons = document.querySelectorAll('.hero-cta .btn');
  ctaButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      // Create ripple element
      const ripple = document.createElement('span');
      ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        width: 20px;
        height: 20px;
        pointer-events: none;
        animation: ripple-effect 0.6s ease-out;
      `;
      
      // Position ripple at click location
      const rect = this.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      
      this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(ripple);
      
      // Remove ripple after animation
      setTimeout(() => ripple.remove(), 600);
    });
  });

  // ── Parallax Scroll Effect for Hero ──────────────────────
  const hero = document.querySelector('.landing-hero');
  if (hero) {
    let ticking = false;
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const scrolled = window.pageYOffset;
          const rate = scrolled * 0.5;
          
          hero.style.transform = `translateY(${rate}px)`;
          hero.style.opacity = 1 - (scrolled / 600);
          
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  // ── Feature Cards Hover Enhancement ──────────────────────
  const featureCards = document.querySelectorAll('.feature-card');
  featureCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-8px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0) scale(1)';
    });
  });

  // ── Stats Counter Animation ──────────────────────────────
  function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        element.textContent = target;
        clearInterval(timer);
      } else {
        element.textContent = Math.floor(current);
      }
    }, 16);
  }

  // Trigger counters when they come into view
  const counterElements = document.querySelectorAll('[data-counter]');
  if (counterElements.length > 0) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.dataset.counted) {
          const target = parseInt(entry.target.dataset.counter);
          animateCounter(entry.target, target);
          entry.target.dataset.counted = 'true';
        }
      });
    }, { threshold: 0.5 });

    counterElements.forEach(el => counterObserver.observe(el));
  }

  // ── Easter Egg: Konami Code ──────────────────────────────
  let konamiCode = [];
  const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
  
  document.addEventListener('keydown', (e) => {
    konamiCode.push(e.key);
    konamiCode = konamiCode.slice(-konamiSequence.length);
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
      // Secret unlocked! 
      createConfetti();
      showSecretMessage();
      konamiCode = [];
    }
  });

  function createConfetti() {
    const colors = ['var(--moss)', 'var(--honey)', 'var(--sage)', 'var(--peach)', 'var(--rose)'];
    
    for (let i = 0; i < 50; i++) {
      const confetti = document.createElement('div');
      confetti.style.cssText = `
        position: fixed;
        width: 8px;
        height: 8px;
        background: ${colors[Math.floor(Math.random() * colors.length)]};
        top: -10px;
        left: ${Math.random() * 100}vw;
        opacity: ${Math.random() * 0.7 + 0.3};
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        animation: confetti-fall ${Math.random() * 2 + 2}s ease-out forwards;
      `;
      
      document.body.appendChild(confetti);
      setTimeout(() => confetti.remove(), 4000);
    }
  }

  function showSecretMessage() {
    const message = document.createElement('div');
    message.className = 'flash-success';
    message.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 10000;
      animation: sparkle-pop 0.6s ease-out;
    `;
    message.innerHTML = `
      <span class="flash-icon">✨</span>
      <span class="flash-message">Secret discovered! You're a true scholar! 🌸</span>
      <button type="button" class="flash-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(message);
    setTimeout(() => message.remove(), 3000);
  }

  // ── Loading State Enhancement ─────────────────────────────
  // Add a subtle loading animation to buttons on click
  const actionButtons = document.querySelectorAll('a.btn[href]');
  actionButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      if (!this.classList.contains('loading')) {
        this.classList.add('loading');
        const originalText = this.innerHTML;
        this.innerHTML = '<span class="spinner" style="display:inline-block;width:14px;height:14px"></span>';
        
        // Restore original state if navigation takes too long
        setTimeout(() => {
          this.classList.remove('loading');
          this.innerHTML = originalText;
        }, 3000);
      }
    });
  });

  // ── Initialize ─────────────────────────────────────────────
  console.log('🌸 Study Quest landing page initialized');
  
  // Trigger initial animations
  setTimeout(() => {
    document.body.classList.add('loaded');
  }, 100);
});

// ── CSS Animation Keyframes (injected via JS) ──────────────
const style = document.createElement('style');
style.textContent = `
  @keyframes ripple-effect {
    from {
      transform: scale(0);
      opacity: 1;
    }
    to {
      transform: scale(20);
      opacity: 0;
    }
  }
  
  @keyframes confetti-fall {
    to {
      transform: translateY(100vh) rotate(360deg);
      opacity: 0;
    }
  }
  
  .animate-in {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s ease, transform 0.6s ease;
  }
  
  .animate-in.visible {
    opacity: 1;
    transform: translateY(0);
  }
  
  .feature-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
`;
document.head.appendChild(style);
