#!/usr/bin/env node
/**
 * auto-translate.mjs — Sync missing keys from en.json → es.json via OpenAI
 *
 * Usage:
 *   OPENAI_API_KEY=sk-... node scripts/auto-translate.mjs
 *
 * What it does:
 *   1. Reads messages/en.json and messages/es.json
 *   2. Finds keys present in EN but missing in ES
 *   3. Sends them to OpenAI for translation (gpt-4o-mini)
 *   4. Merges results into es.json and writes the file
 *
 * Supports nested JSON. Existing ES translations are never overwritten.
 */

import { readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const EN_PATH = resolve(__dirname, "../messages/en.json");
const ES_PATH = resolve(__dirname, "../messages/es.json");

/* ── Helpers ── */

/** Flatten nested obj to dot-separated keys */
function flatten(obj, prefix = "") {
  const result = {};
  for (const [key, value] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (typeof value === "object" && value !== null) {
      Object.assign(result, flatten(value, path));
    } else {
      result[path] = value;
    }
  }
  return result;
}

/** Expand dot-separated keys back to nested object */
function unflatten(flat) {
  const result = {};
  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split(".");
    let current = result;
    for (let i = 0; i < parts.length - 1; i++) {
      if (!(parts[i] in current)) current[parts[i]] = {};
      current = current[parts[i]];
    }
    current[parts[parts.length - 1]] = value;
  }
  return result;
}

/** Deep merge source into target (target wins on conflicts) */
function deepMerge(target, source) {
  for (const [key, value] of Object.entries(source)) {
    if (
      typeof value === "object" &&
      value !== null &&
      typeof target[key] === "object"
    ) {
      deepMerge(target[key], value);
    } else if (!(key in target)) {
      target[key] = value;
    }
  }
  return target;
}

/* ── Main ── */

async function main() {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error(
      "❌  Set OPENAI_API_KEY environment variable.\n" +
        "   Example: OPENAI_API_KEY=sk-... node scripts/auto-translate.mjs",
    );
    process.exit(1);
  }

  const en = JSON.parse(readFileSync(EN_PATH, "utf-8"));
  const es = JSON.parse(readFileSync(ES_PATH, "utf-8"));

  const enFlat = flatten(en);
  const esFlat = flatten(es);

  // Find keys present in EN but missing in ES
  const missing = {};
  for (const [key, value] of Object.entries(enFlat)) {
    if (!(key in esFlat)) {
      missing[key] = value;
    }
  }

  const missingCount = Object.keys(missing).length;
  if (missingCount === 0) {
    console.log("✅  All EN keys already have ES translations. Nothing to do.");
    return;
  }

  console.log(`🔍  Found ${missingCount} missing ES translations. Translating…`);

  // Batch into chunks of 50 to stay within token limits
  const BATCH_SIZE = 50;
  const entries = Object.entries(missing);
  const translated = {};

  for (let i = 0; i < entries.length; i += BATCH_SIZE) {
    const batch = Object.fromEntries(entries.slice(i, i + BATCH_SIZE));
    const batchNum = Math.floor(i / BATCH_SIZE) + 1;
    const totalBatches = Math.ceil(entries.length / BATCH_SIZE);
    console.log(`   Batch ${batchNum}/${totalBatches} (${Object.keys(batch).length} keys)…`);

    const prompt = `Translate these English UI strings to Latin American Spanish (El Salvador dialect where appropriate). Return ONLY a JSON object with the same keys and translated values. Keep brand names, numbers, URLs, and technical terms unchanged. Preserve any HTML or special characters.\n\n${JSON.stringify(batch, null, 2)}`;

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        temperature: 0.2,
        messages: [
          {
            role: "system",
            content:
              "You are a professional translator specializing in Latin American Spanish. You translate UI copy for a digital platform about El Salvador. Always return valid JSON only — no markdown fences, no explanation.",
          },
          { role: "user", content: prompt },
        ],
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      console.error(`❌  OpenAI API error: ${response.status}\n${error}`);
      process.exit(1);
    }

    const data = await response.json();
    const content = data.choices[0].message.content.trim();

    try {
      // Strip markdown code fences if present
      const jsonStr = content.replace(/^```json?\n?/i, "").replace(/\n?```$/i, "");
      const batchTranslated = JSON.parse(jsonStr);
      Object.assign(translated, batchTranslated);
    } catch (e) {
      console.error(`❌  Failed to parse OpenAI response:\n${content}`);
      process.exit(1);
    }
  }

  // Merge translated keys into ES
  const translatedNested = unflatten(translated);
  deepMerge(es, translatedNested);

  writeFileSync(ES_PATH, JSON.stringify(es, null, 2) + "\n");
  console.log(
    `✅  Translated ${Object.keys(translated).length} keys → messages/es.json`,
  );
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
