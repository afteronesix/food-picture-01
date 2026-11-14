// food-picture-01 entry v3: copies the winning food picture to the output directory.
// v3 picture: steaming tonkotsu ramen, chopsticks lifting a tall noodle pull
// above the bowl — jammy egg, chili-oil swirls, nori, green onion, dark moody
// background, warm light. v3 replaces the v2 tight mango photo, which ranked
// #2,403 of 3,196 (3W-9L): a competent but generic crop with no drama, no
// action, no story, and a pale palette. The new hypothesis is a different dish
// with a moment in it — the pull, the steam, the color contrast — picked by
// direct visual inspection after the CrowLLM vision routes proved blind again
// (hallucinated dishes + first-presented bias on every probe call).
// Deterministic: a straight byte copy, same bytes every run. No network, no deps.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1048576; // 1 MiB
const MAX_DIM = 1024;

function resolveSource(): string {
  const here = dirname(fileURLToPath(import.meta.url));
  const fromScript = join(here, "entry.png");
  if (existsSync(fromScript)) return fromScript;
  const fromCwd = resolve("entry.png");
  if (existsSync(fromCwd)) return fromCwd;
  throw new Error("entry.png not found next to main.ts or in the working directory");
}

function readPngDimensions(buf: Buffer): { width: number; height: number } {
  // PNG signature (8 bytes) + IHDR chunk: length(4) "IHDR"(4) width(4) height(4)
  if (buf.length < 33) throw new Error("file too small to be a PNG");
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  if (!buf.subarray(0, 8).equals(sig)) throw new Error("not a PNG (bad signature)");
  if (buf.toString("ascii", 12, 16) !== "IHDR") throw new Error("not a PNG (no IHDR chunk)");
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

function hasIendChunk(buf: Buffer): boolean {
  // A complete PNG ends with the 12-byte IEND chunk: length 0, "IEND", CRC.
  // The signature/IHDR checks above cannot catch a file truncated at the tail.
  if (buf.length < 12) return false;
  const tail = buf.subarray(buf.length - 12);
  return tail.readUInt32BE(0) === 0 && tail.toString("ascii", 4, 8) === "IEND";
}

function main(): void {
  const src = resolveSource();
  const buf = readFileSync(src);
  const { width, height } = readPngDimensions(buf);
  if (!hasIendChunk(buf)) {
    throw new Error("entry.png is truncated (no IEND chunk at the end)");
  }
  if (width > MAX_DIM || height > MAX_DIM) {
    throw new Error(`entry.png is ${width}x${height}, over the ${MAX_DIM}x${MAX_DIM} limit`);
  }
  if (buf.length > MAX_BYTES) {
    throw new Error(`entry.png is ${buf.length} bytes, over the ${MAX_BYTES} byte limit`);
  }
  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  mkdirSync(outDir, { recursive: true });
  const out = join(outDir, "entry.png");
  copyFileSync(src, out);
  const written = statSync(out);
  // Post-copy verification: the written file must match the source exactly.
  if (written.size !== buf.length) {
    throw new Error(`copy mismatch: wrote ${written.size} bytes, source is ${buf.length}`);
  }
  const back = readFileSync(out);
  if (!back.equals(buf)) {
    throw new Error("copy mismatch: written bytes differ from entry.png");
  }
  // Validate the written output as a standalone entry, independent of the
  // source comparison: the file on disk must itself be a valid PNG within the
  // bounty limits, so a corrupt or truncated write can never pass silently.
  const outDims = readPngDimensions(back);
  if (outDims.width !== width || outDims.height !== height) {
    throw new Error(
      `output dimensions changed: ${outDims.width}x${outDims.height}, source is ${width}x${height}`
    );
  }
  if (back.length > MAX_BYTES) {
    throw new Error(`output is ${back.length} bytes, over the ${MAX_BYTES} byte limit`);
  }
  if (!hasIendChunk(back)) {
    throw new Error("output is truncated (no IEND chunk at the end)");
  }
  console.log(`wrote ${out} (${written.size} bytes, ${width}x${height})`);
}

main();
