# This script clusters job listing related words into broader categories
# Investment words are untouched cause clustering them is not needed

import json
from collections import defaultdict


with open("./originalData.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# get all job listing words
terms = [entry["word"] for entry in data if entry["group"] == "2"]

# Define the keyword map for matching and replacing substrings
# This seemingly random mapping has just been done manually by looking at the words in the data
# and trying to find the most common substrings that can be used to group them together.
# this is not the best for semantic matching but it works well enough for now
keyword_map = {
    "asen": "asennus",
    "automa": "automaatio",
    "hits": "hitsaus",
    "sähk": "sähkö",
    "terv": "terveys",
    "maala": "maalaus",
    "mitta": "mittaus",
    "elektr": "elektroniikka",
    "materiaa": "materiaali",
    "cnc": "CNC",
    "hio": "hiominen",
    "tekni": "tekniikka",
    "aarpora": "aarporaus",
    "prosess": "prosessi",
    "elintar": "elintarvike",
    "suunnit": "suunnittelu",
    "rakent": "rakentaminen",
    "huolt": "huolto",
    "logisti": "logistiikka",
    "laat": "laatu",
    "valmist": "valmistus",
    "metall": "metalli",
    "polttoleikka": "polttoleikkaus",
    "pintakäsitte": "pintakäsittely",
    "rahdinkäsittelijät": "rahdinkäsittelijät ja varastotyöntekijät",
    "raken": "rakentaminen",
    "varasto": "varastotyö",
    "autoteollisuu": "autoteollisuuden vianmäärityslaitteet",
    "kone": "koneet", # this could be just "kone" but kone exists in investment data and data should not have duplicates between groups
    "suojavarus": "suojavarusteet",
    "komponent": "komponentit",
    "tuotet": "tuotetuntemus",
    "elinkaari": "tuotteen elinkaari",

}

# Prepare the result dictionary where we will store replaced terms
result = {full_word: [] for full_word in keyword_map.values()}

# Iterate through the terms and check if they match any of the substrings
for term in terms:
    for substring, full_word in keyword_map.items():
        if substring in term:
            result[full_word].append(term)
            break  # Found a match, no need to check further

# Load the data from JSON file
with open("./originalData.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Modify the original data in place
for full_word, group_terms in result.items():
    # Find all the matching entries from the original data that belong to the group
    group_entries = [entry for entry in data if entry["word"] in group_terms and entry["group"] == "2"]

    if group_entries:
        # Sum the values of all terms in the group
        total_value = sum(entry["value"] for entry in group_entries)

        # Add the "replaced_words" key to the group entries to store the original list of words
        replaced_words = group_terms

        # Merge the "similar_sources_found" objects
        merged_similar_sources = defaultdict(int)
        for entry in group_entries:
            for key, value in entry.get("similar_sources_found", {}).items():
                merged_similar_sources[key] += value
        # Replace all words in the group with the group name and update their values
        for entry in group_entries:
            entry["word"] = full_word
            entry["value"] = total_value
            entry["replaced_words"] = replaced_words  # New key for the original list of words
            entry["similar_sources_found"] = dict(merged_similar_sources)  # Combined similar sources

        # Remove all but the first occurrence of the group word
        new_data = []
        seen_words = set()

        for entry in data:
            word = entry["word"]
            if word not in seen_words:
                seen_words.add(word)
                new_data.append(entry)

        data = new_data  # replace original data with deduplicated list

# Loop through the updated result mapping again to replace the keys in "similar_sources_found"
# with the updated word
for group_word, original_words in result.items():
    for entry in data:
        if "similar_sources_found" not in entry:
            print(f"Entry {entry['word']} does not have 'similar_sources_found' key.")
            continue

        updated_similar = defaultdict(int)
        for key, val in entry["similar_sources_found"].items():
            # If the key is part of a group, replace it with the group name
            replacement_key = group_word if key in original_words else key
            updated_similar[replacement_key] += val
            if replacement_key == group_word:
                continue

        # Replace the original with the merged one
        entry["similar_sources_found"] = dict(updated_similar)

data.sort(key=lambda x: (int(x["group"]), -x["value"]))



# Optionally, save the updated data back to a file
with open("../visual/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

new_terms = [entry["word"] for entry in data if entry["group"] == "2"]
new_terms = sorted(new_terms)
# just to keep track of how much has been clustered
with open("./job_listing_words_modified.txt", "w", encoding="utf-8") as f:
    for term in new_terms:
        f.write(term + "\n")
print("Data processing complete.")
