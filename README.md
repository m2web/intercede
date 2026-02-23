# Intercede - Daily Intercessory Prayer

> *"I urge that supplications, prayers, intercessions, and thanksgivings*
> *be made for all people..." — 1 Timothy 2:1 (ESV)*

An AI-powered prayer companion that fetches the top 3 news headlines each day,
reasons over them theologically, and generates Reformed Christian intercessory
prayers complete with relevant ESV Scripture.

## Architecture

```text
intercede/
├── backend/              # Python FastAPI
│   ├── app.py            # API routes
│   ├── news_service.py   # Google News RSS -> top 3 headlines
│   ├── prayer_service.py # OpenAI -> Reformed prayers
│   └── requirements.txt
└── frontend/             # Vite (vanilla JS)
    ├── index.html
    └── src/
        ├── main.js
        ├── api.js
        ├── newsCard.js
        ├── prayerCard.js
        └── style.css
```

## Setup

### 1. Add your OpenAI key

```bash
cp .env.example .env
# Then edit .env and add your OPENAI_API_KEY
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

The API will be at `http://localhost:8000`.

- `GET /api/health` - health check
- `GET /api/prayers` - fetch headlines + generate prayers

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

## How it works

1. **News**: Google News Top Stories RSS is parsed for the top 3 US headlines
   (free, no API key required).
2. **Reasoning**: All 3 headlines are sent to `gpt-4o-mini` with a Reformed
   Christian system prompt that instructs the model to:
   - Begin each prayer with *"Lord, you ordain all things for your glory..."*
   - Reflect briefly on the headline's spiritual significance
   - Write a substantive intercessory petition for those affected
   - Include a relevant ESV Bible verse
   - Close with a doxological phrase
3. **Display**: The Vite frontend renders news + prayer cards side-by-side in a
   dark glassmorphism UI.
