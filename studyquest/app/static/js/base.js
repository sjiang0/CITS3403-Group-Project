  // Mobile menu toggle
  document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (menuBtn && sidebar && overlay) {
      menuBtn.addEventListener('click', function() {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
      });
      
      overlay.addEventListener('click', function() {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
      });
    }

    // Auto-dismiss flash messages after 5 seconds
    const flashes = document.querySelectorAll('.flash-container > div');
    flashes.forEach(flash => {
      setTimeout(() => {
        flash.classList.add('removing');
        setTimeout(() => flash.remove(), 300);
      }, 5000);
    });
  });