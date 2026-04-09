import os
import requests
from .vector_store import update_dataset as update_vector_dataset
from basketball_reference_scraper.seasons import get_schedule
import pandas as pd
import json

# list of NBA teams used to fetch schedules/games from basketball reference scraper
NBA_TEAMS = [
    "ATL","BOS","BRK","CHO","CHI","CLE","DAL","DEN","DET","GSW",
    "HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NOP","NYK",
    "OKC","ORL","PHI","PHO","POR","SAC","SAS","TOR","UTA","WAS"
]

DATASET_FOLDER = os.path.join(os.path.dirname(__file__), "../../dataset")

def get_latest_json_file():
    """Return the path to the latest JSON file in the dataset folder."""
    files = [f for f in os.listdir(DATASET_FOLDER) if f.endswith(".json")]
    if not files:
        return None
    else:
        print("FOUND THE FILES")
    files.sort(
        key=lambda x: os.path.getmtime(os.path.join(DATASET_FOLDER, x)),
        reverse=True
    )
    print("LATEST FILE: ", files[0])
    return os.path.join(DATASET_FOLDER, files[0])

def update_dataset_from_json():
    """Load latest JSON dataset and update vector store."""
    latest_file = get_latest_json_file()
    if not latest_file:
        print("No JSON files found in dataset folder.")
        return

    print(f"Updating dataset from: {latest_file}")

    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert to DataFrame for preprocessing
        if isinstance(data, dict) and "events" in data:
            df = pd.DataFrame(data["events"])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            raise ValueError("JSON data format not recognized")

        # Ensure all required columns exist
        required_columns = ["DATE", "TEAM", "OPPONENT", "HOME/AWAY", "PTS", "OPP_PTS"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = None  # fill missing columns with None

        preprocessed_data = preprocess_data(df)
        update_vector_dataset(preprocessed_data)
        print("Dataset updated successfully from JSON file.")

    except Exception as e:
        print(f"Error loading JSON dataset: {e}")

def fetch_latest_data(season):
    """
    Fetches schedule/results for all NBA teams for a given season.
    Returns a single combined DataFrame with duplicates removed.
    """
    all_games = []

    for team in NBA_TEAMS:
        try:
            df = get_schedule(season, playoffs=False)
            print(f"Fetched {team} {season}")
        except Exception as e:
            print(f"Error fetching {team}: {e}")

    if not all_games:
        return None

    combined = pd.concat(all_games, ignore_index=True)

    # Remove duplicates - this step necessary because each game 
    # appears twice (once from each involved team's schedule)
    combined = combined.drop_duplicates(subset=["DATE", "OPPONENT", "PTS", "OPP_PTS"])

    return combined

def preprocess_data(data):
    preprocessed_data = []

    for _, row in data.iterrows():
        date = row["DATE"]
        team = row["TEAM"]
        opponent = row["OPPONENT"]
        home_away = row["HOME/AWAY"]
        team_score = row["PTS"]
        opp_score = row["OPP_PTS"]

        # Determine home/away teams
        if home_away == "HOME":
            home_team = team
            away_team = opponent
        else:
            home_team = opponent
            away_team = team

        content = (
            f"{home_team} vs {away_team} - {date}\n"
            f"Location: {'Home' if home_away == 'HOME' else 'Away'}\n"
            f"Score: {team_score} - {opp_score}"
        )

        document = {
            "content": content,
            "metadata": {
                "source": "BasketballReference",
                "date": str(date),
                "home_team": home_team,
                "away_team": away_team,
                "team_score": team_score,
                "opponent_score": opp_score,
            }
        }

        preprocessed_data.append(document)

    return preprocessed_data

def update_dataset(season):
    #latest_data = fetch_latest_data(season)
    a = get_latest_json_file()
    if a is not None: 
        update_dataset_from_json()
        print(f'Dataset updated successfully from JSON file for season {season}.')

    latest_data = None

    if latest_data is not None:
        preprocessed_data = preprocess_data(latest_data)
        update_vector_dataset(preprocessed_data)
        print(f'Dataset updated successfully for all NBA teams from season {season}.')
    else:
        print(f'Failed to update dataset for all NBA teams from season {season}.')

if __name__ == '__main__':
    # Example usage: Update dataset for 2024 season
    update_dataset(2020)