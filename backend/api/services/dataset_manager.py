import os
import json
from .vector_store import update_dataset as update_vector_dataset

DATASET_FOLDER = os.path.join(os.path.dirname(__file__), "../../dataset")
DEFAULT_DATASET = os.path.join(DATASET_FOLDER, "demo_nba_2024.json")


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
        for key in ("events", "data", "records", "items", "results"):
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

    update_vector_dataset(preprocessed)
    print(f"Dataset updated successfully: {len(preprocessed)} records ingested.")


def update_dataset(season):
    a = get_latest_json_file()
    if a is not None:
        update_dataset_from_json()
        print(f"Dataset updated successfully from JSON file for season {season}.")
    else:
        print(f"No dataset files found for season {season}.")


if __name__ == '__main__':
    update_dataset(2020)
