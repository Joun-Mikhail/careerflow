/**
 * Record a short demo GIF of key CareerFlow workflows from the running app.
 *
 * Drives the real SPA with Puppeteer (installed Chrome), captures frames while
 * navigating dashboard → applications board → application detail → analytics,
 * and encodes them to docs/screenshots/demo.gif. Requires the frontend and a
 * seeded backend to be running.
 *
 * Usage:
 *   CHROME_PATH="…\\chrome.exe" BASE_URL="http://localhost:5173" \
 *   node scripts/demo-gif.mjs
 */
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import gifenc from 'gifenc';
import pngjs from 'pngjs';
import puppeteer from 'puppeteer-core';

const { GIFEncoder, quantize, applyPalette } = gifenc;
const { PNG } = pngjs;

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = resolve(__dirname, '../../docs/screenshots/demo.gif');
const BASE_URL = process.env.BASE_URL ?? 'http://localhost:5173';
const CHROME_PATH = process.env.CHROME_PATH;
const FRAME_DELAY_MS = 1400;

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  if (!CHROME_PATH) throw new Error('Set CHROME_PATH to the Chrome executable.');
  await mkdir(dirname(OUT), { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });

  const frames = [];
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1100, height: 700, deviceScaleFactor: 1 });

    const capture = async () => {
      const png = PNG.sync.read(await page.screenshot({ type: 'png' }));
      frames.push({ data: new Uint8Array(png.data), width: png.width, height: png.height });
    };

    // Sign in (form pre-filled with demo credentials).
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'load' });
    await page.waitForSelector('.auth-card');
    await page.click('button[type="submit"]');
    await page.waitForFunction(() => window.location.pathname === '/', { timeout: 15000 });
    await page.waitForSelector('.stat-value');
    await wait(800);
    await capture(); // dashboard

    await page.goto(`${BASE_URL}/applications`, { waitUntil: 'load' });
    await page.waitForSelector('.kanban-col');
    await wait(900);
    await capture(); // pipeline board

    await page.click('.kanban-card');
    await page.waitForSelector('.detail-grid');
    await wait(900);
    await capture(); // application detail

    await page.goto(`${BASE_URL}/tasks`, { waitUntil: 'load' });
    await page.waitForSelector('.card');
    await wait(900);
    await capture(); // tasks

    await page.goto(`${BASE_URL}/analytics`, { waitUntil: 'load' });
    await page.waitForSelector('svg.recharts-surface', { timeout: 15000 });
    await wait(1300);
    await capture(); // analytics
  } finally {
    await browser.close();
  }

  // Encode the captured frames into a looping GIF.
  const { width, height } = frames[0];
  const encoder = GIFEncoder();
  for (const frame of frames) {
    const palette = quantize(frame.data, 256);
    const index = applyPalette(frame.data, palette);
    encoder.writeFrame(index, width, height, { palette, delay: FRAME_DELAY_MS });
  }
  encoder.finish();
  await writeFile(OUT, Buffer.from(encoder.bytes()));
  console.log(`wrote ${OUT} (${frames.length} frames, ${width}x${height})`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
