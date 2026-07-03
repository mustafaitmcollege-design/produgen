/**
 * ProduGen - Frontend JavaScript
 * Handles chat, upload, generation, and results display.
 */

const API_BASE = '';  // Same origin
let currentSessionId = null;

// =============================================================================
// DOM Elements
// =============================================================================
const apiStatus = document.getElementById('api-status');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');
const startChatBtn = document.getElementById('start-chat-btn');

const uploadSection = document.getElementById('upload-section');
const uploadZone = document.getElementById('upload-zone');
const uploadPlaceholder = document.getElementById('upload-placeholder');
const uploadPreview = document.getElementById('upload-preview');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');

const generateSection = document.getElementById('generate-section');
const generateBtn = document.getElementById('generate-btn');
const generateProgress = document.getElementById('generate-progress');
const progressText = document.getElementById('progress-text');
const numImagesSelect = document.getElementById('num-images');
const platformSelect = document.getElementById('platform');

const resultsSection = document.getElementById('results-section');
const resultsGrid = document.getElementById('results-grid');
const newSessionBtn = document.getElementById('new-session-btn');

const briefPreview = document.getElementById('brief-preview');
const briefContent = document.getElementById('brief-content');


// =============================================================================
// Initialize
// =============================================================================
async function init() {
    await checkHealth();

    // Event listeners
    startChatBtn.addEventListener('click', startChat);
    chatSendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Upload events
    uploadZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    uploadBtn.addEventListener('click', uploadImage);

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect();
        }
    });

    // Generate
    generateBtn.addEventListener('click', generateImages);

    // New session
    newSessionBtn.addEventListener('click', resetSession);
}


// =============================================================================
// Health Check
// =============================================================================
async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();

        let statusHtml = '';
        if (data.api_keys.gemini) {
            statusHtml += '<span class="status-ok">✅ Gemini</span> ';
        } else {
            statusHtml += '<span class="status-error">❌ Gemini key missing</span> ';
        }
        if (data.api_keys.replicate) {
            statusHtml += '<span class="status-ok">✅ Replicate</span>';
        } else {
            statusHtml += '<span class="status-error">❌ Replicate key missing</span>';
        }
        apiStatus.innerHTML = statusHtml;
    } catch (err) {
        apiStatus.innerHTML = '<span class="status-error">❌ Server not reachable</span>';
    }
}


// =============================================================================
// Chat Functions
// =============================================================================
async function startChat() {
    startChatBtn.disabled = true;
    startChatBtn.textContent = 'Starting...';

    try {
        const res = await fetch(`${API_BASE}/api/chat/start`, { method: 'POST' });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || 'Failed to start chat');

        currentSessionId = data.session_id;
        addChatBubble(data.message, 'ai');

        chatInput.disabled = false;
        chatSendBtn.disabled = false;
        chatInput.focus();
        startChatBtn.classList.add('hidden');
    } catch (err) {
        alert('Error: ' + err.message);
        startChatBtn.disabled = false;
        startChatBtn.textContent = 'Start Chat with AI';
    }
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !currentSessionId) return;

    addChatBubble(message, 'user');
    chatInput.value = '';
    chatInput.disabled = true;
    chatSendBtn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/api/chat/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message,
            }),
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || 'Failed to send message');

        addChatBubble(data.message, 'ai');

        if (data.is_complete && data.brief) {
            // Show brief and move to upload step
            briefContent.textContent = JSON.stringify(data.brief, null, 2);
            briefPreview.classList.remove('hidden');
            uploadSection.classList.remove('hidden');

            chatInput.disabled = true;
            chatSendBtn.disabled = true;
            chatInput.placeholder = 'Questionnaire complete! Upload your image below.';
        } else {
            chatInput.disabled = false;
            chatSendBtn.disabled = false;
            chatInput.focus();
        }
    } catch (err) {
        alert('Error: ' + err.message);
        chatInput.disabled = false;
        chatSendBtn.disabled = false;
    }
}

function addChatBubble(message, role) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    const label = document.createElement('div');
    label.className = 'bubble-label';
    label.textContent = role === 'ai' ? '🤖 ProduGen AI' : '👤 You';

    const content = document.createElement('div');
    content.className = 'bubble-content';
    content.textContent = message;

    bubble.appendChild(label);
    bubble.appendChild(content);
    chatMessages.appendChild(bubble);

    // Clear float
    const clearDiv = document.createElement('div');
    clearDiv.style.clear = 'both';
    chatMessages.appendChild(clearDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


// =============================================================================
// Upload Functions
// =============================================================================
function handleFileSelect() {
    const file = fileInput.files[0];
    if (!file) return;

    // Preview
    const reader = new FileReader();
    reader.onload = (e) => {
        uploadPreview.src = e.target.result;
        uploadPreview.classList.remove('hidden');
        uploadPlaceholder.classList.add('hidden');
        uploadBtn.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

async function uploadImage() {
    const file = fileInput.files[0];
    if (!file || !currentSessionId) return;

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';

    try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${API_BASE}/api/upload?session_id=${currentSessionId}`, {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || 'Upload failed');

        uploadBtn.textContent = '✅ Uploaded!';
        generateSection.classList.remove('hidden');
    } catch (err) {
        alert('Upload error: ' + err.message);
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload Image';
    }
}


// =============================================================================
// Generation Functions
// =============================================================================
async function generateImages() {
    if (!currentSessionId) return;

    generateBtn.classList.add('hidden');
    generateProgress.classList.remove('hidden');

    const numImages = parseInt(numImagesSelect.value);
    const platform = platformSelect.value;

    try {
        const res = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                num_images: numImages,
                platform: platform,
            }),
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || 'Generation failed');

        displayResults(data.images);
    } catch (err) {
        alert('Generation error: ' + err.message);
        generateBtn.classList.remove('hidden');
        generateProgress.classList.add('hidden');
    }
}

function displayResults(images) {
    generateProgress.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    resultsGrid.innerHTML = '';

    images.forEach((img) => {
        if (!img.path) return;

        const card = document.createElement('div');
        card.className = 'result-card';

        card.innerHTML = `
            <img src="/api/images/file/${img.session_id}/${img.filename}" alt="${img.variation}">
            <div class="card-info">
                <h4>${img.variation_description || img.variation}</h4>
                <p>${img.platform} • ${img.variation}</p>
            </div>
            <a href="/api/images/file/${img.session_id}/${img.filename}" 
               download="${img.filename}" 
               class="download-btn">
                ⬇ Download
            </a>
        `;

        resultsGrid.appendChild(card);
    });
}


// =============================================================================
// Reset
// =============================================================================
function resetSession() {
    currentSessionId = null;
    chatMessages.innerHTML = '';
    chatInput.value = '';
    chatInput.disabled = true;
    chatInput.placeholder = 'Type your answer...';
    chatSendBtn.disabled = true;
    startChatBtn.classList.remove('hidden');
    startChatBtn.disabled = false;
    startChatBtn.textContent = 'Start Chat with AI';

    uploadSection.classList.add('hidden');
    uploadPreview.classList.add('hidden');
    uploadPreview.src = '';
    uploadPlaceholder.classList.remove('hidden');
    uploadBtn.classList.add('hidden');
    uploadBtn.disabled = false;
    uploadBtn.textContent = 'Upload Image';
    fileInput.value = '';

    generateSection.classList.add('hidden');
    generateBtn.classList.remove('hidden');
    generateProgress.classList.add('hidden');

    resultsSection.classList.add('hidden');
    resultsGrid.innerHTML = '';

    briefPreview.classList.add('hidden');
    briefContent.textContent = '';
}


// Start the app
init();
