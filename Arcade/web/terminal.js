// Terminal.js - xterm.js integration for Arcade Terminal

let term;
let socket;
let sessionId = null;
let fitAddon;
let webLinksAddon;

// Initialize terminal
function initTerminal() {
    // Create terminal
    term = new Terminal({
        cursorBlink: true,
        cursorStyle: 'block',
        fontSize: 14,
        fontFamily: 'Courier New, monospace',
        theme: {
            background: '#000000',
            foreground: '#00ff00',
            cursor: '#00ff00',
            selection: 'rgba(0, 255, 0, 0.3)'
        },
        allowTransparency: true
    });

    // Add addons
    fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    
    webLinksAddon = new WebLinksAddon.WebLinksAddon();
    term.loadAddon(webLinksAddon);

    // Open terminal
    term.open(document.getElementById('terminal'));
    fitAddon.fit();

    // Handle window resize
    window.addEventListener('resize', () => {
        fitAddon.fit();
    });

    // Connect to WebSocket
    connectWebSocket();

    // Handle keyboard shortcuts
    term.attachCustomKeyEventHandler((event) => {
        // F1 for help
        if (event.key === 'F1') {
            event.preventDefault();
            toggleHelp();
            return false;
        }
        return true;
    });
}

// Connect to WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/arcade/ws`;
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
        updateStatus('connected', 'Connected');
        term.writeln('\r\n\x1b[32mConnected to Arcade Terminal!\x1b[0m');
        term.writeln('\x1b[36mType "help" for commands or press F1 for help.\x1b[0m');
        term.writeln('\x1b[33mTry: analyze 808-bass | visualize 3d | game list | playground\x1b[0m\r\n');
    };

    socket.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleMessage(message);
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus('error', 'Connection Error');
        term.writeln('\r\n\x1b[31mConnection error. Please refresh the page.\x1b[0m\r\n');
    };

    socket.onclose = () => {
        updateStatus('disconnected', 'Disconnected');
        term.writeln('\r\n\x1b[33mConnection closed. Reconnecting...\x1b[0m\r\n');
        // Try to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };

    // Send input to server
    term.onData((data) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            sendCommand(data);
        }
    });

    // Handle terminal output
    term.onLineFeed = () => {
        // Custom line feed handling if needed
    };
}

// Handle incoming messages
function handleMessage(message) {
    switch (message.type) {
        case 'welcome':
            if (message.session_id) {
                sessionId = message.session_id;
            }
            term.writeln(`\r\n\x1b[36m${message.message}\x1b[0m\r\n`);
            if (message.location) {
                updateGameLocation(message.location);
            }
            break;

        case 'terminal_output':
            if (message.stdout) {
                term.write(message.stdout);
            }
            if (message.stderr) {
                term.write(`\x1b[31m${message.stderr}\x1b[0m`);
            }
            break;

        case 'game_response':
            if (message.result) {
                handleGameResponse(message.result);
            }
            break;

        case 'error':
            term.writeln(`\r\n\x1b[31mError: ${message.message}\x1b[0m\r\n`);
            break;

        case 'status':
            if (message.game) {
                updateGameStatus(message.game);
            }
            break;

        case 'tool_output':
            // Stream tool output in real-time
            if (message.line) {
                // Write colored output (preserve ANSI codes)
                // xterm.js handles ANSI codes natively
                term.write(message.line);
            }
            break;

        case 'tool_complete':
            // Tool execution complete
            if (message.result && message.result.success) {
                term.writeln(`\r\n\x1b[32m✅ Tool '${message.tool}' completed successfully\x1b[0m\r\n`);
            } else {
                term.writeln(`\r\n\x1b[31m❌ Tool '${message.tool}' failed\x1b[0m\r\n`);
                if (message.result && message.result.error) {
                    term.writeln(`\x1b[31mError: ${message.result.error}\x1b[0m\r\n`);
                }
            }
            break;

        case 'pong':
            // Heartbeat response
            break;

        default:
            console.log('Unknown message type:', message.type);
    }
}

// Handle game responses
function handleGameResponse(result) {
    if (result.message) {
        // Color code based on effect
        let color = '\x1b[36m'; // Default cyan
        if (result.effect === 'time_travel_backward') {
            color = '\x1b[35m'; // Magenta for time travel
        } else if (result.effect === 'navigation') {
            color = '\x1b[33m'; // Yellow for navigation
        }
        
        term.writeln(`\r\n${color}${result.message}\x1b[0m\r\n`);
    }

    if (result.location) {
        updateGameLocation(result.location);
    }

    if (result.speed !== undefined) {
        updateGameSpeed(result.speed);
    }

    if (result.locations) {
        term.writeln('\r\n\x1b[36mAvailable locations:\x1b[0m');
        result.locations.forEach(loc => {
            const marker = loc === result.current ? '→' : ' ';
            term.writeln(`  ${marker} ${loc}`);
        });
        term.writeln('');
    }
}

// Send command to server
function sendCommand(command) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const message = {
            type: 'command',
            command: command
        };
        socket.send(JSON.stringify(message));
    }
}

// Update status indicator
function updateStatus(status, text) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    indicator.className = 'status-indicator';
    if (status === 'connected') {
        indicator.classList.add('connected');
    }
    
    statusText.textContent = text;
}

// Update game UI
function updateGameLocation(location) {
    document.getElementById('gameLocation').textContent = location;
}

function updateGameSpeed(speed) {
    document.getElementById('gameSpeed').textContent = speed.toFixed(1);
}

function updateGameStatus(gameState) {
    if (gameState.location) {
        updateGameLocation(gameState.location);
    }
    if (gameState.speed !== undefined) {
        updateGameSpeed(gameState.speed);
    }
    if (gameState.score !== undefined) {
        document.getElementById('gameScore').textContent = gameState.score;
    }
    if (gameState.level !== undefined) {
        document.getElementById('gameLevel').textContent = gameState.level;
    }
}

// Toggle help panel
function toggleHelp() {
    const panel = document.getElementById('helpPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

// Send heartbeat
setInterval(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'ping' }));
    }
}, 30000); // Every 30 seconds

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initTerminal();
});

