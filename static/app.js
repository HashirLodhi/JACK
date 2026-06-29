const API_BASE = '/api';

const factCheckForm = document.getElementById('verify-form');
const queryForm = document.getElementById('query-form');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
const tabs = document.querySelectorAll('.tab');
const tabPanels = document.querySelectorAll('.tab-panel');

function formatResult(text) {
    let html = text.replace(/^##\s*(.+)$/gm, '<strong>$1</strong>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    html = html.replace(/\n/g, '<br/>');
    return html;
}

function setLoading(form, loading) {
    const btn = form.querySelector('button.primary');
    if (btn) {
        btn.disabled = loading;
        btn.textContent = loading ? 'Working...' : (form.id === 'verify-form' ? 'Verify Claim' : 'Ask Question');
    }
}

function showStatus(message) {
    statusEl.textContent = message;
    statusEl.classList.remove('hidden');
}

function hideStatus() {
    statusEl.classList.add('hidden');
}

function showResult(html) {
    resultEl.innerHTML = html;
    resultEl.classList.remove('hidden');
}

function hideResult() {
    resultEl.classList.add('hidden');
    resultEl.innerHTML = '';
}

function switchTab(tabName) {
    tabs.forEach(tab => {
        const isActive = tab.dataset.tab === tabName;
        tab.classList.toggle('active', isActive);
        tab.setAttribute('aria-selected', isActive);
    });
    tabPanels.forEach(panel => {
        panel.classList.toggle('hidden', panel.id !== `${tabName}-panel`);
    });
    hideStatus();
    hideResult();
}

tabs.forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
});

factCheckForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const claim = document.getElementById('claim').value.trim();
    const speaker = document.getElementById('speaker').value.trim();
    
    if (!claim || !speaker) {
        showStatus('Please provide both claim and speaker name.');
        return;
    }
    
    setLoading(factCheckForm, true);
    hideResult();
    showStatus('🤖 Agents are handling your research — just sit tight!');
    
    try {
        const response = await fetch(`${API_BASE}/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim, speaker })
        });
        const data = await response.json();
        
        if (!response.ok) {
            showStatus('❌ ' + (data.error || 'An error occurred.'));
            return;
        }
        
        hideStatus();
        showResult(formatResult(data.result));
    } catch (err) {
        showStatus('❌ Network error – please try again.');
    } finally {
        setLoading(factCheckForm, false);
    }
});

queryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const question = document.getElementById('question').value.trim();
    
    if (!question) {
        showStatus('Please provide a question.');
        return;
    }
    
    setLoading(queryForm, true);
    hideResult();
    showStatus('🔍 Searching the web and generating answer...');
    
    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        const data = await response.json();
        
        if (!response.ok) {
            showStatus('❌ ' + (data.error || 'An error occurred.'));
            return;
        }
        
        hideStatus();
        showResult(formatResult(data.result));
    } catch (err) {
        showStatus('❌ Network error – please try again.');
    } finally {
        setLoading(queryForm, false);
    }
});