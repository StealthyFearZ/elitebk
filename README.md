# Project 3

## Tech
Frontend: TypeScript, React 
Backend: Django Rest Framework /backend
RAG: LangChain and Supabase (with the psycog2-binary library so we can still use Django models.py)

## !! Need to decide AI providers we want to use
We'll likely do multiple different AI providers cause of free tier limitations. Groq and Gemini looking like frontrunners right now.

## Architecture (had some help creating this diagram)
rag-project/
├── backend/                # Django DRF Project
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

## Methodology
Definitely use AI here as a peer throughout development cause the repo is looking quite complex right now. Especially use for frontend or UI, or if you need help with React / TypeScript or DRF.