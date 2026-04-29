// AndroMate Neural Interface Engine
const chat = document.getElementById('chat');
const quickActions = document.getElementById('quickActions');
const contactsPanel = document.getElementById('contactsPanel');
const commandInput = document.getElementById('command');
const sendBtn = document.getElementById('sendBtn');
const batterySpan = document.getElementById('batteryValue');
const wifiSpan = document.getElementById('wifiValue');
const memorySpan = document.getElementById('memoryValue');
const storageSpan = document.getElementById('storageValue');
const networkSpan = document.getElementById('networkValue');
const themeIcon = document.getElementById('themeIcon');
let isTyping = false;
let messageHistory = [];
let autoScroll = true;
let saveHistory = true;
let enterKeyEnabled = true;
let isDarkTheme = true;
let quickActionsData = [];
let contactsData = [];

// Initialize Workspace
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadChatHistory();
    applyTheme();
    updateStatus();
    loadQuickActions();
    loadContacts();
    loadProvider();
    setInterval(updateStatus, 30000);
});

// Settings Management
function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('andromate_settings') || '{}');
    autoScroll = settings.autoScroll !== false;
    saveHistory = settings.saveHistory !== false;
    enterKeyEnabled = settings.enterKey !== false;
    isDarkTheme = settings.darkTheme !== false;

    if (document.getElementById('lightThemeToggle')) document.getElementById('lightThemeToggle').checked = !isDarkTheme;
    if (document.getElementById('autoScrollToggle')) document.getElementById('autoScrollToggle').checked = autoScroll;
    if (document.getElementById('saveHistoryToggle')) document.getElementById('saveHistoryToggle').checked = saveHistory;
    if (document.getElementById('enterKeyToggle')) document.getElementById('enterKeyToggle').checked = enterKeyEnabled;
}

function saveSettings() {
    const autoScrollToggle = document.getElementById('autoScrollToggle');
    const saveHistoryToggle = document.getElementById('saveHistoryToggle');
    const enterKeyToggle = document.getElementById('enterKeyToggle');

    if (autoScrollToggle) autoScroll = autoScrollToggle.checked;
    if (saveHistoryToggle) saveHistory = saveHistoryToggle.checked;
    if (enterKeyToggle) enterKeyEnabled = enterKeyToggle.checked;

    localStorage.setItem('andromate_settings', JSON.stringify({
        autoScroll,
        saveHistory,
        enterKey: enterKeyEnabled,
        darkTheme: isDarkTheme
    }));

    showToast('Settings saved', 'success');
}

// Aesthetic Toggles
function toggleTheme() {
    isDarkTheme = !isDarkTheme;
    updateThemeIcons();
    document.body.classList.toggle('light-theme', !isDarkTheme);
    saveSettings();
}

function applyTheme() {
    updateThemeIcons();
    document.body.classList.toggle('light-theme', !isDarkTheme);
}

function updateThemeIcons() {
    const iconClass = isDarkTheme ? 'fas fa-moon' : 'fas fa-sun';
    const icons = [themeIcon, document.getElementById('themeIconMobile')].filter(Boolean);
    icons.forEach(icon => icon.className = iconClass + ' text-xs');
}

// Sidebar Drawer (Mobile)
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const isOpen = !sidebar.classList.contains('-translate-x-full');

    if (isOpen) {
        sidebar.classList.add('-translate-x-full');
        overlay.classList.add('hidden');
        overlay.classList.remove('opacity-100');
    } else {
        sidebar.classList.remove('-translate-x-full');
        overlay.classList.remove('hidden');
        setTimeout(() => overlay.classList.add('opacity-100'), 10);
    }
}

// Logic Overlays
function toggleSearch() {
    const searchBar = document.getElementById('searchBar');
    const isHidden = searchBar.classList.contains('hidden');

    if (isHidden) {
        searchBar.classList.remove('hidden');
        document.getElementById('searchInput').focus();
    } else {
        searchBar.classList.add('hidden');
    }
}

function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.classList.toggle('translate-x-full');
}

