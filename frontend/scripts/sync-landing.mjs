// Mirrors the canonical landing page at /landing into the Vite public/install
// directory so the production build ships /install as a static page alongside
// the SPA. Run automatically as the `prebuild` step.
import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, '..', '..', 'landing');
const dest = resolve(here, '..', 'public', 'install');

if (!existsSync(src)) {
  console.warn(`[sync-landing] source not found at ${src}, skipping`);
  process.exit(0);
}

rmSync(dest, { recursive: true, force: true });
mkdirSync(dest, { recursive: true });
cpSync(src, dest, { recursive: true });
console.log(`[sync-landing] copied landing/ → ${dest}`);
