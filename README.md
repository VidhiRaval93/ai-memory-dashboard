# 🧠 AI Memory Dashboard

The **AI Memory Dashboard** is a Chrome extension + backend system that passively captures your interactions with **ChatGPT** and **Perplexity**, 
categorizes them (e.g. career, personal, education), and visualizes them in a clean, filterable UI — giving you a personal memory layer over your AI usage.

---

## 🚀 Features

- ✅ Real-time Q&A extraction from ChatGPT & Perplexity
- ✅ Chrome Extension auto-captures questions and answers
- ✅ Tag categorization (career, personal, education, misc)
- ✅ Filter by:
  - Source (ChatGPT / Perplexity)
  - Date
  - Tag type
- ✅ Timeline chart of daily AI usage
- ✅ Expandable cards to view full conversations
- ✅ Responsive and modern UI built with HTML + CSS Grid
- ✅ Backend powered by FastAPI, autostart via `launchd` or `pm2`

---

## 🧱 Project Structure
save-my-research-perplexity/
├── backend/
│ ├── summarizer.py # FastAPI backend
│ ├── conversations.json # Logged memory
├── extension/
│ ├── contentScript.js # Extracts data from webpages
│ ├── background.js # Handles persistent listeners
│ ├── manifest.json # Chrome extension config
├── dashboard.html # Main visual dashboard
├── logs/
│ └── fastapi.log # Runtime logs
├── venv/ # Python virtual environment
├── ai.memory.fastapi.plist # macOS launchd autostart config
└── README.md


---

## 🛠️ Installation

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/save-my-research-perplexity.git
cd save-my-research-perplexity
2. Set up Python environment
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
3. Start the FastAPI backend
bash
Copy
Edit
python -m uvicorn summarizer:app --host 0.0.0.0 --port 8001
You can now visit the dashboard at:
http://localhost:8001/dashboard

💡 Auto-Start on Boot (macOS)
To run the backend automatically on login:

bash
Copy
Edit
cp ai.memory.fastapi.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.memory.fastapi.plist
Or use pm2 (cross-platform):

bash
Copy
Edit
npm install -g pm2
pm2 start "uvicorn summarizer:app --host 0.0.0.0 --port 8001" --name ai-memory
pm2 save
🧩 Load Chrome Extension
Open chrome://extensions

Enable Developer mode

Click Load unpacked

Select the /extension/ folder

The extension will begin logging ChatGPT & Perplexity sessions

📊 Using the Dashboard
Timeline at the top shows usage by day

Filter by tag (career, personal, education, etc.)

Toggle between ChatGPT and Perplexity sources

Click on cards to expand and read full Q&A

🧪 Health Check
Test backend availability:

bash
Copy
Edit
curl http://localhost:8001/health
🧠 Future Improvements
Automatic tag classification using LLMs

Dark mode toggle

Search functionality across Q&A

Memory decay visualization

🧑‍💻 Author
Vidhi Raval

