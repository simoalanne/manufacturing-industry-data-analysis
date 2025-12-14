import requests
import json

# The data is confidential so the URL is not provided here.
url = "https://realurlhere.com/data.json"


def fetch():
    print(f"Downloading from {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            #Append the title from the JSON file
            filename = "raw-data.json"
            #Pretty print it and indent
            with open(filename, "w") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"Saved as {filename}")
        except (ValueError, KeyError) as e:
            print(f"Failed to process JSON from {url}: {e}")
    else:
        print(f"Failed to download from {url}, status code: {response.status_code}")

fetch()
