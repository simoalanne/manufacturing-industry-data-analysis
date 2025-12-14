import json
import sys

def swap_entries(word1, word2):
    with open('../visual/data.json', 'r') as f:
        data = json.load(f)

    index1, index2 = None, None

    # Find the indices of the entries containing word1 and word2
    for i, item in enumerate(data):
        if index1 is not None and index2 is not None:
            break
        if word1 == item['word']:
            index1 = i
        if word2 == item['word']:
            index2 = i

    for i, item in enumerate(data):
        if index1 is not None and index2 is not None:
            break
        if word1 in item['word']:
            index1 = i
        if word2 in item['word']:
            index2 = i

    # Swap the entries if both are found
    if index1 is not None and index2 is not None:
        data[index1], data[index2] = data[index2], data[index1]
        with open('../visual/data.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Swapped entries containing '{data[index1]['word']}' and '{data[index2]['word']}'.")
    else:
        print(f"Could not find entries containing both '{word1}' and '{word2}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python swap_entries.py <word1> <word2>")
    else:
        swap_entries(sys.argv[1], sys.argv[2])
