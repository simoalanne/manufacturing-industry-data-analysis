import { GoogleGenAI } from "@google/genai";
import 'dotenv/config';
import { readFile, readdir, writeFile } from 'fs/promises';

const WAIT_TIME_MS = Number(process.env.WAIT_TIME_MS) || 4000;
const CHUNK_SIZE = Number(process.env.CHUNK_SIZE) || 100;

/**
 * Generates a prompt for the AI model to rate the confidence of words related to manufacturing.
 * Multiple different prompts have been tested, but really it doesnt matter much what the exact prompt is,
 * the results will still greatly vary in each run because the whole question: "Is this word related to manufacturing?"
 * is so subjective.
 *
 * @param {Array} chunk - An array of objects containing words to be rated.
 * @returns {string} - The generated prompt for the AI model.
 */
const generatePrompt = (chunk) => `I have a list of technology-related words.
I need you to give a confidence score between 0 and 1 for each word based on how strongly related/connected
the English or Finnish word is specifically to the manufacturing industry or in Finnish "valmistava teollisuus".
The score should be 0 if the word is not related at all and 1 if the word is very strongly related. The words could
be related to manufacturing either in the context of skills required to working in the manufacturing industry or
in the context of manufacturing itself such as manufacturing processes, tools, or technologies etc.
Never skip over any words. Every single word must be rated even if they are duplicates or whatever.

Return your answer strictly as a JSON array with no additional text, comments, or explanations.
Example response format:

[
  { "word": "word1", "confidence_score": 0.5, "id": "1" },
  { "word": "word2", "confidence_score": 0.8, "id": "2" },
]

Here are the words you need to rate:
${chunk.join("\n")}
`;

const processChunk = async (ai, chunk) => {
    const response = await ai.models.generateContent({
        model: "gemini-2.0-flash",
        contents: generatePrompt(chunk),
    });
    return JSON.parse(response.text.replace(/```json/g, '').replace(/```/g, ''));
};

/**
 * Reads the contents of a directory and returns the next available run number.
 * The run number is determined by the highest number found in the filenames that match the
 * file pattern "manufacturing-scores-run-<number>.json" that this script generates.
 * If no previous runs are found, it returns 1.
 *
 * @returns {Promise<number>} - The next available run number.
 */
const getNextRunNumber = async () => {
    const files = await readdir("./ai-generated-scores");
    const runNumbers = files.map(file => {
        const match = file.match(/manufacturing-scores-run-(\d+)\.json/);
        return match ? Number(match[1]) : null;
    }).filter(num => num !== null);

    return runNumbers.length > 0 ? Math.max(...runNumbers) + 1 : 1;
};

const main = async () => {
    const inputFilePath = "../raw-data/extracted_labels.txt";
    // The output files should be named based on how many times this script has been run
    // e.g. manufacturing-scores-run-1.json, manufacturing-scores-run-2.json, etc.
    // This is to avoid overwriting the previous runs and to keep track of the progress
    // and the results of the previous runs.
    const runNumber = await getNextRunNumber();
    const outputFilePath = `./ai-generated-scores/manufacturing-scores-run-${runNumber}.json`;
    console.log(`Output file path: ${outputFilePath}`);

    if (!process.env.GEMINI_API_KEY) {
        console.error("Missing GEMINI_API_KEY in .env");
        return;
    }

    const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

    try {
        const labels = (await readFile(inputFilePath, 'utf-8'))
            .split('\n')
            .map(label => label.trim())
            .filter(Boolean);

        console.log(`total labels: ${labels.length}`);
        let count = 0;

        const chunks = [];
        for (let i = 0; i < labels.length; i += CHUNK_SIZE) {
            chunks.push(labels.slice(i, i + CHUNK_SIZE));
        }

        const confidenceScores = await Promise.all(
            chunks.map(async (chunk, index) => {
                const waitTime = index * WAIT_TIME_MS;
                await new Promise(resolve => setTimeout(resolve, waitTime));

                console.log(`Processing chunk ${index + 1}/${chunks.length}...`);
                const result = await processChunk(ai, chunk);
                console.log(`Chunk ${index + 1} done`);
                count += result.length;
                console.log(`progress: ${count} / ${labels.length}`);
                return result;
            })
        );
        const flatResults = confidenceScores.flat();

        flatResults.sort((a, b) => {
            if (b.confidence_score !== a.confidence_score) {
                return b.confidence_score - a.confidence_score;
            }
            return a.word.localeCompare(b.word);
        });

        // using the labels as the keys will make it so that the output json will have fewer keys
        // than originally were labels. this is because some of the labels are duplicates
        // and json keys cannot be duplicates so this will overwrite the duplicates
        // and only keep the last one in the list
        const scoresObject = Object.fromEntries(
            flatResults.map(({ word, confidence_score }) => [word, confidence_score])
        );

        await writeFile(outputFilePath, JSON.stringify(scoresObject, null, 2), 'utf-8');
        console.log(`Manufacturing scores saved to: ${outputFilePath}`);
    } catch (err) {
        console.error("Error during processing:", err.message);
    }
};

main();
