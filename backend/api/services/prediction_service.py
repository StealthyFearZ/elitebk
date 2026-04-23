import base64
import io
import json
import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .dataset_manager import get_latest_json_file

load_dotenv()

NBA_TEAMS: List[str] = [
    "Atlanta Hawks",
    "Boston Celtics",
    "Brooklyn Nets",
    "Charlotte Hornets",
    "Chicago Bulls",
    "Cleveland Cavaliers",
    "Dallas Mavericks",
    "Denver Nuggets",
    "Detroit Pistons",
    "Golden State Warriors",
    "Houston Rockets",
    "Indiana Pacers",
    "Los Angeles Clippers",
    "Los Angeles Lakers",
    "Memphis Grizzlies",
    "Miami Heat",
    "Milwaukee Bucks",
    "Minnesota Timberwolves",
    "New Orleans Pelicans",
    "New York Knicks",
    "Oklahoma City Thunder",
    "Orlando Magic",
    "Philadelphia 76ers",
    "Phoenix Suns",
    "Portland Trail Blazers",
    "Sacramento Kings",
    "San Antonio Spurs",
    "Toronto Raptors",
    "Utah Jazz",
    "Washington Wizards",
]

TEAM_ALIASES: Dict[str, str] = {
    # Common short names
    "warriors": "Golden State Warriors",
    "lakers": "Los Angeles Lakers",
    "clippers": "Los Angeles Clippers",
    "celtics": "Boston Celtics",
    "knicks": "New York Knicks",
    "nets": "Brooklyn Nets",
    "sixers": "Philadelphia 76ers",
    "76ers": "Philadelphia 76ers",
    "thunder": "Oklahoma City Thunder",
    "suns": "Phoenix Suns",
    "heat": "Miami Heat",
    "bucks": "Milwaukee Bucks",
    "bulls": "Chicago Bulls",
    "cavs": "Cleveland Cavaliers",
    "cavaliers": "Cleveland Cavaliers",
    "mavs": "Dallas Mavericks",
    "mavericks": "Dallas Mavericks",
    "spurs": "San Antonio Spurs",
    "raptors": "Toronto Raptors",
    "jazz": "Utah Jazz",
    "kings": "Sacramento Kings",
    "pelicans": "New Orleans Pelicans",
    "wolves": "Minnesota Timberwolves",
    "timberwolves": "Minnesota Timberwolves",
    "grizzlies": "Memphis Grizzlies",
    "magic": "Orlando Magic",
    "pacers": "Indiana Pacers",
    "pistons": "Detroit Pistons",
    "rockets": "Houston Rockets",
    "wizards": "Washington Wizards",
    "hornets": "Charlotte Hornets",
    "hawks": "Atlanta Hawks",
    "nuggets": "Denver Nuggets",
    # A few common city-only mentions (safe ones)
    "denver": "Denver Nuggets",
    "boston": "Boston Celtics",
    "miami": "Miami Heat",
    "phoenix": "Phoenix Suns",
    "dallas": "Dallas Mavericks",
    "milwaukee": "Milwaukee Bucks",
    "cleveland": "Cleveland Cavaliers",
    "chicago": "Chicago Bulls",
    "brooklyn": "Brooklyn Nets",
    "orlando": "Orlando Magic",
    "memphis": "Memphis Grizzlies",
    "houston": "Houston Rockets",
    "indiana": "Indiana Pacers",
    "oklahoma city": "Oklahoma City Thunder",
    "new york": "New York Knicks",
    "sacramento": "Sacramento Kings",
    "san antonio": "San Antonio Spurs",
    "toronto": "Toronto Raptors",
    "utah": "Utah Jazz",
    "washington": "Washington Wizards",
    "atlanta": "Atlanta Hawks",
    "detroit": "Detroit Pistons",
    "portland": "Portland Trail Blazers",
    "minnesota": "Minnesota Timberwolves",
    "new orleans": "New Orleans Pelicans",
}


def _get_llm():
    chat_model = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.1-flash-lite-preview")
    return ChatGoogleGenerativeAI(
        model=chat_model,
        temperature=0.2,
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )


def encode_xlsx(xlsx_bytes: bytes) -> str:
    return base64.b64encode(xlsx_bytes).decode("utf-8")


def build_xlsx_bytes(rows: List[Dict[str, Any]]) -> bytes:
    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Predictions")
    return buffer.getvalue()


