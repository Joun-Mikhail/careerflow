/**
 * Render the CareerFlow favicon SVG as a 1024×1024 app icon (and optional splash).
 *
 * Uses Puppeteer + installed Chrome — no extra image deps.
 *
 * Usage:
 *   CHROME_PATH="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" \
 *   node scripts/generate-icon.mjs
 */
import { mkdir, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import puppeteer from 'puppeteer-core';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');
const ASSETS_DIR = resolve(ROOT, 'public/native-assets');
const SVG_PATH = resolve(ROOT, 'public/favicon.svg');
const CHROME_PATH = process.env.CHROME_PATH;

async function main() {
  if (!CHROME_PATH) {
    throw new Error(
      'Set CHROME_PATH to your Chrome executable, e.g.\n' +
        '  Windows: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\n' +
        '  macOS:   /Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    );
  }

  mkdir(ASSETS_DIR, { recursive: true }, () => {});

  const svg = readFileSync(SVG_PATH, 'utf8');
  const iconDataUri = `data:image/svg+xml,${encodeURIComponent(svg)}`;

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });

  try {
    const page = await browser.newPage();

    // 1024×1024 app icon
    await page.setViewport({ width: 1024, height: 1024, deviceScaleFactor: 1 });
    await page.setContent(
      `<!doctype html><html><body style="margin:0;padding:0;background:#4f46e5">
        <img src="${iconDataUri}" width="1024" height="1024" alt="" />
      </body></html>`,
      { waitUntil: 'load' },
    );
    await page.screenshot({
      path: resolve(ASSETS_DIR, 'icon.png'),
      clip: { x: 0, y: 0, width: 1024, height: 1024 },
    });
    console.log('Wrote public/native-assets/icon.png (1024×1024)');

    // 2732×2732 splash (centered icon on brand background)
    await page.setViewport({ width: 2732, height: 2732, deviceScaleFactor: 1 });
    await page.setContent(
      `<!doctype html><html><body style="margin:0;display:flex;align-items:center;justify-content:center;width:2732px;height:2732px;background:#4f46e5">
        <img src="${iconDataUri}" width="512" height="512" alt="" />
      </body></html>`,
      { waitUntil: 'load' },
    );
    await page.screenshot({
      path: resolve(ASSETS_DIR, 'splash.png'),
      clip: { x: 0, y: 0, width: 2732, height: 2732 },
    });
    console.log('Wrote public/native-assets/splash.png (2732×2732)');
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
