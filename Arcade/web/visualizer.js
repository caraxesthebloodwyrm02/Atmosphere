// Visualizer.js - Handle visualization rendering in web terminal

// ANSI color to HTML conversion for better visualization display
function ansiToHtml(text) {
    // Basic ANSI color codes
    const colors = {
        '30': 'color: #000',
        '31': 'color: #ff0000',
        '32': 'color: #00ff00',
        '33': 'color: #ffff00',
        '34': 'color: #0000ff',
        '35': 'color: #ff00ff',
        '36': 'color: #00ffff',
        '37': 'color: #ffffff',
        '90': 'color: #808080',
    };
    
    // Simple ANSI to HTML conversion
    let html = text;
    html = html.replace(/\x1b\[32m/g, '<span style="color: #00ff00">');
    html = html.replace(/\x1b\[36m/g, '<span style="color: #00ffff">');
    html = html.replace(/\x1b\[33m/g, '<span style="color: #ffff00">');
    html = html.replace(/\x1b\[31m/g, '<span style="color: #ff0000">');
    html = html.replace(/\x1b\[35m/g, '<span style="color: #ff00ff">');
    html = html.replace(/\x1b\[90m/g, '<span style="color: #808080">');
    html = html.replace(/\x1b\[0m/g, '</span>');
    html = html.replace(/\x1b\[1m/g, '<strong>');
    
    return html;
}

// Display visualization image
function displayVisualization(imageUrl, caption) {
    const container = document.getElementById('terminal');
    if (!container) return;
    
    // Create visualization overlay
    const overlay = document.createElement('div');
    overlay.id = 'visualization-overlay';
    overlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.9);
        z-index: 2000;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    `;
    
    const img = document.createElement('img');
    img.src = imageUrl;
    img.style.cssText = `
        max-width: 90%;
        max-height: 80%;
        border: 2px solid #00ff00;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'Close (ESC)';
    closeBtn.style.cssText = `
        margin-top: 1rem;
        padding: 0.5rem 1.5rem;
        background: #00ff00;
        color: #000;
        border: none;
        cursor: pointer;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    `;
    closeBtn.onclick = () => overlay.remove();
    
    if (caption) {
        const cap = document.createElement('p');
        cap.textContent = caption;
        cap.style.cssText = 'color: #00ffff; margin-top: 1rem;';
        overlay.appendChild(cap);
    }
    
    overlay.appendChild(img);
    overlay.appendChild(closeBtn);
    
    // Close on ESC
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            overlay.remove();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
    
    container.parentElement.appendChild(overlay);
}

// Handle visualization data
function handleVisualizationData(data) {
    if (data.type === 'image' && data.url) {
        displayVisualization(data.url, data.caption);
    } else if (data.type === 'text') {
        // Text-based visualization is already handled by terminal
        return data.text;
    }
}

// Export for use in terminal.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ansiToHtml,
        displayVisualization,
        handleVisualizationData
    };
}

