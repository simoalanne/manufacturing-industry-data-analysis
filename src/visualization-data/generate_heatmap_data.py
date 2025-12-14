import json
import argparse


def isFilteredOut(label, source_filter_mode, manufacturing_words):
    """
    This function checks if a label should be filtered out based on the source filter mode.
    """
    if source_filter_mode == "all":
        return False
    if source_filter_mode == "heatmap-only":
        return label not in manufacturing_words
    if source_filter_mode == "non-heatmap-only":
        return label in manufacturing_words
    print("invalid source_filter_mode, defaulting to all")
    return False


def generate_heatmap_data(min_score=0.7, source_filter_mode="all", min_similar_sources=5, ai_run_id="1", output_file="heatmap-data.json"):
    """
    This function processes raw JSON data with label keys and confidence scores,
    filters based on the minimum confidence score, adds new fields and removes unwanted keys,
    and saves to a new JSON file.
    """

    with open(f'../label-scoring/ai-generated-scores/manufacturing-scores-run-{ai_run_id}.json', 'r', encoding='utf-8') as f:
        label_scores = json.load(f)

    # Filter the labels based on the minimum confidence score
    manufacturing_words = {label for label, score in label_scores.items() if score >= min_score}
    print(f"length of manufacturing words: {len(manufacturing_words)}")

    with open('../raw-data/raw-data.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        nodes = raw_data["data"]["nodes"]

    # Lookup table for group to legend mapping
    group_to_legend_lookup_table = {
        "1": "job listings and investments",
        "2": "job listings",
        "3": "investments",
    }

    for node in nodes:
        # start by adding some new fields
        node["group_name"] = group_to_legend_lookup_table[node["group"]]
        node["word"] = node["label"].replace("_", " ").lower()
        node["correlation"] = node["group"] == "1"

    for node in nodes:
        if node["word"] in manufacturing_words:
            current_node_titles = {source["title"] for source in node.get("sources", [])}
            similar_sources_found = {}

            for other_node in nodes:
                if other_node["id"] != node["id"] and not isFilteredOut(other_node["label"], source_filter_mode, manufacturing_words):
                    other_node_titles = {source["title"] for source in other_node.get("sources", [])}
                    shared_titles = current_node_titles.intersection(other_node_titles)

                    if shared_titles and len(shared_titles) >= min_similar_sources:
                        similar_sources_found[other_node["word"]] = len(shared_titles)

            # Sort by count descending, then by word ascending
            sorted_similar_sources = dict(
                sorted(
                    similar_sources_found.items(),
                    key=lambda x: (-x[1], x[0])  # negative count for descending
                )
            )
            # This will be set to null in json if empty for consistency
            node["similar_sources_found"] = sorted_similar_sources

    nodes = [node for node in nodes if node["word"] in manufacturing_words]

    # print whar words are not in the nodes from the manufacturing words
    missing_words = manufacturing_words - {node["word"] for node in nodes}
    if missing_words:
        print(f"Missing words from nodes: {missing_words}")
        print("This is likely an issue with either casing or underscores instead of spaces.")
    else:
        print("All manufacturing words are present in the nodes.")

    keys_to_delete = ["sources", "weight", "id", "search_center", "explain_api_call", "label"]
    for node in nodes:
        for key in keys_to_delete:
            node.pop(key, None)

    # Sort the remaining nodes
    nodes.sort(
        key=lambda x: (
            int(x["group"]),
            -x["value"],  # Negate value for descending order
            x["word"],
        )
    )
    # Ideally data should be in this directory only and in gitinore too because it
    # can be generated from the raw data easily
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(nodes)} nodes for heatmap in {output_file}")

# Command-line argument to pass the minimum score
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate heatmap data from raw JSON file.")
    parser.add_argument(
        "--min-score", type=float, default=0.7,
        help="The minimum confidence score to include entries (default: 0.7)."
    )
    parser.add_argument(
        "--min-similar-sources", type=int, default=5,
        help="The minimum number of similar sources the words must share to be included in the output (default: 5)."
    )
    parser.add_argument(
        "--source-filter-mode", type=str, default="all",
        choices=["all", "heatmap-only", "non-heatmap-only"],
        help="How sources should be filtered. All means all words that shared sources with the heatmap word are included. "
                "heatmap-only means that only words that are already in the heatmap are included. "
                "non-heatmap-only means that only words that are not in the heatmap are included. "
                "(default: all)"
    )
    parser.add_argument(
        "--ai-run-id", type=str, default="1",
        help="The AI run ID to use for generating the heatmap data (default: 1)."
    )
    parser.add_argument(
        "--output-file", type=str, default="heatmap-data.json",
        help="The output file name for the generated heatmap data (default: heatmap-data.json)."
    )
    args = parser.parse_args()

    generate_heatmap_data(
        min_score=args.min_score,
        source_filter_mode=args.source_filter_mode,
        min_similar_sources=args.min_similar_sources,
        ai_run_id=args.ai_run_id,
        output_file=args.output_file
    )