// Update README store badges from store-urls.json.
// Run after Apple approves the app and you set the real App Store URL.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const urls = JSON.parse(readFileSync(resolve(repoRoot, 'store-urls.json'), 'utf8'));
const readmePath = resolve(repoRoot, 'README.md');
let readme = readFileSync(readmePath, 'utf8');

const appLabel = urls.appStorePublished ? 'Download' : 'coming soon';
const playLabel = urls.playStorePublished ? 'Download' : 'coming soon';

readme = readme.replace(
  /\[!\[App Store\]\([^)]+\)\]\([^)]+\)/,
  `[![App Store](https://img.shields.io/badge/App%20Store-${encodeURIComponent(appLabel)}-000?logo=apple&logoColor=white)](${urls.appStoreUrl})`,
);
readme = readme.replace(
  /\[!\[Google Play\]\([^)]+\)\]\([^)]+\)/,
  `[![Google Play](https://img.shields.io/badge/Google%20Play-${encodeURIComponent(playLabel)}-000?logo=googleplay&logoColor=white)](${urls.playStoreUrl})`,
);

writeFileSync(readmePath, readme);
console.log(`Updated README badges (appStorePublished=${urls.appStorePublished})`);
