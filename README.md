# ResuMind 📝

A modern, **free** Flask app that analyzes your resume against any job description using Groq's fast LLMs and shows a polished, dark-themed UI.

## ✨ What's new vs. the old version

| Old | New |
|-----|-----|
| Streamlit single-file UI | Flask + clean HTML/CSS/JS, dark gradient design |
| PDF only | **PDF, DOCX, and TXT** upload + paste-text option |
| 500MB sentence-transformers download | Lightweight **TF-IDF** ATS score (scikit-learn only) |
| Plain text report download | **Styled PDF report** with score, charts, sections |
| Basic Llama prompt | Structured JSON output with section breakdown |
| No error handling | Friendly errors, drag-drop upload, animated score |

Still **100% free** with a free Groq API key (no credit card).

---

## 🚀 Quick Start (Mac)

### 1. Requirements
- **Python 3.10 or newer**
- A free **Groq API key**: https://console.groq.com/keys

Check Python:
```bash
python3 --version
```
If missing/older: `brew install python@3.12`

### 2. Set up the project
```bash
cd ~/Downloads
unzip ResuMind.zip
cd ResuMind

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Add your API key
```bash
cp .env.example .env
```
Open `.env` and replace `your-groq-api-key-here` with your real Groq key. Easiest way:
```bash
echo "GROQ_API_KEY=PASTE_YOUR_KEY_HERE" > .env
```

### 4. Run
```bash
python run.py
```
Open **http://127.0.0.1:5050** in your browser.

Stop with `Ctrl+C`.

---

## 🧠 Features

- 📄 Upload **PDF / DOCX / TXT** resume — or paste text directly
- 🎯 Optional job description for targeted analysis
- ⚡ AI score (0–100) + section-by-section breakdown
- ✅ Strengths, ⚠️ weaknesses, 🔑 missing keywords, 💡 suggestions
- 📊 ATS similarity score (TF-IDF cosine)
- 🏷️ Visual matched / missing keyword chips
- ⬇️ Download a **professionally styled PDF report**
- 📱 Responsive, dark-mode UI with drag-drop upload

---

## 🛠️ Project Structure

```
resumind/
├── run.py                    # Entry point
├── requirements.txt
├── .env.example
├── README.md
└── app/
    ├── __init__.py           # Flask app factory
    ├── routes/main.py        # /  /api/analyze  /api/report
    ├── services/
    │   ├── extractor.py      # PDF / DOCX / TXT text extraction
    │   ├── ats.py            # TF-IDF + keyword matching
    │   ├── analyzer.py       # Groq LLM analysis
    │   └── report.py         # ReportLab PDF builder
    ├── templates/index.html
    └── static/
        ├── css/style.css
        └── js/app.js
```

---

## 🐛 Troubleshooting

- **`GROQ_API_KEY is not set`** — check `cat .env`, then **restart** `python run.py`.
- **Port 5050 busy** — change `port=5050` to `port=5060` in `run.py`.
- **`ModuleNotFoundError`** — run `source venv/bin/activate` first, then `pip install -r requirements.txt`.
- **Scanned PDF read fails** — the file is an image, not text. Use the **Paste text** tab instead.
- **Model deprecated error** — open `.env` and change `GROQ_MODEL` to `openai/gpt-oss-120b` or `llama-3.1-8b-instant`.

---

## 🔁 Switching the AI Model

Edit `.env`:
```
GROQ_MODEL=llama-3.3-70b-versatile     # default — best quality
# GROQ_MODEL=llama-3.1-8b-instant      # fastest
# GROQ_MODEL=openai/gpt-oss-120b       # OSS GPT-style on Groq
```

Restart the server after changing.

---

## 📜 License

MIT — original concept based on the Altoks-AI AI Resume Analyzer, rebuilt with a modern stack.
