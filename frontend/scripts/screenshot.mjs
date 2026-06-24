/**
 * Capture real screenshots of the running CareerFlow SPA.
 *
 * Drives the actual application with Puppeteer against an installed Chrome
 * (no bundled Chromium download). Requires the frontend (http://localhost:5173)
 * and backend to be running with seeded demo data. Output: docs/screenshots/.
 *
 * Usage:
 *   CHROME_PATH="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" \
 *   BASE_URL="http://localhost:5173" node scripts/screenshot.mjs
 */
import { mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import puppeteer from 'puppeteer-core';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = resolve(__dirname, '../../docs/screenshots');
const BASE_URL = process.env.BASE_URL ?? 'http://localhost:5173';
const CHROME_PATH = process.env.CHROME_PATH;

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  if (!CHROME_PATH) throw new Error('Set CHROME_PATH to the Chrome executable.');
  await mkdir(OUT_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--window-size=1440,900'],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });

    const shot = async (name) => {
      await page.screenshot({ path: resolve(OUT_DIR, `${name}.png`) });
      console.log(`captured ${name}.png`);
    };

    // 1. Login screen.
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'load' });
    await page.waitForSelector('.auth-card');
    await wait(400);
    await shot('login');

    // Sign in with the demo account and land on the dashboard.
    await page.type('#email', 'demo@careerflow.app');
    await page.type('#password', 'DemoPass123!');
    await page.click('button[type="submit"]');
    await page.waitForFunction(() => window.location.pathname === '/', { timeout: 15000 });
    await page.waitForSelector('.stat-value');
    await wait(700);
    await shot('dashboard');

    // Dark mode.
    await page.click('.theme-toggle');
    await wait(500);
    await shot('dashboard-dark');
    await page.click('.theme-toggle');
    await wait(300);

    // 2. Applications pipeline board.
    await page.goto(`${BASE_URL}/applications`, { waitUntil: 'load' });
    await page.waitForSelector('.kanban-col');
    await wait(700);
    await shot('applications-board');

    // 3. Application detail (open the first card on the board).
    await page.click('.kanban-card');
    await page.waitForSelector('.detail-grid');
    await wait(700);
    await shot('application-detail');

    // 4. Analytics with charts.
    await page.goto(`${BASE_URL}/analytics`, { waitUntil: 'load' });
    await page.waitForSelector('svg.recharts-surface', { timeout: 15000 });
    await wait(1200);
    await shot('analytics');

    // 5. Interviews (global list).
    await page.goto(`${BASE_URL}/interviews`, { waitUntil: 'load' });
    await page.waitForSelector('.page-title');
    await wait(700);
    await shot('interviews');

    // 6. Offers.
    await page.goto(`${BASE_URL}/offers`, { waitUntil: 'load' });
    await page.waitForSelector('.page-title');
    await wait(700);
    await shot('offers');

    // 7. Settings.
    await page.goto(`${BASE_URL}/settings`, { waitUntil: 'load' });
    await page.waitForSelector('.page-title');
    await wait(700);
    await shot('settings');

    // 8. Mobile view with the navigation drawer open (phone viewport).
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
    await page.goto(`${BASE_URL}/`, { waitUntil: 'load' });
    await page.waitForSelector('.stat-value');
    await wait(600);
    await page.click('.nav-toggle');
    await wait(500);
    await shot('mobile-dashboard');
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
