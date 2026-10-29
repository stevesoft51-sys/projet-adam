/* ============================================
   RESTAURANT ADAM - Client JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {

    // ---- Mobile menu ----
    const mobileToggle = document.getElementById('mobileMenuToggle');
    const clientNav = document.getElementById('clientNav');
    if (mobileToggle && clientNav) {
        mobileToggle.addEventListener('click', () => {
            clientNav.classList.toggle('open');
        });
        document.addEventListener('click', (e) => {
            if (!clientNav.contains(e.target) && e.target !== mobileToggle) {
                clientNav.classList.remove('open');
            }
        });
    }

    // ---- Auto-close alerts ----
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // ---- Smooth scroll for anchors ----
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    // ---- Scroll reveal animation ----
    const revealElements = document.querySelectorAll(
        '.trust-item, .featured-card, .story-content, .story-card, .testimonial-card, .cta-box, .info-card'
    );
    revealElements.forEach(el => el.classList.add('reveal'));

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    revealElements.forEach(el => revealObserver.observe(el));

    // ---- Animated counter ----
    const counters = document.querySelectorAll('.story-stat-number[data-target]');
    let countersAnimated = false;

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !countersAnimated) {
                countersAnimated = true;
                counters.forEach(counter => {
                    const target = parseInt(counter.dataset.target);
                    const duration = 1500;
                    const step = Math.ceil(target / (duration / 16));
                    let current = 0;
                    const timer = setInterval(() => {
                        current += step;
                        if (current >= target) {
                            current = target;
                            clearInterval(timer);
                        }
                        counter.textContent = current.toLocaleString('fr-FR');
                    }, 16);
                });
                counterObserver.disconnect();
            }
        });
    }, { threshold: 0.3 });

    counters.forEach(el => counterObserver.observe(el));

    // ---- Parallax hero effect ----
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            hero.style.backgroundPositionY = scrolled * 0.3 + 'px';
        });
    }

    // ---- Menu category filter (client) ----
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const filter = this.dataset.filter;
            document.querySelectorAll('.menu-category-section').forEach(section => {
                if (filter === 'all' || section.dataset.category === filter) {
                    section.style.display = '';
                } else {
                    section.style.display = 'none';
                }
            });
        });
    });

    // ---- Auto-refresh menu page (admin-client synchronization) ----
    const menuFilters = document.getElementById('menuFilters');
    if (menuFilters && window.location.pathname === '/menu') {
        let lastMenuHTML = document.querySelector('.admin-content, .client-main')?.innerHTML || '';
        setInterval(function() {
            fetch('/menu', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(r => r.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newContent = doc.querySelector('.client-main')?.innerHTML || '';
                    const currentContent = document.querySelector('.client-main')?.innerHTML || '';
                    if (newContent !== currentContent) {
                        document.querySelector('.client-main').innerHTML = newContent;
                        // Re-bind filter buttons after refresh
                        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                        const allBtn = document.querySelector('.filter-btn[data-filter="all"]');
                        if (allBtn) allBtn.classList.add('active');
                    }
                })
                .catch(() => {});
        }, 30000);
    }
});
