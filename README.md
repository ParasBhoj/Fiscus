# Fiscus — AI-Powered Regulatory Intelligence

> Real-time AI-powered monitoring, extraction, and semantic search across Indian financial regulatory updates from RBI and SEBI.

## Problem Statement

Financial institutions, compliance officers, and fintech companies must manually track hundreds of regulatory circulars published by RBI and SEBI daily. Missing a critical update can result in penalties, license revocations, or non-compliance. There is no unified, intelligent system that monitors, extracts, classifies, and enables natural-language search across these regulatory feeds.

## Our Solution

Fiscus is an end-to-end AI pipeline that:

- 📡 **Monitors** official RBI and SEBI RSS feeds in real-time
- 🕷️ **Scrapes** full circular text using headless browser automation
- 🧠 **Extracts** structured data via Gemini LLM — summary, regulatory impact (High/Medium/Low), affected entities
- 🔢 **Embeds** full documents as 3072-dimensional vectors for semantic search
- 🔍 **Enables** natural-language queries (e.g., *"any new rules for farmers?"* returns relevant circulars even when exact keywords don't match)
- 📱 **Serves** a responsive web dashboard and native mobile app

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| RSS Ingestion | `feedparser` | Monitors official RBI & SEBI XML feeds |
| Web Scraping | `Playwright` + `Trafilatura` | Headless browser for full-text extraction |
| AI Extraction | `Gemini 2.5 Flash` | Structured JSON extraction — summary, impact, entities |
| Semantic Embeddings | `Gemini Embedding v2` | 3072-dim vectors for meaning-based search |
| Vector Search | `NumPy` | Cosine similarity ranking |
| Database | `SQLite` | Zero-config storage with BLOB support for embeddings |
| API Server | `FastAPI` + `Uvicorn` | REST API with semantic search endpoint |
| Web Frontend | `HTML/CSS/JS` | Mobile-first dark theme UI with 3 theme modes |
| Mobile App | `React Native` + `Expo Router` | Native Android/iOS app |
| Language | `Python 3.14`, `TypeScript` | |

## Architecture

```
RSS Feeds (RBI + SEBI)
        │
        ▼
   RSS Monitor ──── feedparser: normalize, sort, deduplicate
        │
        ▼
  Playwright Scraper ──── Full text extraction from JS-heavy govt sites
        │
        ▼
  Gemini LLM Extractor ──── Summary + Impact Level + Affected Entities
        │
        ▼
  Gemini Embedder ──── 3072-dimensional semantic vectors
        │
        ▼
   SQLite Database ──── Structured data + embedding BLOBs
        │
        ▼
   FastAPI REST API
      ├── /api/updates ──── Chronological feed
      └── /api/search?q= ──── Semantic search
        │
   ┌────┴────┐
   ▼         ▼
Web App   Mobile App
```

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ (for mobile app)
- [Gemini API Key](https://aistudio.google.com/apikey)

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/fiscus.git
cd fiscus
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run the Scraping Daemon
```bash
python main.py --daemon --limit 5
```

### 4. Start the API + Web Dashboard
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000` in your browser.

### 5. Mobile App (Optional)
```bash
cd regwatch-mobile
npm install
npx expo start --lan
```
Scan the QR code with Expo Go on your phone.

## Project Structure

```
fiscus/
├── main.py              # Orchestrator daemon
├── rss_monitor.py       # RSS feed polling
├── scraper.py           # Playwright + Trafilatura scraper
├── extractor.py         # Gemini LLM structured extraction
├── embedder.py          # Gemini embedding + cosine similarity
├── db_connector.py      # SQLite database interface
├── api.py               # FastAPI REST endpoints
├── config.py            # Configuration & env vars
├── search_cli.py        # CLI semantic search tool
├── frontend/
│   ├── index.html       # Web dashboard
│   └── style.css        # Light/Dark/Midnight themes
├── regwatch-mobile/     # Expo Router mobile app
│   └── src/
│       ├── app/         # File-based routes
│       ├── components/  # React Native components
│       └── constants/   # API client & theme
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Team

<!-- Add your names here -->

---

*Built for [Hackathon Name] 2026*
