# Label Scoring for Manufacturing Relevance

This directory contains scripts and data related to generating confidence scores for a set of labels (keywords/phrases) indicating how strongly each is associated with the manufacturing industry.

## Overview

The main script, `scoreRawDataLabels.js`, uses the Gemini AI model to score each label found from the raw data `../raw-data/raw-data.json` with a confidence value between 0 and 1.

Each run of the script generates a new output JSON in the `ai-generated-scores/` directory, preserving the results of each scoring round:

## Why Multiple Files?

Each run might produces quite different results due to the subjective nature of the task and AI's variability. To keep track of progress, compare changes, and avoid overwriting, each output is saved as a seperate file.

## Suggested Thresholds

From initial runs and manual inspection, it appears that confidence scores in the range of **0.8 to 1.0** tend to have the most consistently relevant results. Words in this range often reflect terminology that is clearly connected to manufacturing — including job roles, job skills, processes, machines, tools, and key industry concepts.

The **0.7** values are bit more tricky. These often **do contain** relevant words and many of these words are also **rated higher** in some of the runs but on the other hand some of the words in this range **aren't as obviously related**.

Still as a compromise using a cutoff of **0.7** typically results in **about 300 high-confidence labels**, making it a practical threshold for visualization.

## Notes

- **Duplicate labels** are only represented once in the final JSON, as JSON keys must be unique. If the same label appeared multiple times in the input, only the last occurrence is stored. There are about 30 duplicate
entries in the **raw-data.json** file.
- These runs are generated via a script that processes chunks of labels at once eg., 100 words at the time to avoid overwhelming the AI model with too many labels per single request.

## Output format
Each file is a JSON object structured followingly:
```bash
{
  "label1": 1,
  "label2": 0.9,
  ...
}
```

The data is sorted primarily by values (descending) and secondarily by the key name alphabetically.
