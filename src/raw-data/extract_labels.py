import json

def extract_labels():
    """
    This function extracts and normalizes labels from a JSON file containing raw data
    and stores them elsewhere for further processing.
    The labels are normalized by stripping whitespace, converting to lowercase,
    and replacing underscores with spaces.
    """
    # Raw json file that should have been fetched using fetchdata.py
    input_file_path = "raw-data.json"

    output_file_path = "extracted_labels.txt"

    try:
        # Load the raw data
        with open(input_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        labels = [node["label"].strip().lower().replace("_", " ") for node in raw_data["data"]["nodes"]]

        # Write labels to a file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for label in labels:
                f.write(label + "\n")

        print(f"Labels have been successfully extracted to {output_file_path}")

    except Exception as e:
        print(f"Error extracting labels: {e}")

extract_labels()
