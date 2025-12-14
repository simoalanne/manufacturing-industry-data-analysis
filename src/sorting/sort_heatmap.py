import json

# This script sorts a JSON file containing data about different groups of items.
# it sorts them so that in visualization, the first group (group 1) is at the center,
# group 2 on the left, and group 3 on the right. This script does not work perfectly
# because there isn't an enen number of items in the groups 2 and 3. In addition to this
# script, another script is needed that will be used to manually swap entry indexes in the
# JSON file.
def sort_heatmap():
    with open('../visual/data.json', 'r') as f:
        data = json.load(f)

    group1 = [item for item in data if item['group'] == "1"] # greens
    group2 = [item for item in data if item['group'] == "2"] # reds
    group3 = [item for item in data if item['group'] == "3"] # blues

    sorted_data = group1.copy()

    cells_per_ring = 12

    while len(group2) > 0 or len(group3) > 0:
        half_ring = cells_per_ring // 2

        # Fill half the ring with group 2 (reds)
        for _ in range(half_ring):
            if group2:
                sorted_data.append(group2.pop(0))

        # Fill the other half with group 3 (blues)
        for _ in range(half_ring):
            if group3:
                sorted_data.append(group3.pop(0))

        cells_per_ring += 6  # Increase the number of cells for the next ring

    with open('../visual/data.json', 'w') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)

sort_heatmap()
