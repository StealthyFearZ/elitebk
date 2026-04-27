import importlib
import os
import json
from .vector_store import update_dataset as update_vector_dataset

DATASET_FOLDER = os.path.join(os.path.dirname(__file__), "../../dataset")
DEFAULT_DATASET = os.path.join(DATASET_FOLDER, "demo_nba_2024.json")


def normalize_season(season):
    season_str = str(season)
    if season_str.isdigit() and len(season_str) == 4:
        return f"{int(season_str) - 1}-{season_str[-2:]}"
    if "-" not in season_str:
        raise ValueError("Season must be 'YYYY-YY' or a four-digit year")
    return season_str


def get_latest_json_file():
    # Returns most recent json file
    # Defaults to a Default Dataset if no dataset upload
    uploads = [f for f in os.listdir(DATASET_FOLDER) if f.startswith("upload_") and f.endswith(".json")]
    if uploads:
        uploads.sort(key=lambda x: os.path.getmtime(os.path.join(DATASET_FOLDER, x)), reverse=True)
        print("LATEST UPLOAD: ", uploads[0])
        return os.path.join(DATASET_FOLDER, uploads[0])

    if os.path.exists(DEFAULT_DATASET):
        print("No uploads found, using default dataset: demo_nba_2024.json")
        return DEFAULT_DATASET

    return None


def preprocess_data(records):
    # Turns the Docs into key-value pairs so that the AI can do its thing
    # Should work for any JSON Structure :)
    preprocessed = []
    for record in records:
        if not isinstance(record, dict):
            continue
        content = "\n".join(f"{k}: {v}" for k, v in record.items() if v is not None)
        document = {
            "content": content,
            "metadata": {str(k): str(v) for k, v in record.items() if v is not None},
        }
        preprocessed.append(document)
    return preprocessed


def update_dataset_from_json():
    """Load the latest JSON file and update the vector store."""
    latest_file = get_latest_json_file()
    if not latest_file:
        print("No JSON files found in dataset folder.")
        return

    print(f"Updating dataset from: {latest_file}")

    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize tolist of records
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ("events", "data", "records", "items", "results", "player_stats"):
            if key in data and isinstance(data[key], list):
                records = data[key]
                break
        else:
            records = [data]
    else:
        raise ValueError("JSON must be a list of records or a dict containing a list")

    preprocessed = preprocess_data(records)
    if not preprocessed:
        raise ValueError("No valid records found in the uploaded file")

    yield from update_vector_dataset(preprocessed)
    print(f"Dataset updated successfully: {len(preprocessed)} records ingested.")


def fetch_nba_api_player_stats(season="2024"):
    try:
        nba_stats = importlib.import_module("nba_api.stats.endpoints")
        LeagueDashPlayerStats = getattr(nba_stats, "LeagueDashPlayerStats")
    except ImportError:
        raise ImportError(
            "nba_api is not installed. Install it with `pip install nba_api` and restart the backend."
        )

    season_key = normalize_season(season)
    stats = LeagueDashPlayerStats(season=season_key, per_mode_detailed="PerGame")
    return stats.get_data_frames()[0].to_dict(orient="records")


def save_nba_api_dataset(records, season="2024"):
    os.makedirs(DATASET_FOLDER, exist_ok=True)
    season_key = normalize_season(season).replace('-', '_')
    filename = f"upload_nba_api_{season_key}.json"
    save_path = os.path.join(DATASET_FOLDER, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump({"player_stats": records}, f, indent=2, default=str)
    return save_path


def _select_top_nba_records(records, max_records: int = 50):
    def score(record):
        for key in ("PTS", "PTS_PER_GAME", "MIN", "MPG"):
            try:
                value = record.get(key)
                if value is None:
                    continue
                return float(value)
            except (TypeError, ValueError):
                continue
        return 0.0

    sorted_records = sorted(records, key=score, reverse=True)
    return sorted_records[:max_records]


def update_dataset_from_nba_api(season="2024", max_players: int = 50):
    records = fetch_nba_api_player_stats(season)
    if not records:
        raise ValueError(f"NBA API returned no records for season {season}")

    save_nba_api_dataset(records, season)
    selected_records = _select_top_nba_records(records, max_records=max_players)
    print(f"NBA API returned {len(records)} records, ingesting top {len(selected_records)} records.")

    preprocessed = preprocess_data(selected_records)
    if not preprocessed:
        raise ValueError("No valid records found in NBA API data")

    yield from update_vector_dataset(preprocessed)
    print(f"NBA API dataset updated successfully: {len(preprocessed)} records ingested.")
    return len(preprocessed)


def update_dataset(season, source="json", max_players: int = 50):
    if source.lower() == "nba_api":
        yield "Fetching NBA API data..."
        record_count = yield from update_dataset_from_nba_api(season, max_players)
        print(f"Dataset updated successfully from NBA API for season {season}.")
        return record_count
    else:
        a = get_latest_json_file()
        if a is not None:
            yield from update_dataset_from_json()
            print(f"Dataset updated successfully from JSON file for season {season}.")
            return None
        else:
            print(f"No dataset files found for season {season}.")
            return None


if __name__ == '__main__':
    update_dataset(2020)
