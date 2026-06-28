# JACK — AI Fact Verification Agent

JACK is an AI-powered fact-checking web application. Enter any claim and the speaker's name, and JACK deploys multiple AI agents to research, verify, and report on the accuracy of the statement with cited sources.

---

## ✨ Features

- 🔍 **Automatic Search Query Generation** — Groq LLM crafts a precise verification query from your claim
- 🌐 **Neural Web Search** — Exa AI performs semantic search across the web for relevant sources
- 🤖 **Multi-Agent Analysis** — Three specialized agents answer:
  1. Was the claim actually made by the speaker?
  2. Did the event/action actually occur?
  3. What were the consequences?
- 📎 **Clickable Sources** — All references are rendered as inline hyperlinks
- 💬 **ChatGPT-style UI** — Full-screen, dark-themed interface built with Flask + Vanilla CSS

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| LLM | Groq (`llama-3.3-70b-versatile`) |
| Search | Exa AI (neural search) |
| Frontend | HTML, Vanilla CSS, JavaScript |
| Deployment | Vercel |

---

## 🚀 Getting Started (Local)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/jack.git
cd jack
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
EXA_API=your_exa_api_key_here
```

> Get your Groq API key at [console.groq.com](https://console.groq.com)  
> Get your Exa API key at [exa.ai](https://exa.ai)

### 4. Run the app
```bash
python app.py
```

Visit `http://localhost:5001` in your browser.

---

## ☁️ Deploy to Vercel

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Set environment variables on Vercel

In your Vercel project settings, add:
- `GROQ_API_KEY`
- `EXA_API`

### 3. Deploy
```bash
vercel --prod
```

That's it! Vercel picks up `vercel.json` automatically.

---

## 📁 Project Structure

```
jack/
├── app.py               # Flask app + AI agents
├── requirements.txt     # Python dependencies
├── vercel.json          # Vercel deployment config
├── .gitignore
├── templates/
│   └── index.html       # Main UI template
└── static/
    └── style.css        # Full-screen dark UI styles
```

---

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | API key for Groq LLM |
| `EXA_API` | API key for Exa neural search |

---

## 📄 License

MIT License — free to use, modify, and distribute.
