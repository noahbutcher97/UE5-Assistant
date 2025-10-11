"""Dashboard HTML template for the UE5 AI Assistant."""

def get_dashboard_html() -> str:
    """Return the dashboard HTML content."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UE5 AI Assistant - Dashboard</title>
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #0a0e27;
        background-image: 
            linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        min-height: 100vh;
        padding: 20px;
        color: #e0e6ed;
    }
    
    .container {
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .header {
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 245, 255, 0.2);
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.1), 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    .header h1 {
        color: #00f5ff;
        margin-bottom: 10px;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
        letter-spacing: -0.5px;
    }
    
    .header p {
        color: #94a3b8;
        font-size: 0.95em;
    }
    
    .stats {
        display: flex;
        gap: 15px;
        margin-top: 20px;
    }
    
    .stat-card {
        flex: 1;
        background: rgba(0, 245, 255, 0.05);
        border: 1px solid rgba(0, 245, 255, 0.2);
        color: #e0e6ed;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        background: rgba(0, 245, 255, 0.1);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
    }
    
    .stat-card .number {
        font-size: 2em;
        font-weight: bold;
        color: #00f5ff;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    .stat-card .label {
        opacity: 0.7;
        font-size: 0.9em;
        color: #94a3b8;
    }
    
    .tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .tab {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(0, 245, 255, 0.2);
        color: #94a3b8;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .tab.active {
        background: rgba(0, 245, 255, 0.1);
        border-color: #00f5ff;
        color: #00f5ff;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
    }
    
    .tab:hover {
        transform: translateY(-2px);
        border-color: #00f5ff;
        color: #00f5ff;
    }
    
    .tab-content {
        display: none;
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 245, 255, 0.2);
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.1);
    }
    
    .tab-content h2 {
        color: #00f5ff;
        margin-bottom: 15px;
    }
    
    .tab-content.active {
        display: block;
    }
    
    .conversation-list {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    
    .conversation-item {
        border: 1px solid rgba(0, 245, 255, 0.15);
        background: rgba(0, 20, 40, 0.5);
        border-radius: 8px;
        padding: 20px;
        transition: all 0.3s;
    }
    
    .conversation-item:hover {
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
        border-color: #00f5ff;
        background: rgba(0, 20, 40, 0.8);
    }
    
    .conversation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .timestamp {
        color: #64748b;
        font-size: 0.85em;
        font-family: 'Courier New', monospace;
    }
    
    .command-type {
        background: rgba(0, 245, 255, 0.2);
        color: #00f5ff;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        border: 1px solid rgba(0, 245, 255, 0.3);
        font-family: 'Courier New', monospace;
    }
    
    .user-input {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 245, 255, 0.1);
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 12px;
        color: #cbd5e1;
        border-left: 3px solid #667eea;
    }
    
    .user-input strong {
        color: #00f5ff;
    }
    
    .assistant-response {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 245, 255, 0.1);
        padding: 12px;
        border-radius: 6px;
        border-left: 3px solid #00f5ff;
        max-height: 200px;
        overflow-y: auto;
        color: #cbd5e1;
    }
    
    .assistant-response strong {
        color: #00f5ff;
    }
    
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #64748b;
    }
    
    .empty-state svg {
        width: 80px;
        height: 80px;
        margin-bottom: 20px;
        opacity: 0.3;
        stroke: #00f5ff;
    }
    
    .refresh-btn {
        background: rgba(0, 245, 255, 0.1);
        border: 1px solid #00f5ff;
        color: #00f5ff;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.3s;
    }
    
    .refresh-btn:hover {
        background: rgba(0, 245, 255, 0.2);
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
    }
    
    .auto-refresh {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #94a3b8;
        font-size: 14px;
    }
    
    .controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .setting-group {
        background: rgba(0, 20, 40, 0.4);
        border: 1px solid rgba(0, 245, 255, 0.15);
        padding: 20px;
        border-radius: 8px;
        transition: all 0.3s;
    }
    
    .setting-group:hover {
        border-color: rgba(0, 245, 255, 0.3);
        background: rgba(0, 20, 40, 0.6);
    }
    
    .setting-label {
        display: flex;
        flex-direction: column;
        gap: 5px;
        margin-bottom: 12px;
    }
    
    .setting-label strong {
        color: #00f5ff;
    }
    
    .setting-description {
        font-size: 13px;
        color: #94a3b8;
        font-weight: normal;
    }
    
    .setting-input, .setting-slider {
        width: 100%;
        padding: 10px;
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: 6px;
        font-size: 14px;
        color: #e0e6ed;
        transition: all 0.3s;
    }
    
    .setting-input:focus {
        outline: none;
        border-color: #00f5ff;
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.2);
    }
    
    .setting-slider {
        padding: 0;
        height: 8px;
        cursor: pointer;
        accent-color: #00f5ff;
    }
    
    .save-btn, .reset-btn {
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .save-btn {
        background: rgba(0, 245, 255, 0.1);
        border: 1px solid #00f5ff;
        color: #00f5ff;
        flex: 1;
    }
    
    .save-btn:hover {
        background: rgba(0, 245, 255, 0.2);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
        transform: translateY(-2px);
    }
    
    .reset-btn {
        background: rgba(100, 116, 139, 0.1);
        border: 1px solid #64748b;
        color: #94a3b8;
        flex: 1;
    }
    
    .reset-btn:hover {
        background: rgba(100, 116, 139, 0.2);
        border-color: #94a3b8;
        color: #cbd5e1;
    }
    
    .clear-history-btn:hover {
        background: #c0392b !important;
        box-shadow: 0 0 20px rgba(231, 76, 60, 0.4) !important;
        transform: translateY(-2px);
    }
    
    .save-status {
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .save-status.success {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .save-status.error {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🎮 UE5 AI Assistant Dashboard</h1>
        <p>Real-time conversation monitoring and analytics</p>
        <div class="stats">
            <div class="stat-card">
                <div class="number" id="total-conversations">0</div>
                <div class="label">Total Conversations</div>
            </div>
            <div class="stat-card">
                <div class="number" id="recent-conversations">0</div>
                <div class="label">Recent (Last 50)</div>
            </div>
            <div class="stat-card">
                <div class="number" id="max-storage">100</div>
                <div class="label">Max Storage</div>
            </div>
        </div>
    </div>
    
    <div class="tabs">
        <button class="tab active" onclick="showTab('dashboard')">📊 Dashboard</button>
        <button class="tab" onclick="showTab('settings')">⚙️ Settings</button>
        <button class="tab" onclick="showTab('api')">🔧 API Info</button>
        <button class="tab" onclick="showTab('about')">ℹ️ About</button>
    </div>
    
    <div id="dashboard" class="tab-content active">
        <div class="controls">
            <h2>Recent Conversations</h2>
            <div style="display: flex; gap: 15px; align-items: center;">
                <label class="auto-refresh">
                    <input type="checkbox" id="auto-refresh" checked>
                    Auto-refresh (5s)
                </label>
                <button class="refresh-btn" onclick="loadConversations()">
                    <span>🔄</span> Refresh Now
                </button>
            </div>
        </div>
        <div id="conversation-list" class="conversation-list">
            <div class="empty-state">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
                <p>No conversations yet. Start using the AI Assistant in Unreal Engine!</p>
            </div>
        </div>
    </div>
    
    <div id="settings" class="tab-content">
        <h2>⚙️ Configuration Settings</h2>
        <p style="margin: 15px 0; color: #666;">
            Configure AI behavior and response style in real-time without code changes
        </p>
        
        <div style="display: grid; gap: 25px; margin-top: 30px;">
            <!-- AI Model Selection -->
            <div class="setting-group">
                <label class="setting-label">
                    <strong>🤖 AI Model</strong>
                    <span class="setting-description">Choose the GPT model for responses</span>
                </label>
                <select id="model" class="setting-input">
                    <option value="gpt-4o-mini">GPT-4o Mini (Fast & Efficient)</option>
                    <option value="gpt-4o">GPT-4o (Balanced)</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo (Powerful)</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Legacy)</option>
                </select>
            </div>
            
            <!-- Response Style -->
            <div class="setting-group">
                <label class="setting-label">
                    <strong>📝 Response Style</strong>
                    <span class="setting-description">Adjust how the AI communicates</span>
                </label>
                <select id="response_style" class="setting-input">
                    <option value="descriptive">Descriptive (Default) - Clear and factual</option>
                    <option value="technical">Technical/Precise - Highly technical with exact specs</option>
                    <option value="natural">Natural/Conversational - Friendly and approachable</option>
                    <option value="balanced">Balanced - Mix of technical and readable</option>
                    <option value="concise">Concise/Brief - Short and to the point</option>
                    <option value="detailed">Detailed/Verbose - Comprehensive analysis</option>
                    <option value="creative">Creative/Imaginative - Vivid imagery and storytelling</option>
                </select>
            </div>
            
            <!-- Temperature -->
            <div class="setting-group">
                <label class="setting-label">
                    <strong>🌡️ Temperature: <span id="temp-value">0.7</span></strong>
                    <span class="setting-description">Higher = more creative, Lower = more focused</span>
                </label>
                <input type="range" id="temperature" class="setting-slider" min="0" max="1" step="0.1" value="0.7" 
                       oninput="document.getElementById('temp-value').textContent = this.value">
            </div>
            
            <!-- Max Context Turns -->
            <div class="setting-group">
                <label class="setting-label">
                    <strong>💬 Max Context Turns: <span id="turns-value">6</span></strong>
                    <span class="setting-description">Number of previous conversation turns to remember</span>
                </label>
                <input type="range" id="max_context_turns" class="setting-slider" min="2" max="20" step="1" value="6"
                       oninput="document.getElementById('turns-value').textContent = this.value">
            </div>
            
            <!-- Timeout -->
            <div class="setting-group">
                <label class="setting-label">
                    <strong>⏱️ Request Timeout: <span id="timeout-value">25</span>s</strong>
                    <span class="setting-description">Maximum time to wait for API response</span>
                </label>
                <input type="range" id="timeout" class="setting-slider" min="10" max="60" step="5" value="25"
                       oninput="document.getElementById('timeout-value').textContent = this.value">
            </div>
            
            <!-- Save Button -->
            <div style="display: flex; gap: 15px; margin-top: 10px;">
                <button onclick="saveSettings()" class="save-btn">
                    💾 Save Settings
                </button>
                <button onclick="resetSettings()" class="reset-btn">
                    🔄 Reset to Defaults
                </button>
            </div>
            
            <div id="save-status" class="save-status"></div>
            
            <!-- Conversation History Management -->
            <div class="setting-group" style="margin-top: 30px; border: 2px solid rgba(231, 76, 60, 0.5); background: rgba(231, 76, 60, 0.05);">
                <label class="setting-label">
                    <strong>🗑️ Conversation History</strong>
                    <span class="setting-description" style="color: #ef4444;">
                        Clear all stored conversations (both memory and persistent file)
                    </span>
                </label>
                <button onclick="clearHistory()" class="clear-history-btn" style="background: rgba(231, 76, 60, 0.2); color: #ef4444; padding: 12px 24px; border: 1px solid #ef4444; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; width: 100%; transition: all 0.3s;">
                    🗑️ Clear All Conversations
                </button>
            </div>
        </div>
    </div>
    
    <div id="api" class="tab-content">
        <h2>API Endpoints</h2>
        <p style="margin: 15px 0; color: #94a3b8;">Available API endpoints for the UE5 AI Assistant:</p>
        <ul style="list-style: none; line-height: 2;">
            <li><strong style="color: #00f5ff;">GET /</strong> <span style="color: #94a3b8;">- Health check</span></li>
            <li><strong style="color: #00f5ff;">POST /execute_command</strong> <span style="color: #94a3b8;">- Execute AI commands</span></li>
            <li><strong style="color: #00f5ff;">POST /describe_viewport</strong> <span style="color: #94a3b8;">- Generate viewport descriptions</span></li>
            <li><strong style="color: #00f5ff;">GET /api/conversations</strong> <span style="color: #94a3b8;">- Retrieve conversation history</span></li>
            <li><strong style="color: #00f5ff;">POST /api/log_conversation</strong> <span style="color: #94a3b8;">- Manually log a conversation</span></li>
            <li><strong style="color: #00f5ff;">DELETE /api/conversations</strong> <span style="color: #94a3b8;">- Clear all conversation history</span></li>
            <li><strong style="color: #00f5ff;">GET /dashboard</strong> <span style="color: #94a3b8;">- This dashboard</span></li>
        </ul>
    </div>
    
    <div id="about" class="tab-content">
        <h2>About UE5 AI Assistant</h2>
        <p style="margin: 15px 0; line-height: 1.6; color: #94a3b8;">
            This is a FastAPI backend service that provides AI-powered technical documentation 
            of Unreal Engine 5 editor viewport contexts. The system receives structured viewport 
            data from the Unreal Engine Python environment and uses OpenAI's GPT models to generate 
            technical prose descriptions.
        </p>
        <p style="margin: 15px 0; line-height: 1.6; color: #cbd5e1;">
            <strong style="color: #00f5ff;">Version:</strong> 2.0 (Modular Architecture)<br>
            <strong style="color: #00f5ff;">Model:</strong> GPT-4o-mini<br>
            <strong style="color: #00f5ff;">Project by:</strong> Noah Butcher
        </p>
    </div>
</div>

<script>
    let autoRefreshInterval = null;
    
    function showTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(tabName).classList.add('active');
        event.target.classList.add('active');
    }
    
    function formatTimestamp(isoString) {
        const date = new Date(isoString);
        return date.toLocaleString();
    }
    
    function truncateText(text, maxLength = 300) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    async function loadConversations() {
        try {
            const response = await fetch(`${window.location.origin}/api/conversations?limit=50`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // Update stats
            document.getElementById('total-conversations').textContent = data.total;
            document.getElementById('recent-conversations').textContent = data.conversations.length;
            document.getElementById('max-storage').textContent = data.max_size;
            
            // Render conversations
            const listElement = document.getElementById('conversation-list');
            
            if (data.conversations.length === 0) {
                listElement.innerHTML = `
                    <div class="empty-state">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                        </svg>
                        <p>No conversations yet. Start using the AI Assistant in Unreal Engine!</p>
                    </div>
                `;
                return;
            }
            
            listElement.innerHTML = data.conversations.map(conv => `
                <div class="conversation-item">
                    <div class="conversation-header">
                        <span class="command-type">${conv.command_type}</span>
                        <span class="timestamp">${formatTimestamp(conv.timestamp)}</span>
                    </div>
                    <div class="user-input">
                        <strong>User:</strong> ${conv.user_input}
                    </div>
                    <div class="assistant-response">
                        <strong>Assistant:</strong> ${truncateText(conv.assistant_response)}
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Failed to load conversations:', error);
        }
    }
    
    // Auto-refresh toggle
    document.getElementById('auto-refresh').addEventListener('change', function(e) {
        if (e.target.checked) {
            autoRefreshInterval = setInterval(loadConversations, 5000);
        } else {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
            }
        }
    });
    
    // Initial load
    loadConversations();
    
    // Start auto-refresh
    autoRefreshInterval = setInterval(loadConversations, 5000);
    
    // ============================================================
    // SETTINGS FUNCTIONS
    // ============================================================
    
    async function loadSettings() {
        try {
            const response = await fetch(`${window.location.origin}/api/config`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const config = data.config;
            
            // Populate form fields
            document.getElementById('model').value = config.model || 'gpt-4o-mini';
            document.getElementById('response_style').value = config.response_style || 'descriptive';
            document.getElementById('temperature').value = config.temperature || 0.7;
            document.getElementById('temp-value').textContent = config.temperature || 0.7;
            document.getElementById('max_context_turns').value = config.max_context_turns || 6;
            document.getElementById('turns-value').textContent = config.max_context_turns || 6;
            document.getElementById('timeout').value = config.timeout || 25;
            document.getElementById('timeout-value').textContent = config.timeout || 25;
            
            console.log('Settings loaded:', config);
        } catch (error) {
            console.error('Failed to load settings:', error);
            showStatus('Failed to load settings', 'error');
        }
    }
    
    async function saveSettings() {
        const statusEl = document.getElementById('save-status');
        
        try {
            const settings = {
                model: document.getElementById('model').value,
                response_style: document.getElementById('response_style').value,
                temperature: parseFloat(document.getElementById('temperature').value),
                max_context_turns: parseInt(document.getElementById('max_context_turns').value),
                timeout: parseInt(document.getElementById('timeout').value)
            };
            
            const response = await fetch(`${window.location.origin}/api/config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                showStatus('✅ Settings saved successfully!', 'success');
            } else {
                showStatus('❌ Failed to save settings', 'error');
            }
        } catch (error) {
            console.error('Failed to save settings:', error);
            showStatus('❌ Error: ' + error.message, 'error');
        }
    }
    
    async function resetSettings() {
        if (!confirm('Reset all settings to defaults?')) return;
        
        try {
            const response = await fetch(`${window.location.origin}/api/config`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const defaults = data.defaults;
            
            // Reset to defaults
            const settings = {
                model: defaults.model,
                response_style: defaults.response_style,
                temperature: defaults.temperature,
                max_context_turns: defaults.max_context_turns,
                timeout: defaults.timeout
            };
            
            const saveResponse = await fetch(`${window.location.origin}/api/config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            
            if (saveResponse.ok) {
                loadSettings(); // Reload to update UI
                showStatus('✅ Settings reset to defaults', 'success');
            } else {
                showStatus('❌ Failed to reset settings', 'error');
            }
        } catch (error) {
            console.error('Failed to reset settings:', error);
            showStatus('❌ Error: ' + error.message, 'error');
        }
    }
    
    async function clearHistory() {
        if (!confirm('⚠️ Are you sure you want to delete ALL conversation history? This cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`${window.location.origin}/api/conversations`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                showStatus('✅ All conversation history cleared', 'success');
                // Refresh conversation list if on that tab
                if (document.getElementById('conversations').classList.contains('active')) {
                    fetchConversations();
                }
            } else {
                showStatus('❌ ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to clear history:', error);
            showStatus('❌ Error: ' + error.message, 'error');
        }
    }
    
    function showStatus(message, type) {
        const statusEl = document.getElementById('save-status');
        statusEl.textContent = message;
        statusEl.className = 'save-status ' + type;
        
        // Clear after 3 seconds
        setTimeout(() => {
            statusEl.textContent = '';
            statusEl.className = 'save-status';
        }, 3000);
    }
    
    // Load settings when opening settings tab
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            if (this.textContent.includes('Settings')) {
                loadSettings();
            }
        });
    });
</script>
</body>
</html>
"""
