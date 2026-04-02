# Project 3

RAG chat web app with own documents, organized reports, and data sheets with DRF on the backend and a React frontend.

## Setup
INSTALL NODE and NPM IF NECESSARY

1. cd into /backend and `pip install -r requirements.txt`
Any time you add a dependency, add the library name to that file.

2. cd back and then into /frontend and `npm install`

3. Get .env keys from someone or something

## Running the Dev Servers (Windows)
2 separate terminal windows to run the app locally.
**Terminal 1 (Backend):**
```powershell
cd backend
python manage.py runserver
```
**Terminal 2 (Frontend):**
```powershell
cd frontend
npm run dev
```

## Tech
- Frontend (/frontend): TypeScript, React
- Backend (/backend): Django Rest Framework 
- RAG (also /backend): LangChain and Supabase (with the psycog2-binary library so we can still use Django models.py)

## !! Need to decide AI providers we want to use
We'll likely do multiple different AI providers cause of free tier limitations. Gemini and/or HF Inference looking like frontrunners right now, but maybe Groq.
Also, we'll prolly use Tailwind, but we don't have to.

## Architecture (had some help creating this diagram)
```
rag-project/
├── backend/                # Django RF Project (really similar to normal Django)
│   ├── core/               # Project settings
│   ├── api/                # Main logic (RAG, Ingestion, Exports)
│   ├── manage.py
│   ├── requirements.txt
│   └── .env                # API Keys (e.g. Gemini, Supabase)
├── frontend/               # React + Vite Project
│   ├── src/
│   │   ├── components/     # UI Elements (Chat, Sidebar)
│   │   ├── hooks/          # API fetching logic
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Methodology
Definitely use AI here as a peer throughout development cause the repo is looking quite complex right now. Especially use for frontend or UI, or if you need help with React / TypeScript or DRF.
It was going to be this complex regardless unfortunately.