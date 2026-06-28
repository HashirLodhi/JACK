const API_BASE = '/api';

const form = document.getElementById('verify-form');
const verifyBtn = document.getElementById('verify-btn');
const btnText = verifyBtn.querySelector('.btn-text');
const btnLoader = verifyBtn.querySelector('.btn-loader');
const statusEl = document.getElementById('status');
const resultsEl = document.getElementById('results');
const resultsContent = document.getElementById('results-content');
const errorEl = document.getElementById('error');
const copyBtn = document.getElementById('copy-btn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const claim = document.getElementById('claim').value.trim();
    const speaker = document.getElementById('speaker').value.trim();
    
    if (!claim || !speaker) {
        showError('Please provide both claim and speaker name.');
        return;
    }
    
    setLoading(true);
    hideError();
    hideResults();
    showStatus();
    
    try {
        const response = await fetch(`${API_BASE}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ claim, speaker })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Verification failed');
        }
        
        showResults(data.result);
        
    } catch (err) {
        showError(err.message);
    } finally {
        setLoading(false);
        hideStatus();
    }
});

copyBtn.addEventListener('click', async () => {
    const text = resultsContent.textContent;
    try {
        await navigator.clipboard.writeText(text);
        copyBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyBtn.textContent = 'Copy Result';
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
    }
});

function setLoading(loading) {
    verifyBtn.disabled = loading;
    btnText.style.display = loading ? 'none' : 'inline';
    btnLoader.style.display = loading ? 'flex' : 'none';
}

function showStatus() {
    statusEl.style.display = 'block';
}

function hideStatus() {
    statusEl.style.display = 'none';
}

function showResults(result) {
    resultsContent.textContent = result;
    resultsEl.style.display = 'block';
    copyBtn.style.display = 'block';
}

function hideResults() {
    resultsEl.style.display = 'none';
    copyBtn.style.display = 'none';
}

function showError(message) {
    errorEl.textContent = message;
    errorEl.style.display = 'block';
}

function hideError() {
    errorEl.style.display = 'none';
}