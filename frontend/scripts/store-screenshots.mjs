/**
 * Capture App Store / Play Store screenshots at the required device sizes.
 *
 * Prerequisites:
 *   - Backend + frontend running with demo data (docker compose up --build)
 *   - CHROME_PATH set to installed Chrome
 *
 * Usage:
 *   CHROME_PATH="..." node scripts/store-screenshots.mjs appstore
 *   CHROME_PATH="..." node scripts/store-screenshots.mjs playstore
 */
import { mkdir, cpSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import puppeteer from 'puppeteer-core';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '../..');
const BASE_URL = process.env.BASE_URL ?? 'http://localhost:5173';
const CHROME_PATH = process.env.CHROME_PATH;
const DEMO_EMAIL = 'demo@careerflow.app';
const DEMO_PASSWORD = 'DemoPass123!';

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

/** iPhone 15 Pro Max logical size @3x → 1290×2796 (App Store 6.7") */
const APPSTORE_VIEWPORT = { width: 430, height: 932, deviceScaleFactor: 3 };

/** Pixel 7 logical size @2.5x → 1080×2400 (Play Store phone) */
const PLAYSTORE_VIEWPORT = { width: 432, height: 960, deviceScaleFactor: 2.5 };

const SCREENS = [
  { name: '01_login', path: '/login', setup: async (page) => {
    await page.waitForSelector('.auth-card');
  }},
  { name: '02_dashboard', path: '/', setup: null, needsAuth: true },
  { name: '03_applications', path: '/applications', setup: async (page) => {
    await page.waitForSelector('.kanban-col');
  }, needsAuth: true },
  { name: '04_analytics', path: '/analytics', setup: async (page) => {
    await page.waitForSelector('svg.recharts-surface', { timeout: 15000 });
    await wait(800);
  }, needsAuth: true },
  { name: '05_interviews', path: '/interviews', setup: async (page) => {
    await page.waitForSelector('.page-title');
  }, needsAuth: true },
];

async function login(page) {
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'load' });
  await page.waitForSelector('#email');
  await page.type('#email', DEMO_EMAIL);
  await page.type('#password', DEMO_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForFunction(() => window.location.pathname === '/', { timeout: 20000 });
  await page.waitForSelector('.stat-value');
  await wait(600);
}

async function captureSet(page, outDir, viewport) {
  await mkdir(outDir, { recursive: true });
  await page.setViewport(viewport);

  let authed = false;
  for (const screen of SCREENS) {
    if (screen.needsAuth && !authed) {
      await login(page);
      authed = true;
    }
    await page.goto(`${BASE_URL}${screen.path}`, { waitUntil: 'load' });
    if (screen.setup) await screen.setup(page);
    else await wait(600);
    const file = resolve(outDir, `${screen.name}.png`);
    await page.screenshot({ path: file });
    console.log(`captured ${file}`);
  }
}

function copyDir(src, dest) {
  mkdir(dest, { recursive: true }, () => {});
  for (const name of ['01_login.png', '02_dashboard.png', '03_applications.png', '04_analytics.png', '05_interviews.png']) {
    cpSync(resolve(src, name), resolve(dest, name));
  }
}

async function main() {
  const target = process.argv[2] ?? 'appstore';
  if (!CHROME_PATH) throw new Error('Set CHROME_PATH to the Chrome executable.');

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });

  try {
    const page = await browser.newPage();

    if (target === 'appstore' || target === 'all') {
      const primary = resolve(REPO_ROOT, 'fastlane/metadata/ios/en-US/screenshots/iphone67');
      await captureSet(page, primary, APPSTORE_VIEWPORT);
      // Re-use 6.7" captures for other required slots (same aspect ratio family)
      copyDir(primary, resolve(REPO_ROOT, 'fastlane/metadata/ios/en-US/screenshots/iphone65'));
      copyDir(primary, resolve(REPO_ROOT, 'fastlane/metadata/ios/en-US/screenshots/iphone55'));
      copyDir(primary, resolve(REPO_ROOT, 'store-meta/appstore/screenshots'));
      console.log('App Store screenshots → fastlane/metadata/ios/en-US/screenshots/');
    }

    if (target === 'playstore' || target === 'all') {
      const out = resolve(REPO_ROOT, 'store-meta/playstore/screenshots');
      await captureSet(page, out, PLAYSTORE_VIEWPORT);
      console.log('Play Store screenshots → store-meta/playstore/screenshots/');
    }
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