function searchMessages() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const messages = chat.querySelectorAll('.message-row');

    messages.forEach(msg => {
        const text = msg.querySelector('.bubble').textContent.toLowerCase();
        msg.style.display = (query === '' || text.includes(query)) ? 'flex' : 'none';
    });
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-circle-check' : 'fa-circle-info'}"></i> ${message}`;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// Neural Stream Management
function addMessage(sender, text, isError = false, saveToHistory = true, thought = "") {
    const row = document.createElement('div');
    row.className = `message-row ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = `avatar ${sender}`;
    // avatar.innerHTML = sender === 'assistant' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';

    const bubble = document.createElement('div');
    bubble.className = `bubble bubble-${sender}${isError ? ' border-red-500/50 bg-red-500/10' : ''}`;

    if (thought && sender === 'assistant') {
        const thoughtWrapper = document.createElement('div');
        thoughtWrapper.className = 'thought-wrapper';

        const thoughtToggle = document.createElement('button');
        thoughtToggle.className = 'thought-toggle';
        thoughtToggle.innerHTML = '<i class="fas fa-brain"></i> Reasoning Trace';
        thoughtToggle.onclick = () => {
            const content = thoughtWrapper.querySelector('.thought-content');
            content.classList.toggle('visible');
            thoughtToggle.classList.toggle('active');
        };

        const thoughtContent = document.createElement('div');
        thoughtContent.className = 'thought-content';
        thoughtContent.innerHTML = thought;

        thoughtWrapper.appendChild(thoughtToggle);
        thoughtWrapper.appendChild(thoughtContent);
        bubble.appendChild(thoughtWrapper);
    }

    const content = parseMarkdown(text);
    bubble.appendChild(content);

    const time = document.createElement('span');
    time.className = 'timestamp';
    time.innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    bubble.appendChild(time);

    if (sender === 'assistant') {
        row.appendChild(avatar);
        row.appendChild(bubble);
    } else {
        row.appendChild(bubble);
        row.appendChild(avatar);
    }

    chat.appendChild(row);
    if (autoScroll) chat.scrollTop = chat.scrollHeight;

    if (saveHistory && saveToHistory) {
        messageHistory.push({ sender, text, isError, timestamp: Date.now() });
        localStorage.setItem('andromate_history', JSON.stringify(messageHistory));
    }

    return row;
}

function parseMarkdown(text) {
    const container = document.createElement('div');
    container.className = 'markdown-content';
    const parts = text.split(/(```[\s\S]*?```)/g);
    parts.forEach(part => {
        if (part.startsWith('```') && part.endsWith('```')) {
            container.appendChild(createCodeBlock(part));
        } else {
            const textBlock = parseInlineMarkdown(part);
            if (textBlock.childNodes.length > 0) container.appendChild(textBlock);
        }
    });
    return container;
}

function createCodeBlock(codeText) {
    const wrapper = document.createElement('div');
    wrapper.className = 'code-block-wrapper';
    const match = codeText.match(/^```(\w*)\n([\s\S]*?)```$/);
    const language = match && match[1] ? match[1] : 'code';
    const code = match && match[2] ? match[2].trim() : codeText.replace(/^```|```$/g, '').trim();

    const header = document.createElement('div');
    header.className = 'code-block-header';
    header.innerHTML = `<span class="code-language">${language}</span>`;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-code-btn';
    copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
    copyBtn.onclick = () => {
        navigator.clipboard.writeText(code);
        const originalText = copyBtn.innerText;
        copyBtn.innerText = 'Copied!';
        setTimeout(() => copyBtn.innerText = originalText, 2000);
    };
    header.appendChild(copyBtn);

    const pre = document.createElement('pre');
    pre.innerHTML = `<code>${code}</code>`;
    wrapper.appendChild(header);
    wrapper.appendChild(pre);
    return wrapper;
}

function parseInlineMarkdown(text) {
    const container = document.createElement('div');
    if (!text.trim()) return container;
    let html = text
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
        .replace(/\n/g, '<br>');
    container.innerHTML = html;
    return container;
}

function addImageMessage(imageUrl) {
    const row = document.createElement('div');
    row.className = 'message-row assistant';
    const avatar = document.createElement('div');
    avatar.className = 'avatar assistant';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    const bubble = document.createElement('div');
    bubble.className = 'bubble bubble-assistant';
    const img = document.createElement('img');
    img.src = imageUrl;
    img.className = 'w-full rounded-2xl mb-2';
    bubble.appendChild(img);
    const time = document.createElement('span');
    time.className = 'timestamp';
    time.innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    bubble.appendChild(time);
    row.appendChild(avatar);
    row.appendChild(bubble);
    chat.appendChild(row);
    if (autoScroll) chat.scrollTop = chat.scrollHeight;
}

function showTyping() {
    if (isTyping) return;
    isTyping = true;
    const row = document.createElement('div');
    row.className = 'message-row assistant';
    row.id = 'typingIndicator';
    const avatar = document.createElement('div');
    avatar.className = 'avatar assistant';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    row.appendChild(avatar);
    row.appendChild(indicator);
    chat.appendChild(row);
    if (autoScroll) chat.scrollTop = chat.scrollHeight;
}

function hideTyping() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
    isTyping = false;
}

async function clearChat() {
    if (confirm('Clear all conversation history?')) {
        try {
            // Clear backend memory
            const response = await fetch('/api/clear-history', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                // Clear local UI and storage
                chat.innerHTML = '';
                messageHistory = [];
                localStorage.removeItem('andromate_history');
                addMessage('assistant', 'Memory wiped. Ready for new instructions.', false, false);
                showToast('History cleared', 'success');
            } else {
                throw new Error(data.error || 'Server failed to clear history');
            }
        } catch (e) {
            console.error('Clear History Error:', e);
            showToast('Failed to clear history: ' + e.message, 'error');
        }
    }
}

function loadChatHistory() {
    if (!saveHistory) return;
    const saved = localStorage.getItem('andromate_history');
    if (saved) {
        try {
            messageHistory = JSON.parse(saved);
            messageHistory.forEach(msg => { addMessage(msg.sender, msg.text, msg.isError, false); });
        } catch (e) { }
    }
    if (messageHistory.length === 0) {
        addMessage('assistant', 'Neural link established. How can I assist you today?', false, false);
    }
}

async function sendCommand() {
    const cmd = commandInput.value.trim();
    if (!cmd) return;
    addMessage('user', cmd);
    commandInput.value = '';
    commandInput.disabled = true;
    sendBtn.disabled = true;
    showTyping();
    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd })
        });
        const data = await response.json();
        hideTyping();
        if (data.error) {
            addMessage('assistant', `Error: ${data.error}`, true);
        } else {
            if (data.image) addImageMessage(data.image);
            const output = data.output ? data.output.trim() : '';
            if (output) addMessage('assistant', output, false, true, data.thought);
            else if (!data.image) addMessage('assistant', 'Action complete.', false, true, data.thought);
        }
    } catch (e) {
        hideTyping();
        addMessage('assistant', `Connection failure: ${e.message}`, true);
    } finally {
        commandInput.disabled = false;
        sendBtn.disabled = false;
        commandInput.focus();
    }
}

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        if (data.battery !== undefined && data.battery !== 'unknown') batterySpan.innerHTML = `${data.battery}%`;
        if (data.wifi && data.wifi !== 'unknown') wifiSpan.innerText = data.wifi;
    } catch (e) { }
}

sendBtn.addEventListener('click', sendCommand);
commandInput.addEventListener('keypress', (e) => { if (e.key === 'Enter' && enterKeyEnabled) sendCommand(); });

function exportChat() {
    const data = { exportDate: new Date().toISOString(), messages: messageHistory };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `andromate-chat-${new Date().getTime()}.json`;
    a.click();
    showToast('History exported.', 'success');
}

function importChat() {
    document.getElementById('importFile').click();
}

function handleImport(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);
            if (data.messages) {
                chat.innerHTML = '';
                messageHistory = [];
                data.messages.forEach(msg => { addMessage(msg.sender, msg.text, msg.isError, true); });
                localStorage.setItem('andromate_history', JSON.stringify(messageHistory));
                showToast('History restored.', 'success');
            }
        } catch (err) { }
    };
    reader.readAsText(file);
    event.target.value = '';
}

// Tab Navigation
function switchTab(tab) {
    const navChat = document.getElementById('navChat');
    const navActions = document.getElementById('navActions');
    const navContacts = document.getElementById('navContacts');

    chat.classList.add('hidden');
    quickActions.classList.add('hidden');
    contactsPanel.classList.add('hidden');

    navChat.classList.remove('bg-primary/10', 'border-primary/20', 'text-primary');
    navChat.classList.add('text-slate-400', 'hover:text-white', 'hover:bg-white/5');
    navActions.classList.remove('bg-primary/10', 'border-primary/20', 'text-primary');
    navActions.classList.add('text-slate-400', 'hover:text-white', 'hover:bg-white/5');
    navContacts.classList.remove('bg-primary/10', 'border-primary/20', 'text-primary');
    navContacts.classList.add('text-slate-400', 'hover:text-white', 'hover:bg-white/5');

    if (tab === 'chat') {
        chat.classList.remove('hidden');
        navChat.classList.add('bg-primary/10', 'border-primary/20', 'text-primary');
        navChat.classList.remove('text-slate-400', 'hover:text-white', 'hover:bg-white/5');
    } else if (tab === 'actions') {
        quickActions.classList.remove('hidden');
        navActions.classList.add('bg-primary/10', 'border-primary/20', 'text-primary');
        navActions.classList.remove('text-slate-400', 'hover:text-white', 'hover:bg-white/5');
    } else if (tab === 'contacts') {
        contactsPanel.classList.remove('hidden');
        navContacts.classList.add('bg-primary/10', 'border-primary/20', 'text-primary');
        navContacts.classList.remove('text-slate-400', 'hover:text-white', 'hover:bg-white/5');
    }

    // Close sidebar on mobile
    if (window.innerWidth < 768) {
        toggleSidebar();
    }
}

// Quick Actions
async function loadQuickActions() {
    try {
        const response = await fetch('/api/quick-actions');
        quickActionsData = await response.json();
        renderQuickActions();
    } catch (e) { }
}

function renderQuickActions() {
    const container = quickActions.querySelector('.grid');
    container.innerHTML = quickActionsData.map(action => `
        <button onclick="executeQuickAction('${action.id}')"
            class="action-btn bg-dark-800/50 border border-white/5 rounded-2xl p-5 flex flex-col items-center gap-3 hover:bg-primary/10 hover:border-primary/30 transition-all group">
            <div class="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                <i class="fas ${action.icon} text-xl"></i>
            </div>
            <span class="text-xs font-bold text-slate-400 group-hover:text-white">${action.name}</span>
        </button>
    `).join('');
}

async function executeQuickAction(actionId) {
    const btn = event.currentTarget;
    btn.classList.add('opacity-50', 'pointer-events-none');

    try {
        const response = await fetch('/api/quick-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action_id: actionId })
        });
        const data = await response.json();

        switchTab('chat');
        if (data.error) {
            addMessage('assistant', `Error: ${data.error}`, true);
        } else {
            addMessage('user', `Action: ${actionId}`);
            addMessage('assistant', data.output || 'Action completed.', false, true, data.thought);
        }
    } catch (e) {
        addMessage('assistant', `Connection error: ${e.message}`, true);
    }

    btn.classList.remove('opacity-50', 'pointer-events-none');
}

// Contacts
async function loadContacts() {
    try {
        const response = await fetch('/api/contacts');
        contactsData = await response.json();
        renderContacts();
    } catch (e) { }
}

function renderContacts(filter = '') {
    const container = document.getElementById('contactsList');
    const filtered = contactsData.filter(c =>
        c.name.toLowerCase().includes(filter.toLowerCase())
    );

    if (filtered.length === 0) {
        container.innerHTML = '<div class="text-center text-slate-500 py-10">No contacts found</div>';
        return;
    }

    container.innerHTML = filtered.slice(0, 50).map(contact => `
        <div class="contact-item bg-dark-800/30 border border-white/5 rounded-2xl p-4 flex items-center justify-between hover:bg-white/5 transition-all">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-emerald-600 flex items-center justify-center text-white font-bold">
                    ${contact.name.charAt(0).toUpperCase()}
                </div>
                <div>
                    <div class="font-bold text-white text-sm">${contact.name}</div>
                    <div class="text-xs text-slate-500">${contact.number || 'No number'}</div>
                </div>
            </div>
            <div class="flex gap-2">
                <button onclick="contactAction('sms', '${contact.number}')" class="action-icon text-green-400 hover:text-green-300">
                    <i class="fas fa-message"></i>
                </button>
                <button onclick="contactAction('call', '${contact.number}')" class="action-icon text-blue-400 hover:text-blue-300">
                    <i class="fas fa-phone"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function filterContacts() {
    const query = document.getElementById('contactSearch').value;
    renderContacts(query);
}

async function contactAction(type, number) {
    const cmd = type === 'sms' ? `send sms to ${number}` : `call ${number}`;
    addMessage('user', `${type === 'sms' ? 'SMS' : 'Call'} to ${number}`);
    switchTab('chat');

    const response = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd })
    });
    const data = await response.json();
    addMessage('assistant', data.output || 'Action completed.', false, true, data.thought);
}

// Enhanced Status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        if (data.battery !== undefined && data.battery !== 'unknown') {
            batterySpan.innerHTML = `${data.battery}%`;
        }
        if (data.wifi && data.wifi !== 'unknown') wifiSpan.innerText = data.wifi;
        if (data.memory_used) memorySpan.innerText = `${data.memory_used} MB`;
        if (data.storage_used && data.storage_total) {
            storageSpan.innerText = `${data.storage_used} / ${data.storage_total}`;
        }
        if (data.network_type && data.network_type !== 'Unknown') {
            networkSpan.innerText = data.network_type;
        }
    } catch (e) { }
}

// Provider Management
async function loadProvider() {
    try {
        const response = await fetch('/api/provider');
        const data = await response.json();
        document.getElementById('providerSelect').value = data.provider;
    } catch (e) { }
}

async function changeProvider() {
    const provider = document.getElementById('providerSelect').value;
    try {
        const response = await fetch('/api/provider', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider })
        });
        const data = await response.json();
        if (data.success) {
            showToast(`Switched to ${provider}`, 'success');
        }
    } catch (e) {
        showToast('Failed to change provider', 'error');
    }
}
