# This script reads the main heatmap-data.json file and gets the similar sources for a specific word.
# it then uses those to filter out all items from the json that aren't in the similar sources
# and writes the filtered data to a new json file that can be used for visualization.

# for visualization you can copy the previous visualization script and just change the input file to the new one
# and possibly adjust the cell sizes and other parameters to better fit how many words this new json data contains

import json
import sys
import os

target_word = sys.argv[1] if len(sys.argv) > 1 else "robotiikka"

# check if the main heatmap-data.json file exists
if not os.path.exists("heatmap-data.json"):
    print("heatmap-data.json file not found")
    print("Run following command first: python generate_heatmap_data.py --min-similar-sources 1 --source-filter-mode heatmap-only")
    sys.exit(1)

with open("heatmap-data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

similar_sources = None
for item in data:
    if item["word"] == target_word:
        similar_sources = list(item["similar_sources_found"].keys())
        print(f"Found {len(similar_sources)} similar sources for {target_word}")
        similar_sources.append(item["word"])
        break

if similar_sources is None:
    print(f"No similar sources found for word: {target_word}")
    sys.exit(1)


new_data = []
for item in data:
    if item["word"] in similar_sources:
        new_data.append(item)
        print(f"Added {item['word']} to new data")

print(f"Filtered data contains {len(new_data)} items")

# Write the filtered data to a new json file
with open(f"../visual/heatmap-data-{target_word}.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)
print(f"Filtered data written to ../visual/heatmap-data-{target_word}.json")
