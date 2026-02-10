import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, "..");
const HASH_FILE = path.join(ROOT_DIR, "src/canvas-host/a2ui/.bundle.hash");
const OUTPUT_FILE = path.join(ROOT_DIR, "src/canvas-host/a2ui/a2ui.bundle.js");
const A2UI_RENDERER_DIR = path.join(ROOT_DIR, "vendor/a2ui/renderers/lit");
const A2UI_APP_DIR = path.join(ROOT_DIR, "apps/shared/OpenClawKit/Tools/CanvasA2UI");

if (!(await exists(A2UI_RENDERER_DIR)) || !(await exists(A2UI_APP_DIR))) {
  console.log("A2UI sources missing; keeping prebuilt bundle.");
  process.exit(0);
}

const INPUT_PATHS = [
  path.join(ROOT_DIR, "package.json"),
  path.join(ROOT_DIR, "pnpm-lock.yaml"),
  A2UI_RENDERER_DIR,
  A2UI_APP_DIR,
];

async function exists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

async function walk(entryPath) {
  const files = [];
  const st = await fs.stat(entryPath);
  if (st.isDirectory()) {
    const entries = await fs.readdir(entryPath);
    for (const entry of entries) {
      files.push(...(await walk(path.join(entryPath, entry))));
    }
  } else {
    files.push(entryPath);
  }
  return files;
}

async function computeHash() {
  const files = [];
  for (const input of INPUT_PATHS) {
    if (await exists(input)) {
      files.push(...(await walk(input)));
    }
  }

  function normalize(p) {
    return p.split(path.sep).join("/");
  }

  files.sort((a, b) => normalize(a).localeCompare(normalize(b)));

  const hash = createHash("sha256");
  for (const filePath of files) {
    const rel = normalize(path.relative(ROOT_DIR, filePath));
    hash.update(rel);
    hash.update("\0");
    hash.update(await fs.readFile(filePath));
    hash.update("\0");
  }
  return hash.digest("hex");
}

async function main() {
  try {
    const currentHash = await computeHash();
    if ((await exists(HASH_FILE)) && (await exists(OUTPUT_FILE))) {
      const previousHash = (await fs.readFile(HASH_FILE, "utf-8")).trim();
      if (previousHash === currentHash) {
        console.log("A2UI bundle up to date; skipping.");
        return;
      }
    }

    // Run tsc
    console.log("Running TSC...");
    const tscResult = spawnSync(
      "pnpm",
      ["exec", "tsc", "-p", path.join(A2UI_RENDERER_DIR, "tsconfig.json")],
      {
        stdio: "inherit",
        shell: true,
      },
    );
    if (tscResult.status !== 0) {
      throw new Error("TSC failed");
    }

    // Run rolldown
    console.log("Running Rolldown...");
    const rolldownResult = spawnSync(
      "npx",
      ["rolldown", "-c", path.join(A2UI_APP_DIR, "rolldown.config.mjs")],
      {
        stdio: "inherit",
        shell: true,
      },
    );
    if (rolldownResult.status !== 0) {
      throw new Error("Rolldown failed");
    }

    await fs.writeFile(HASH_FILE, currentHash);
  } catch (e) {
    console.error("A2UI bundling failed.");
    console.error(e);
    process.exit(1);
  }
}

main();
