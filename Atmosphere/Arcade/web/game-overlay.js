// Game Overlay - Additional game mechanics and UI updates

// Game state
let gameState = {
    location: 'Arcade',
    speed: 0.0,
    score: 0,
    level: 1,
    locationHistory: []
};

// Update game overlay with animation
function animateGameUpdate(property, newValue, oldValue) {
    const element = document.getElementById(`game${property}`);
    if (!element) return;

    // Add animation class
    element.classList.add('glitch-effect');
    
    // Update value
    if (property === 'Speed') {
        element.textContent = parseFloat(newValue).toFixed(1);
    } else {
        element.textContent = newValue;
    }

    // Remove animation after delay
    setTimeout(() => {
        element.classList.remove('glitch-effect');
    }, 300);
}

// Handle special game events
function handleGameEvent(event) {
    switch (event.type) {
        case 'time_travel':
            // Time travel effect
            showTimeTravelEffect(event.direction);
            break;
        
        case 'navigation':
            // Navigation effect
            showNavigationEffect(event.to, event.from);
            break;
        
        case 'speed_boost':
            // Speed boost effect
            showSpeedBoostEffect(event.speed);
            break;
    }
}

// Show time travel effect
function showTimeTravelEffect(direction) {
    const overlay = document.querySelector('.game-overlay');
    overlay.style.animation = 'glitch 0.5s';
    
    setTimeout(() => {
        overlay.style.animation = '';
    }, 500);
}

// Show navigation effect
function showNavigationEffect(to, from) {
    const locationElement = document.getElementById('gameLocation');
    locationElement.textContent = `→ ${to}`;
    locationElement.style.color = '#00ffff';
    
    setTimeout(() => {
        locationElement.style.color = '#00ff00';
    }, 1000);
}

// Show speed boost effect
function showSpeedBoostEffect(speed) {
    const speedElement = document.getElementById('gameSpeed');
    speedElement.style.fontSize = '1.2em';
    speedElement.style.color = '#ff00ff';
    
    setTimeout(() => {
        speedElement.style.fontSize = '';
        speedElement.style.color = '';
    }, 500);
}

// Request game status
function requestGameStatus() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'get_status' }));
    }
}

// Periodically update game status
setInterval(() => {
    requestGameStatus();
}, 5000); // Every 5 seconds

// Export for use in terminal.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        handleGameEvent,
        updateGameStatus: updateGameStatus
    };
}