def _extract_team_candidates_from_json(data: Any) -> List[str]:
    # Tries to pull team names out of many possible JSON shapes:
    # - {"events": [{"home_team": "...", "away_team": "..."}]}
    # - [{"strHomeTeam": "...", "strAwayTeam": "..."}]
    teams: set[str] = set()

    def consider_value(k: str, v: Any):
        if not isinstance(v, str):
            return
        lk = k.lower()
        if "team" in lk:
            val = v.strip()
            if val and len(val) >= 3:
                teams.add(val)

    def walk(obj: Any):
        if isinstance(obj, dict):
            for k, v in obj.items():
                consider_value(str(k), v)
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    return sorted(teams, key=len, reverse=True)


def get_known_teams() -> List[str]:
    path = get_latest_json_file()
    if not path or not os.path.exists(path):
        return NBA_TEAMS[:]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    extracted = _extract_team_candidates_from_json(data)

    # Filter extracted values down to known NBA teams only (prevents arenas/other strings).
    extracted_set = set(extracted)
    filtered = [t for t in NBA_TEAMS if t in extracted_set]
    return filtered if filtered else NBA_TEAMS[:]


def detect_teams_in_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Very simple deterministic detector:
    - Pull team candidates from the latest dataset JSON
    - Choose the longest team name that appears as a substring in the text
    - Choose a second distinct team (if present) as opponent
    """
    if not text:
        return None, None
    teams = get_known_teams()
    if not teams:
        return None, None

    t = text.lower()
    found: List[str] = []

    # 1) Exact full team-name matches
    for team in teams:
        if team.lower() in t:
            found.append(team)

    # 2) Alias matches (only map to canonical NBA team names)
    for alias, canonical in TEAM_ALIASES.items():
        if alias.lower() in t and canonical in teams:
            found.append(canonical)

    # Deduplicate while preserving length ordering
    unique: List[str] = []
    for team in found:
        if team not in unique:
            unique.append(team)

    detected = unique[0] if unique else None
    opponent = unique[1] if len(unique) > 1 else None
    return detected, opponent


PREDICTION_PROMPT = """You are an NBA analytics assistant for EliteBK.
Given a team (and optionally an opponent), generate a predicted stat line table for the likely starting five.

IMPORTANT RULES:
- Return ONLY valid JSON with exactly this shape:
{
  "rows": [
    {
      "player": "Full Name",
      "position": "PG/SG/SF/PF/C (best guess)",
      "min": 0,
      "pts": 0,
      "reb": 0,
      "ast": 0,
      "stl": 0,
      "blk": 0,
      "tov": 0,
      "fg_pct": 0,
      "tp_pct": 0,
      "ft_pct": 0
    }
  ],
  "notes": "1-2 short sentences describing assumptions."
}
- rows must contain EXACTLY 5 entries.
- Use numbers (not strings) for numeric fields.
- Keep percentages as 0-100 numbers (e.g. 47.2).
- If opponent is missing, still produce a reasonable prediction.

TEAM: {team}
OPPONENT: {opponent}
QUESTION CONTEXT: {question}
"""


def generate_predicted_rows(team: str, opponent: Optional[str], question: str) -> Dict[str, Any]:
    prompt_template = ChatPromptTemplate.from_template(PREDICTION_PROMPT)
    chain = prompt_template | _get_llm() | StrOutputParser()
    raw = chain.invoke(
        {
            "team": team,
            "opponent": opponent or "",
            "question": question or "",
        }
    )

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    data = json.loads(cleaned)
    rows = data.get("rows", [])
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("Prediction model did not return exactly 5 rows.")

    # Minimal normalization so Excel creation and UI don't crash.
    normalized: List[Dict[str, Any]] = []
    for r in rows:
        normalized.append(
            {
                "player": r.get("player", ""),
                "position": r.get("position", ""),
                "min": r.get("min", 0),
                "pts": r.get("pts", 0),
                "reb": r.get("reb", 0),
                "ast": r.get("ast", 0),
                "stl": r.get("stl", 0),
                "blk": r.get("blk", 0),
                "tov": r.get("tov", 0),
                "fg_pct": r.get("fg_pct", 0),
                "tp_pct": r.get("tp_pct", 0),
                "ft_pct": r.get("ft_pct", 0),
            }
        )

    return {"rows": normalized, "notes": data.get("notes", "")}

