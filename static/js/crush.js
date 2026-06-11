/**
 * Crush Proposal Page - JavaScript
 * Handles: Envelope animation, typing effect, floating emojis,
 * No button escape, Yes click celebration, confetti, notifications
 */

(function() {
    'use strict';

    // ========================
    // INITIALIZATION
    // ========================

    const envelopeContainer = document.getElementById('envelopeContainer');
    const mainContent = document.getElementById('mainContent');
    const btnNo = document.getElementById('btnNo');
    const btnYes = document.getElementById('btnYes');
    const crushNameText = document.getElementById('crushNameText');
    const messageText = document.getElementById('messageText');
    const celebrationOverlay = document.getElementById('celebrationOverlay');
    const confettiContainer = document.getElementById('confettiContainer');
    const bgMusic = document.getElementById('bgMusic');
    const celebrationMusic = document.getElementById('celebrationMusic');
    const floatingEmojis = document.getElementById('floatingEmojis');
    const floatingHearts = document.getElementById('floatingHearts');

    let hasClickedYes = false;

    // ========================
    // ENVELOPE CLICK
    // ========================

    if (envelopeContainer) {
        envelopeContainer.addEventListener('click', openEnvelope);
        envelopeContainer.addEventListener('touchend', function(e) {
            e.preventDefault();
            openEnvelope();
        });
    }

    function openEnvelope() {
        envelopeContainer.classList.add('hidden');
        
        setTimeout(() => {
            mainContent.classList.add('visible');
            startTypingEffect();
            startFloatingEmojis();
            startFloatingHearts();
            playBgMusic();
        }, 400);
    }

    // ========================
    // TYPING EFFECT
    // ========================

    function startTypingEffect() {
        const crushName = PAGE_DATA.crushName;
        const message = PAGE_DATA.message;

        // Type crush name
        typeText(crushNameText, crushName, 80, () => {
            // Then type message
            setTimeout(() => {
                typeText(messageText, message, 50);
            }, 500);
        });
    }

    function typeText(element, text, speed, callback) {
        element.innerHTML = '';
        const cursor = document.createElement('span');
        cursor.className = 'typing-cursor';
        element.appendChild(cursor);

        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                element.insertBefore(document.createTextNode(text[i]), cursor);
                i++;
            } else {
                clearInterval(interval);
                // Remove cursor after a delay
                setTimeout(() => {
                    if (cursor.parentNode) {
                        cursor.remove();
                    }
                    if (callback) callback();
                }, 1000);
            }
        }, speed);
    }

    // ========================
    // FLOATING EMOJIS
    // ========================

    function startFloatingEmojis() {
        const emoji = PAGE_DATA.emoji || '💕';
        
        function createFloatingEmoji() {
            const el = document.createElement('div');
            el.className = 'floating-emoji';
            el.textContent = emoji;
            el.style.left = Math.random() * 100 + '%';
            el.style.animationDuration = (6 + Math.random() * 6) + 's';
            el.style.animationDelay = Math.random() * 3 + 's';
            el.style.fontSize = (18 + Math.random() * 16) + 'px';
            floatingEmojis.appendChild(el);

            // Remove after animation
            setTimeout(() => {
                if (el.parentNode) el.remove();
            }, 14000);
        }

        // Create initial batch
        for (let i = 0; i < 8; i++) {
            setTimeout(createFloatingEmoji, i * 600);
        }

        // Continue creating
        setInterval(createFloatingEmoji, 2000);
    }

    // ========================
    // FLOATING HEARTS
    // ========================

    function startFloatingHearts() {
        const hearts = ['❤️', '💕', '💗', '💖', '💝'];
        
        function createHeart() {
            const el = document.createElement('div');
            el.className = 'float-heart';
            el.textContent = hearts[Math.floor(Math.random() * hearts.length)];
            el.style.left = Math.random() * 100 + '%';
            el.style.animationDuration = (5 + Math.random() * 5) + 's';
            el.style.animationDelay = Math.random() * 2 + 's';
            el.style.fontSize = (14 + Math.random() * 14) + 'px';
            floatingHearts.appendChild(el);

            setTimeout(() => {
                if (el.parentNode) el.remove();
            }, 12000);
        }

        for (let i = 0; i < 6; i++) {
            setTimeout(createHeart, i * 800);
        }

        setInterval(createHeart, 2500);
    }

    // ========================
    // BACKGROUND MUSIC
    // ========================

    function playBgMusic() {
        if (bgMusic && PAGE_DATA.bgMusic) {
            bgMusic.volume = 0.3;
            bgMusic.play().catch(() => {
                // Auto-play blocked, play on next user interaction
                document.addEventListener('click', function playOnce() {
                    bgMusic.play().catch(() => {});
                    document.removeEventListener('click', playOnce);
                }, { once: true });
            });
        }
    }

    // ========================
    // NO BUTTON ESCAPE
    // ========================

    function moveNoButton() {
        if (hasClickedYes) return;

        const container = btnNo.closest('.buttons-container');
        const card = btnNo.closest('.paper-card');
        const cardRect = card.getBoundingClientRect();
        const btnRect = btnNo.getBoundingClientRect();

        // Calculate random position within the card bounds
        const maxX = cardRect.width - btnRect.width - 40;
        const maxY = cardRect.height - btnRect.height - 40;

        const randomX = Math.random() * maxX - maxX / 2;
        const randomY = Math.random() * maxY - maxY / 2;

        // Apply position
        btnNo.style.position = 'absolute';
        btnNo.style.left = Math.max(20, Math.min(cardRect.width - btnRect.width - 20, 
            (cardRect.width / 2) + randomX)) + 'px';
        btnNo.style.top = Math.max(20, Math.min(cardRect.height - btnRect.height - 20,
            (cardRect.height / 2) + randomY)) + 'px';
        btnNo.style.zIndex = '50';
    }

    // Desktop: mouseover
    if (btnNo) {
        btnNo.addEventListener('mouseover', function(e) {
            e.preventDefault();
            moveNoButton();
        });

        // Mobile: touchstart
        btnNo.addEventListener('touchstart', function(e) {
            e.preventDefault();
            moveNoButton();
        }, { passive: false });

        // Also handle click just in case
        btnNo.addEventListener('click', function(e) {
            e.preventDefault();
            moveNoButton();
            // Track no attempt
            fetch('/api/no/' + PAGE_DATA.linkId, { method: 'POST' }).catch(() => {});
        });
    }

    // ========================
    // YES BUTTON HANDLER
    // ========================

    window.handleYes = function() {
        if (hasClickedYes) return;
        hasClickedYes = true;

        // Send YES to server
        fetch('/api/yes/' + PAGE_DATA.linkId, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }).catch(() => {});

        // Show celebration
        showCelebration();
    };

    // ========================
    // CELEBRATION
    // ========================

    function showCelebration() {
        // Stop background music
        if (bgMusic) {
            bgMusic.pause();
        }

        // Play celebration music
        if (celebrationMusic) {
            celebrationMusic.volume = 0.5;
            celebrationMusic.play().catch(() => {});
        }

        // Show overlay
        celebrationOverlay.style.display = 'flex';
        setTimeout(() => {
            celebrationOverlay.classList.add('active');
        }, 50);

        // Launch confetti
        launchConfetti();

        // Continue confetti
        setTimeout(launchConfetti, 1000);
        setTimeout(launchConfetti, 2000);
    }

    // ========================
    // CONFETTI
    // ========================

    function launchConfetti() {
        const colors = [
            '#ff6b8a', '#ff4757', '#ffd93d', '#6c5ce7',
            '#a8e6cf', '#ff8a80', '#ea80fc', '#80d8ff',
            '#ffab91', '#e040fb', '#69f0ae', '#ffd740'
        ];
        const shapes = ['circle', 'square', 'triangle'];

        for (let i = 0; i < 60; i++) {
            setTimeout(() => {
                createConfettiPiece(colors, shapes);
            }, i * 30);
        }
    }

    function createConfettiPiece(colors, shapes) {
        const piece = document.createElement('div');
        piece.className = 'confetti';
        
        const color = colors[Math.floor(Math.random() * colors.length)];
        const shape = shapes[Math.floor(Math.random() * shapes.length)];
        
        piece.style.left = Math.random() * 100 + '%';
        piece.style.backgroundColor = color;
        piece.style.width = (8 + Math.random() * 8) + 'px';
        piece.style.height = (8 + Math.random() * 8) + 'px';
        piece.style.animationDuration = (2 + Math.random() * 2) + 's';
        piece.style.animationDelay = Math.random() * 0.5 + 's';
        
        if (shape === 'circle') {
            piece.style.borderRadius = '50%';
        } else if (shape === 'triangle') {
            piece.style.width = '0';
            piece.style.height = '0';
            piece.style.backgroundColor = 'transparent';
            piece.style.borderLeft = '6px solid transparent';
            piece.style.borderRight = '6px solid transparent';
            piece.style.borderBottom = '12px solid ' + color;
        }

        confettiContainer.appendChild(piece);

        // Remove after animation
        setTimeout(() => {
            if (piece.parentNode) piece.remove();
        }, 5000);
    }

})();
