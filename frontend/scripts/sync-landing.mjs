// Mirrors the canonical landing page at /landing into the Vite public/install
// directory so the production build ships /install as a static page alongside
// the SPA. Injects store URLs from store-urls.json. Run as the `prebuild` step.
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, '..', '..');
const src = resolve(repoRoot, 'landing');
const dest = resolve(here, '..', 'public', 'install');
const urlsPath = resolve(repoRoot, 'store-urls.json');

if (!existsSync(src)) {
  console.warn(`[sync-landing] source not found at ${src}, skipping`);
  process.exit(0);
}

rmSync(dest, { recursive: true, force: true });
mkdirSync(dest, { recursive: true });
cpSync(src, dest, { recursive: true });

// Inject live store URLs from store-urls.json into the install page
if (existsSync(urlsPath)) {
  const urls = JSON.parse(readFileSync(urlsPath, 'utf8'));
  const indexPath = resolve(dest, 'index.html');
  if (existsSync(indexPath)) {
    let html = readFileSync(indexPath, 'utf8');
    html = html.replace(/var APPSTORE_URL = '[^']*';/, `var APPSTORE_URL = '${urls.appStoreUrl}';`);
    html = html.replace(/var PLAYSTORE_URL = '[^']*';/, `var PLAYSTORE_URL = '${urls.playStoreUrl}';`);
    writeFileSync(indexPath, html);
    console.log(`[sync-landing] injected store URLs (appStorePublished=${urls.appStorePublished})`);
  }
}

console.log(`[sync-landing] copied landing/ → ${dest}`);
